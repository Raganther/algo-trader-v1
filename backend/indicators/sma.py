import pandas as pd

def sma(series: pd.Series, period: int) -> pd.Series:
    """
    Calculate Simple Moving Average (SMA).
    
    Args:
        series (pd.Series): Price series (e.g., Close).
        period (int): Lookback period.
        
    Returns:
        pd.Series: SMA values.
    """
    return series.rolling(window=period).mean()
