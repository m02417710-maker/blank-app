"""
EGX Pro Terminal v27 - Configuration Settings
Ultra-Advanced Configuration for World-Class Analysis
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum

class MarketSession(Enum):
    PRE_MARKET = "pre_market"
    OPEN = "open"
    CLOSE = "close"
    AFTER_HOURS = "after_hours"

@dataclass
class AppConfig:
    APP_NAME: str = "EGX Pro Terminal"
    APP_VERSION: str = "27.0.0"
    APP_CODENAME: str = "Phoenix"
    APP_DESCRIPTION: str = "Ultra-Professional Egyptian Stock Market Analysis Platform"
    AUTHOR: str = "EGX Pro Team"
    LICENSE: str = "MIT"

    # Data Settings
    DEFAULT_PERIOD: str = "1y"
    DEFAULT_INTERVAL: str = "1d"
    CACHE_TTL_DATA: int = 300
    CACHE_TTL_ANALYSIS: int = 600
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.5

    # Technical Analysis
    RSI_PERIOD: int = 14
    RSI_OVERBOUGHT: float = 70.0
    RSI_OVERSOLD: float = 30.0
    MACD_FAST: int = 12
    MACD_SLOW: int = 26
    MACD_SIGNAL: int = 9
    BB_PERIOD: int = 20
    BB_STD_DEV: float = 2.0
    ATR_PERIOD: int = 14
    ADX_PERIOD: int = 14
    STOCH_K: int = 14
    STOCH_D: int = 3
    EMA_PERIODS: List[int] = field(default_factory=lambda: [9, 21, 50, 200])
    SMA_PERIODS: List[int] = field(default_factory=lambda: [20, 50, 200])

    # Advanced Indicators
    ICHIMOKU_TENKAN: int = 9
    ICHIMOKU_KIJUN: int = 26
    ICHIMOKU_SENKOU_B: int = 52
    VWAP_ANCHOR: str = "D"
    CCI_PERIOD: int = 20
    WILLIAMS_R_PERIOD: int = 14
    MFI_PERIOD: int = 14

    # AI/ML Settings
    AI_PREDICTION_HORIZON: int = 5
    AI_CONFIDENCE_THRESHOLD: float = 0.72
    AI_MIN_DATA_POINTS: int = 60
    AI_FEATURE_WINDOW: int = 20
    AI_ENSEMBLE_MODELS: int = 7
    AI_RETRAIN_INTERVAL: int = 7

    # Alert Settings
    ALERT_CHECK_INTERVAL: int = 60
    ALERT_COOLDOWN_MINUTES: int = 30
    MAX_ALERTS_PER_SYMBOL: int = 15
    ALERT_BATCH_SIZE: int = 50

    # Backtest Settings
    BACKTEST_INITIAL_CAPITAL: float = 100000.0
    BACKTEST_COMMISSION: float = 0.0015
    BACKTEST_SLIPPAGE: float = 0.001
    BACKTEST_RISK_PER_TRADE: float = 0.10
    BACKTEST_MAX_POSITIONS: int = 5
    BACKTEST_WALK_FORWARD_WINDOWS: int = 5

    # Risk Management
    DEFAULT_STOP_LOSS_PCT: float = 0.05
    DEFAULT_TAKE_PROFIT_PCT: float = 0.10
    MAX_PORTFOLIO_RISK: float = 0.20
    VAR_CONFIDENCE: float = 0.95
    CVAR_CONFIDENCE: float = 0.99

    # UI Settings
    REFRESH_INTERVALS: List[int] = field(default_factory=lambda: [30, 60, 120, 300, 600])
    CHART_HEIGHT: int = 700
    CHART_TEMPLATE: str = "plotly_dark"
    DEFAULT_THEME: str = "dark"

    def __post_init__(self):
        os.makedirs("data", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        os.makedirs("backups", exist_ok=True)

@dataclass
class EGXConfig:
    MARKET_NAME: str = "Egyptian Exchange"
    MARKET_CODE: str = "EGX"
    CURRENCY: str = "EGP"
    YAHOO_SUFFIX: str = ""
    MARKET_OPEN: str = "10:00"
    MARKET_CLOSE: str = "14:30"
    MARKET_DAYS: List[str] = field(default_factory=lambda: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"])

    TOP_STOCKS: List[str] = field(default_factory=lambda: [
        'COMI', 'HRHO', 'ABUK', 'EGBE', 'NSGB', 'HDBK', 'FAIT', 'CBKD',
        'TMGH', 'PHDC', 'MNHD', 'GDWA', 'HELL', 'ORAS', 'MISR',
        'EAST', 'ESRS', 'DOMT', 'JUHO', 'UNIP', 'OLFI', 'MPCI', 'JFEF',
        'ORWE', 'SWDY', 'AMOC', 'HELW', 'SKPC', 'EGTS', 'ETEL',
        'TAQA', 'EDBM', 'SWVL', 'FWRY', 'EGTS3',
        'PHAR', 'RMDA', 'IDHC', 'CLHO', 'SPIN', 'PCI', 'EKHO',
        'EFIC', 'KZPC', 'NIPH', 'MICH', 'MFPC', 'ABUK',
        'HELI', 'TRTO', 'EGCH', 'HOTS'
    ])

    SECTORS: Dict[str, List[str]] = field(default_factory=lambda: {
        'Banking': ['COMI', 'HRHO', 'ABUK', 'EGBE', 'NSGB', 'HDBK', 'FAIT', 'CBKD'],
        'Real Estate': ['TMGH', 'PHDC', 'MNHD', 'GDWA', 'HELL', 'ORAS', 'MISR'],
        'Food & Beverage': ['EAST', 'ESRS', 'DOMT', 'JUHO', 'UNIP', 'OLFI', 'MPCI', 'JFEF'],
        'Construction': ['ORWE', 'SWDY', 'AMOC', 'HELW', 'SKPC'],
        'Telecom': ['EGTS', 'ETEL'],
        'Energy': ['TAQA', 'EDBM'],
        'Healthcare': ['PHAR', 'RMDA', 'IDHC', 'CLHO', 'SPIN', 'PCI', 'EKHO'],
        'Chemicals': ['EFIC', 'KZPC', 'NIPH', 'MICH', 'MFPC', 'ABUK'],
        'Technology': ['FWRY', 'EGTS3', 'SWVL'],
        'Tourism': ['HELI', 'TRTO', 'EGCH', 'HOTS'],
        'Textiles': ['COTN', 'UNIR', 'NIND'],
        'Transport': ['EAST', 'TRTO'],
        'Mining': ['CEFM', 'MISR'],
        'Investment': ['HRHO', 'EFIC']
    })

    INDICES: Dict[str, str] = field(default_factory=lambda: {
        'EGX30': '^CASE30',
        'EGX70': '^CASE70',
        'EGX100': '^CASE100',
        'EGX20': '^EGX20'
    })

@dataclass
class DatabaseConfig:
    DB_PATH: str = "data/egx_database_v27.db"
    BACKUP_DIR: str = "backups"
    MAX_BACKUPS: int = 10
    BACKUP_INTERVAL_DAYS: int = 1

    def __post_init__(self):
        os.makedirs(os.path.dirname(self.DB_PATH), exist_ok=True)
        os.makedirs(self.BACKUP_DIR, exist_ok=True)

@dataclass
class LoggingConfig:
    LOG_DIR: str = "logs"
    LOG_FILE: str = "egx_terminal.log"
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    MAX_LOG_SIZE: int = 10 * 1024 * 1024
    LOG_BACKUPS: int = 5

@dataclass
class AdvancedConfig:
    PATTERN_CONFIDENCE_THRESHOLD: float = 0.65
    PATTERN_MIN_CANDLES: int = 3
    PATTERN_MAX_CANDLES: int = 5
    CORRELATION_WINDOW: int = 60
    COINTEGRATION_THRESHOLD: float = 0.05
    MONTE_CARLO_SIMULATIONS: int = 1000
    MONTE_CARLO_HORIZON: int = 30
    PORTFOLIO_OPTIMIZATION_METHOD: str = "sharpe"
    REBALANCE_THRESHOLD: float = 0.05

app_config = AppConfig()
egx_config = EGXConfig()
db_config = DatabaseConfig()
log_config = LoggingConfig()
advanced_config = AdvancedConfig()
