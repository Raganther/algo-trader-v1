"""Generate all valid strategy combinations from building blocks.

Produces parameter dicts that can be passed to ComposableStrategy
and run through the sweep engine or backtester.
"""

import itertools

from backend.optimizer.building_blocks import ENTRIES, EXITS, FILTERS, SIZERS


# Compatibility rules: some entry/exit pairings don't make sense.
# e.g., a StochRSI entry pairs naturally with opposite_zone exit
# but a Donchian breakout entry shouldn't use opposite_zone exit.
#
# Rather than complex rules, we use a simple type system:
#   "mean_reversion" entries pair with "mean_reversion" + "generic" exits
#   "trend" entries pair with "trend" + "generic" exits

ENTRY_TYPE = {
    "stochrsi_cross": "mean_reversion",
    "macd_cross": "trend",
    "bollinger_bounce": "mean_reversion",
    "donchian_breakout": "trend",
    "rsi_extreme": "mean_reversion",
    "sma_cross": "trend",
}

EXIT_TYPE = {
    "opposite_zone": "mean_reversion",
    "atr_stop": "generic",
    "bollinger_exit": "mean_reversion",
    "donchian_exit": "trend",
    "trailing_atr": "generic",
}

# Filters also have compatibility
FILTER_COMPAT = {
    "mean_reversion": ["no_filter", "adx_ranging", "chop_ranging", "sma_uptrend"],
    "trend": ["no_filter", "adx_trending", "chop_trending", "sma_uptrend"],
}


def _get_base_name(block):
    """Extract base name (without parameters) from a block."""
    name = block.name
    paren = name.find("(")
    return name[:paren] if paren != -1 else name


def _is_compatible(entry, exit_fn, filter_fn):
    """Check if entry/exit/filter combination makes sense."""
    entry_base = _get_base_name(entry)
    exit_base = _get_base_name(exit_fn)
    filter_base = _get_base_name(filter_fn)

    entry_t = ENTRY_TYPE.get(entry_base, "generic")
    exit_t = EXIT_TYPE.get(exit_base, "generic")

    # Exit must match entry type or be generic
    if exit_t not in (entry_t, "generic"):
        return False

    # Filter must be compatible with entry type
    allowed = FILTER_COMPAT.get(entry_t, ["no_filter"])
    if filter_base not in allowed:
        return False

    return True


def generate_combinations(
    entries=None, exits=None, filters=None, sizers=None,
    symbol="GLD", timeframe="1h", check_compat=True
):
    """Generate all valid parameter dicts for ComposableStrategy.

    Args:
        entries: List of entry callables (default: all)
        exits: List of exit callables (default: all)
        filters: List of filter callables (default: all)
        sizers: List of sizer callables (default: all)
        symbol: Trading symbol
        timeframe: Bar timeframe
        check_compat: If True, skip incompatible combos

    Returns:
        List of (params_dict, label_string) tuples
    """
    entries = entries or ENTRIES
    exits = exits or EXITS
    filters = filters or FILTERS
    sizers = sizers or SIZERS

    combos = []

    for entry, exit_fn, filter_fn, sizer in itertools.product(
        entries, exits, filters, sizers
    ):
        if check_compat and not _is_compatible(entry, exit_fn, filter_fn):
            continue

        label = f"{entry.name} | {exit_fn.name} | {filter_fn.name} | {sizer.name}"

        params = {
            "symbol": symbol,
            "entry_fn": entry,
            "exit_fn": exit_fn,
            "filter_fn": filter_fn,
            "sizer_fn": sizer,
            # Label for experiment tracking
            "_entry_name": entry.name,
            "_exit_name": exit_fn.name,
            "_filter_name": filter_fn.name,
            "_sizer_name": sizer.name,
            "_label": label,
        }

        combos.append((params, label))

    return combos


def count_combinations(check_compat=True):
    """Count total combinations without generating them."""
    return len(generate_combinations(check_compat=check_compat))


def describe():
    """Print a summary of available blocks and combination counts."""
    print(f"Entries:  {len(ENTRIES)}")
    for e in ENTRIES:
        print(f"  - {e.name}")

    print(f"\nExits:   {len(EXITS)}")
    for e in EXITS:
        print(f"  - {e.name}")

    print(f"\nFilters: {len(FILTERS)}")
    for f in FILTERS:
        print(f"  - {f.name}")

    print(f"\nSizers:  {len(SIZERS)}")
    for s in SIZERS:
        print(f"  - {s.name}")

    total = len(ENTRIES) * len(EXITS) * len(FILTERS) * len(SIZERS)
    compatible = count_combinations(check_compat=True)
    print(f"\nTotal cartesian: {total}")
    print(f"After compatibility filter: {compatible}")
