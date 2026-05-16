"""
EGX Pro Terminal - Technical Analysis Engine
Advanced indicators for Egyptian Stock Exchange
"""

import pandas as pd
import numpy as np
import yfinance as yf
from ta.trend import EMAIndicator, SMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import VolumeWeightedAveragePrice
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import *

class EGXAnalyzer:
    """Professional technical analysis engine for EGX stocks"""

    def __init__(self, symbol: str, period: str = DEFAULT_PERIOD, interval: str = DEFAULT_INTERVAL):
        self.symbol = symbol.upper()
        self.yahoo_symbol = f"{self.symbol}{YAHOO_FINANCE_SUFFIX}"
        self.period = period
        self.interval = interval
        self.data = None
        self.indicators = {}

    def fetch_data(self) -> pd.DataFrame:
        """Fetch historical data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(self.yahoo_symbol)
            self.data = ticker.history(period=self.period, interval=self.interval)
            if self.data.empty:
                raise ValueError(f"No data found for {self.yahoo_symbol}")
            self.data.dropna(inplace=True)
            return self.data
        except Exception as e:
            raise ConnectionError(f"Failed to fetch data: {str(e)}")

    def calculate_all_indicators(self) -> dict:
        """Calculate comprehensive technical indicators"""
        if self.data is None:
            self.fetch_data()

        close = self.data['Close']
        high = self.data['High']
        low = self.data['Low']
        volume = self.data['Volume']

        # Trend Indicators
        self.indicators['EMA_9'] = EMAIndicator(close=close, window=EMA_SHORT).ema_indicator()
        self.indicators['EMA_20'] = EMAIndicator(close=close, window=EMA_MEDIUM).ema_indicator()
        self.indicators['EMA_50'] = EMAIndicator(close=close, window=EMA_LONG).ema_indicator()
        self.indicators['EMA_200'] = EMAIndicator(close=close, window=EMA_TREND).ema_indicator()
        self.indicators['SMA_50'] = SMAIndicator(close=close, window=EMA_LONG).sma_indicator()
        self.indicators['SMA_200'] = SMAIndicator(close=close, window=EMA_TREND).sma_indicator()

        # Momentum
        rsi = RSIIndicator(close=close, window=RSI_PERIOD)
        self.indicators['RSI'] = rsi.rsi()

        macd = MACD(close=close, window_slow=MACD_SLOW, window_fast=MACD_FAST, window_sign=MACD_SIGNAL)
        self.indicators['MACD'] = macd.macd()
        self.indicators['MACD_Signal'] = macd.macd_signal()
        self.indicators['MACD_Hist'] = macd.macd_diff()

        # Volatility
        bb = BollingerBands(close=close, window=BOLLINGER_PERIOD, window_dev=BOLLINGER_STD)
        self.indicators['BB_Upper'] = bb.bollinger_hband()
        self.indicators['BB_Lower'] = bb.bollinger_lband()
        self.indicators['BB_Middle'] = bb.bollinger_mavg()
        self.indicators['BB_Width'] = bb.bollinger_wband()

        atr = AverageTrueRange(high=high, low=low, close=close, window=ATR_PERIOD)
        self.indicators['ATR'] = atr.average_true_range()

        # Trend Strength
        adx = ADXIndicator(high=high, low=low, close=close, window=ADX_PERIOD)
        self.indicators['ADX'] = adx.adx()
        self.indicators['ADX_Pos'] = adx.adx_pos()
        self.indicators['ADX_Neg'] = adx.adx_neg()

        # Volume
        self.indicators['Volume_MA'] = volume.rolling(window=VOLUME_MA_PERIOD).mean()
        self.indicators['Volume_Ratio'] = volume / self.indicators['Volume_MA']

        # Price Action
        self.indicators['Daily_Return'] = close.pct_change()
        self.indicators['Cumulative_Return'] = (1 + self.indicators['Daily_Return']).cumprod() - 1

        return self.indicators

    def get_trend_analysis(self) -> dict:
        """Analyze overall trend direction and strength"""
        if not self.indicators:
            self.calculate_all_indicators()

        latest = self.data.index[-1]
        close = self.data['Close'].iloc[-1]

        ema9 = self.indicators['EMA_9'].iloc[-1]
        ema20 = self.indicators['EMA_20'].iloc[-1]
        ema50 = self.indicators['EMA_50'].iloc[-1]
        ema200 = self.indicators['EMA_200'].iloc[-1]
        adx = self.indicators['ADX'].iloc[-1]
        rsi = self.indicators['RSI'].iloc[-1]

        # Trend Classification
        trend = {
            'direction': 'Neutral',
            'strength': 'Weak',
            'score': 0,
            'signals': []
        }

        # EMA Alignment
        if close > ema9 > ema20 > ema50 > ema200:
            trend['direction'] = 'Strong Bullish'
            trend['score'] += 3
            trend['signals'].append('Price above all EMAs (Golden alignment)')
        elif close > ema50 > ema200:
            trend['direction'] = 'Bullish'
            trend['score'] += 2
            trend['signals'].append('Price above EMA50 and EMA200')
        elif close < ema9 < ema20 < ema50 < ema200:
            trend['direction'] = 'Strong Bearish'
            trend['score'] -= 3
            trend['signals'].append('Price below all EMAs (Death alignment)')
        elif close < ema50 < ema200:
            trend['direction'] = 'Bearish'
            trend['score'] -= 2
            trend['signals'].append('Price below EMA50 and EMA200')

        # ADX Strength
        if adx > 25:
            trend['strength'] = 'Strong'
            trend['signals'].append(f'ADX = {adx:.1f} (Strong trend)')
        elif adx > 20:
            trend['strength'] = 'Moderate'
            trend['signals'].append(f'ADX = {adx:.1f} (Moderate trend)')
        else:
            trend['strength'] = 'Weak/Consolidation'
            trend['signals'].append(f'ADX = {adx:.1f} (Weak trend/consolidation)')

        # RSI Context
        if rsi > RSI_OVERBOUGHT:
            trend['signals'].append(f'RSI = {rsi:.1f} (Overbought zone)')
        elif rsi < RSI_OVERSOLD:
            trend['signals'].append(f'RSI = {rsi:.1f} (Oversold zone)')
        else:
            trend['signals'].append(f'RSI = {rsi:.1f} (Neutral zone)')

        return trend

    def get_support_resistance(self, lookback: int = 20) -> dict:
        """Calculate dynamic support and resistance levels"""
        if self.data is None:
            self.fetch_data()

        recent = self.data.tail(lookback)

        support = recent['Low'].min()
        resistance = recent['High'].max()
        pivot = (recent['High'].max() + recent['Low'].min() + recent['Close'].iloc[-1]) / 3

        return {
            'support': round(support, 2),
            'resistance': round(resistance, 2),
            'pivot': round(pivot, 2),
            'range_pct': round((resistance - support) / support * 100, 2)
        }

    def get_summary(self) -> dict:
        """Get complete analysis summary"""
        if not self.indicators:
            self.calculate_all_indicators()

        latest = self.data.index[-1]
        close = self.data['Close'].iloc[-1]

        return {
            'symbol': self.symbol,
            'date': latest.strftime('%Y-%m-%d'),
            'price': round(close, 2),
            'change_pct': round(self.indicators['Daily_Return'].iloc[-1] * 100, 2),
            'volume': int(self.data['Volume'].iloc[-1]),
            'rsi': round(self.indicators['RSI'].iloc[-1], 1),
            'macd': round(self.indicators['MACD'].iloc[-1], 3),
            'adx': round(self.indicators['ADX'].iloc[-1], 1),
            'atr': round(self.indicators['ATR'].iloc[-1], 2),
            'bb_position': round((close - self.indicators['BB_Lower'].iloc[-1]) / 
                                  (self.indicators['BB_Upper'].iloc[-1] - self.indicators['BB_Lower'].iloc[-1]) * 100, 1),
            'trend': self.get_trend_analysis(),
            'levels': self.get_support_resistance()
        }
