"""
EGX Pro Terminal v27 - Utility Functions and Formatters
Professional formatting and helper functions
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import re

def format_number(value: float, decimals: int = 2) -> str:
    if value is None or np.isnan(value):
        return "N/A"
    if abs(value) >= 1e9:
        return f"{value/1e9:.{decimals}f}B"
    elif abs(value) >= 1e6:
        return f"{value/1e6:.{decimals}f}M"
    elif abs(value) >= 1e3:
        return f"{value/1e3:.{decimals}f}K"
    return f"{value:.{decimals}f}"

def format_currency(value: float, suffix: str = "EGP") -> str:
    if value is None or np.isnan(value):
        return f"N/A {suffix}"
    return f"{format_number(value)} {suffix}"

def format_percentage(value: float, decimals: int = 2) -> str:
    if value is None or np.isnan(value):
        return "N/A%"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.{decimals}f}%"

def format_volume(value: float) -> str:
    if value is None or np.isnan(value):
        return "N/A"
    if value >= 1e9:
        return f"{value/1e9:.2f}B"
    elif value >= 1e6:
        return f"{value/1e6:.2f}M"
    elif value >= 1e3:
        return f"{value/1e3:.2f}K"
    return f"{value:.0f}"

def get_signal_color(signal: str) -> str:
    colors = {
        "STRONG BUY": "#00ff00",
        "BUY": "#4caf50",
        "NEUTRAL": "#ff9800",
        "SELL": "#f44336",
        "STRONG SELL": "#ff0000",
        "UP": "#4caf50",
        "DOWN": "#f44336",
        "SIDEWAYS": "#ff9800",
        "BULLISH": "#4caf50",
        "BEARISH": "#f44336"
    }
    return colors.get(signal.upper(), "#888888")

def get_trend_color(trend: str) -> str:
    colors = {
        "Strong Up": "#00ff00",
        "Up": "#4caf50",
        "Neutral": "#ff9800",
        "Down": "#f44336",
        "Strong Down": "#ff0000"
    }
    return colors.get(trend, "#888888")

def get_severity_color(severity: str) -> str:
    colors = {"info": "#2196f3", "warning": "#ff9800", "critical": "#f44336"}
    return colors.get(severity.lower(), "#888888")

def get_severity_emoji(severity: str) -> str:
    emojis = {"info": "ℹ️", "warning": "⚠️", "critical": "🚨"}
    return emojis.get(severity.lower(), "📋")

def render_metric_card(label: str, value: str, delta: str = "", color: str = "#ffffff") -> str:
    return f"""
    <div style="background: rgba(255,255,255,0.05); border-radius: 10px; padding: 15px; text-align: center;">
        <div style="color: #888; font-size: 12px; margin-bottom: 5px;">{label}</div>
        <div style="color: {color}; font-size: 24px; font-weight: bold;">{value}</div>
        <div style="color: {'#4caf50' if '+' in delta else '#f44336' if '-' in delta else '#888'}; font-size: 12px;">{delta}</div>
    </div>
    """

def render_signal_badge(signal: str, strength: float = 0) -> str:
    color = get_signal_color(signal)
    return f"""
    <div style="background: {color}; color: white; padding: 8px 16px; border-radius: 20px;
                font-weight: bold; display: inline-block; font-size: 14px;">
        {signal} ({strength:.0%})
    </div>
    """

def render_progress_bar(value: float, max_value: float = 100, label: str = "") -> str:
    pct = min(max(value / max_value * 100, 0), 100)
    color = "#4caf50" if pct > 60 else "#ff9800" if pct > 30 else "#f44336"
    return f"""
    <div style="width: 100%; background: rgba(255,255,255,0.1); border-radius: 5px; height: 20px;">
        <div style="width: {pct}%; background: {color}; height: 100%; border-radius: 5px;
                    transition: width 0.3s; display: flex; align-items: center; justify-content: center;">
            <span style="color: white; font-size: 10px; font-weight: bold;">{label} {value:.0f}%</span>
        </div>
    </div>
    """

def render_alert_card(alert: Dict) -> str:
    color = get_severity_color(alert.get("severity", "info"))
    emoji = get_severity_emoji(alert.get("severity", "info"))
    return f"""
    <div style="background: rgba(255,255,255,0.05); border-left: 4px solid {color};
                padding: 12px; margin: 8px 0; border-radius: 0 8px 8px 0;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-weight: bold; color: {color};">{emoji} {alert.get("symbol", "")}</span>
            <span style="color: #888; font-size: 11px;">{alert.get("timestamp", "")[:10]}</span>
        </div>
        <div style="color: #ccc; margin-top: 5px; font-size: 13px;">{alert.get("message", "")}</div>
    </div>
    """

def render_separator() -> str:
    return "<hr style='border: none; border-top: 1px solid rgba(255,255,255,0.1); margin: 20px 0;'>"

def get_arabic_number(num: int) -> str:
    arabic_digits = {"0": "٠", "1": "١", "2": "٢", "3": "٣", "4": "٤",
                     "5": "٥", "6": "٦", "7": "٧", "8": "٨", "9": "٩"}
    return "".join(arabic_digits.get(d, d) for d in str(num))

def time_ago(dt_str: str) -> str:
    try:
        if isinstance(dt_str, str):
            dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        else:
            dt = dt_str

        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        diff = now - dt

        if diff.days > 365:
            return f"{diff.days // 365}y ago"
        elif diff.days > 30:
            return f"{diff.days // 30}mo ago"
        elif diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600}h ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60}m ago"
        else:
            return "Just now"
    except:
        return "Unknown"

def validate_symbol(symbol: str) -> bool:
    if not symbol or not isinstance(symbol, str):
        return False
    return bool(re.match(r"^[A-Z]{2,6}$", symbol.upper()))

def get_sector_performance(quotes_df: pd.DataFrame) -> pd.DataFrame:
    from data.egx_symbols import SECTOR_MAP

    if quotes_df.empty or "symbol" not in quotes_df.columns:
        return pd.DataFrame()

    sector_data = {}
    for _, row in quotes_df.iterrows():
        sector = SECTOR_MAP.get(row["symbol"])
        if sector:
            if sector not in sector_data:
                sector_data[sector] = {"changes": [], "prices": []}
            sector_data[sector]["changes"].append(row.get("change_pct", 0))
            sector_data[sector]["prices"].append(row.get("price", 0))

    result = []
    for sector, data in sector_data.items():
        result.append({
            "sector": sector,
            "avg_change": np.mean(data["changes"]),
            "stocks_count": len(data["changes"]),
            "avg_price": np.mean(data["prices"])
        })

    return pd.DataFrame(result).sort_values("avg_change", ascending=False)

def calculate_portfolio_metrics(returns: pd.Series) -> Dict[str, float]:
    if returns.empty or returns.std() == 0:
        return {"sharpe": 0, "sortino": 0, "max_dd": 0, "volatility": 0}

    annual_return = returns.mean() * 252
    annual_vol = returns.std() * np.sqrt(252)
    sharpe = annual_return / annual_vol if annual_vol > 0 else 0

    downside = returns[returns < 0]
    downside_vol = downside.std() * np.sqrt(252) if len(downside) > 0 else 0
    sortino = annual_return / downside_vol if downside_vol > 0 else 0

    cumulative = (1 + returns).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max
    max_dd = drawdown.min()

    return {
        "sharpe": round(sharpe, 3),
        "sortino": round(sortino, 3),
        "max_dd": round(max_dd * 100, 2),
        "volatility": round(annual_vol * 100, 2),
        "annual_return": round(annual_return * 100, 2)
    }

def detect_outliers(data: pd.Series, method: str = "iqr", threshold: float = 1.5) -> pd.Series:
    if method == "iqr":
        q1 = data.quantile(0.25)
        q3 = data.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - threshold * iqr
        upper = q3 + threshold * iqr
        return (data < lower) | (data > upper)
    elif method == "zscore":
        z_scores = np.abs((data - data.mean()) / data.std())
        return z_scores > threshold
    return pd.Series(False, index=data.index)

def rolling_sharpe(returns: pd.Series, window: int = 63) -> pd.Series:
    return (returns.rolling(window).mean() / returns.rolling(window).std() * np.sqrt(252)).fillna(0)

def calculate_beta(stock_returns: pd.Series, market_returns: pd.Series) -> float:
    covariance = stock_returns.cov(market_returns)
    market_variance = market_returns.var()
    return covariance / market_variance if market_variance > 0 else 1.0

def calculate_alpha(stock_returns: pd.Series, market_returns: pd.Series,
                    risk_free_rate: float = 0.15) -> float:
    beta = calculate_beta(stock_returns, market_returns)
    alpha = stock_returns.mean() * 252 - risk_free_rate - beta * (market_returns.mean() * 252 - risk_free_rate)
    return alpha
