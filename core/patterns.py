"""
EGX Pro Terminal v34 - Pattern Recognition Engine
Candlestick pattern detection with confidence scoring
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class PatternType(Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"

@dataclass
class Pattern:
    name: str
    type: PatternType
    confidence: float
    candles_required: int
    description: str

class PatternEngine:
    def __init__(self):
        self.patterns = {
            "hammer": self._is_hammer,
            "inverted_hammer": self._is_inverted_hammer,
            "engulfing_bullish": self._is_bullish_engulfing,
            "engulfing_bearish": self._is_bearish_engulfing,
            "morning_star": self._is_morning_star,
            "evening_star": self._is_evening_star,
            "doji": self._is_doji,
            "shooting_star": self._is_shooting_star,
            "harami_bullish": self._is_bullish_harami,
            "harami_bearish": self._is_bearish_harami,
            "piercing_line": self._is_piercing_line,
            "dark_cloud_cover": self._is_dark_cloud_cover,
            "three_white_soldiers": self._is_three_white_soldiers,
            "three_black_crows": self._is_three_black_crows,
        }

    def detect_all(self, df: pd.DataFrame) -> List[Dict]:
        """Detect all patterns in the dataframe."""
        if df is None or len(df) < 5:
            return []

        detected = []
        for name, detector in self.patterns.items():
            try:
                result = detector(df)
                if result and result.get("found", False):
                    detected.append({
                        "pattern": name,
                        "type": result.get("type", PatternType.NEUTRAL).value,
                        "confidence": result.get("confidence", 0.5),
                        "index": result.get("index", len(df) - 1),
                        "description": result.get("description", "")
                    })
            except Exception:
                continue
        return detected

    def get_pattern_summary(self, df: pd.DataFrame) -> Dict:
        patterns = self.detect_all(df)
        bullish = [p for p in patterns if p["type"] == "bullish"]
        bearish = [p for p in patterns if p["type"] == "bearish"]
        return {
            "total": len(patterns),
            "bullish_count": len(bullish),
            "bearish_count": len(bearish),
            "bullish_patterns": bullish,
            "bearish_patterns": bearish,
            "latest_signal": self._get_latest_signal(patterns)
        }

    def _get_latest_signal(self, patterns: List[Dict]) -> str:
        if not patterns:
            return "NEUTRAL"
        latest = patterns[-1]
        if latest["type"] == "bullish" and latest["confidence"] > 0.7:
            return "BULLISH"
        elif latest["type"] == "bearish" and latest["confidence"] > 0.7:
            return "BEARISH"
        return "NEUTRAL"

    def _body_size(self, o, h, l, c):
        return abs(c - o)

    def _upper_shadow(self, o, h, l, c):
        return h - max(o, c)

    def _lower_shadow(self, o, h, l, c):
        return min(o, c) - l

    def _is_hammer(self, df):
        i = len(df) - 1
        if i < 1: return None
        o, h, l, c = df.iloc[i][["open", "high", "low", "close"]]
        body = self._body_size(o, h, l, c)
        lower = self._lower_shadow(o, h, l, c)
        upper = self._upper_shadow(o, h, l, c)

        if body > 0 and lower > 2 * body and upper < body * 0.5 and c > o:
            return {"found": True, "type": PatternType.BULLISH, "confidence": 0.75,
                    "index": i, "description": "Hammer - potential bullish reversal"}
        return {"found": False}

    def _is_inverted_hammer(self, df):
        i = len(df) - 1
        if i < 1: return None
        o, h, l, c = df.iloc[i][["open", "high", "low", "close"]]
        body = self._body_size(o, h, l, c)
        upper = self._upper_shadow(o, h, l, c)
        lower = self._lower_shadow(o, h, l, c)

        if body > 0 and upper > 2 * body and lower < body * 0.5:
            return {"found": True, "type": PatternType.BULLISH, "confidence": 0.65,
                    "index": i, "description": "Inverted Hammer - potential bullish reversal"}
        return {"found": False}

    def _is_bullish_engulfing(self, df):
        i = len(df) - 1
        if i < 1: return None
        prev = df.iloc[i-1]
        curr = df.iloc[i]

        if (prev["close"] < prev["open"] and curr["close"] > curr["open"] and
            curr["open"] < prev["close"] and curr["close"] > prev["open"]):
            return {"found": True, "type": PatternType.BULLISH, "confidence": 0.85,
                    "index": i, "description": "Bullish Engulfing - strong reversal signal"}
        return {"found": False}

    def _is_bearish_engulfing(self, df):
        i = len(df) - 1
        if i < 1: return None
        prev = df.iloc[i-1]
        curr = df.iloc[i]

        if (prev["close"] > prev["open"] and curr["close"] < curr["open"] and
            curr["open"] > prev["close"] and curr["close"] < prev["open"]):
            return {"found": True, "type": PatternType.BEARISH, "confidence": 0.85,
                    "index": i, "description": "Bearish Engulfing - strong reversal signal"}
        return {"found": False}

    def _is_morning_star(self, df):
        i = len(df) - 1
        if i < 2: return None
        c1, c2, c3 = df.iloc[i-2], df.iloc[i-1], df.iloc[i]

        if (c1["close"] < c1["open"] and abs(c2["close"] - c2["open"]) < abs(c1["close"] - c1["open"]) * 0.3 and
            c3["close"] > c3["open"] and c3["close"] > (c1["open"] + c1["close"]) / 2):
            return {"found": True, "type": PatternType.BULLISH, "confidence": 0.80,
                    "index": i, "description": "Morning Star - bullish reversal"}
        return {"found": False}

    def _is_evening_star(self, df):
        i = len(df) - 1
        if i < 2: return None
        c1, c2, c3 = df.iloc[i-2], df.iloc[i-1], df.iloc[i]

        if (c1["close"] > c1["open"] and abs(c2["close"] - c2["open"]) < abs(c1["close"] - c1["open"]) * 0.3 and
            c3["close"] < c3["open"] and c3["close"] < (c1["open"] + c1["close"]) / 2):
            return {"found": True, "type": PatternType.BEARISH, "confidence": 0.80,
                    "index": i, "description": "Evening Star - bearish reversal"}
        return {"found": False}

    def _is_doji(self, df):
        i = len(df) - 1
        o, h, l, c = df.iloc[i][["open", "high", "low", "close"]]
        body = self._body_size(o, h, l, c)
        range_ = h - l

        if range_ > 0 and body / range_ < 0.1:
            return {"found": True, "type": PatternType.NEUTRAL, "confidence": 0.60,
                    "index": i, "description": "Doji - market indecision"}
        return {"found": False}

    def _is_shooting_star(self, df):
        i = len(df) - 1
        if i < 1: return None
        o, h, l, c = df.iloc[i][["open", "high", "low", "close"]]
        body = self._body_size(o, h, l, c)
        upper = self._upper_shadow(o, h, l, c)
        lower = self._lower_shadow(o, h, l, c)

        if body > 0 and upper > 2 * body and lower < body * 0.3 and c < o:
            return {"found": True, "type": PatternType.BEARISH, "confidence": 0.75,
                    "index": i, "description": "Shooting Star - bearish reversal"}
        return {"found": False}

    def _is_bullish_harami(self, df):
        i = len(df) - 1
        if i < 1: return None
        prev, curr = df.iloc[i-1], df.iloc[i]

        if (prev["close"] < prev["open"] and curr["close"] > curr["open"] and
            curr["open"] > prev["close"] and curr["close"] < prev["open"]):
            return {"found": True, "type": PatternType.BULLISH, "confidence": 0.70,
                    "index": i, "description": "Bullish Harami - potential reversal"}
        return {"found": False}

    def _is_bearish_harami(self, df):
        i = len(df) - 1
        if i < 1: return None
        prev, curr = df.iloc[i-1], df.iloc[i]

        if (prev["close"] > prev["open"] and curr["close"] < curr["open"] and
            curr["open"] < prev["close"] and curr["close"] > prev["open"]):
            return {"found": True, "type": PatternType.BEARISH, "confidence": 0.70,
                    "index": i, "description": "Bearish Harami - potential reversal"}
        return {"found": False}

    def _is_piercing_line(self, df):
        i = len(df) - 1
        if i < 1: return None
        prev, curr = df.iloc[i-1], df.iloc[i]

        if (prev["close"] < prev["open"] and curr["close"] > curr["open"] and
            curr["open"] < prev["low"] and curr["close"] > (prev["open"] + prev["close"]) / 2):
            return {"found": True, "type": PatternType.BULLISH, "confidence": 0.75,
                    "index": i, "description": "Piercing Line - bullish reversal"}
        return {"found": False}

    def _is_dark_cloud_cover(self, df):
        i = len(df) - 1
        if i < 1: return None
        prev, curr = df.iloc[i-1], df.iloc[i]

        if (prev["close"] > prev["open"] and curr["close"] < curr["open"] and
            curr["open"] > prev["high"] and curr["close"] < (prev["open"] + prev["close"]) / 2):
            return {"found": True, "type": PatternType.BEARISH, "confidence": 0.75,
                    "index": i, "description": "Dark Cloud Cover - bearish reversal"}
        return {"found": False}

    def _is_three_white_soldiers(self, df):
        i = len(df) - 1
        if i < 2: return None
        c1, c2, c3 = df.iloc[i-2], df.iloc[i-1], df.iloc[i]

        if (c1["close"] > c1["open"] and c2["close"] > c2["open"] and c3["close"] > c3["open"] and
            c2["open"] > c1["open"] and c3["open"] > c2["open"] and
            c2["close"] > c1["close"] and c3["close"] > c2["close"]):
            return {"found": True, "type": PatternType.BULLISH, "confidence": 0.85,
                    "index": i, "description": "Three White Soldiers - strong bullish"}
        return {"found": False}

    def _is_three_black_crows(self, df):
        i = len(df) - 1
        if i < 2: return None
        c1, c2, c3 = df.iloc[i-2], df.iloc[i-1], df.iloc[i]

        if (c1["close"] < c1["open"] and c2["close"] < c2["open"] and c3["close"] < c3["open"] and
            c2["open"] < c1["open"] and c3["open"] < c2["open"] and
            c2["close"] < c1["close"] and c3["close"] < c2["close"]):
            return {"found": True, "type": PatternType.BEARISH, "confidence": 0.85,
                    "index": i, "description": "Three Black Crows - strong bearish"}
        return {"found": False}

pattern_engine = PatternEngine()
