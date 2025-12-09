import pandas as pd
import numpy as np

def chop_index(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Choppiness Index (CHOP).
    Values > 61.8 indicate consolidation (chop).
    Values < 38.2 indicate trend.
    """
    # 1. True Range
    tr1 = pd.DataFrame(high - low)
    tr2 = pd.DataFrame(abs(high - close.shift(1)))
    tr3 = pd.DataFrame(abs(low - close.shift(1)))
    frames = [tr1, tr2, tr3]
    tr = pd.concat(frames, axis=1, join='inner').max(axis=1)
    
    # 2. Sum of True Range over period
    atr_sum = tr.rolling(window=period).sum()
    
    # 3. Range (Max High - Min Low) over period
    high_max = high.rolling(window=period).max()
    low_min = low.rolling(window=period).min()
    range_diff = high_max - low_min
    
    # 4. Calculate CHOP
    # Avoid division by zero
    range_diff = range_diff.replace(0, np.nan)
    
    chop = 100 * np.log10(atr_sum / range_diff) / np.log10(period)
    
    return chop
