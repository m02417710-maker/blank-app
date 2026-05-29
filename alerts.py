"""
EGX Pro Terminal v27 - Intelligent Alert Engine
Multi-condition alerts with severity levels and notification channels
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading
import time
import logging

from config.settings import app_config
from data.storage import local_storage
from core.analysis import analysis_engine

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AlertType(Enum):
    PRICE_TARGET = "price_target"
    STOP_LOSS = "stop_loss"
    RSI_OVERSOLD = "rsi_oversold"
    RSI_OVERBOUGHT = "rsi_overbought"
    MACD_CROSS = "macd_cross"
    EMA_CROSS = "ema_cross"
    BB_BREAKOUT = "bb_breakout"
    VOLUME_SPIKE = "volume_spike"
    TREND_CHANGE = "trend_change"
    PATTERN_DETECTED = "pattern_detected"
    SUPPORT_RESISTANCE = "support_resistance"
    FIBONACCI_LEVEL = "fibonacci_level"
    BREAKOUT = "breakout"
    MEAN_REVERSION = "mean_reversion"
    CUSTOM = "custom"

@dataclass
class AlertCondition:
    name: str
    alert_type: AlertType
    symbol: str
    condition_func: Callable
    severity: AlertSeverity = AlertSeverity.INFO
    cooldown_minutes: int = 30
    enabled: bool = True
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    params: Dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

class AlertEngine:
    def __init__(self):
        self.conditions: List[AlertCondition] = []
        self.notification_callbacks: List[Callable] = []
        self.running = False
        self._thread = None
        self._lock = threading.Lock()

    def add_condition(self, condition: AlertCondition) -> bool:
        with self._lock:
            self.conditions.append(condition)
            return True

    def add_price_alert(self, symbol: str, target_price: float, direction: str = 'above',
                        severity: AlertSeverity = AlertSeverity.INFO) -> bool:
        def condition_func(df, params):
            if df is None or df.empty: return False
            current = df['close'].iloc[-1]
            if params['direction'] == 'above': return current >= params['target']
            else: return current <= params['target']

        alert = AlertCondition(
            name=f"Price {direction} {target_price} for {symbol}",
            alert_type=AlertType.PRICE_TARGET,
            symbol=symbol, condition_func=condition_func, severity=severity,
            params={'target': target_price, 'direction': direction})
        return self.add_condition(alert)

    def add_rsi_alert(self, symbol: str, threshold: float = 30, direction: str = 'below') -> bool:
        def condition_func(df, params):
            if df is None or len(df) < 15: return False
            latest = df.iloc[-1]
            rsi = latest.get('rsi', 50)
            if params['direction'] == 'below': return rsi <= params['threshold']
            else: return rsi >= params['threshold']

        alert_type = AlertType.RSI_OVERSOLD if direction == 'below' else AlertType.RSI_OVERBOUGHT
        severity = AlertSeverity.WARNING if direction == 'below' else AlertSeverity.INFO
        alert = AlertCondition(
            name=f"RSI {direction} {threshold} for {symbol}",
            alert_type=alert_type, symbol=symbol, condition_func=condition_func,
            severity=severity, params={'threshold': threshold, 'direction': direction})
        return self.add_condition(alert)

    def add_macd_alert(self, symbol: str, cross_type: str = 'bullish') -> bool:
        def condition_func(df, params):
            if df is None or len(df) < 3: return False
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            if params['cross_type'] == 'bullish':
                return (prev['macd'] < prev['macd_signal']) and (latest['macd'] > latest['macd_signal'])
            else:
                return (prev['macd'] > prev['macd_signal']) and (latest['macd'] < latest['macd_signal'])

        alert = AlertCondition(
            name=f"MACD {cross_type} cross for {symbol}",
            alert_type=AlertType.MACD_CROSS, symbol=symbol,
            condition_func=condition_func, severity=AlertSeverity.WARNING,
            params={'cross_type': cross_type})
        return self.add_condition(alert)

    def add_ema_alert(self, symbol: str, fast: int = 9, slow: int = 21,
                      cross_type: str = 'bullish') -> bool:
        def condition_func(df, params):
            if df is None or len(df) < 3: return False
            fast_col = f"ema_{params['fast']}"
            slow_col = f"ema_{params['slow']}"
            if fast_col not in df.columns or slow_col not in df.columns: return False
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            if params['cross_type'] == 'bullish':
                return (prev[fast_col] < prev[slow_col]) and (latest[fast_col] > latest[slow_col])
            else:
                return (prev[fast_col] > prev[slow_col]) and (latest[fast_col] < latest[slow_col])

        alert = AlertCondition(
            name=f"EMA{fast}/{slow} {cross_type} cross for {symbol}",
            alert_type=AlertType.EMA_CROSS, symbol=symbol,
            condition_func=condition_func, severity=AlertSeverity.CRITICAL,
            params={'fast': fast, 'slow': slow, 'cross_type': cross_type})
        return self.add_condition(alert)

    def add_bb_alert(self, symbol: str, breakout_type: str = 'upper') -> bool:
        def condition_func(df, params):
            if df is None or df.empty: return False
            latest = df.iloc[-1]
            if params['breakout_type'] == 'upper':
                return latest['close'] > latest.get('bb_upper', float('inf'))
            else:
                return latest['close'] < latest.get('bb_lower', 0)

        alert = AlertCondition(
            name=f"BB {breakout_type} breakout for {symbol}",
            alert_type=AlertType.BB_BREAKOUT, symbol=symbol,
            condition_func=condition_func, severity=AlertSeverity.WARNING,
            params={'breakout_type': breakout_type})
        return self.add_condition(alert)

    def add_volume_alert(self, symbol: str, multiplier: float = 2.0) -> bool:
        def condition_func(df, params):
            if df is None or len(df) < 20: return False
            latest = df.iloc[-1]
            return latest.get('volume_ratio', 0) >= params['multiplier']

        alert = AlertCondition(
            name=f"Volume spike {multiplier}x for {symbol}",
            alert_type=AlertType.VOLUME_SPIKE, symbol=symbol,
            condition_func=condition_func, severity=AlertSeverity.INFO,
            params={'multiplier': multiplier})
        return self.add_condition(alert)

    def add_trend_change_alert(self, symbol: str) -> bool:
        def condition_func(df, params):
            if df is None or len(df) < 3: return False
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            current_trend = latest.get('trend', 'Neutral')
            prev_trend = prev.get('trend', 'Neutral')
            return current_trend != prev_trend and current_trend != 'Neutral'

        alert = AlertCondition(
            name=f"Trend change for {symbol}",
            alert_type=AlertType.TREND_CHANGE, symbol=symbol,
            condition_func=condition_func, severity=AlertSeverity.WARNING, params={})
        return self.add_condition(alert)

    def add_breakout_alert(self, symbol: str, level_type: str = 'resistance') -> bool:
        def condition_func(df, params):
            if df is None or df.empty: return False
            latest = df.iloc[-1]
            if params['level_type'] == 'resistance':
                return latest['close'] > latest.get('nearest_resistance', float('inf')) * 0.98
            else:
                return latest['close'] < latest.get('nearest_support', 0) * 1.02

        alert = AlertCondition(
            name=f"{level_type.title()} breakout for {symbol}",
            alert_type=AlertType.BREAKOUT, symbol=symbol,
            condition_func=condition_func, severity=AlertSeverity.CRITICAL,
            params={'level_type': level_type})
        return self.add_condition(alert)

    def add_mean_reversion_alert(self, symbol: str) -> bool:
        def condition_func(df, params):
            if df is None or df.empty: return False
            latest = df.iloc[-1]
            score = latest.get('mean_reversion_score', 0)
            return abs(score) > 0.7

        alert = AlertCondition(
            name=f"Mean reversion signal for {symbol}",
            alert_type=AlertType.MEAN_REVERSION, symbol=symbol,
            condition_func=condition_func, severity=AlertSeverity.WARNING, params={})
        return self.add_condition(alert)

    def check_all(self, symbol: str, df: pd.DataFrame) -> List[Dict]:
        triggered = []
        with self._lock:
            conditions = [c for c in self.conditions if c.symbol == symbol and c.enabled]
            for condition in conditions:
                if condition.last_triggered:
                    cooldown = timedelta(minutes=condition.cooldown_minutes)
                    if datetime.now() - condition.last_triggered < cooldown:
                        continue
                try:
                    if condition.condition_func(df, condition.params):
                        latest = df.iloc[-1]
                        alert_data = {
                            'symbol': symbol,
                            'alert_type': condition.alert_type.value,
                            'name': condition.name,
                            'severity': condition.severity.value,
                            'price': latest['close'],
                            'timestamp': datetime.now().isoformat(),
                            'message': self._generate_message(condition, latest),
                            'condition': condition.name
                        }
                        triggered.append(alert_data)
                        condition.last_triggered = datetime.now()
                        condition.trigger_count += 1

                        try:
                            local_storage.add_alert(
                                symbol=symbol, alert_type=condition.alert_type.value,
                                condition=condition.name, price=latest['close'],
                                message=alert_data['message'], severity=condition.severity.value)
                        except Exception as e:
                            logger.warning(f"Could not store alert: {e}")

                        self._notify(alert_data)
                except Exception as e:
                    logger.error(f"Error checking condition {condition.name}: {e}")
        return triggered

    def _generate_message(self, condition: AlertCondition, latest: pd.Series) -> str:
        price = latest['close']
        rsi_val = latest.get('rsi', None)
        rsi_str = f"{rsi_val:.1f}" if rsi_val is not None else "N/A"
        vol_ratio = latest.get('volume_ratio', None)
        vol_str = f"{vol_ratio:.1f}x average" if vol_ratio is not None else "detected"
        trend = latest.get('trend', 'Unknown')

        messages = {
            AlertType.PRICE_TARGET: f"🎯 Price target reached: {price:.2f} EGP",
            AlertType.STOP_LOSS: f"🛑 Stop loss triggered at {price:.2f} EGP",
            AlertType.RSI_OVERSOLD: f"🥶 RSI oversold: {rsi_str}",
            AlertType.RSI_OVERBOUGHT: f"🥵 RSI overbought: {rsi_str}",
            AlertType.MACD_CROSS: f"📈 MACD crossover detected at {price:.2f} EGP",
            AlertType.EMA_CROSS: f"📊 EMA crossover at {price:.2f} EGP",
            AlertType.BB_BREAKOUT: f"🎢 Bollinger Bands breakout at {price:.2f} EGP",
            AlertType.VOLUME_SPIKE: f"📢 Volume spike: {vol_str}",
            AlertType.TREND_CHANGE: f"📉 Trend changed to {trend}",
            AlertType.PATTERN_DETECTED: f"🔍 Pattern detected at {price:.2f} EGP",
            AlertType.SUPPORT_RESISTANCE: f"🎯 Support/Resistance test at {price:.2f} EGP",
            AlertType.FIBONACCI_LEVEL: f"📐 Fibonacci level reached at {price:.2f} EGP",
            AlertType.BREAKOUT: f"💥 Breakout detected at {price:.2f} EGP",
            AlertType.MEAN_REVERSION: f"🔄 Mean reversion signal at {price:.2f} EGP",
            AlertType.CUSTOM: f"🚨 Alert: {condition.name} at {price:.2f} EGP"
        }
        return messages.get(condition.alert_type, f"Alert: {condition.name}")

    def _notify(self, alert_data: Dict):
        for callback in self.notification_callbacks:
            try:
                callback(alert_data)
            except Exception as e:
                logger.error(f"Notification error: {e}")

    def add_notification_callback(self, callback: Callable):
        self.notification_callbacks.append(callback)

    def remove_condition(self, name: str) -> bool:
        with self._lock:
            self.conditions = [c for c in self.conditions if c.name != name]
            return True

    def get_conditions(self, symbol: Optional[str] = None) -> List[AlertCondition]:
        with self._lock:
            if symbol:
                return [c for c in self.conditions if c.symbol == symbol]
            return self.conditions.copy()

    def enable_condition(self, name: str) -> bool:
        with self._lock:
            for c in self.conditions:
                if c.name == name:
                    c.enabled = True
                    return True
            return False

    def disable_condition(self, name: str) -> bool:
        with self._lock:
            for c in self.conditions:
                if c.name == name:
                    c.enabled = False
                    return True
            return False

    def start_monitoring(self, data_fetcher: Callable, interval: int = 60):
        self.running = True
        def monitor():
            while self.running:
                try:
                    symbols = set(c.symbol for c in self.conditions if c.enabled)
                    for symbol in symbols:
                        df = data_fetcher(symbol)
                        if df is not None:
                            self.check_all(symbol, df)
                    time.sleep(interval)
                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
                    time.sleep(interval)

        self._thread = threading.Thread(target=monitor, daemon=True)
        self._thread.start()
        logger.info(f"Alert monitoring started ({interval}s interval)")

    def stop_monitoring(self):
        self.running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Alert monitoring stopped")

alert_engine = AlertEngine()
