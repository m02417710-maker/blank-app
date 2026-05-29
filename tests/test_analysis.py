"""
EGX Pro Terminal v27 - Analysis Unit Tests
Comprehensive testing for technical analysis engine
"""

import unittest
import pandas as pd
import numpy as np
from core.analysis import analysis_engine
from core.patterns import pattern_engine
from core.ai_engine import ai_engine
from core.backtest import backtest_engine

class TestTechnicalAnalysis(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        self.sample_df = pd.DataFrame({
            'date': dates,
            'open': 100 + np.cumsum(np.random.randn(100) * 0.5),
            'high': 102 + np.cumsum(np.random.randn(100) * 0.5),
            'low': 98 + np.cumsum(np.random.randn(100) * 0.5),
            'close': 100 + np.cumsum(np.random.randn(100) * 0.5),
            'volume': np.random.randint(100000, 1000000, 100)
        })
        self.sample_df['high'] = self.sample_df[['open', 'high', 'close']].max(axis=1)
        self.sample_df['low'] = self.sample_df[['open', 'low', 'close']].min(axis=1)

    def test_compute_all(self):
        result = analysis_engine.compute_all(self.sample_df)
        self.assertIsNotNone(result)
        self.assertFalse(result.empty)
        self.assertIn('rsi', result.columns)
        self.assertIn('macd', result.columns)
        self.assertIn('ema_9', result.columns)

    def test_rsi_calculation(self):
        result = analysis_engine.compute_all(self.sample_df)
        rsi = result['rsi'].dropna()
        self.assertTrue((rsi >= 0).all() and (rsi <= 100).all())

    def test_macd_calculation(self):
        result = analysis_engine.compute_all(self.sample_df)
        self.assertIn('macd', result.columns)
        self.assertIn('macd_signal', result.columns)
        self.assertIn('macd_hist', result.columns)

    def test_bollinger_bands(self):
        result = analysis_engine.compute_all(self.sample_df)
        bb_upper = result['bb_upper'].dropna()
        bb_lower = result['bb_lower'].dropna()
        self.assertTrue((bb_upper >= bb_lower).all())

    def test_support_resistance(self):
        result = analysis_engine.compute_all(self.sample_df)
        summary = analysis_engine.get_summary(result)
        self.assertIn('support_resistance', summary)
        self.assertIn('nearest_support', summary['support_resistance'])
        self.assertIn('nearest_resistance', summary['support_resistance'])

    def test_fibonacci_levels(self):
        result = analysis_engine.compute_all(self.sample_df)
        fib = analysis_engine.get_fibonacci_levels(result)
        self.assertEqual(len(fib), 7)
        self.assertIn('0.0', fib)
        self.assertIn('1.0', fib)

    def test_signal_generation(self):
        result = analysis_engine.compute_all(self.sample_df)
        self.assertIn('composite_signal', result.columns)
        self.assertIn('final_signal', result.columns)
        signals = result['final_signal'].unique()
        self.assertTrue(all(s in ['STRONG BUY', 'BUY', 'NEUTRAL', 'SELL', 'STRONG SELL'] for s in signals))

    def test_summary(self):
        result = analysis_engine.compute_all(self.sample_df)
        summary = analysis_engine.get_summary(result)
        self.assertIn('price', summary)
        self.assertIn('rsi', summary)
        self.assertIn('signals', summary)

class TestPatternRecognition(unittest.TestCase):
    def setUp(self):
        self.sample_df = pd.DataFrame({
            'open': [100, 102, 101, 99, 98, 97, 96, 95, 94, 93],
            'high': [103, 104, 103, 101, 100, 99, 98, 97, 96, 95],
            'low': [98, 100, 99, 97, 96, 95, 94, 93, 92, 91],
            'close': [102, 101, 99, 98, 97, 96, 95, 94, 93, 92]
        })

    def test_detect_patterns(self):
        patterns = pattern_engine.detect_all(self.sample_df)
        self.assertIsInstance(patterns, list)

    def test_pattern_summary(self):
        summary = pattern_engine.get_pattern_summary(self.sample_df)
        self.assertIn('total', summary)
        self.assertIn('bullish_count', summary)
        self.assertIn('bearish_count', summary)

class TestAIPrediction(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        self.sample_df = pd.DataFrame({
            'date': dates,
            'open': 100 + np.cumsum(np.random.randn(100) * 0.5),
            'high': 102 + np.cumsum(np.random.randn(100) * 0.5),
            'low': 98 + np.cumsum(np.random.randn(100) * 0.5),
            'close': 100 + np.cumsum(np.random.randn(100) * 0.5),
            'volume': np.random.randint(100000, 1000000, 100)
        })
        self.sample_df = analysis_engine.compute_all(self.sample_df)

    def test_prediction(self):
        result = ai_engine.predict(self.sample_df, "TEST")
        self.assertIsNotNone(result)
        self.assertIn(result.predicted_direction, ['UP', 'DOWN', 'SIDEWAYS'])
        self.assertTrue(0 <= result.confidence <= 1)

    def test_monte_carlo(self):
        result = ai_engine.predict(self.sample_df, "TEST")
        self.assertIsNotNone(result.monte_carlo_results)
        self.assertIn('mean_price', result.monte_carlo_results)

    def test_scenario_analysis(self):
        result = ai_engine.predict(self.sample_df, "TEST")
        self.assertIsNotNone(result.scenario_analysis)
        self.assertIn('bullish', result.scenario_analysis)

class TestBacktest(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        dates = pd.date_range('2024-01-01', periods=200, freq='D')
        self.sample_df = pd.DataFrame({
            'date': dates,
            'open': 100 + np.cumsum(np.random.randn(200) * 0.5),
            'high': 102 + np.cumsum(np.random.randn(200) * 0.5),
            'low': 98 + np.cumsum(np.random.randn(200) * 0.5),
            'close': 100 + np.cumsum(np.random.randn(200) * 0.5),
            'volume': np.random.randint(100000, 1000000, 200)
        })
        self.sample_df = analysis_engine.compute_all(self.sample_df)

    def test_rsi_strategy(self):
        result = backtest_engine.run_strategy(self.sample_df, 'rsi', symbol='TEST')
        self.assertIsNotNone(result)
        self.assertIsInstance(result.total_return_pct, float)

    def test_macd_strategy(self):
        result = backtest_engine.run_strategy(self.sample_df, 'macd', symbol='TEST')
        self.assertIsNotNone(result)

    def test_ema_strategy(self):
        result = backtest_engine.run_strategy(self.sample_df, 'ema', symbol='TEST')
        self.assertIsNotNone(result)

    def test_metrics(self):
        result = backtest_engine.run_strategy(self.sample_df, 'rsi', symbol='TEST')
        self.assertIsNotNone(result.sharpe_ratio)
        self.assertIsNotNone(result.max_drawdown_pct)
        self.assertIsNotNone(result.win_rate)

    def test_strategy_list(self):
        strategies = backtest_engine.get_strategy_list()
        self.assertIsInstance(strategies, dict)
        self.assertTrue(len(strategies) > 0)

if __name__ == '__main__':
    unittest.main()
