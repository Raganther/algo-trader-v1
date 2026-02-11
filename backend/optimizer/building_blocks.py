"""Composable building blocks for strategy generation.

Each block is a factory function that returns a callable.
Blocks are stateless where possible; zone-based entries use
the state dict passed by ComposableStrategy.

Categories:
- Entry signals: (row, prev_row, state) -> 'long' | 'short' | None
- Exit rules:    (row, side, entry_price, state) -> bool
- Filters:       (row) -> bool (True = allow trading)
- Sizers:        (equity, price, atr_val) -> float (position size)
"""


# ─── ENTRY SIGNALS ──────────────────────────────────────────────


def stochrsi_cross(oversold=20, overbought=80):
    """Zone-based mean reversion — the proven GLD entry."""

    def entry(row, prev_row, state):
        k = row["k"]
        prev_k = prev_row["k"]

        # Track oversold zone
        if prev_k <= oversold:
            state["in_oversold"] = True
        if k > 50:
            if state.get("in_oversold"):
                state["in_oversold"] = False
                return "long"
            state["in_oversold"] = False

        # Track overbought zone
        if prev_k >= overbought:
            state["in_overbought"] = True
        if k < 50:
            if state.get("in_overbought"):
                state["in_overbought"] = False
                return "short"
            state["in_overbought"] = False

        return None

    entry.name = f"stochrsi_cross(os={oversold},ob={overbought})"
    entry.required_cols = ["k"]
    return entry


def macd_cross():
    """MACD line crosses signal line."""

    def entry(row, prev_row, state):
        if prev_row["macd"] <= prev_row["macd_signal"] and row["macd"] > row["macd_signal"]:
            return "long"
        if prev_row["macd"] >= prev_row["macd_signal"] and row["macd"] < row["macd_signal"]:
            return "short"
        return None

    entry.name = "macd_cross"
    entry.required_cols = ["macd", "macd_signal"]
    return entry


def bollinger_bounce():
    """Mean reversion — enter when price bounces off Bollinger band."""

    def entry(row, prev_row, state):
        if prev_row["Close"] <= prev_row["bb_lower"] and row["Close"] > row["bb_lower"]:
            return "long"
        if prev_row["Close"] >= prev_row["bb_upper"] and row["Close"] < row["bb_upper"]:
            return "short"
        return None

    entry.name = "bollinger_bounce"
    entry.required_cols = ["bb_upper", "bb_lower"]
    return entry


def donchian_breakout():
    """Trend following — price breaks Donchian channel."""

    def entry(row, prev_row, state):
        if row["Close"] > row["don_upper"]:
            return "long"
        if row["Close"] < row["don_lower"]:
            return "short"
        return None

    entry.name = "donchian_breakout"
    entry.required_cols = ["don_upper", "don_lower"]
    return entry


def rsi_extreme(oversold=30, overbought=70):
    """Mean reversion on RSI extremes."""

    def entry(row, prev_row, state):
        if prev_row["rsi"] <= oversold and row["rsi"] > oversold:
            return "long"
        if prev_row["rsi"] >= overbought and row["rsi"] < overbought:
            return "short"
        return None

    entry.name = f"rsi_extreme(os={oversold},ob={overbought})"
    entry.required_cols = ["rsi"]
    return entry


def sma_cross(fast=50, slow=200):
    """Trend following — fast SMA crosses slow SMA."""

    def entry(row, prev_row, state):
        if prev_row["sma_50"] <= prev_row["sma_200"] and row["sma_50"] > row["sma_200"]:
            return "long"
        if prev_row["sma_50"] >= prev_row["sma_200"] and row["sma_50"] < row["sma_200"]:
            return "short"
        return None

    entry.name = "sma_cross(50/200)"
    entry.required_cols = ["sma_50", "sma_200"]
    return entry


# ─── EXIT RULES ──────────────────────────────────────────────────


def opposite_zone(oversold=20, overbought=80):
    """Exit when StochRSI enters opposite zone."""

    def exit_fn(row, side, entry_price, state):
        if side == "long" and row["k"] > overbought:
            return True
        if side == "short" and row["k"] < oversold:
            return True
        return False

    exit_fn.name = f"opposite_zone(os={oversold},ob={overbought})"
    return exit_fn


def atr_stop(multiplier=3.0):
    """Fixed stop loss at N * ATR from entry."""

    def exit_fn(row, side, entry_price, state):
        stop_dist = state.get("entry_atr", row["atr"]) * multiplier
        if side == "long" and row["Low"] <= entry_price - stop_dist:
            return True
        if side == "short" and row["High"] >= entry_price + stop_dist:
            return True
        return False

    exit_fn.name = f"atr_stop({multiplier}x)"
    return exit_fn


def bollinger_exit():
    """Exit when price reaches opposite Bollinger band."""

    def exit_fn(row, side, entry_price, state):
        if side == "long" and row["Close"] >= row["bb_upper"]:
            return True
        if side == "short" and row["Close"] <= row["bb_lower"]:
            return True
        return False

    exit_fn.name = "bollinger_exit"
    return exit_fn


def donchian_exit():
    """Exit when price breaks Donchian exit channel."""

    def exit_fn(row, side, entry_price, state):
        if side == "long" and row["Close"] < row["don_exit_lower"]:
            return True
        if side == "short" and row["Close"] > row["don_exit_upper"]:
            return True
        return False

    exit_fn.name = "donchian_exit"
    return exit_fn


def trailing_atr(multiplier=2.0):
    """Trailing stop based on ATR distance from highest/lowest since entry."""

    def exit_fn(row, side, entry_price, state):
        atr_val = row["atr"]
        if atr_val <= 0:
            return False

        # Track best price since entry
        if side == "long":
            best = state.get("best_price", entry_price)
            if row["High"] > best:
                best = row["High"]
                state["best_price"] = best
            if row["Low"] <= best - atr_val * multiplier:
                return True

        elif side == "short":
            best = state.get("best_price", entry_price)
            if row["Low"] < best:
                best = row["Low"]
                state["best_price"] = best
            if row["High"] >= best + atr_val * multiplier:
                return True

        return False

    exit_fn.name = f"trailing_atr({multiplier}x)"
    return exit_fn


# ─── REGIME FILTERS ──────────────────────────────────────────────


def no_filter():
    """No filter — always allow trading."""

    def filter_fn(row):
        return True

    filter_fn.name = "no_filter"
    return filter_fn


def adx_ranging(threshold=25):
    """Only trade when ADX < threshold (ranging market)."""

    def filter_fn(row):
        return row["adx"] < threshold

    filter_fn.name = f"adx_ranging(<{threshold})"
    return filter_fn


def adx_trending(threshold=25):
    """Only trade when ADX > threshold (trending market)."""

    def filter_fn(row):
        return row["adx"] > threshold

    filter_fn.name = f"adx_trending(>{threshold})"
    return filter_fn


def chop_trending(threshold=38.2):
    """CHOP < 38.2 = directional market (trending)."""

    def filter_fn(row):
        return row["chop"] < threshold

    filter_fn.name = f"chop_trending(<{threshold})"
    return filter_fn


def chop_ranging(threshold=61.8):
    """CHOP > 61.8 = choppy market (ranging)."""

    def filter_fn(row):
        return row["chop"] > threshold

    filter_fn.name = f"chop_ranging(>{threshold})"
    return filter_fn


def sma_uptrend():
    """Only trade long when price above SMA 200."""

    def filter_fn(row):
        return row["Close"] > row["sma_200"]

    filter_fn.name = "sma_uptrend"
    return filter_fn


# ─── POSITION SIZERS ─────────────────────────────────────────────


def fixed_pct(pct=0.25):
    """Fixed percentage of equity per trade."""

    def sizer(equity, price, atr_val):
        return (equity * pct) / price

    sizer.name = f"fixed_pct({int(pct*100)}%)"
    return sizer


def risk_atr(risk_pct=0.02, atr_mult=3.0):
    """Risk-based sizing: risk_pct of equity, stop at atr_mult * ATR."""

    def sizer(equity, price, atr_val):
        stop_dist = atr_val * atr_mult
        if stop_dist <= 0:
            return 0
        size = (equity * risk_pct) / stop_dist
        max_size = (equity * 0.25) / price
        return min(size, max_size)

    sizer.name = f"risk_atr({int(risk_pct*100)}%,{atr_mult}x)"
    return sizer


# ─── BLOCK REGISTRY ──────────────────────────────────────────────

# Default blocks used by the combination generator.
# Each list can be extended without changing other code.

ENTRIES = [
    stochrsi_cross(oversold=20, overbought=80),
    stochrsi_cross(oversold=15, overbought=85),
    macd_cross(),
    bollinger_bounce(),
    donchian_breakout(),
    rsi_extreme(oversold=30, overbought=70),
    sma_cross(),
]

EXITS = [
    opposite_zone(oversold=20, overbought=80),
    atr_stop(multiplier=2.0),
    atr_stop(multiplier=3.0),
    bollinger_exit(),
    donchian_exit(),
    trailing_atr(multiplier=2.0),
    trailing_atr(multiplier=3.0),
]

FILTERS = [
    no_filter(),
    adx_ranging(threshold=25),
    adx_trending(threshold=25),
    chop_trending(),
    chop_ranging(),
    sma_uptrend(),
]

SIZERS = [
    fixed_pct(0.25),
    risk_atr(risk_pct=0.02, atr_mult=2.0),
    risk_atr(risk_pct=0.02, atr_mult=3.0),
]
