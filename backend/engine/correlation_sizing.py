"""Correlation-aware position sizing.

When a bot enters a position, count peers from the same cluster currently
held in the broker account and scale the per-trade risk fraction by 1/N
(N = existing peers + self). Already-open peers are not resized.

See plan: equal-split risk parity, V1 — live discount only.
"""

CLUSTERS = {
    "gold": frozenset({"GLD", "IAU", "SLV", "GDX"}),
    "energy": frozenset({"OIH", "XOP", "XLE"}),
    "biotech": frozenset({"XBI"}),
}

_SYMBOL_TO_CLUSTER = {
    sym: name for name, members in CLUSTERS.items() for sym in members
}

BASE_RISK = 0.02

# Diagnostic toggle. Default True everywhere (live bots, single-symbol backtests,
# default portfolio runs). The portfolio CLI flips this to False when invoked
# with --no-correlation-discount so the with-vs-without backtest can be run as
# an apples-to-apples comparison.
DISCOUNT_ENABLED = True

# Cluster-aware notional cap (Apr 30 2026 — addresses the V2 finding that the
# 25% per-position cap is the binding constraint, and 4 gold bots can therefore
# pile up to 100% notional on one correlated bet). The cluster total notional
# is capped at CLUSTER_CAP_FRAC of equity; new entries are downsized to fit
# remaining cluster headroom, naturally skipping when headroom < 1 share.
#
# 0.50 = max 2 full-cap positions per cluster. Picked because:
#   - Gold pile-up: caps 4-bot total at 50% vs current potential 100%.
#   - Energy: caps 3-bot total at 50% vs current 75%.
#   - Biotech (single member): cap never binds (25% < 50%) — single-symbol
#     backtests and the lone XBI bot are unaffected.
#   - Leaves room for at least one other cluster to hold a full position
#     without breaching 100% portfolio notional.
# Default OFF — Apr 30 2026 with-vs-without backtest at FRAC=0.50 fails the
# roadmap decision rule (DD −1.14pp ✓ but Sharpe −0.14 exceeds the ≤0.1 loss
# tolerance; return drops 474.67% → 413.38%). Code path preserved for the
# high-volatility regime where the cap would bind more selectively, and as
# a diagnostic toggle on the portfolio runner. Live bots and default backtest
# runs are unaffected.
CLUSTER_CAP_ENABLED = False
CLUSTER_CAP_FRAC = 0.50

# DEFAULT ON since Apr 30 2026 PM. Run A (7-bot + cap @ 100%) confirmed the cap
# is a tiny structural positive: Sharpe 4.86 → 4.95 (+0.09), DD 3.58% → 3.41%,
# trades 4413 → 4344 (the cap binds on gold N=4 stacking, 4.2% of bars in
# baseline). On the live 7-bot lineup the cap rarely binds because cluster
# correlation keeps max-concurrent ≈ 7 with total notional well under 100%,
# but the guard is armed for any future expansion or unusual stacking event.
# Without it, universe expansion (e.g. 20 bots) silently runs at ~4.75× leverage —
# see `.claude/strategies/portfolio-runner-rotation-v1.md`. Toggle preserved for
# diagnostic flips via `--portfolio-cap-frac` on the portfolio runner.

# Portfolio-level total-notional cap (Apr 30 2026 PM — promoted from rotation V1
# side finding: 20-bot universe-expansion control hit max-concurrent 19 →
# ~4.75× leverage on $94k from per-bot fixed-equity sizing). Without an aggregate
# constraint, each bot independently sizes 25% off initial_capital regardless of
# what other bots already hold. The 7-bot baseline didn't surface this because
# cluster correlation kept max-concurrent low. Universe expansion (rotation,
# IWM expansion, anything multi-cluster) requires this cap to produce
# deployable return numbers.
#
# Default OFF to preserve byte-identical baseline. Enable via
# `--portfolio-cap-frac N` on the portfolio runner. Recommended: 1.0 for
# cash-account parity, 2.0 for Reg-T margin parity.
PORTFOLIO_CAP_ENABLED = True
PORTFOLIO_CAP_FRAC = 1.0


def cluster_for(symbol):
    return _SYMBOL_TO_CLUSTER.get(symbol)


def risk_fraction_for(symbol, broker_positions, base_risk=BASE_RISK):
    """Return per-trade risk fraction discounted by cluster occupancy.

    `broker_positions` is the dict returned by broker.get_positions(): keys
    are symbols, values are dicts containing at least a 'size' field.
    A flat position (size == 0) does not count as a peer.

    Self is always counted in N (the caller is about to enter).
    """
    if not DISCOUNT_ENABLED:
        return base_risk

    cluster = _SYMBOL_TO_CLUSTER.get(symbol)
    if cluster is None:
        return base_risk

    members = CLUSTERS[cluster]
    peers_held = 0
    for peer_sym in members:
        if peer_sym == symbol:
            continue
        pos = broker_positions.get(peer_sym) if broker_positions else None
        if pos is None:
            continue
        try:
            size = float(pos.get("size", 0))
        except (AttributeError, TypeError, ValueError):
            size = 0.0
        if size != 0:
            peers_held += 1

    n = peers_held + 1
    return base_risk / n


def cluster_cap_max_size(symbol, broker_positions, equity, entry_price):
    """Max shares allowed by the cluster-notional cap.

    Returns float('inf') when the cap is disabled, the symbol is not in any
    cluster, or entry_price <= 0. Otherwise returns
        (equity * CLUSTER_CAP_FRAC - current_cluster_notional) / entry_price
    where current_cluster_notional uses cost basis ('avg_price' × |size|) for
    already-open peers in the same cluster (self excluded — caller's new size
    will be capped against this remaining headroom).

    Cost basis is used (not current price) for V1 simplicity: the difference
    vs current-price valuation is bounded by trail drift (~2 ATR ≈ 1% of
    price), small relative to a 50% cluster headroom.
    """
    if not CLUSTER_CAP_ENABLED:
        return float('inf')
    cluster = _SYMBOL_TO_CLUSTER.get(symbol)
    if cluster is None or entry_price <= 0:
        return float('inf')

    members = CLUSTERS[cluster]
    cluster_notional = 0.0
    if broker_positions:
        for peer_sym in members:
            if peer_sym == symbol:
                continue
            pos = broker_positions.get(peer_sym)
            if pos is None:
                continue
            try:
                size = float(pos.get('size', 0))
                avg = float(pos.get('avg_price', 0))
            except (AttributeError, TypeError, ValueError):
                continue
            if size != 0 and avg > 0:
                cluster_notional += abs(size) * avg

    remaining = (equity * CLUSTER_CAP_FRAC) - cluster_notional
    if remaining <= 0:
        return 0.0
    return remaining / entry_price


def portfolio_cap_max_size(broker_positions, equity, entry_price):
    """Max shares allowed by the *portfolio-level* total-notional cap.

    Returns float('inf') when the cap is disabled or entry_price <= 0.
    Otherwise returns:
        (equity * PORTFOLIO_CAP_FRAC - sum(|peer_size| * peer_avg_price)) / entry_price

    Cost basis used (matches cluster_cap_max_size). Sums *all* open peer
    positions across all clusters and unclustered symbols — this is the
    aggregate guard. Self is excluded; the new entry's size is then capped
    against this remaining headroom.
    """
    if not PORTFOLIO_CAP_ENABLED or entry_price <= 0:
        return float('inf')

    total_notional = 0.0
    if broker_positions:
        for peer_sym, pos in broker_positions.items():
            try:
                size = float(pos.get('size', 0))
                avg = float(pos.get('avg_price', 0))
            except (AttributeError, TypeError, ValueError):
                continue
            if size != 0 and avg > 0:
                total_notional += abs(size) * avg

    remaining = (equity * PORTFOLIO_CAP_FRAC) - total_notional
    if remaining <= 0:
        return 0.0
    return remaining / entry_price
