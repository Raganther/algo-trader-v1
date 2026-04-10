"""
Regime classifier — labels each bar with a market regime.

Four regimes:
    TRENDING_UP    — ADX > adx_threshold AND close > SMA(sma_period)
    TRENDING_DOWN  — ADX > adx_threshold AND close <= SMA(sma_period)
    HIGH_VOL       — ATR > atr_vol_multiplier * ATR rolling mean (spike detection)
    RANGING        — everything else (ADX low, ATR normal)

HIGH_VOL takes priority over TRENDING — a trending but volatile session is HIGH_VOL.

Usage:
    from backend.indicators.regime import classify_regime
    regimes = classify_regime(df)   # df has High, Low, Close columns
"""

import pandas as pd
from backend.indicators.adx import adx as calc_adx
from backend.indicators.atr import atr as calc_atr
from backend.indicators.sma import sma as calc_sma

TRENDING_UP   = 'TRENDING_UP'
TRENDING_DOWN = 'TRENDING_DOWN'
HIGH_VOL      = 'HIGH_VOL'
RANGING       = 'RANGING'


def classify_regime(
    df: pd.DataFrame,
    adx_period: int = 14,
    sma_period: int = 200,
    atr_period: int = 14,
    adx_threshold: float = 25.0,
    atr_vol_lookback: int = 50,
    atr_vol_multiplier: float = 1.5,
) -> pd.Series:
    """
    Classify each bar into a market regime.

    Args:
        df: DataFrame with High, Low, Close columns and DatetimeIndex.
        adx_period: ADX smoothing period (default 14).
        sma_period: SMA period for trend direction (default 200).
        atr_period: ATR period (default 14).
        adx_threshold: ADX level above which a trend is considered active (default 25).
        atr_vol_lookback: Rolling window to compute baseline ATR mean (default 50).
        atr_vol_multiplier: ATR must exceed this multiple of its rolling mean to be HIGH_VOL (default 1.5).

    Returns:
        pd.Series of regime labels (TRENDING_UP, TRENDING_DOWN, HIGH_VOL, RANGING).
    """
    adx_vals  = calc_adx(df['High'], df['Low'], df['Close'], period=adx_period)
    atr_vals  = calc_atr(df['High'], df['Low'], df['Close'], period=atr_period)
    sma_vals  = calc_sma(df['Close'], period=sma_period)
    atr_mean  = atr_vals.rolling(window=atr_vol_lookback).mean()

    trending  = adx_vals > adx_threshold
    above_sma = df['Close'] > sma_vals
    high_vol  = atr_vals > (atr_vol_multiplier * atr_mean)

    labels = pd.Series(RANGING, index=df.index)
    labels[trending &  above_sma] = TRENDING_UP
    labels[trending & ~above_sma] = TRENDING_DOWN
    labels[high_vol]               = HIGH_VOL   # overrides trend labels

    # NaN period (insufficient history for SMA/ADX) — label as RANGING
    labels[sma_vals.isna() | adx_vals.isna()] = RANGING

    return labels


def regime_stats(regimes: pd.Series) -> pd.DataFrame:
    """
    Compute duration statistics per regime.

    Returns a DataFrame with columns:
        regime, occurrences, total_bars, pct_of_time, avg_duration, max_duration
    """
    # Build run-length encoding
    runs = []
    current = None
    length = 0
    for label in regimes:
        if label == current:
            length += 1
        else:
            if current is not None:
                runs.append((current, length))
            current = label
            length = 1
    if current is not None:
        runs.append((current, length))

    if not runs:
        return pd.DataFrame()

    run_df = pd.DataFrame(runs, columns=['regime', 'duration'])
    total_bars = len(regimes)

    stats = (
        run_df.groupby('regime')['duration']
        .agg(occurrences='count', total_bars='sum', avg_duration='mean', max_duration='max')
        .reset_index()
    )
    stats['pct_of_time'] = (stats['total_bars'] / total_bars * 100).round(1)
    stats['avg_duration'] = stats['avg_duration'].round(1)
    stats = stats[['regime', 'occurrences', 'total_bars', 'pct_of_time', 'avg_duration', 'max_duration']]
    return stats.sort_values('total_bars', ascending=False).reset_index(drop=True)
