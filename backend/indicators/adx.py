import pandas as pd
import numpy as np

def adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate the Average Directional Index (ADX).
    
    Args:
        high (pd.Series): High prices
        low (pd.Series): Low prices
        close (pd.Series): Close prices
        period (int): The period for ADX calculation (default 14)
        
    Returns:
        pd.Series: The ADX values
    """
    # 1. Calculate True Range (TR)
    # TR = max(high-low, abs(high-prev_close), abs(low-prev_close))
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # 2. Calculate Directional Movement (DM)
    # +DM = current_high - prev_high (if > prev_low - current_low and > 0)
    # -DM = prev_low - current_low (if > current_high - prev_high and > 0)
    up_move = high - high.shift(1)
    down_move = low.shift(1) - low
    
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
    
    # 3. Smooth TR and DM (Wilder's Smoothing)
    # First value is simple sum, subsequent are smoothed
    # smoothed = (prev_smoothed * (period-1) + current) / period
    # This is equivalent to EWMA with alpha = 1/period
    
    atr = tr.ewm(alpha=1/period, adjust=False).mean()
    plus_di = pd.Series(plus_dm, index=high.index).ewm(alpha=1/period, adjust=False).mean()
    minus_di = pd.Series(minus_dm, index=high.index).ewm(alpha=1/period, adjust=False).mean()
    
    # 4. Calculate +DI and -DI
    # DI = (Smoothed DM / ATR) * 100
    plus_di = (plus_di / atr) * 100
    minus_di = (minus_di / atr) * 100
    
    # 5. Calculate DX
    # DX = (abs(+DI - -DI) / (+DI + -DI)) * 100
    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    
    # 6. Calculate ADX (Smoothed DX)
    adx_series = dx.ewm(alpha=1/period, adjust=False).mean()
    
    return adx_series
