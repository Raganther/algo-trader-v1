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
