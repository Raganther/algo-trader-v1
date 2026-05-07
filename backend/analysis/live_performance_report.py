"""Weekly live-performance report.

Pulls live-trade data and equity curve from Alpaca, computes the negative-signal
tripwires from CLAUDE.md (Sharpe, win rate, avg-win/avg-loss, right-tail count,
exit-reason mix), compares to backtest expectation, writes a markdown snapshot.

Run on demand:
    python3 -m backend.analysis.live_performance_report

Or via cron weekly. Reads ALPACA_API_KEY / ALPACA_SECRET_KEY from env.

Output: .claude/calibration/live-performance-report.md
"""

from __future__ import annotations

import os
import statistics
from datetime import datetime, timezone, timedelta
from pathlib import Path

import numpy as np

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import QueryOrderStatus
from alpaca.trading.requests import GetOrdersRequest, GetPortfolioHistoryRequest


# Forward-test clock reset May 7 2026 PM when HWM trail anchor was deployed live
# on all 7 bots (see trail-anchor-hwm.md). Pre-May-7 data was close-anchored;
# May 7 onward is HWM-anchored. Anchor live tripwires to HWM-backtest baseline.
DEPLOY_DATE = datetime(2026, 5, 7, 21, 0, tzinfo=timezone.utc)  # HWM live deploy
SYMBOLS = ["GLD", "IAU", "SLV", "GDX", "OIH", "XBI", "XOP"]

# May 7 2026 — HWM trail anchor is live. The 1-bar polling delay artifact that
# previously made backtest ~0.7 Sharpe optimistic is structurally bypassed by
# HWM (it anchors trail to the trade's actual high-water-mark, not a noisy
# bar-Close reference). Live expectation now anchors to HWM backtest baseline
# (Sharpe 5.73), not the close-anchored 4.95 - 0.7 adjustment.
BACKTEST_DELAY_ADJUSTMENT = 0.0  # HWM bypasses the artifact; no adjustment needed
BACKTEST_EXPECTED = {
    "annualised_return": 0.39,  # HWM long-window: +517% over 5.75y ≈ 39%/yr
    "sharpe_backtest": 5.73,    # HWM long-window 7-bot
    "sharpe": 5.73,             # live anchor = HWM backtest (no delay artifact)
    "max_dd_pct": 3.05,         # HWM long-window 7-bot
    "win_rate_low": 0.41,
    "win_rate_high": 0.47,
    "avg_win_loss_ratio_min": 1.3,
}

OUTPUT_PATH = Path(__file__).resolve().parents[2] / ".claude/calibration/live-performance-report.md"


def get_client() -> TradingClient:
    return TradingClient(os.environ["ALPACA_API_KEY"], os.environ["ALPACA_SECRET_KEY"], paper=True)


def pull_equity_curve(client: TradingClient, start: datetime) -> tuple[list[datetime], list[float]]:
    days = max(1, (datetime.now(timezone.utc) - start).days + 1)
    period = f"{days}D" if days <= 30 else "1M" if days <= 31 else "3M"
    req = GetPortfolioHistoryRequest(period=period, timeframe="1D")
    h = client.get_portfolio_history(history_filter=req)
    timestamps = [datetime.fromtimestamp(t, tz=timezone.utc) for t in h.timestamp]
    equity = list(h.equity)
    pairs = [(t, e) for t, e in zip(timestamps, equity) if t >= start - timedelta(days=1) and e is not None]
    return [p[0] for p in pairs], [p[1] for p in pairs]


def pull_closed_orders(client: TradingClient, start: datetime) -> list:
    req = GetOrdersRequest(status=QueryOrderStatus.CLOSED, after=start, symbols=SYMBOLS, limit=500)
    return [o for o in client.get_orders(filter=req) if o.filled_avg_price is not None]


def compute_equity_metrics(equity: list[float]) -> dict:
    if len(equity) < 2:
        last = float(equity[-1]) if equity else 0.0
        return {
            "return_pct": 0.0, "sharpe": 0.0, "max_dd_pct": 0.0, "trading_days": 0,
            "start_equity": last, "end_equity": last, "rets": np.array([]),
        }
    arr = np.array(equity)
    rets = np.diff(arr) / arr[:-1]
    mean = rets.mean()
    std = rets.std(ddof=1) if len(rets) > 1 else 0.0
    sharpe = (mean / std * np.sqrt(252)) if std > 0 else 0.0
    peak = np.maximum.accumulate(arr)
    dd = (arr - peak) / peak
    max_dd_pct = abs(dd.min()) * 100
    return {
        "return_pct": (arr[-1] / arr[0] - 1) * 100,
        "sharpe": float(sharpe),
        "max_dd_pct": float(max_dd_pct),
        "trading_days": len(equity) - 1,
        "start_equity": float(arr[0]),
        "end_equity": float(arr[-1]),
        "rets": rets,
    }


def pair_trades(orders: list) -> list[dict]:
    """FIFO pair each closed cycle per symbol → per-trade P&L + duration + exit type."""
    by_sym: dict[str, list] = {}
    for o in sorted(orders, key=lambda x: x.filled_at):
        by_sym.setdefault(o.symbol, []).append(o)

    trades = []
    for sym, orders_for_sym in by_sym.items():
        position = 0.0
        entry_price = None
        entry_time = None
        entry_side = None
        for o in orders_for_sym:
            qty = float(o.qty)
            price = float(o.filled_avg_price)
            side = str(o.side).split(".")[-1].lower()
            order_type = str(getattr(o, "order_type", "")).split(".")[-1].lower()
            if position == 0:
                position = qty if side == "buy" else -qty
                entry_price = price
                entry_time = o.filled_at
                entry_side = side
            else:
                # Closing the position
                if entry_side == "buy":
                    pnl = (price - entry_price) * abs(position)
                else:
                    pnl = (entry_price - price) * abs(position)
                duration_min = (o.filled_at - entry_time).total_seconds() / 60
                trades.append({
                    "symbol": sym,
                    "entry_time": entry_time,
                    "exit_time": o.filled_at,
                    "side": entry_side,
                    "qty": abs(position),
                    "entry_price": entry_price,
                    "exit_price": price,
                    "pnl": pnl,
                    "duration_min": duration_min,
                    "exit_type": "stop" if "stop" in order_type else "market",
                })
                position = 0.0
                entry_price = None
                entry_time = None
                entry_side = None
    return trades


def compute_trade_metrics(trades: list[dict]) -> dict:
    if not trades:
        return {"n": 0}
    pnls = [t["pnl"] for t in trades]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p < 0]
    win_rate = len(wins) / len(pnls)
    avg_win = statistics.mean(wins) if wins else 0
    avg_loss = abs(statistics.mean(losses)) if losses else 0
    ratio = avg_win / avg_loss if avg_loss > 0 else 0
    stop_exits = sum(1 for t in trades if t["exit_type"] == "stop")
    return {
        "n": len(trades),
        "win_rate": win_rate,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "win_loss_ratio": ratio,
        "total_pnl": sum(pnls),
        "stop_exit_pct": stop_exits / len(trades) * 100,
        "by_symbol": {
            sym: {
                "n": sum(1 for t in trades if t["symbol"] == sym),
                "pnl": sum(t["pnl"] for t in trades if t["symbol"] == sym),
                "wins": sum(1 for t in trades if t["symbol"] == sym and t["pnl"] > 0),
            }
            for sym in SYMBOLS
        },
    }


def assess_tripwires(eq: dict, tr: dict) -> list[tuple[str, str, str]]:
    """Return list of (severity, signal, note). Severity: ok / watch / warn."""
    out = []
    days = eq["trading_days"]

    # Tripwire bars anchored to HWM backtest expectation (Sharpe 5.73).
    # HWM bypasses the 1-bar polling delay artifact, so live should track HWM
    # backtest within noise — no -0.7 adjustment needed.
    # Bars: 1.5 (30d) / 3.0 (60d) / 4.0 (90d) — proportionally scaled from
    # the close-anchored thresholds (0.5/1.5/2.0 against 4.25 expectation).
    if days >= 30:
        bar = 1.5 if days < 60 else 3.0 if days < 90 else 4.0
        if eq["sharpe"] < bar:
            out.append(("warn", f"Live Sharpe {eq['sharpe']:.2f} < {bar:.1f}", f"At {days} days, expected ≥ {bar:.1f}"))
        else:
            out.append(("ok", f"Live Sharpe {eq['sharpe']:.2f} ≥ {bar:.1f}", f"At {days} days threshold"))
    else:
        out.append(("watch", f"Live Sharpe {eq['sharpe']:.2f}", f"Threshold not yet binding ({days} days, need 30+)"))

    if eq["max_dd_pct"] > BACKTEST_EXPECTED["max_dd_pct"] + 1.6:
        out.append(("warn", f"Max DD {eq['max_dd_pct']:.2f}% exceeds backtest+1.6pp", f"Backtest {BACKTEST_EXPECTED['max_dd_pct']:.2f}%"))
    else:
        out.append(("ok", f"Max DD {eq['max_dd_pct']:.2f}% within tolerance", f"Backtest {BACKTEST_EXPECTED['max_dd_pct']:.2f}%, +1.6pp tolerance"))

    if tr.get("n", 0) >= 20:
        if tr["win_rate"] < 0.35:
            out.append(("warn", f"Win rate {tr['win_rate']*100:.1f}% < 35%", f"Backtest 41–47%"))
        elif tr["win_rate"] < BACKTEST_EXPECTED["win_rate_low"]:
            out.append(("watch", f"Win rate {tr['win_rate']*100:.1f}% below backtest band", f"Backtest 41–47%"))
        else:
            out.append(("ok", f"Win rate {tr['win_rate']*100:.1f}% in band", f"Backtest 41–47%"))

        if tr["win_loss_ratio"] < 1.3:
            out.append(("warn", f"Avg-win/avg-loss {tr['win_loss_ratio']:.2f} < 1.3", "Right tail collapsing"))
        else:
            out.append(("ok", f"Avg-win/avg-loss {tr['win_loss_ratio']:.2f} ≥ 1.3", "Right tail intact"))
    else:
        out.append(("watch", f"Trade sample {tr.get('n',0)} too small", "Need 20+ trades for distributional read"))

    if "rets" in eq and len(eq["rets"]) >= 8:
        big_days = (np.abs(eq["rets"]) > 0.005).sum()
        big_per_8d = big_days / len(eq["rets"]) * 8
        if big_per_8d < 0.5:
            out.append(("warn", f"|daily P&L|>0.5% only {big_days}× in {len(eq['rets'])}d", "Right tail missing"))
        else:
            out.append(("ok", f"Big-day rate {big_per_8d:.1f}/8d", "Backtest expects ~1/8d"))

    return out


def write_report(eq: dict, tr: dict, tripwires: list, equity_series: list[tuple[datetime, float]]) -> None:
    now = datetime.now(timezone.utc)
    sev_marker = {"ok": "✓", "watch": "·", "warn": "⚠"}

    lines = [
        f"Status: current | Epistemic: live observation | Last verified: {now.strftime('%Y-%m-%d')} ({now.strftime('%H:%M UTC')})",
        "",
        "# Live Performance Report",
        "",
        f"Live forward-test on 7-bot lineup, deployed Apr 15-16 (metals four) + Apr 28 (energy/biotech three). "
        f"Re-run with `python3 -m backend.analysis.live_performance_report`.",
        "",
        "## Headline metrics (Apr 15 → today)",
        "",
        f"| Metric | Live | Backtest expectation | Status |",
        f"|---|---:|---:|---|",
        f"| Trading days | {eq['trading_days']} | – | – |",
        f"| Equity start → end | ${eq['start_equity']:,.0f} → ${eq['end_equity']:,.0f} | – | – |",
        f"| Cumulative return | {eq['return_pct']:+.2f}% | +{(eq['trading_days']/252)*BACKTEST_EXPECTED['annualised_return']*100:.2f}% | – |",
        f"| Sharpe (daily-resampled) | {eq['sharpe']:.2f} | {BACKTEST_EXPECTED['sharpe']:.2f} | – |",
        f"| Max DD | {eq['max_dd_pct']:.2f}% | {BACKTEST_EXPECTED['max_dd_pct']:.2f}% | – |",
        f"| Total trades closed | {tr.get('n', 0)} | – | – |",
    ]

    if tr.get("n", 0) > 0:
        lines += [
            f"| Win rate | {tr['win_rate']*100:.1f}% | 41–47% | – |",
            f"| Avg win / avg loss | {tr['win_loss_ratio']:.2f} | ≥1.3 | – |",
            f"| Total realised P&L | ${tr['total_pnl']:,.2f} | – | – |",
            f"| Stop-exit % | {tr['stop_exit_pct']:.1f}% | – | – |",
        ]

    lines += ["", "## Tripwires", "", "| Status | Signal | Context |", "|---|---|---|"]
    for sev, signal, note in tripwires:
        lines.append(f"| {sev_marker[sev]} {sev.upper()} | {signal} | {note} |")

    if tr.get("n", 0) > 0:
        lines += ["", "## Per-symbol breakdown", "", "| Symbol | Trades | P&L | Wins |", "|---|---:|---:|---:|"]
        for sym, s in tr["by_symbol"].items():
            if s["n"] > 0:
                lines.append(f"| {sym} | {s['n']} | ${s['pnl']:+,.2f} | {s['wins']} |")

    lines += ["", "## Daily equity curve", "", "```"]
    for t, e in equity_series:
        lines.append(f"  {t.strftime('%Y-%m-%d')}  ${e:>10,.2f}")
    lines += ["```", "",
              "## Decision rules (from CLAUDE.md tripwires section)",
              "",
              "Anchored to **HWM backtest expectation** (Sharpe 5.73, deployed live May 7 2026 PM). HWM bypasses the 1-bar polling delay artifact (see `trail-anchor-hwm.md`), so live should track backtest within noise.",
              "",
              "- **Sharpe < 1.5 at 30 days → degraded.** Investigate execution (slippage, fills, stop behaviour, HWM tracking).",
              "- **Sharpe < 3.0 at 60 days → degraded.** Stop adding capital; root-cause analysis.",
              "- **Sharpe < 4.0 at 90 days → stop & investigate.** Real-money pilot blocked.",
              "- **Win rate < 35% on 50+ trades → distributional shift.** Compare to backtest per-symbol win rates.",
              "- **Avg-win/avg-loss < 1.3 → right tail collapsing.** Trailing-stop or K-exit may be clipping winners.",
              "- **No |daily P&L|>0.5% day in 4+ weeks → swing days missing.** The strategy depends on these.",
              "- **Single-day loss > 1.5% of equity → cluster correlation tighter live than backtest.**",
              ""]

    OUTPUT_PATH.write_text("\n".join(lines))
    print(f"Wrote {OUTPUT_PATH}")


def main() -> None:
    client = get_client()
    print(f"Pulling equity curve since {DEPLOY_DATE.date()}...")
    timestamps, equity = pull_equity_curve(client, DEPLOY_DATE)
    eq_metrics = compute_equity_metrics(equity)
    print(f"  {eq_metrics['trading_days']} trading days, equity {eq_metrics['start_equity']:,.0f} → {eq_metrics['end_equity']:,.0f}, Sharpe {eq_metrics['sharpe']:.2f}")

    print("Pulling closed orders...")
    orders = pull_closed_orders(client, DEPLOY_DATE)
    trades = pair_trades(orders)
    tr_metrics = compute_trade_metrics(trades)
    print(f"  {tr_metrics.get('n', 0)} paired trades, win rate {tr_metrics.get('win_rate', 0)*100:.1f}%")

    tripwires = assess_tripwires(eq_metrics, tr_metrics)
    write_report(eq_metrics, tr_metrics, tripwires, list(zip(timestamps, equity)))


if __name__ == "__main__":
    main()
