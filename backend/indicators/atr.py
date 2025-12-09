import pandas as pd
import numpy as np

def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int) -> pd.Series:
    """
    Calculate Average True Range (ATR).
    
    Args:
        high (pd.Series): High prices.
        low (pd.Series): Low prices.
        close (pd.Series): Close prices.
        period (int): Lookback period.
        
    Returns:
        pd.Series: ATR values.
    """
    # Calculate True Range (TR)
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # Calculate ATR (Wilder's Smoothing is standard, but simple rolling mean is often used in simple backtests)
    # Let's use Wilder's Smoothing for accuracy if possible, or simple rolling for consistency with previous simple tests.
    # For now, let's stick to Simple Rolling Mean to match our previous ad-hoc implementations, 
    # but we can upgrade to Wilder's later if needed.
    # Actually, standard ATR is usually Wilder's. Let's provide Rolling for now as it's robust.
    return tr.rolling(window=period).mean()
