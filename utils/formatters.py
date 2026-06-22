"""
EGX Pro Terminal v34 - Data Formatters
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

def format_price(value: float, currency: str = "EGP") -> str:
    """Format price with currency."""
    return f"{value:,.2f} {currency}"

def format_percentage(value: float, decimals: int = 2) -> str:
    """Format percentage with sign."""
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.{decimals}f}%"

def format_volume(value: int) -> str:
    """Format large numbers with K/M/B suffix."""
    if value >= 1_000_000_000:
        return f"{value/1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"{value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"{value/1_000:.1f}K"
    return str(value)

def format_market_cap(value: float) -> str:
    """Format market cap in millions/billions."""
    if value >= 1000:
        return f"{value/1000:.2f}B EGP"
    return f"{value:.0f}M EGP"

def format_time_ago(dt: datetime) -> str:
    """Format datetime as time ago."""
    diff = datetime.now() - dt
    if diff.days > 365:
        return f"{diff.days // 365}y ago"
    if diff.days > 30:
        return f"{diff.days // 30}mo ago"
    if diff.days > 0:
        return f"{diff.days}d ago"
    hours = diff.seconds // 3600
    if hours > 0:
        return f"{hours}h ago"
    minutes = (diff.seconds % 3600) // 60
    return f"{minutes}m ago"

def format_number(value: float, decimals: int = 2) -> str:
    """Format number with commas."""
    return f"{value:,.{decimals}f}"

def colorize_change(value: float) -> str:
    """Return color class for change value."""
    if value > 0:
        return "change-up"
    elif value < 0:
        return "change-down"
    return "change-neutral"

def format_signal(signal: str) -> str:
    """Format trading signal with emoji."""
    signals = {
        "BUY": "🟢 BUY",
        "SELL": "🔴 SELL",
        "HOLD": "🟡 HOLD",
        "STRONG_BUY": "🟢🟢 STRONG BUY",
        "STRONG_SELL": "🔴🔴 STRONG SELL",
        "NEUTRAL": "⚪ NEUTRAL",
    }
    return signals.get(signal, signal)

def format_indicator(value: float, indicator: str) -> str:
    """Format technical indicator with context."""
    if indicator == "rsi":
        if value > 70:
            return f"{value:.1f} (Overbought)"
        elif value < 30:
            return f"{value:.1f} (Oversold)"
        return f"{value:.1f} (Neutral)"
    elif indicator == "macd":
        if value > 0:
            return f"{value:.3f} (Bullish)"
        return f"{value:.3f} (Bearish)"
    return f"{value:.2f}"

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def format_date(dt: datetime, format_str: str = "%Y-%m-%d") -> str:
    """Format datetime."""
    return dt.strftime(format_str)

def format_currency(value: float, currency: str = "EGP") -> str:
    """Format currency value."""
    return f"{currency} {value:,.2f}"
