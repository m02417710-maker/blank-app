"""
EGX Pro Terminal v34 - Market Data Fetcher
Fixed imports to use data.egx_symbols instead of date.egx_symbols
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import time
import logging

from data.egx_symbols import get_yahoo_symbol, get_stock_info, StockInfo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketDataFetcher:
    def __init__(self):
        self.cache: Dict[str, pd.DataFrame] = {}
        self.cache_ttl = 300
        self.last_fetch: Dict[str, datetime] = {}

    def fetch_stock_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> Optional[pd.DataFrame]:
        cache_key = f"{symbol}_{period}_{interval}"
        if cache_key in self.cache:
            last_time = self.last_fetch.get(cache_key, datetime.min)
            if (datetime.now() - last_time).seconds < self.cache_ttl:
                logger.info(f"Using cached data for {symbol}")
                return self.cache[cache_key].copy()
        try:
            yahoo_sym = get_yahoo_symbol(symbol)
            logger.info(f"Fetching data for {symbol} ({yahoo_sym})")
            ticker = yf.Ticker(yahoo_sym)
            df = ticker.history(period=period, interval=interval)
            if df.empty:
                logger.warning(f"No data returned for {symbol}")
                return None
            df.columns = [c.lower().replace(' ', '_') for c in df.columns]
            df = df.reset_index()
            self.cache[cache_key] = df.copy()
            self.last_fetch[cache_key] = datetime.now()
            return df
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {e}")
            return None

    def fetch_multiple(self, symbols: List[str], period: str = "1y") -> Dict[str, pd.DataFrame]:
        results = {}
        for symbol in symbols:
            df = self.fetch_stock_data(symbol, period)
            if df is not None:
                results[symbol] = df
            time.sleep(0.5)
        return results

    def get_real_time_quote(self, symbol: str) -> Optional[Dict]:
        try:
            yahoo_sym = get_yahoo_symbol(symbol)
            ticker = yf.Ticker(yahoo_sym)
            info = ticker.info
            return {
                "symbol": symbol,
                "price": info.get("regularMarketPrice"),
                "change": info.get("regularMarketChange"),
                "change_percent": info.get("regularMarketChangePercent"),
                "volume": info.get("regularMarketVolume"),
                "high": info.get("regularMarketDayHigh"),
                "low": info.get("regularMarketDayLow"),
                "open": info.get("regularMarketOpen"),
                "previous_close": info.get("regularMarketPreviousClose"),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting quote for {symbol}: {e}")
            return None

    def clear_cache(self):
        self.cache.clear()
        self.last_fetch.clear()

fetcher = MarketDataFetcher()

def generate_mock_data(symbol: str, days: int = 252) -> pd.DataFrame:
    np.random.seed(hash(symbol) % 2**31)
    info = get_stock_info(symbol)
    if info and info.fifty_two_week_high and info.fifty_two_week_low:
        base_price = (info.fifty_two_week_high + info.fifty_two_week_low) / 2
    else:
        base_price = np.random.uniform(5, 200)
    dates = pd.date_range(end=datetime.now(), periods=days, freq="B")
    returns = np.random.normal(0.0005, 0.02, days)
    trend = np.linspace(0, np.random.uniform(-0.1, 0.15), days)
    returns += trend / days
    prices = base_price * np.exp(np.cumsum(returns))
    df = pd.DataFrame({
        "date": dates,
        "open": prices * (1 + np.random.uniform(-0.01, 0.01, days)),
        "high": prices * (1 + np.random.uniform(0, 0.02, days)),
        "low": prices * (1 + np.random.uniform(-0.02, 0, days)),
        "close": prices,
        "volume": np.random.randint(100000, 5000000, days),
    })
    df["high"] = np.maximum(df["high"], np.maximum(df["open"], df["close"]))
    df["low"] = np.minimum(df["low"], np.minimum(df["open"], df["close"]))
    df.set_index("date", inplace=True)
    return df

def fetch_egx_index(index_symbol: str = "EGX30", period: str = "1y") -> Optional[pd.DataFrame]:
    return generate_mock_data(index_symbol, 252)

def get_market_summary() -> Dict:
    return {
        "market_status": "OPEN",
        "trading_date": datetime.now().strftime("%Y-%m-%d"),
        "egx30": 28450.25,
        "egx30_change": 2.85,
        "egx70": 7850.15,
        "egx70_change": 1.92,
        "total_volume": 1250000000,
        "total_value": 2850000000,
        "trades_count": 12450,
        "advancers": 85,
        "decliners": 62,
        "unchanged": 18,
        "foreign_buy": 450000000,
        "foreign_sell": 380000000,
        "foreign_net": 70000000,
    }
