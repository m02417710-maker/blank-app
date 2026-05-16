"""
EGX Pro Terminal - Smart Alert System
Automated trading alerts and signal generation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import *
from core.analysis import EGXAnalyzer

class SignalType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    STRONG_BUY = "STRONG_BUY"
    STRONG_SELL = "STRONG_SELL"

class AlertPriority(Enum):
    HIGH = "🔴 عالي"
    MEDIUM = "🟡 متوسط"
    LOW = "🟢 منخفض"

@dataclass
class TradingAlert:
    symbol: str
    signal: SignalType
    priority: AlertPriority
    price: float
    timestamp: datetime
    message: str
    indicators: Dict

    def to_dict(self) -> dict:
        return {
            'symbol': self.symbol,
            'signal': self.signal.value,
            'priority': self.priority.value,
            'price': self.price,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M'),
            'message': self.message,
            'indicators': self.indicators
        }

class AlertEngine:
    """Professional alert engine for EGX stocks"""

    def __init__(self):
        self.alerts_history: List[TradingAlert] = []
        self.watchlist: List[str] = []

    def add_to_watchlist(self, symbol: str):
        """Add stock to monitoring watchlist"""
        if symbol.upper() not in self.watchlist:
            self.watchlist.append(symbol.upper())

    def remove_from_watchlist(self, symbol: str):
        """Remove stock from watchlist"""
        if symbol.upper() in self.watchlist:
            self.watchlist.remove(symbol.upper())

    def scan_stock(self, symbol: str) -> List[TradingAlert]:
        """Scan single stock for trading signals"""
        alerts = []
        try:
            analyzer = EGXAnalyzer(symbol)
            analyzer.fetch_data()
            analyzer.calculate_all_indicators()

            data = analyzer.data
            indicators = analyzer.indicators
            latest_idx = data.index[-1]
            close = data['Close'].iloc[-1]

            # 1. RSI Extreme Levels
            rsi = indicators['RSI'].iloc[-1]
            if rsi < ALERT_RSI_DEEP:
                alerts.append(TradingAlert(
                    symbol=symbol,
                    signal=SignalType.STRONG_BUY,
                    priority=AlertPriority.HIGH,
                    price=close,
                    timestamp=latest_idx,
                    message=f"RSI متطرف منخفض ({rsi:.1f}) - منطقة تشبع بيعي قوية",
                    indicators={'RSI': rsi, 'level': 'Oversold'}
                ))
            elif rsi < RSI_OVERSOLD:
                alerts.append(TradingAlert(
                    symbol=symbol,
                    signal=SignalType.BUY,
                    priority=AlertPriority.MEDIUM,
                    price=close,
                    timestamp=latest_idx,
                    message=f"RSI في منطقة التشبع البيعي ({rsi:.1f})",
                    indicators={'RSI': rsi, 'level': 'Near Oversold'}
                ))
            elif rsi > ALERT_RSI_EXTREME:
                alerts.append(TradingAlert(
                    symbol=symbol,
                    signal=SignalType.STRONG_SELL,
                    priority=AlertPriority.HIGH,
                    price=close,
                    timestamp=latest_idx,
                    message=f"RSI متطرف مرتفع ({rsi:.1f}) - منطقة تشبع شرائي قوية",
                    indicators={'RSI': rsi, 'level': 'Overbought'}
                ))
            elif rsi > RSI_OVERBOUGHT:
                alerts.append(TradingAlert(
                    symbol=symbol,
                    signal=SignalType.SELL,
                    priority=AlertPriority.MEDIUM,
                    price=close,
                    timestamp=latest_idx,
                    message=f"RSI في منطقة التشبع الشرائي ({rsi:.1f})",
                    indicators={'RSI': rsi, 'level': 'Near Overbought'}
                ))

            # 2. MACD Crossover
            macd = indicators['MACD'].iloc[-1]
            macd_signal = indicators['MACD_Signal'].iloc[-1]
            macd_prev = indicators['MACD'].iloc[-2]
            signal_prev = indicators['MACD_Signal'].iloc[-2]

            if macd_prev < signal_prev and macd > macd_signal:
                alerts.append(TradingAlert(
                    symbol=symbol,
                    signal=SignalType.BUY,
                    priority=AlertPriority.HIGH,
                    price=close,
                    timestamp=latest_idx,
                    message="تقاطع MACD إيجابي (الخط السريع يتجاوز البطيء من أسفل)",
                    indicators={'MACD': macd, 'Signal': macd_signal, 'cross': 'Golden Cross'}
                ))
            elif macd_prev > signal_prev and macd < macd_signal:
                alerts.append(TradingAlert(
                    symbol=symbol,
                    signal=SignalType.SELL,
                    priority=AlertPriority.HIGH,
                    price=close,
                    timestamp=latest_idx,
                    message="تقاطع MACD سلبي (الخط السريع يتجاوز البطيء من أعلى)",
                    indicators={'MACD': macd, 'Signal': macd_signal, 'cross': 'Death Cross'}
                ))

            # 3. EMA Crossover (9 vs 20)
            ema9 = indicators['EMA_9'].iloc[-1]
            ema20 = indicators['EMA_20'].iloc[-1]
            ema9_prev = indicators['EMA_9'].iloc[-2]
            ema20_prev = indicators['EMA_20'].iloc[-2]

            if ema9_prev < ema20_prev and ema9 > ema20:
                alerts.append(TradingAlert(
                    symbol=symbol,
                    signal=SignalType.BUY,
                    priority=AlertPriority.MEDIUM,
                    price=close,
                    timestamp=latest_idx,
                    message="تقاطع EMA9/20 إيجابي - إشارة دخول قصيرة المدى",
                    indicators={'EMA9': ema9, 'EMA20': ema20}
                ))
            elif ema9_prev > ema20_prev and ema9 < ema20:
                alerts.append(TradingAlert(
                    symbol=symbol,
                    signal=SignalType.SELL,
                    priority=AlertPriority.MEDIUM,
                    price=close,
                    timestamp=latest_idx,
                    message="تقاطع EMA9/20 سلبي - إشارة خروج قصيرة المدى",
                    indicators={'EMA9': ema9, 'EMA20': ema20}
                ))

            # 4. Volume Spike
            vol_ratio = indicators['Volume_Ratio'].iloc[-1]
            if vol_ratio > ALERT_VOLUME_SPIKE:
                direction = "شرائي" if close > data['Open'].iloc[-1] else "بيعي"
                alerts.append(TradingAlert(
                    symbol=symbol,
                    signal=SignalType.BUY if direction == "شرائي" else SignalType.SELL,
                    priority=AlertPriority.MEDIUM,
                    price=close,
                    timestamp=latest_idx,
                    message=f"ارتفاع حجم تداول استثنائي ({vol_ratio:.1f}x المتوسط) - ضغط {direction}",
                    indicators={'Volume_Ratio': vol_ratio, 'Volume': int(data['Volume'].iloc[-1])}
                ))

            # 5. Bollinger Bands Breakout
            bb_upper = indicators['BB_Upper'].iloc[-1]
            bb_lower = indicators['BB_Lower'].iloc[-1]
            bb_width = indicators['BB_Width'].iloc[-1]

            if close > bb_upper and bb_width > bb_width * 0.5:  # Not too narrow
                alerts.append(TradingAlert(
                    symbol=symbol,
                    signal=SignalType.BUY,
                    priority=AlertPriority.LOW,
                    price=close,
                    timestamp=latest_idx,
                    message="اختراق Bollinger Bands العلوي - زخم صاعد",
                    indicators={'BB_Upper': bb_upper, 'BB_Width': bb_width}
                ))
            elif close < bb_lower and bb_width > bb_width * 0.5:
                alerts.append(TradingAlert(
                    symbol=symbol,
                    signal=SignalType.SELL,
                    priority=AlertPriority.LOW,
                    price=close,
                    timestamp=latest_idx,
                    message="اختراق Bollinger Bands السفلي - زخم هابط",
                    indicators={'BB_Lower': bb_lower, 'BB_Width': bb_width}
                ))

            # 6. ADX Trend Strength Alert
            adx = indicators['ADX'].iloc[-1]
            if adx > 30:
                adx_pos = indicators['ADX_Pos'].iloc[-1]
                adx_neg = indicators['ADX_Neg'].iloc[-1]
                trend_dir = "صاعد" if adx_pos > adx_neg else "هابط"
                alerts.append(TradingAlert(
                    symbol=symbol,
                    signal=SignalType.BUY if trend_dir == "صاعد" else SignalType.SELL,
                    priority=AlertPriority.LOW,
                    price=close,
                    timestamp=latest_idx,
                    message=f"ADX قوي ({adx:.1f}) - اتجاه {trend_dir} مؤكد",
                    indicators={'ADX': adx, 'DI+': adx_pos, 'DI-': adx_neg}
                ))

            # Store alerts
            self.alerts_history.extend(alerts)

        except Exception as e:
            print(f"Error scanning {symbol}: {str(e)}")

        return alerts

    def scan_watchlist(self) -> Dict[str, List[TradingAlert]]:
        """Scan all stocks in watchlist"""
        results = {}
        for symbol in self.watchlist:
            results[symbol] = self.scan_stock(symbol)
        return results

    def get_recent_alerts(self, hours: int = 24) -> List[TradingAlert]:
        """Get alerts from last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [a for a in self.alerts_history if a.timestamp > cutoff]

    def get_alert_summary(self) -> dict:
        """Get summary of all alerts"""
        if not self.alerts_history:
            return {"total": 0, "by_signal": {}, "by_priority": {}}

        by_signal = {}
        by_priority = {}

        for alert in self.alerts_history:
            by_signal[alert.signal.value] = by_signal.get(alert.signal.value, 0) + 1
            by_priority[alert.priority.value] = by_priority.get(alert.priority.value, 0) + 1

        return {
            "total": len(self.alerts_history),
            "by_signal": by_signal,
            "by_priority": by_priority
        }
