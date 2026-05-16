"""
EGX Pro Terminal - Unit Tests for Analysis Engine
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.analysis import EGXAnalyzer
from config.settings import *

class TestEGXAnalyzer:
    """Test suite for EGXAnalyzer class"""

    @pytest.fixture
    def mock_data(self):
        """Create mock OHLCV data"""
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        np.random.seed(42)

        data = pd.DataFrame({
            'Open': np.random.normal(100, 2, 100),
            'High': np.random.normal(102, 2, 100),
            'Low': np.random.normal(98, 2, 100),
            'Close': np.random.normal(101, 2, 100),
            'Volume': np.random.randint(1000000, 5000000, 100)
        }, index=dates)

        # Ensure High >= Low and High >= Close >= Low
        data['High'] = data[['Open', 'Close', 'High']].max(axis=1) + 0.5
        data['Low'] = data[['Open', 'Close', 'Low']].min(axis=1) - 0.5

        return data

    def test_init(self):
        """Test analyzer initialization"""
        analyzer = EGXAnalyzer("COMI", period="6mo", interval="1d")
        assert analyzer.symbol == "COMI"
        assert analyzer.yahoo_symbol == "COMI.CA"
        assert analyzer.period == "6mo"
        assert analyzer.interval == "1d"

    @patch('core.analysis.yf.Ticker')
    def test_fetch_data(self, mock_ticker, mock_data):
        """Test data fetching"""
        mock_instance = Mock()
        mock_instance.history.return_value = mock_data
        mock_ticker.return_value = mock_instance

        analyzer = EGXAnalyzer("COMI")
        result = analyzer.fetch_data()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 100
        assert all(col in result.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume'])

    @patch('core.analysis.yf.Ticker')
    def test_calculate_indicators(self, mock_ticker, mock_data):
        """Test indicator calculations"""
        mock_instance = Mock()
        mock_instance.history.return_value = mock_data
        mock_ticker.return_value = mock_instance

        analyzer = EGXAnalyzer("COMI")
        analyzer.fetch_data()
        indicators = analyzer.calculate_all_indicators()

        required_indicators = [
            'EMA_9', 'EMA_20', 'EMA_50', 'EMA_200',
            'RSI', 'MACD', 'MACD_Signal', 'MACD_Hist',
            'BB_Upper', 'BB_Lower', 'BB_Middle',
            'ATR', 'ADX', 'ADX_Pos', 'ADX_Neg',
            'Volume_MA', 'Volume_Ratio'
        ]

        for ind in required_indicators:
            assert ind in indicators, f"Missing indicator: {ind}"
            assert isinstance(indicators[ind], pd.Series)

    @patch('core.analysis.yf.Ticker')
    def test_trend_analysis(self, mock_ticker, mock_data):
        """Test trend analysis"""
        mock_instance = Mock()
        mock_instance.history.return_value = mock_data
        mock_ticker.return_value = mock_instance

        analyzer = EGXAnalyzer("COMI")
        analyzer.fetch_data()
        analyzer.calculate_all_indicators()

        trend = analyzer.get_trend_analysis()

        assert 'direction' in trend
        assert 'strength' in trend
        assert 'score' in trend
        assert 'signals' in trend
        assert isinstance(trend['score'], int)
        assert isinstance(trend['signals'], list)

    @patch('core.analysis.yf.Ticker')
    def test_support_resistance(self, mock_ticker, mock_data):
        """Test support/resistance calculation"""
        mock_instance = Mock()
        mock_instance.history.return_value = mock_data
        mock_ticker.return_value = mock_instance

        analyzer = EGXAnalyzer("COMI")
        analyzer.fetch_data()

        levels = analyzer.get_support_resistance(lookback=20)

        assert 'support' in levels
        assert 'resistance' in levels
        assert 'pivot' in levels
        assert 'range_pct' in levels

        assert levels['support'] < levels['resistance']
        assert levels['pivot'] > levels['support']
        assert levels['pivot'] < levels['resistance']

    @patch('core.analysis.yf.Ticker')
    def test_summary(self, mock_ticker, mock_data):
        """Test summary generation"""
        mock_instance = Mock()
        mock_instance.history.return_value = mock_data
        mock_ticker.return_value = mock_instance

        analyzer = EGXAnalyzer("COMI")
        summary = analyzer.get_summary()

        required_keys = [
            'symbol', 'date', 'price', 'change_pct', 'volume',
            'rsi', 'macd', 'adx', 'atr', 'bb_position',
            'trend', 'levels'
        ]

        for key in required_keys:
            assert key in summary, f"Missing summary key: {key}"

    def test_empty_data_error(self):
        """Test handling of empty data"""
        with patch('core.analysis.yf.Ticker') as mock_ticker:
            mock_instance = Mock()
            mock_instance.history.return_value = pd.DataFrame()
            mock_ticker.return_value = mock_instance

            analyzer = EGXAnalyzer("COMI")

            with pytest.raises(ValueError):
                analyzer.fetch_data()


class TestSettings:
    """Test configuration settings"""

    def test_app_info(self):
        """Test application info constants"""
        assert APP_NAME == "EGX Pro Terminal"
        assert APP_VERSION == "v26.0.0"
        assert APP_AUTHOR == "m02417710-maker"

    def test_data_sources(self):
        """Test data source configuration"""
        assert YAHOO_FINANCE_SUFFIX == ".CA"
        assert DEFAULT_PERIOD == "1y"
        assert DEFAULT_INTERVAL == "1d"

    def test_indicator_params(self):
        """Test indicator parameters"""
        assert RSI_PERIOD == 14
        assert RSI_OVERBOUGHT == 70
        assert RSI_OVERSOLD == 30
        assert MACD_FAST == 12
        assert MACD_SLOW == 26
        assert MACD_SIGNAL == 9
        assert BOLLINGER_PERIOD == 20
        assert BOLLINGER_STD == 2

    def test_alert_thresholds(self):
        """Test alert thresholds"""
        assert ALERT_RSI_EXTREME == 80
        assert ALERT_RSI_DEEP == 20
        assert ALERT_VOLUME_SPIKE == 2.0
        assert ALERT_PRICE_CHANGE == 0.05


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
