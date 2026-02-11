"""Pre-compute all indicators on a DataFrame.

Called once per symbol/timeframe during ComposableStrategy init.
Adds indicator columns so building blocks can read them directly.
"""

import pandas as pd
from backend.indicators.stoch_rsi import StochRSI
from backend.indicators.adx import adx
from backend.indicators.atr import atr
from backend.indicators.macd import macd
from backend.indicators.bollinger import bollinger_bands
from backend.indicators.donchian import donchian_channels
from backend.indicators.rsi import rsi
from backend.indicators.sma import sma
from backend.indicators.chop import chop_index


def compute_indicators(df, config=None):
    """Compute all indicators and add columns to df.

    Args:
        df: DataFrame with Open, High, Low, Close columns.
        config: Optional dict to override indicator parameters.
            Defaults to standard settings.

    Returns:
        DataFrame with indicator columns added.
    """
    config = config or {}

    # StochRSI (stateful — must iterate)
    rsi_period = config.get("rsi_period", 14)
    stoch_period = config.get("stoch_period", 14)
    k_smooth = config.get("k_period", 3)
    d_smooth = config.get("d_period", 3)

    stoch = StochRSI(rsi_period, stoch_period, k_smooth, d_smooth)
    k_vals, d_vals = [], []
    for price in df["Close"]:
        stoch.update(price)
        k_vals.append(stoch.k if stoch.ready else None)
        d_vals.append(stoch.d if stoch.ready else None)

    df["k"] = k_vals
    df["d"] = d_vals
    df["k"] = df["k"].fillna(50)
    df["d"] = df["d"].fillna(50)

    # ADX
    df["adx"] = adx(df["High"], df["Low"], df["Close"], 14)

    # ATR
    df["atr"] = atr(df["High"], df["Low"], df["Close"], 14)

    # RSI
    df["rsi"] = rsi(df["Close"], 14)

    # MACD
    macd_df = macd(df["Close"], 12, 26, 9)
    df["macd"] = macd_df["macd"]
    df["macd_signal"] = macd_df["signal"]
    df["macd_hist"] = macd_df["histogram"]

    # Bollinger Bands
    bb = bollinger_bands(df["Close"], 20, 2.0)
    df["bb_upper"] = bb["upper"]
    df["bb_middle"] = bb["middle"]
    df["bb_lower"] = bb["lower"]

    # Donchian Channels
    don = donchian_channels(df["High"], df["Low"], 20, 10)
    df["don_upper"] = don["upper_entry"]
    df["don_lower"] = don["lower_entry"]
    df["don_exit_upper"] = don["upper_exit"]
    df["don_exit_lower"] = don["lower_exit"]

    # SMA (50 and 200 for trend)
    df["sma_50"] = sma(df["Close"], 50)
    df["sma_200"] = sma(df["Close"], 200)

    # CHOP (Choppiness Index)
    df["chop"] = chop_index(df["High"], df["Low"], df["Close"], 14)

    # Fill remaining NaNs with neutral values
    df["adx"] = df["adx"].fillna(25)
    df["atr"] = df["atr"].fillna(0)
    df["rsi"] = df["rsi"].fillna(50)
    df["macd"] = df["macd"].fillna(0)
    df["macd_signal"] = df["macd_signal"].fillna(0)
    df["macd_hist"] = df["macd_hist"].fillna(0)
    df["chop"] = df["chop"].fillna(50)

    return df
