# 🇪🇬 EGX Pro Terminal

**Professional Egyptian Stock Market (EGX) Analysis Platform**

A comprehensive Streamlit-based application for analyzing the Egyptian Exchange (EGX) with real-time data, technical analysis, AI predictions, backtesting, and intelligent alerts.

## 🚀 Features

- **Real-time Market Data**: 150+ EGX listed stocks with live quotes
- **Technical Analysis**: 20+ indicators (RSI, MACD, Bollinger, Ichimoku, etc.)
- **AI Predictions**: Ensemble machine learning models with Monte Carlo simulation
- **Backtesting**: 8 strategy types with walk-forward optimization
- **Smart Alerts**: Multi-condition alerts with severity levels
- **Portfolio Tracking**: Watchlist and position management
- **News & Dividends**: Market news and distribution announcements
- **Sector Analysis**: Performance heatmaps and correlation matrices

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/m02417710-maker/blank-app.git
cd blank-app

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

## 🏗️ Architecture

```
blank-app/
├── app.py                 # Main Streamlit entry point
├── requirements.txt       # Python dependencies
├── .streamlit/
│   └── config.toml        # Streamlit configuration
├── pages/                 # Multi-page Streamlit app
│   ├── 01_Dashboard.py
│   ├── 02_Technical.py
│   ├── 03_AI_Predictions.py
│   ├── 04_Backtest.py
│   ├── 05_Alerts.py
│   ├── 06_News_Dividends.py
│   └── 07_Settings.py
├── core/                  # Backend engines
│   ├── analysis.py        # Technical analysis engine
│   ├── ai_engine.py       # AI/ML prediction engine
│   ├── backtest.py        # Strategy backtesting
│   ├── alerts.py          # Alert engine
│   └── charts.py          # Chart visualization
├── data/                  # Data layer
│   ├── egx_symbols.py     # EGX stock database (150+)
│   ├── market_data.py     # Data fetcher (Yahoo Finance)
│   └── storage.py         # SQLite persistence
├── config/                # Configuration
│   └── settings.py         # App settings & constants
├── utils/                 # Utilities
│   ├── formatters.py      # Data formatting
│   ├── validators.py      # Input validation
│   └── helpers.py         # Helper functions
└── tests/                 # Unit tests
```

## 🎯 EGX Coverage

### Listed Stocks (150+)
- **Banking**: COMI, HRHO, ABUK, EGBE, NSGB, HDBK, FAIT, CBKD
- **Real Estate**: TMGH, PHDC, MNHD, GDWA, HELL, ORAS, MISR
- **Food & Beverage**: EAST, ESRS, DOMT, JUHO, UNIP, OLFI, MPCI, JFEF
- **Construction**: ORWE, SWDY, AMOC, HELW, SKPC
- **Telecom**: EGTS, ETEL
- **Energy**: TAQA, EDBM
- **Healthcare**: PHAR, RMDA, IDHC, CLHO, SPIN, PCI, EKHO
- **Chemicals**: EFIC, KZPC, NIPH, MICH, MFPC
- **Technology**: FWRY, EGTS3, SWVL
- **Tourism**: HELI, TRTO, EGCH, HOTS
- **And more...**

### Market Indices
- EGX 30 (^CASE30)
- EGX 70 (^CASE70)
- EGX 100 (^CASE100)
- EGX 20 (^EGX20)

## 📊 Technical Indicators

| Category | Indicators |
|----------|-----------|
| Trend | EMA (9,21,50,200), SMA (20,50,200), HMA, VWAP, Parabolic SAR |
| Momentum | RSI, MACD, Stochastic, CCI, Williams %R, MFI, ROC, Ultimate Oscillator |
| Volatility | Bollinger Bands, Keltner Channels, ATR, Historical Volatility |
| Volume | OBV, Volume Profile, Chaikin Money Flow, Accumulation/Distribution |
| Trend Strength | ADX, +DI, -DI, Ichimoku Cloud |
| Advanced | Support/Resistance, Fibonacci, Z-Score, Skewness, Kurtosis |

## 🤖 AI Models

- **Ensemble Voting**: 8 rule-based models + statistical signals
- **Monte Carlo**: 1000 simulation paths for price forecasting
- **Scenario Analysis**: Bullish/Base/Bearish scenarios
- **Feature Importance**: RSI, MACD, Trend Strength, Volume, Momentum

## 🔔 Alert Types

- Price Target (Above/Below)
- RSI Oversold/Overbought
- MACD Crossover
- EMA Crossover
- Bollinger Bands Breakout
- Volume Spike
- Trend Change
- Support/Resistance Breakout
- Mean Reversion
- Custom Conditions

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_analysis.py -v
```

## 📝 License

MIT License - See LICENSE file for details.

## 👤 Author

EGX Pro Team

---
**Disclaimer**: This application is for educational and research purposes only. Not financial advice. Always consult a licensed financial advisor before making investment decisions.
