"""
EGX Pro Terminal - Tests for Technical Analysis Module
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.analysis import TechnicalAnalysis
from core.patterns import PatternEngine, PatternType
from data.market_data import generate_mock_data

class TestTechnicalAnalysis(unittest.TestCase):
    def setUp(self):
        self.ta = TechnicalAnalysis()
        self.df = generate_mock_data("COMI", 252)

    def test_rsi_calculation(self):
        rsi = self.ta.calculate_rsi(self.df["close"])
        self.assertIsNotNone(rsi)
        self.assertTrue(0 <= rsi <= 100)

    def test_macd_calculation(self):
        macd, signal, hist = self.ta.calculate_macd(self.df["close"])
        self.assertIsNotNone(macd)
        self.assertIsNotNone(signal)
        self.assertEqual(len(macd), len(self.df))

    def test_bollinger_bands(self):
        upper, middle, lower = self.ta.calculate_bollinger_bands(self.df["close"])
        self.assertIsNotNone(upper)
        self.assertIsNotNone(middle)
        self.assertIsNotNone(lower)
        self.assertTrue((upper >= middle).all())
        self.assertTrue((middle >= lower).all())

    def test_all_indicators(self):
        indicators = self.ta.calculate_all_indicators(self.df)
        self.assertIn("rsi", indicators)
        self.assertIn("macd", indicators)
        self.assertIn("sma20", indicators)
        self.assertIn("sma50", indicators)

    def test_support_resistance(self):
        levels = self.ta.find_support_resistance(self.df)
        self.assertIn("support", levels)
        self.assertIn("resistance", levels)
        self.assertIn("pivot", levels)
        self.assertIsInstance(levels["support"], list)
        self.assertIsInstance(levels["resistance"], list)

class TestPatternEngine(unittest.TestCase):
    def setUp(self):
        self.engine = PatternEngine()
        self.df = generate_mock_data("COMI", 50)

    def test_pattern_detection(self):
        patterns = self.engine.detect_all(self.df)
        self.assertIsInstance(patterns, list)

    def test_pattern_summary(self):
        summary = self.engine.get_pattern_summary(self.df)
        self.assertIn("total", summary)
        self.assertIn("bullish_count", summary)
        self.assertIn("bearish_count", summary)
        self.assertIn("latest_signal", summary)

    def test_pattern_types(self):
        for name, detector in self.engine.patterns.items():
            result = detector(self.df)
            if result and result.get("found"):
                self.assertIn("type", result)
                self.assertIn(result["type"], [PatternType.BULLISH, PatternType.BEARISH, PatternType.NEUTRAL])

class TestMarketData(unittest.TestCase):
    def test_mock_data_generation(self):
        df = generate_mock_data("COMI", 100)
        self.assertEqual(len(df), 100)
        self.assertIn("open", df.columns)
        self.assertIn("high", df.columns)
        self.assertIn("low", df.columns)
        self.assertIn("close", df.columns)
        self.assertIn("volume", df.columns)

    def test_data_integrity(self):
        df = generate_mock_data("COMI", 50)
        # High should be >= max(open, close)
        self.assertTrue((df["high"] >= df[["open", "close"]].max(axis=1)).all())
        # Low should be <= min(open, close)
        self.assertTrue((df["low"] <= df[["open", "close"]].min(axis=1)).all())
        # Volume should be positive
        self.assertTrue((df["volume"] > 0).all())

if __name__ == "__main__":
    unittest.main()
