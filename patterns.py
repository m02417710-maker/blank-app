"""
EGX Pro Terminal - Candlestick Pattern Recognition
Detects common Japanese candlestick patterns for EGX stocks
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class PatternType(Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"

@dataclass
class CandlePattern:
    name: str
    name_ar: str
    type: PatternType
    reliability: int  # 1-5, 5 being most reliable
    description: str

class PatternRecognizer:
    """Recognizes candlestick patterns in OHLC data"""

    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.patterns: List[CandlePattern] = []

    def _get_candle_properties(self, idx: int) -> dict:
        """Calculate candle properties"""
        row = self.data.iloc[idx]
        open_p = row['Open']
        high = row['High']
        low = row['Low']
        close = row['Close']

        body = abs(close - open_p)
        upper_shadow = high - max(open_p, close)
        lower_shadow = min(open_p, close) - low
        total_range = high - low

        is_bullish = close > open_p
        is_bearish = close < open_p

        return {
            'open': open_p,
            'high': high,
            'low': low,
            'close': close,
            'body': body,
            'upper_shadow': upper_shadow,
            'lower_shadow': lower_shadow,
            'total_range': total_range,
            'is_bullish': is_bullish,
            'is_bearish': is_bearish,
            'body_pct': body / total_range if total_range > 0 else 0,
            'upper_pct': upper_shadow / total_range if total_range > 0 else 0,
            'lower_pct': lower_shadow / total_range if total_range > 0 else 0
        }

    def detect_doji(self, idx: int) -> Optional[CandlePattern]:
        """Detect Doji pattern"""
        c = self._get_candle_properties(idx)

        if c['body_pct'] < 0.1 and c['total_range'] > 0:
            return CandlePattern(
                name="Doji",
                name_ar="دوجي",
                type=PatternType.NEUTRAL,
                reliability=2,
                description="شمعة بجسم صغير جداً تشير إلى تردد السوق"
            )
        return None

    def detect_hammer(self, idx: int) -> Optional[CandlePattern]:
        """Detect Hammer pattern (bullish reversal)"""
        c = self._get_candle_properties(idx)

        if c['is_bullish'] and c['lower_pct'] > 0.6 and c['body_pct'] > 0.2 and c['upper_pct'] < 0.1:
            return CandlePattern(
                name="Hammer",
                name_ar="المطرقة",
                type=PatternType.BULLISH,
                reliability=3,
                description="شمعة صاعدة بظل سفلي طويل تشير إلى انعكاس هابط"
            )
        return None

    def detect_shooting_star(self, idx: int) -> Optional[CandlePattern]:
        """Detect Shooting Star pattern (bearish reversal)"""
        c = self._get_candle_properties(idx)

        if c['is_bearish'] and c['upper_pct'] > 0.6 and c['body_pct'] > 0.2 and c['lower_pct'] < 0.1:
            return CandlePattern(
                name="Shooting Star",
                name_ar="النجمة الرماية",
                type=PatternType.BEARISH,
                reliability=3,
                description="شمعة هابطة بظل علوي طويل تشير إلى انعكاس صاعد"
            )
        return None

    def detect_engulfing(self, idx: int) -> Optional[CandlePattern]:
        """Detect Bullish/Bearish Engulfing pattern"""
        if idx < 1:
            return None

        prev = self._get_candle_properties(idx - 1)
        curr = self._get_candle_properties(idx)

        # Bullish Engulfing
        if (prev['is_bearish'] and curr['is_bullish'] and 
            curr['open'] < prev['close'] and curr['close'] > prev['open'] and
            curr['body'] > prev['body']):
            return CandlePattern(
                name="Bullish Engulfing",
                name_ar="الابتلاع الصاعد",
                type=PatternType.BULLISH,
                reliability=4,
                description="شمعة صاعدة تبتلع الشمعة السابقة الهابطة - إشارة انعكاس قوية"
            )

        # Bearish Engulfing
        if (prev['is_bullish'] and curr['is_bearish'] and 
            curr['open'] > prev['close'] and curr['close'] < prev['open'] and
            curr['body'] > prev['body']):
            return CandlePattern(
                name="Bearish Engulfing",
                name_ar="الابتلاع الهابط",
                type=PatternType.BEARISH,
                reliability=4,
                description="شمعة هابطة تبتلع الشمعة السابقة الصاعدة - إشارة انعكاس قوية"
            )
        return None

    def detect_morning_star(self, idx: int) -> Optional[CandlePattern]:
        """Detect Morning Star pattern (bullish reversal)"""
        if idx < 2:
            return None

        first = self._get_candle_properties(idx - 2)
        second = self._get_candle_properties(idx - 1)
        third = self._get_candle_properties(idx)

        if (first['is_bearish'] and first['body_pct'] > 0.5 and
            second['body_pct'] < 0.3 and
            third['is_bullish'] and third['body_pct'] > 0.5 and
            third['close'] > (first['open'] + first['close']) / 2):
            return CandlePattern(
                name="Morning Star",
                name_ar="نجمة الصباح",
                type=PatternType.BULLISH,
                reliability=5,
                description="نمط ثلاثي شموع يشير إلى انعكاس صاعد قوي"
            )
        return None

    def detect_evening_star(self, idx: int) -> Optional[CandlePattern]:
        """Detect Evening Star pattern (bearish reversal)"""
        if idx < 2:
            return None

        first = self._get_candle_properties(idx - 2)
        second = self._get_candle_properties(idx - 1)
        third = self._get_candle_properties(idx)

        if (first['is_bullish'] and first['body_pct'] > 0.5 and
            second['body_pct'] < 0.3 and
            third['is_bearish'] and third['body_pct'] > 0.5 and
            third['close'] < (first['open'] + first['close']) / 2):
            return CandlePattern(
                name="Evening Star",
                name_ar="نجمة المساء",
                type=PatternType.BEARISH,
                reliability=5,
                description="نمط ثلاثي شموع يشير إلى انعكاس هابط قوي"
            )
        return None

    def scan_all_patterns(self) -> List[Dict]:
        """Scan all candles for patterns"""
        results = []

        for i in range(len(self.data)):
            patterns_found = []

            # Single candle patterns
            for detector in [self.detect_doji, self.detect_hammer, self.detect_shooting_star]:
                pattern = detector(i)
                if pattern:
                    patterns_found.append(pattern)

            # Multi-candle patterns
            for detector in [self.detect_engulfing, self.detect_morning_star, self.detect_evening_star]:
                pattern = detector(i)
                if pattern:
                    patterns_found.append(pattern)

            if patterns_found:
                results.append({
                    'date': self.data.index[i],
                    'patterns': [
                        {
                            'name': p.name,
                            'name_ar': p.name_ar,
                            'type': p.type.value,
                            'reliability': p.reliability,
                            'description': p.description
                        }
                        for p in patterns_found
                    ]
                })

        return results

    def get_latest_patterns(self, n: int = 5) -> List[Dict]:
        """Get patterns from last N candles"""
        all_patterns = self.scan_all_patterns()
        return all_patterns[-n:] if all_patterns else []
