"""
EGX Pro Terminal v34 - Helper Functions
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import hashlib
import json

def generate_id(prefix: str = "id") -> str:
    """Generate unique ID."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = hashlib.md5(str(np.random.random()).encode()).hexdigest()[:6]
    return f"{prefix}_{timestamp}_{random_suffix}"

def calculate_returns(prices: pd.Series) -> pd.Series:
    """Calculate daily returns."""
    return prices.pct_change().dropna()

def calculate_volatility(returns: pd.Series, window: int = 20) -> float:
    """Calculate annualized volatility."""
    if len(returns) < window:
        return np.nan
    return returns.rolling(window).std().iloc[-1] * np.sqrt(252)

def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.05) -> float:
    """Calculate Sharpe ratio."""
    if len(returns) < 2:
        return np.nan
    excess_returns = returns - risk_free_rate / 252
    return excess_returns.mean() / excess_returns.std() * np.sqrt(252)

def calculate_max_drawdown(prices: pd.Series) -> Tuple[float, datetime, datetime]:
    """Calculate maximum drawdown."""
    cumulative = (1 + prices.pct_change()).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max

    max_dd = drawdown.min()
    max_dd_date = drawdown.idxmin()

    # Find peak date before max drawdown
    peak_dates = running_max[running_max == running_max.loc[:max_dd_date].max()]
    peak_date = peak_dates.index[0] if len(peak_dates) > 0 else prices.index[0]

    return max_dd, peak_date, max_dd_date

def calculate_beta(stock_returns: pd.Series, market_returns: pd.Series) -> float:
    """Calculate beta coefficient."""
    if len(stock_returns) != len(market_returns):
        min_len = min(len(stock_returns), len(market_returns))
        stock_returns = stock_returns.iloc[-min_len:]
        market_returns = market_returns.iloc[-min_len:]

    covariance = stock_returns.cov(market_returns)
    market_variance = market_returns.var()

    if market_variance == 0:
        return np.nan

    return covariance / market_variance

def calculate_correlation_matrix(returns_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate correlation matrix."""
    return returns_df.corr()

def resample_data(df: pd.DataFrame, timeframe: str = "W") -> pd.DataFrame:
    """Resample OHLCV data to different timeframe."""
    resampled = df.resample(timeframe).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()
    return resampled

def detect_outliers(data: pd.Series, threshold: float = 3.0) -> pd.Series:
    """Detect outliers using Z-score."""
    z_scores = np.abs((data - data.mean()) / data.std())
    return z_scores > threshold

def smooth_series(data: pd.Series, window: int = 5, method: str = "sma") -> pd.Series:
    """Smooth time series data."""
    if method == "sma":
        return data.rolling(window).mean()
    elif method == "ema":
        return data.ewm(span=window).mean()
    elif method == "median":
        return data.rolling(window).median()
    else:
        return data

def get_market_hours() -> Dict:
    """Get EGX market trading hours."""
    return {
        "pre_open": "09:30",
        "open": "10:00",
        "close": "14:30",
        "days": ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"],
        "timezone": "Africa/Cairo"
    }

def is_market_open() -> bool:
    """Check if EGX market is currently open."""
    now = datetime.now()
    hours = get_market_hours()

    if now.strftime("%A") not in hours["days"]:
        return False

    current_time = now.strftime("%H:%M")
    return hours["open"] <= current_time <= hours["close"]

def time_to_market_open() -> Optional[timedelta]:
    """Calculate time until market opens."""
    if is_market_open():
        return None

    now = datetime.now()
    hours = get_market_hours()

    next_open = datetime.strptime(hours["open"], "%H:%M")
    next_open = next_open.replace(year=now.year, month=now.month, day=now.day)

    if now > next_open:
        next_open += timedelta(days=1)

    while next_open.strftime("%A") not in hours["days"]:
        next_open += timedelta(days=1)

    return next_open - now

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split list into chunks."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safe division with default value."""
    if denominator == 0 or np.isnan(denominator):
        return default
    return numerator / denominator

def json_serialize(obj) -> str:
    """Serialize object to JSON string."""
    try:
        return json.dumps(obj, default=str)
    except:
        return str(obj)
