import pandas as pd

def donchian_channels(high: pd.Series, low: pd.Series, entry_period: int, exit_period: int) -> pd.DataFrame:
    """
    Calculate Donchian Channels for Entry and Exit.
    
    Args:
        high (pd.Series): High prices.
        low (pd.Series): Low prices.
        entry_period (int): Lookback for Entry (e.g., 20).
        exit_period (int): Lookback for Exit (e.g., 10).
        
    Returns:
        pd.DataFrame: Contains 'upper_entry', 'lower_entry', 'upper_exit', 'lower_exit'.
    """
    # Donchian High/Low are strictly PAST data (shifted by 1) to avoid lookahead bias
    upper_entry = high.rolling(window=entry_period).max().shift(1)
    lower_entry = low.rolling(window=entry_period).min().shift(1)
    
    upper_exit = high.rolling(window=exit_period).max().shift(1)
    lower_exit = low.rolling(window=exit_period).min().shift(1)
    
    return pd.DataFrame({
        'upper_entry': upper_entry,
        'lower_entry': lower_entry,
        'upper_exit': upper_exit,
        'lower_exit': lower_exit
    })
