"""
EGX Pro Terminal - Unit Tests for Alert Engine
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from unittest.mock import Mock, patch
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.alerts import AlertEngine, TradingAlert, SignalType, AlertPriority

class TestAlertEngine:
    """Test suite for AlertEngine"""

    @pytest.fixture
    def engine(self):
        """Create fresh alert engine"""
        return AlertEngine()

    @pytest.fixture
    def mock_analyzer(self):
        """Create mock analyzer with test data"""
        mock = Mock()

        dates = pd.date_range(start='2024-01-01', periods=50, freq='D')
        mock.data = pd.DataFrame({
            'Open': np.linspace(100, 120, 50),
            'High': np.linspace(102, 122, 50),
            'Low': np.linspace(98, 118, 50),
            'Close': np.linspace(101, 121, 50),
            'Volume': np.random.randint(1000000, 5000000, 50)
        }, index=dates)

        mock.indicators = {
            'RSI': pd.Series([35] * 50, index=dates),  # Near oversold
            'MACD': pd.Series([0.5] * 50, index=dates),
            'MACD_Signal': pd.Series([0.3] * 50, index=dates),
            'EMA_9': pd.Series([110] * 50, index=dates),
            'EMA_20': pd.Series([108] * 50, index=dates),
            'Volume_Ratio': pd.Series([1.5] * 50, index=dates),
            'ADX': pd.Series([28] * 50, index=dates),
            'ADX_Pos': pd.Series([25] * 50, index=dates),
            'ADX_Neg': pd.Series([15] * 50, index=dates),
            'BB_Upper': pd.Series([125] * 50, index=dates),
            'BB_Lower': pd.Series([95] * 50, index=dates),
            'BB_Width': pd.Series([30] * 50, index=dates),
        }

        return mock

    def test_init(self, engine):
        """Test engine initialization"""
        assert engine.alerts_history == []
        assert engine.watchlist == []

    def test_watchlist_management(self, engine):
        """Test watchlist add/remove"""
        engine.add_to_watchlist("COMI")
        assert "COMI" in engine.watchlist

        engine.add_to_watchlist("comi")  # Case insensitive
        assert "COMI" in engine.watchlist
        assert len(engine.watchlist) == 1

        engine.remove_from_watchlist("COMI")
        assert "COMI" not in engine.watchlist

    @patch('core.alerts.EGXAnalyzer')
    def test_scan_stock_rsi_alert(self, mock_analyzer_class, engine, mock_analyzer):
        """Test RSI-based alert generation"""
        mock_analyzer_class.return_value = mock_analyzer
        mock_analyzer.fetch_data.return_value = None
        mock_analyzer.calculate_all_indicators.return_value = None

        # Set RSI to oversold level
        mock_analyzer.indicators['RSI'] = pd.Series([25] * 50, index=mock_analyzer.data.index)

        alerts = engine.scan_stock("COMI")

        assert len(alerts) > 0
        assert any(a.signal == SignalType.BUY for a in alerts)

    @patch('core.alerts.EGXAnalyzer')
    def test_scan_stock_macd_crossover(self, mock_analyzer_class, engine, mock_analyzer):
        """Test MACD crossover alert"""
        mock_analyzer_class.return_value = mock_analyzer
        mock_analyzer.fetch_data.return_value = None
        mock_analyzer.calculate_all_indicators.return_value = None

        # Create MACD crossover scenario
        macd_values = [0.2] * 49 + [0.6]
        signal_values = [0.4] * 49 + [0.3]
        mock_analyzer.indicators['MACD'] = pd.Series(macd_values, index=mock_analyzer.data.index)
        mock_analyzer.indicators['MACD_Signal'] = pd.Series(signal_values, index=mock_analyzer.data.index)

        alerts = engine.scan_stock("COMI")

        # Should detect golden cross
        assert any(a.signal in [SignalType.BUY, SignalType.STRONG_BUY] for a in alerts)

    def test_alert_to_dict(self):
        """Test alert serialization"""
        alert = TradingAlert(
            symbol="COMI",
            signal=SignalType.BUY,
            priority=AlertPriority.HIGH,
            price=150.5,
            timestamp=datetime.now(),
            message="Test alert",
            indicators={"RSI": 25}
        )

        d = alert.to_dict()
        assert d['symbol'] == "COMI"
        assert d['signal'] == "BUY"
        assert d['price'] == 150.5
        assert 'timestamp' in d

    def test_recent_alerts(self, engine):
        """Test recent alerts filtering"""
        from datetime import timedelta

        # Add old alert
        old_alert = TradingAlert(
            symbol="COMI",
            signal=SignalType.BUY,
            priority=AlertPriority.LOW,
            price=100,
            timestamp=datetime.now() - timedelta(hours=48),
            message="Old",
            indicators={}
        )
        engine.alerts_history.append(old_alert)

        # Add recent alert
        recent_alert = TradingAlert(
            symbol="TMGH",
            signal=SignalType.SELL,
            priority=AlertPriority.MEDIUM,
            price=200,
            timestamp=datetime.now(),
            message="Recent",
            indicators={}
        )
        engine.alerts_history.append(recent_alert)

        recent = engine.get_recent_alerts(hours=24)
        assert len(recent) == 1
        assert recent[0].symbol == "TMGH"

    def test_alert_summary(self, engine):
        """Test alert summary"""
        summary = engine.get_alert_summary()
        assert summary['total'] == 0
        assert summary['by_signal'] == {}
        assert summary['by_priority'] == {}

        # Add test alerts
        engine.alerts_history.append(TradingAlert(
            symbol="COMI", signal=SignalType.BUY, priority=AlertPriority.HIGH,
            price=100, timestamp=datetime.now(), message="Test", indicators={}
        ))
        engine.alerts_history.append(TradingAlert(
            symbol="TMGH", signal=SignalType.SELL, priority=AlertPriority.MEDIUM,
            price=200, timestamp=datetime.now(), message="Test", indicators={}
        ))

        summary = engine.get_alert_summary()
        assert summary['total'] == 2
        assert summary['by_signal']['BUY'] == 1
        assert summary['by_signal']['SELL'] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
