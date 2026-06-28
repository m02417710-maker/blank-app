"""
EGX Pro Terminal v34 - Application Settings
"""

from dataclasses import dataclass
from typing import Dict, List

@dataclass
class AppConfig:
    APP_NAME: str = "EGX Pro Terminal"
    APP_VERSION: str = "34.0.0"
    APP_AUTHOR: str = "EGX Pro Team"

    # Market Settings
    MARKET_OPEN_TIME: str = "10:00"
    MARKET_CLOSE_TIME: str = "14:30"
    MARKET_DAYS: List[str] = None

    # Data Settings
    DEFAULT_TIMEFRAME: str = "3M"
    DEFAULT_INTERVAL: str = "1d"
    CACHE_TTL_SECONDS: int = 300
    MAX_HISTORY_YEARS: int = 5

    # UI Settings
    DEFAULT_THEME: str = "dark"
    CHART_HEIGHT: int = 600
    MAX_WATCHLIST_SIZE: int = 50
    MAX_ALERTS: int = 100

    # Analysis Settings
    RSI_PERIOD: int = 14
    MACD_FAST: int = 12
    MACD_SLOW: int = 26
    MACD_SIGNAL: int = 9
    BOLLINGER_PERIOD: int = 20
    BOLLINGER_STD: float = 2.0
    EMA_SHORT: int = 9
    EMA_MEDIUM: int = 21
    EMA_LONG: int = 50

    # AI Settings
    MONTE_CARLO_SIMULATIONS: int = 1000
    MONTE_CARLO_DAYS: int = 30
    ENSEMBLE_CONFIDENCE_THRESHOLD: float = 0.65
    AI_PREDICTION_HORIZON: int = 5        # ✅ Fix CFG-1: was missing → AttributeError

    # Backtest Settings
    DEFAULT_INITIAL_CAPITAL: float = 100000.0
    DEFAULT_POSITION_SIZE: float = 0.1
    MAX_POSITION_SIZE: float = 0.25
    SLIPPAGE: float = 0.001
    COMMISSION: float = 0.00185  # ✅ Fix CFG-3: EGX official 18.5 bps

    # Alert Settings
    ALERT_CHECK_INTERVAL: int = 60  # seconds
    MAX_ALERTS_PER_SYMBOL: int = 10
    ALERT_COOLDOWN_HOURS: int = 24

    def __post_init__(self):
        if self.MARKET_DAYS is None:
            self.MARKET_DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]

# Global config instance
config = AppConfig()

# ✅ Fix CFG-2: alias — core/*.py do: from config.settings import app_config
app_config = config

# EGX Sector Colors
SECTOR_COLORS: Dict[str, str] = {
    "Banking": "#1f77b4",
    "Real Estate": "#ff7f0e",
    "Food & Beverage": "#2ca02c",
    "Construction": "#d62728",
    "Telecom": "#9467bd",
    "Energy": "#8c564b",
    "Healthcare": "#e377c2",
    "Chemicals": "#7f7f7f",
    "Technology": "#bcbd22",
    "Tourism": "#17becf",
    "Textiles": "#aec7e8",
    "Transport": "#ffbb78",
    "Mining": "#98df8a",
    "Investment": "#ff9896",
    "Industrial": "#c5b0d5",
    "Automotive": "#c49c94",
    "Education": "#f7b6d3",
    "Media": "#dbdb8d",
    "Plastics": "#9edae5",
    "Printing": "#ad494a",
    "Shipping": "#8c6d31",
    "Agriculture": "#e7ba52",
    "Holding Companies": "#393b79",
    "Financial Services": "#637939",
    "Insurance": "#8ca252",
}

# Technical Indicator Thresholds
INDICATOR_THRESHOLDS = {
    "rsi_overbought": 70,
    "rsi_oversold": 30,
    "macd_bullish_threshold": 0.0,
    "macd_bearish_threshold": 0.0,
    "bollinger_upper_breakout": 1.0,
    "bollinger_lower_breakout": -1.0,
    "volume_spike_multiplier": 2.0,
    "trend_strength_min": 25.0,
}
