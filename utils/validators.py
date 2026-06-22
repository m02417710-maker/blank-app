"""
EGX Pro Terminal v34 - Input Validators
"""

import re
from typing import Optional, List, Tuple
from data.egx_symbols import get_all_symbols, get_stock_info

def validate_symbol(symbol: str) -> Tuple[bool, str]:
    """Validate stock symbol."""
    if not symbol or not isinstance(symbol, str):
        return False, "Symbol must be a non-empty string"

    symbol = symbol.upper().strip()

    if not re.match(r'^[A-Z0-9]{2,10}$', symbol):
        return False, "Symbol must be 2-10 alphanumeric characters"

    valid_symbols = get_all_symbols()
    if symbol not in valid_symbols:
        return False, f"Symbol {symbol} not found in EGX database"

    return True, "Valid"

def validate_price(price: float) -> Tuple[bool, str]:
    """Validate price value."""
    if not isinstance(price, (int, float)):
        return False, "Price must be a number"

    if price <= 0:
        return False, "Price must be positive"

    if price > 1_000_000:
        return False, "Price exceeds maximum allowed value"

    return True, "Valid"

def validate_quantity(quantity: int) -> Tuple[bool, str]:
    """Validate quantity."""
    if not isinstance(quantity, int):
        return False, "Quantity must be an integer"

    if quantity <= 0:
        return False, "Quantity must be positive"

    if quantity > 1_000_000_000:
        return False, "Quantity exceeds maximum allowed value"

    return True, "Valid"

def validate_alert_type(alert_type: str) -> Tuple[bool, str]:
    """Validate alert type."""
    valid_types = [
        "PRICE_ABOVE", "PRICE_BELOW", "RSI_OVERBOUGHT", "RSI_OVERSOLD",
        "MACD_BULLISH", "MACD_BEARISH", "EMA_CROSSOVER", "VOLUME_SPIKE",
        "BOLLINGER_BREAKOUT", "SUPPORT_BREAK", "RESISTANCE_BREAK"
    ]

    if alert_type not in valid_types:
        return False, f"Invalid alert type. Valid types: {', '.join(valid_types)}"

    return True, "Valid"

def validate_email(email: str) -> Tuple[bool, str]:
    """Validate email address."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    return True, "Valid"

def validate_timeframe(timeframe: str) -> Tuple[bool, str]:
    """Validate chart timeframe."""
    valid_timeframes = ["1D", "1W", "1M", "3M", "6M", "1Y", "YTD", "MAX"]
    if timeframe not in valid_timeframes:
        return False, f"Invalid timeframe. Valid options: {', '.join(valid_timeframes)}"
    return True, "Valid"

def validate_strategy(strategy: str) -> Tuple[bool, str]:
    """Validate backtest strategy."""
    valid_strategies = [
        "trend_following", "mean_reversion", "momentum", "breakout",
        "rsi_strategy", "macd_strategy", "bollinger_strategy", "ml_strategy"
    ]
    if strategy not in valid_strategies:
        return False, f"Invalid strategy. Valid options: {', '.join(valid_strategies)}"
    return True, "Valid"

def validate_watchlist(symbols: List[str]) -> Tuple[bool, str, List[str]]:
    """Validate watchlist symbols."""
    if not symbols:
        return False, "Watchlist cannot be empty", []

    if len(symbols) > 50:
        return False, "Watchlist cannot exceed 50 symbols", []

    valid_symbols = get_all_symbols()
    invalid = [s for s in symbols if s not in valid_symbols]

    if invalid:
        return False, f"Invalid symbols: {', '.join(invalid)}", invalid

    return True, "Valid", []

def sanitize_input(text: str, max_length: int = 200) -> str:
    """Sanitize user input."""
    if not text:
        return ""

    # Remove potentially dangerous characters
    text = re.sub(r'[<>"'%;()&+]', '', text)

    # Truncate to max length
    text = text[:max_length]

    return text.strip()

def validate_capital(capital: float) -> Tuple[bool, str]:
    """Validate initial capital."""
    if not isinstance(capital, (int, float)):
        return False, "Capital must be a number"

    if capital < 1000:
        return False, "Minimum capital is 1,000 EGP"

    if capital > 1_000_000_000:
        return False, "Capital exceeds maximum allowed value"

    return True, "Valid"
