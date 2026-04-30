"""Regime-aware asset rotation — V1.

Pre-classifies daily bars per symbol once (causal indicators, no look-ahead),
resamples to W-FRI snapshots, exposes a controller queryable per (symbol, ts):
"is this bot active right now?" The portfolio runner mutates each strategy's
`rotation_paused` flag at the W-FRI boundary based on the active set.

Pause-only semantics: paused symbols cannot open new entries. Existing
positions still ratchet, trail, and exit naturally on stop / signal.

V1 rule: TRENDING_UP only. Rule registry takes new functions trivially.
"""
from __future__ import annotations

from typing import Callable, Iterable

import pandas as pd

from backend.indicators.regime import (
    classify_regime,
    TRENDING_UP,
    TRENDING_DOWN,
    RANGING,
    HIGH_VOL,
)


def build_weekly_regime_panel(
    db,
    symbols: list[str],
    end_date: pd.Timestamp | None = None,
    min_bars: int = 220,
) -> pd.DataFrame:
    """Per-symbol daily classification, resampled to W-FRI.

    For each symbol: pull daily bars from `price_data_daily` via
    `db.get_daily_bars(symbol)`, run `classify_regime` once (causal — same
    label sequence as re-classifying at every Friday), drop the first
    `min_bars` of indicator warm-up, normalise the index to UTC midnight,
    and resample to weekly W-FRI taking `last`.

    Returns a wide panel: index = W-FRI date (UTC midnight),
    columns = symbol, values = regime label string. Forward-filled within
    each column so a missing Friday (e.g. holiday) inherits the prior label.
    """
    end_ts = pd.Timestamp(end_date).tz_convert("UTC") if end_date is not None and pd.Timestamp(end_date).tzinfo else (
        pd.Timestamp(end_date).tz_localize("UTC") if end_date is not None else None
    )

    series_by_symbol: dict[str, pd.Series] = {}
    for sym in symbols:
        df = db.get_daily_bars(sym)
        if df is None or df.empty or len(df) < min_bars:
            # Not enough warm-up; symbol will be all-NaN and never active.
            continue
        # Cap to end_date if provided
        if end_ts is not None:
            df = df[df.index <= end_ts]
        if len(df) < min_bars:
            continue

        labels = classify_regime(df)
        labels = labels.iloc[min_bars:]  # drop warm-up where indicators are unstable
        # Normalise to UTC midnight for clean resampling
        idx = pd.to_datetime(labels.index)
        if idx.tz is None:
            idx = idx.tz_localize("UTC")
        else:
            idx = idx.tz_convert("UTC")
        labels.index = idx.normalize()
        # Drop duplicate timestamps (some price feeds have multiple rows per
        # day after normalisation) — keep last as the authoritative label.
        labels = labels[~labels.index.duplicated(keep="last")]
        series_by_symbol[sym] = labels

    if not series_by_symbol:
        # Return empty panel with the requested symbol columns so consumers don't crash
        return pd.DataFrame(columns=symbols)

    daily_panel = pd.DataFrame(series_by_symbol).sort_index()
    weekly_panel = daily_panel.resample("W-FRI").last().ffill()
    # Ensure every requested symbol is a column even if it had no data
    for sym in symbols:
        if sym not in weekly_panel.columns:
            weekly_panel[sym] = pd.NA
    return weekly_panel[list(symbols)]


# --- Rotation rule registry -----------------------------------------------

def rule_trending_up(row: pd.Series) -> set[str]:
    """V1 rule: active = symbols whose regime label is TRENDING_UP."""
    return set(row[row == TRENDING_UP].index)


def rule_always_active(row: pd.Series) -> set[str]:
    """Validation aid — every symbol always active. Used for plumbing equivalence test."""
    return set(row.index)


def rule_ranging(row: pd.Series) -> set[str]:
    """V2 rule candidate: active = symbols whose regime label is RANGING.

    The strategy's natural habitat — its ADX < 20 entry filter aligns with the
    RANGING regime definition (low ADX). Tests whether the V1 TRENDING_UP
    failure was rule-specific (this should fix it) or concept-specific.
    """
    return set(row[row == RANGING].index)


def rule_no_trending_down_or_high_vol(row: pd.Series) -> set[str]:
    """Permissive rule: active = anything that ISN'T TRENDING_DOWN or HIGH_VOL.

    A "kill switch" framing — pause only the regimes the framework is known
    to handle worst (sharp transitions, volatility spikes). RANGING and
    TRENDING_UP both stay active.
    """
    bad = {TRENDING_DOWN, HIGH_VOL}
    return set(row[~row.isin(bad)].index)


ROTATION_RULES: dict[str, Callable[[pd.Series], set[str]]] = {
    "trending_up": rule_trending_up,
    "ranging": rule_ranging,
    "no_bad_regime": rule_no_trending_down_or_high_vol,
    "always_active": rule_always_active,
}


# --- Active-set controller ------------------------------------------------

class RotationController:
    """Tracks which symbols are active for the week containing a given timestamp.

    Built once with a precomputed W-FRI regime panel. The runner queries
    `active_set_for(ts)` at each weekly boundary and propagates the result
    onto `strategy.rotation_paused`.

    Causal: for a bar at timestamp ts, returns the active set computed from
    the most recent W-FRI snapshot with date <= ts. The W-FRI label was
    classified using daily bars with date <= that Friday.

    When `enabled=False`, every symbol is always active — gives byte-for-byte
    equivalence with the no-rotation baseline.
    """

    def __init__(
        self,
        regime_panel: pd.DataFrame,
        rule: Callable[[pd.Series], set[str]],
        symbols: Iterable[str],
        enabled: bool = True,
    ):
        self.symbols = list(symbols)
        self.rule = rule
        self.enabled = enabled
        # Sort for safe asof lookups
        self.panel = regime_panel.sort_index() if not regime_panel.empty else regime_panel
        self._rebalance_log: list[dict] = []
        # Cache last computed active set for the most recent panel index seen
        self._last_panel_idx = None
        self._last_active: set[str] = set()

    def _panel_row_for(self, ts: pd.Timestamp) -> pd.Series | None:
        if self.panel.empty:
            return None
        ts_norm = pd.Timestamp(ts)
        if ts_norm.tzinfo is None:
            ts_norm = ts_norm.tz_localize("UTC")
        else:
            ts_norm = ts_norm.tz_convert("UTC")
        # asof — most recent W-FRI snapshot with index <= ts_norm
        try:
            idx = self.panel.index.asof(ts_norm)
        except TypeError:
            # tz mismatch on panel index; coerce
            panel = self.panel.copy()
            panel.index = pd.to_datetime(panel.index).tz_convert("UTC")
            self.panel = panel
            idx = self.panel.index.asof(ts_norm)
        if pd.isna(idx):
            return None
        return self.panel.loc[idx]

    def active_set_for(self, ts: pd.Timestamp) -> set[str]:
        if not self.enabled:
            return set(self.symbols)
        row = self._panel_row_for(ts)
        if row is None:
            # Before any panel data — default to no symbols active.
            # (Rotation backtest always starts after a long warm-up; this is safe.)
            return set()
        # Drop NaN labels (symbol had no data this week)
        row = row.dropna()
        active = self.rule(row)
        # Intersect with the controller's known symbols set
        return active & set(self.symbols)

    def is_active(self, symbol: str, ts: pd.Timestamp) -> bool:
        return symbol in self.active_set_for(ts)

    def record_rebalance(self, ts: pd.Timestamp, active: set[str]) -> None:
        row = self._panel_row_for(ts)
        regimes_at_ts = row.dropna().to_dict() if row is not None else {}
        prev = self._last_active
        self._rebalance_log.append({
            "ts": pd.Timestamp(ts).isoformat(),
            "active": sorted(active),
            "added": sorted(active - prev),
            "removed": sorted(prev - active),
            "n_active": len(active),
            "regimes": regimes_at_ts,
        })
        self._last_active = set(active)

    def rebalance_log(self) -> list[dict]:
        return list(self._rebalance_log)
