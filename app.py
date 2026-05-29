"""
EGX Pro Terminal v27 - Phoenix Edition
Ultra-Professional Egyptian Stock Market Analysis Platform
Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import logging
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import app_config, egx_config
from data.egx_symbols import get_all_symbols, get_stock_info, get_stocks_by_sector, get_sector_performance, get_blue_chips, get_high_dividend, SECTOR_MAP
from data.market_data import market_engine
from data.storage import local_storage
from core.analysis import analysis_engine
from core.patterns import pattern_engine
from core.ai_engine import ai_engine
from core.alerts import alert_engine, AlertSeverity, AlertType
from core.backtest import backtest_engine
from core.charts import chart_engine
from utils.helpers import (format_number, format_currency, format_percentage, format_volume,
                           get_signal_color, get_trend_color, get_severity_color, get_severity_emoji,
                           render_metric_card, render_signal_badge, render_progress_bar,
                           render_alert_card, render_separator, time_ago)
from utils.validators import validator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format=app_config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(os.path.join(app_config.LOG_DIR, app_config.LOG_FILE)),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title=f"{app_config.APP_NAME} v{app_config.APP_VERSION}",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════
# CUSTOM CSS - PROFESSIONAL DARK THEME
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
    }

    /* Sidebar */
    .css-1d391kg, .css-1lcbmhc {
        background: linear-gradient(180deg, #0f0f23 0%, #1a1a3e 100%);
    }

    /* Metric Cards */
    .metric-card {
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(0,212,255,0.15);
        border-color: rgba(0,212,255,0.3);
    }

    /* Signal Badges */
    .signal-badge {
        display: inline-block;
        padding: 8px 20px;
        border-radius: 25px;
        font-weight: bold;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,212,255,0.4);
    }

    /* Tables */
    .stDataFrame {
        background: rgba(255,255,255,0.03);
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.1);
    }

    /* Headers */
    h1, h2, h3 {
        color: #00d4ff !important;
        text-shadow: 0 0 20px rgba(0,212,255,0.3);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #888;
        border-radius: 8px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
        color: white !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0a0a0a;
    }
    ::-webkit-scrollbar-thumb {
        background: #00d4ff;
        border-radius: 4px;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.05);
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# SESSION STATE INITIALIZATION
# ═══════════════════════════════════════════════════════════════
def init_session_state():
    defaults = {
        'page': 'Dashboard',
        'selected_symbol': 'COMI',
        'analysis_period': '1y',
        'analysis_interval': '1d',
        'watchlist': [],
        'alerts': [],
        'comparison_symbols': ['COMI', 'TMGH', 'EAST', 'ORAS'],
        'refresh_interval': 60,
        'last_refresh': datetime.now(),
        'theme': 'dark'
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ═══════════════════════════════════════════════════════════════
# SIDEBAR NAVIGATION
# ═══════════════════════════════════════════════════════════════
def render_sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="color: #00d4ff; font-size: 28px; margin: 0;">
                📈 EGX Pro
            </h1>
            <p style="color: #888; font-size: 12px; margin: 5px 0;">
                v{app_config.APP_VERSION} {app_config.APP_CODENAME}
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Navigation
        pages = {
            'Dashboard': '📊',
            'Analysis': '🔍',
            'Charts': '📈',
            'Alerts': '🔔',
            'AI': '🤖',
            'Watchlist': '📋',
            'Backtest': '🧪',
            'Market': '🏢',
            'Settings': '⚙️'
        }

        for page, icon in pages.items():
            if st.button(f"{icon} {page}", use_container_width=True,
                        type="primary" if st.session_state.page == page else "secondary"):
                st.session_state.page = page
                st.rerun()

        st.markdown("---")

        # Quick Symbol Selector
        st.markdown("### ⚡ Quick Select")
        quick_symbol = st.selectbox(
            "Symbol",
            get_all_symbols()[:50],
            index=get_all_symbols()[:50].index(st.session_state.selected_symbol)
            if st.session_state.selected_symbol in get_all_symbols()[:50] else 0
        )
        if quick_symbol != st.session_state.selected_symbol:
            st.session_state.selected_symbol = quick_symbol

        # Market Status
        st.markdown("---")
        st.markdown("### 📡 Market Status")
        now = datetime.now()
        st.markdown(f"""
        <div style="background: rgba(0,255,136,0.1); border-radius: 8px; padding: 10px;">
            <span style="color: #00ff88;">●</span> 
            <span style="color: #ccc;">{now.strftime('%Y-%m-%d %H:%M')}</span>
        </div>
        """, unsafe_allow_html=True)

        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; font-size: 11px;">
            <p>EGX Pro Terminal</p>
            <p>Educational purposes only</p>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# DASHBOARD PAGE
# ═══════════════════════════════════════════════════════════════
def render_dashboard():
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="color: #00d4ff; font-size: 36px;">📊 Dashboard</h1>
        <p style="color: #888;">Real-time EGX Market Overview</p>
    </div>
    """, unsafe_allow_html=True)

    # Market Overview Cards
    try:
        quotes = market_engine.get_market_overview(egx_config.TOP_STOCKS[:20])
        if not quotes.empty:
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                st.markdown(render_metric_card(
                    "Market Sentiment",
                    "Bullish" if quotes['change_pct'].mean() > 0 else "Bearish",
                    f"{quotes['change_pct'].mean():+.2f}%",
                    "#4caf50" if quotes['change_pct'].mean() > 0 else "#f44336"
                ), unsafe_allow_html=True)

            with col2:
                gainers = (quotes['change_pct'] > 0).sum()
                st.markdown(render_metric_card(
                    "Gainers", str(gainers),
                    f"{(gainers/len(quotes)*100):.0f}%",
                    "#4caf50"
                ), unsafe_allow_html=True)

            with col3:
                losers = (quotes['change_pct'] < 0).sum()
                st.markdown(render_metric_card(
                    "Losers", str(losers),
                    f"{(losers/len(quotes)*100):.0f}%",
                    "#f44336"
                ), unsafe_allow_html=True)

            with col4:
                avg_vol = quotes['volume'].mean()
                st.markdown(render_metric_card(
                    "Avg Volume", format_volume(avg_vol),
                    "", "#00d4ff"
                ), unsafe_allow_html=True)

            with col5:
                top_gainer = quotes.loc[quotes['change_pct'].idxmax()]
                st.markdown(render_metric_card(
                    "Top Gainer", top_gainer['symbol'],
                    f"{top_gainer['change_pct']:+.2f}%",
                    "#4caf50"
                ), unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Market data loading: {e}")

    st.markdown(render_separator(), unsafe_allow_html=True)

    # Featured Analysis
    st.markdown("### 🎯 Featured Analysis")
    featured = get_blue_chips()[:4]
    cols = st.columns(4)

    for idx, symbol in enumerate(featured):
        with cols[idx]:
            try:
                df = market_engine.fetch(symbol, period='1y', interval='1d')
                if df is not None and not df.empty:
                    df = analysis_engine.compute_all(df)
                    summary = analysis_engine.get_summary(df)

                    signal = summary.get('final_signal', 'NEUTRAL')
                    color = get_signal_color(signal)

                    st.markdown(f"""
                    <div class="metric-card" style="text-align: center;">
                        <div style="color: #00d4ff; font-size: 20px; font-weight: bold;">{symbol}</div>
                        <div style="color: #ccc; font-size: 14px;">{summary.get('price', 0):.2f} EGP</div>
                        <div style="color: {'#4caf50' if summary.get('change_pct', 0) >= 0 else '#f44336'}; font-size: 12px;">
                            {summary.get('change_pct', 0):+.2f}%
                        </div>
                        <div style="margin-top: 10px;">
                            <span style="background: {color}; color: white; padding: 4px 12px; 
                                         border-radius: 12px; font-size: 11px; font-weight: bold;">
                                {signal}
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error loading {symbol}")

    # AI Market Sentiment
    st.markdown(render_separator(), unsafe_allow_html=True)
    st.markdown("### 🤖 AI Market Sentiment")

    try:
        predictions = {}
        for sym in egx_config.TOP_STOCKS[:15]:
            df = market_engine.fetch(sym, period='3mo', interval='1d')
            if df is not None and not df.empty:
                df = analysis_engine.compute_all(df)
                pred = ai_engine.predict(df, sym)
                if pred:
                    predictions[sym] = pred

        if predictions:
            sentiment = ai_engine.get_market_sentiment(predictions)

            col1, col2, col3 = st.columns(3)
            with col1:
                sentiment_color = {"BULLISH": "#4caf50", "BEARISH": "#f44336", "NEUTRAL": "#ff9800"}
                st.markdown(f"""
                <div class="metric-card" style="text-align: center;">
                    <div style="color: #888; font-size: 12px;">Market Sentiment</div>
                    <div style="color: {sentiment_color.get(sentiment['sentiment'], '#888')}; 
                                font-size: 28px; font-weight: bold;">
                        {sentiment['sentiment']}
                    </div>
                    <div style="color: #888; font-size: 12px;">Score: {sentiment['score']}/100</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="metric-card" style="text-align: center;">
                    <div style="color: #888; font-size: 12px;">Bullish Stocks</div>
                    <div style="color: #4caf50; font-size: 28px; font-weight: bold;">
                        {sentiment['bullish']} ({sentiment['bullish_pct']}%)
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div class="metric-card" style="text-align: center;">
                    <div style="color: #888; font-size: 12px;">Bearish Stocks</div>
                    <div style="color: #f44336; font-size: 28px; font-weight: bold;">
                        {sentiment['bearish']} ({sentiment['bearish_pct']}%)
                    </div>
                </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        st.info("AI analysis loading...")

# ═══════════════════════════════════════════════════════════════
# ANALYSIS PAGE
# ═══════════════════════════════════════════════════════════════
def render_analysis():
    st.markdown("## 🔍 Technical Analysis")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        symbol = st.selectbox("Select Symbol", get_all_symbols(),
                             index=get_all_symbols().index(st.session_state.selected_symbol))
        st.session_state.selected_symbol = symbol
    with col2:
        period = st.selectbox("Period", ['1mo', '3mo', '6mo', '1y', '2y', '5y'],
                             index=3)
    with col3:
        interval = st.selectbox("Interval", ['1d', '1wk', '1mo'],
                               index=0)

    # Fetch and analyze data
    with st.spinner("Analyzing..."):
        df = market_engine.fetch(symbol, period=period, interval=interval)
        if df is None or df.empty:
            st.error("Failed to load data. Please try another symbol.")
            return

        df = analysis_engine.compute_all(df)
        summary = analysis_engine.get_summary(df)

    # Price Header
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.05); border-radius: 15px; padding: 20px; margin: 20px 0;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="color: #00d4ff; font-size: 32px; font-weight: bold;">{symbol}</span>
                <span style="color: #888; font-size: 16px; margin-left: 10px;">
                    {get_stock_info(symbol).name if get_stock_info(symbol) else ''}
                </span>
            </div>
            <div style="text-align: right;">
                <div style="color: white; font-size: 36px; font-weight: bold;">
                    {summary.get('price', 0):.2f} EGP
                </div>
                <div style="color: {'#4caf50' if summary.get('change_pct', 0) >= 0 else '#f44336'}; font-size: 18px;">
                    {summary.get('change', 0):+.2f} ({summary.get('change_pct', 0):+.2f}%)
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Signal Badge
    signal = summary.get('final_signal', 'NEUTRAL')
    strength = summary.get('signal_strength', 0)
    st.markdown(f"""
    <div style="text-align: center; margin: 20px 0;">
        {render_signal_badge(signal, strength)}
    </div>
    """, unsafe_allow_html=True)

    # Key Metrics Grid
    st.markdown("### 📊 Key Metrics")
    metrics = [
        ("RSI (14)", f"{summary.get('rsi', 0):.1f}", 
         "Oversold" if summary.get('rsi', 50) < 30 else "Overbought" if summary.get('rsi', 50) > 70 else "Neutral",
         "#ff4444" if summary.get('rsi', 50) > 70 else "#00ff88" if summary.get('rsi', 50) < 30 else "#ff9800"),
        ("MACD", f"{summary.get('macd', 0):.4f}", 
         summary.get('signals', {}).get('macd', 'Neutral'), "#00d4ff"),
        ("ADX", f"{summary.get('adx', 0):.1f}", 
         "Strong Trend" if summary.get('adx', 0) > 25 else "Weak Trend", "#ffaa00"),
        ("ATR %", f"{summary.get('atr_pct', 0):.2f}%", 
         summary.get('volatility_regime', 'Normal'), "#ff69b4"),
        ("Volume", format_volume(summary.get('volume', 0)), 
         "Above Avg" if summary.get('volume', 0) > 1.5 else "Normal", "#00ff88"),
        ("Trend", summary.get('trend', 'Neutral'), 
         f"Strength: {summary.get('trend_strength', 0)}", get_trend_color(summary.get('trend', 'Neutral'))),
    ]

    cols = st.columns(3)
    for i, (label, value, sublabel, color) in enumerate(metrics):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="metric-card" style="margin: 5px 0;">
                <div style="color: #888; font-size: 11px;">{label}</div>
                <div style="color: {color}; font-size: 22px; font-weight: bold;">{value}</div>
                <div style="color: #666; font-size: 10px;">{sublabel}</div>
            </div>
            """, unsafe_allow_html=True)

    # Moving Averages
    st.markdown("### 📈 Moving Averages")
    ma_data = {
        'EMA 9': summary.get('ema_9', 0),
        'EMA 21': summary.get('ema_21', 0),
        'EMA 50': summary.get('ema_50', 0),
        'EMA 200': summary.get('ema_200', 0),
        'SMA 20': summary.get('sma_20', 0),
        'SMA 50': summary.get('sma_50', 0),
        'SMA 200': summary.get('sma_200', 0),
    }

    current_price = summary.get('price', 0)
    ma_df = pd.DataFrame([
        {'Indicator': k, 'Value': v, 'Distance': f"{((current_price - v) / v * 100):+.2f}%",
         'Status': 'Above' if current_price > v else 'Below'}
        for k, v in ma_data.items() if v > 0
    ])
    st.dataframe(ma_df, use_container_width=True, hide_index=True)

    # Support & Resistance
    st.markdown("### 🎯 Support & Resistance")
    sr = summary.get('support_resistance', {})
    if sr:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid #00ff88;">
                <div style="color: #888; font-size: 12px;">Nearest Support</div>
                <div style="color: #00ff88; font-size: 24px; font-weight: bold;">
                    {sr.get('nearest_support', 0):.2f}
                </div>
                <div style="color: #666; font-size: 11px;">
                    {sr.get('support_distance_pct', 0):.2f}% below current
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid #ffaa00;">
                <div style="color: #888; font-size: 12px;">Pivot Point</div>
                <div style="color: #ffaa00; font-size: 24px; font-weight: bold;">
                    {sr.get('pivot_point', 0):.2f}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid #ff4444;">
                <div style="color: #888; font-size: 12px;">Nearest Resistance</div>
                <div style="color: #ff4444; font-size: 24px; font-weight: bold;">
                    {sr.get('nearest_resistance', 0):.2f}
                </div>
                <div style="color: #666; font-size: 11px;">
                    {sr.get('resistance_distance_pct', 0):.2f}% above current
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Fibonacci Levels
    st.markdown("### 📐 Fibonacci Retracement")
    fib = summary.get('fibonacci', {})
    if fib:
        fib_cols = st.columns(7)
        levels = ['0.0', '0.236', '0.382', '0.5', '0.618', '0.786', '1.0']
        colors = ['#ff4444', '#ff6600', '#ffaa00', '#ffcc00', '#00ff88', '#00ccff', '#00ff00']
        for i, (level, color) in enumerate(zip(levels, colors)):
            with fib_cols[i]:
                val = fib.get(level, 0)
                st.markdown(f"""
                <div style="text-align: center; background: rgba(255,255,255,0.05); 
                            border-radius: 8px; padding: 10px;">
                    <div style="color: {color}; font-size: 10px;">{level}</div>
                    <div style="color: white; font-size: 14px; font-weight: bold;">{val:.2f}</div>
                </div>
                """, unsafe_allow_html=True)

    # Pattern Recognition
    st.markdown("### 🔍 Pattern Recognition")
    try:
        pattern_summary = pattern_engine.get_pattern_summary(df)
        if pattern_summary.get('total', 0) > 0:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="color: #888; font-size: 12px;">Latest Pattern</div>
                    <div style="color: #00d4ff; font-size: 18px; font-weight: bold;">
                        {pattern_summary['latest']['name']}
                    </div>
                    <div style="color: #888; font-size: 11px;">
                        Confidence: {pattern_summary['latest']['confidence']:.0%} | 
                        {'Bullish' if pattern_summary['latest']['bullish'] else 'Bearish' if pattern_summary['latest']['bullish'] is False else 'Neutral'}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="color: #888; font-size: 12px;">Pattern Bias</div>
                    <div style="color: {'#4caf50' if pattern_summary['dominant_bias'] == 'Bullish' else '#f44336' if pattern_summary['dominant_bias'] == 'Bearish' else '#ff9800'}; 
                                font-size: 18px; font-weight: bold;">
                        {pattern_summary['dominant_bias']}
                    </div>
                    <div style="color: #888; font-size: 11px;">
                        {pattern_summary['bullish_count']} Bullish | 
                        {pattern_summary['bearish_count']} Bearish
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No significant patterns detected in the current period.")
    except Exception as e:
        st.warning(f"Pattern analysis: {e}")

    # Signal Breakdown
    st.markdown("### 📋 Signal Breakdown")
    signals = summary.get('signals', {})
    signal_data = []
    for sig_name, sig_value in signals.items():
        signal_data.append({'Indicator': sig_name.replace('_', ' ').title(), 'Signal': sig_value})

    if signal_data:
        sig_df = pd.DataFrame(signal_data)
        st.dataframe(sig_df, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════
# CHARTS PAGE
# ═══════════════════════════════════════════════════════════════
def render_charts():
    st.markdown("## 📈 Advanced Charts")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        symbol = st.selectbox("Symbol", get_all_symbols(),
                             index=get_all_symbols().index(st.session_state.selected_symbol),
                             key="chart_symbol")
    with col2:
        period = st.selectbox("Period", ['1mo', '3mo', '6mo', '1y', '2y', '5y'],
                             index=3, key="chart_period")
    with col3:
        interval = st.selectbox("Interval", ['1d', '1wk', '1mo'],
                               index=0, key="chart_interval")

    # Indicator selection
    st.markdown("### 📊 Indicators")
    indicator_options = {
        'EMA 9': 'ema_9', 'EMA 21': 'ema_21', 'EMA 50': 'ema_50', 'EMA 200': 'ema_200',
        'SMA 20': 'sma_20', 'SMA 50': 'sma_50', 'Bollinger Bands': 'bb',
        'VWAP': 'vwap', 'Parabolic SAR': 'psar'
    }
    selected_indicators = st.multiselect("Overlay Indicators", list(indicator_options.keys()),
                                        default=['EMA 9', 'EMA 21', 'EMA 50'],
                                        key="chart_indicators")

    indicator_cols = [indicator_options[k] for k in selected_indicators if k in indicator_options]

    # Fetch data
    with st.spinner("Loading charts..."):
        df = market_engine.fetch(symbol, period=period, interval=interval)
        if df is not None and not df.empty:
            df = analysis_engine.compute_all(df)

            # Main Chart
            fig = chart_engine.create_main_chart(df, symbol, indicators=indicator_cols)
            st.plotly_chart(fig, use_container_width=True, key="main_chart")

            # Sub-charts
            st.markdown("### 📉 Sub-Charts")
            tabs = st.tabs(["RSI", "MACD", "ADX", "Stochastic", "Ichimoku", "Volume"])

            with tabs[0]:
                if 'rsi' in df.columns:
                    fig_rsi = chart_engine.create_rsi_chart(df)
                    st.plotly_chart(fig_rsi, use_container_width=True, key="rsi_chart")

            with tabs[1]:
                if 'macd' in df.columns:
                    fig_macd = chart_engine.create_macd_chart(df)
                    st.plotly_chart(fig_macd, use_container_width=True, key="macd_chart")

            with tabs[2]:
                if 'adx' in df.columns:
                    fig_adx = chart_engine.create_adx_chart(df)
                    st.plotly_chart(fig_adx, use_container_width=True, key="adx_chart")

            with tabs[3]:
                if 'stochastic_k' in df.columns:
                    fig_stoch = chart_engine.create_stochastic_chart(df)
                    st.plotly_chart(fig_stoch, use_container_width=True, key="stoch_chart")

            with tabs[4]:
                if 'tenkan_sen' in df.columns:
                    fig_ichi = chart_engine.create_ichimoku_chart(df, symbol)
                    st.plotly_chart(fig_ichi, use_container_width=True, key="ichi_chart")

            with tabs[5]:
                if 'volume' in df.columns:
                    fig_vol = go.Figure()
                    colors = ['#00ff88' if df['close'].iloc[i] >= df['open'].iloc[i] 
                              else '#ff4444' for i in range(len(df))]
                    x_vals = df['date'] if 'date' in df.columns else df.index
                    fig_vol.add_trace(go.Bar(x=x_vals, y=df['volume'], marker_color=colors, opacity=0.6))
                    if 'volume_sma' in df.columns:
                        fig_vol.add_trace(go.Scatter(x=x_vals, y=df['volume_sma'], 
                                                     mode='lines', name='SMA 20',
                                                     line=dict(color='#ffaa00', width=2)))
                    fig_vol.update_layout(title="Volume Analysis", template='plotly_dark', height=400)
                    st.plotly_chart(fig_vol, use_container_width=True, key="volume_chart")
        else:
            st.error("No data available for this symbol.")

# ═══════════════════════════════════════════════════════════════
# ALERTS PAGE
# ═══════════════════════════════════════════════════════════════
def render_alerts():
    st.markdown("## 🔔 Alert Center")

    # Create Alert
    with st.expander("➕ Create New Alert", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            alert_symbol = st.selectbox("Symbol", get_all_symbols(), key="alert_symbol")
        with col2:
            alert_type = st.selectbox("Alert Type", [
                "Price Target", "RSI Level", "MACD Cross", "EMA Cross",
                "BB Breakout", "Volume Spike", "Trend Change", "Breakout", "Mean Reversion"
            ], key="alert_type")
        with col3:
            alert_severity = st.selectbox("Severity", ["Info", "Warning", "Critical"], key="alert_severity")

        if alert_type == "Price Target":
            col1, col2 = st.columns(2)
            with col1:
                target_price = st.number_input("Target Price", min_value=0.01, value=20.0, step=0.1)
            with col2:
                direction = st.selectbox("Direction", ["Above", "Below"])
            if st.button("Add Price Alert", use_container_width=True):
                alert_engine.add_price_alert(alert_symbol, target_price, direction.lower(), 
                                            AlertSeverity[alert_severity.upper()])
                st.success(f"Price alert added for {alert_symbol}")

        elif alert_type == "RSI Level":
            col1, col2 = st.columns(2)
            with col1:
                rsi_threshold = st.slider("RSI Threshold", 0, 100, 30)
            with col2:
                rsi_direction = st.selectbox("Condition", ["Below (Oversold)", "Above (Overbought)"])
            if st.button("Add RSI Alert", use_container_width=True):
                alert_engine.add_rsi_alert(alert_symbol, rsi_threshold, 
                                          'below' if 'Below' in rsi_direction else 'above')
                st.success(f"RSI alert added for {alert_symbol}")

        elif alert_type == "MACD Cross":
            cross_type = st.selectbox("Cross Type", ["Bullish", "Bearish"])
            if st.button("Add MACD Alert", use_container_width=True):
                alert_engine.add_macd_alert(alert_symbol, cross_type.lower())
                st.success(f"MACD alert added for {alert_symbol}")

        elif alert_type == "EMA Cross":
            col1, col2, col3 = st.columns(3)
            with col1:
                fast_ema = st.selectbox("Fast EMA", [5, 9, 12, 20], index=1)
            with col2:
                slow_ema = st.selectbox("Slow EMA", [21, 26, 50, 200], index=0)
            with col3:
                ema_cross = st.selectbox("Cross", ["Bullish", "Bearish"])
            if st.button("Add EMA Alert", use_container_width=True):
                alert_engine.add_ema_alert(alert_symbol, fast_ema, slow_ema, ema_cross.lower())
                st.success(f"EMA alert added for {alert_symbol}")

        elif alert_type == "Volume Spike":
            multiplier = st.slider("Volume Multiplier", 1.5, 5.0, 2.0, 0.5)
            if st.button("Add Volume Alert", use_container_width=True):
                alert_engine.add_volume_alert(alert_symbol, multiplier)
                st.success(f"Volume alert added for {alert_symbol}")

    # Active Alerts
    st.markdown("### 📋 Active Alerts")
    try:
        conditions = alert_engine.get_conditions()
        if conditions:
            alert_data = []
            for cond in conditions:
                alert_data.append({
                    'Name': cond.name,
                    'Symbol': cond.symbol,
                    'Type': cond.alert_type.value,
                    'Severity': cond.severity.value,
                    'Status': 'Active' if cond.enabled else 'Disabled',
                    'Triggers': cond.trigger_count
                })
            st.dataframe(pd.DataFrame(alert_data), use_container_width=True, hide_index=True)
        else:
            st.info("No active alerts. Create one above.")
    except Exception as e:
        st.info("Alert system loading...")

    # Alert History
    st.markdown("### 🕐 Alert History")
    try:
        history = local_storage.get_alerts(limit=20)
        if not history.empty:
            for _, alert in history.iterrows():
                st.markdown(render_alert_card({
                    'symbol': alert['symbol'],
                    'severity': alert['severity'],
                    'message': alert['message'],
                    'timestamp': alert['triggered_at']
                }), unsafe_allow_html=True)
        else:
            st.info("No alert history yet.")
    except Exception as e:
        st.info("History loading...")

# ═══════════════════════════════════════════════════════════════
# AI PREDICTIONS PAGE
# ═══════════════════════════════════════════════════════════════
def render_ai():
    st.markdown("## 🤖 AI Predictions")

    symbol = st.selectbox("Select Symbol", get_all_symbols(),
                         index=get_all_symbols().index(st.session_state.selected_symbol),
                         key="ai_symbol")

    with st.spinner("Running AI analysis..."):
        df = market_engine.fetch(symbol, period='1y', interval='1d')
        if df is None or df.empty:
            st.error("No data available.")
            return

        df = analysis_engine.compute_all(df)
        prediction = ai_engine.predict(df, symbol)

    if prediction:
        # Main Prediction Card
        st.markdown("### 🔮 Prediction Result")

        pred_color = get_signal_color(prediction.predicted_direction)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <div style="color: #888; font-size: 12px;">Direction</div>
                <div style="color: {pred_color}; font-size: 28px; font-weight: bold;">
                    {prediction.predicted_direction}
                </div>
                <div style="color: #888; font-size: 12px;">Confidence: {prediction.confidence:.0%}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <div style="color: #888; font-size: 12px;">Target ({prediction.horizon_days} days)</div>
                <div style="color: #4caf50; font-size: 28px; font-weight: bold;">
                    {prediction.target_price:.2f}
                </div>
                <div style="color: #888; font-size: 12px;">EGP</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <div style="color: #888; font-size: 12px;">Stop Loss</div>
                <div style="color: #f44336; font-size: 28px; font-weight: bold;">
                    {prediction.stop_loss:.2f}
                </div>
                <div style="color: #888; font-size: 12px;">EGP</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <div style="color: #888; font-size: 12px;">Expected Return</div>
                <div style="color: {'#4caf50' if prediction.expected_return > 0 else '#f44336'}; 
                            font-size: 28px; font-weight: bold;">
                    {prediction.expected_return:+.2f}%
                </div>
                <div style="color: #888; font-size: 12px;">R/R: 1:{prediction.risk_reward_ratio:.1f}</div>
            </div>
            """, unsafe_allow_html=True)

        # Probability Distribution
        st.markdown("### 📊 Probability Distribution")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card" style="text-align: center; border-left: 4px solid #4caf50;">
                <div style="color: #4caf50; font-size: 14px;">🟢 Up</div>
                <div style="color: #4caf50; font-size: 32px; font-weight: bold;">
                    {prediction.probability_up:.1%}
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card" style="text-align: center; border-left: 4px solid #ff9800;">
                <div style="color: #ff9800; font-size: 14px;">🟡 Sideways</div>
                <div style="color: #ff9800; font-size: 32px; font-weight: bold;">
                    {prediction.probability_sideways:.1%}
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card" style="text-align: center; border-left: 4px solid #f44336;">
                <div style="color: #f44336; font-size: 14px;">🔴 Down</div>
                <div style="color: #f44336; font-size: 32px; font-weight: bold;">
                    {prediction.probability_down:.1%}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Monte Carlo Simulation
        if prediction.monte_carlo_results:
            st.markdown("### 🎲 Monte Carlo Simulation (1000 Paths)")
            mc = prediction.monte_carlo_results

            col1, col2, col3, col4, col5 = st.columns(5)
            mc_data = [
                ("P5 (Worst)", mc['percentile_5'], "#f44336"),
                ("P25", mc['percentile_25'], "#ff9800"),
                ("Median", mc['median_price'], "#00d4ff"),
                ("P75", mc['percentile_75'], "#4caf50"),
                ("P95 (Best)", mc['percentile_95'], "#00ff88")
            ]
            for (label, value, color), col in zip(mc_data, [col1, col2, col3, col4, col5]):
                with col:
                    st.markdown(f"""
                    <div class="metric-card" style="text-align: center;">
                        <div style="color: {color}; font-size: 12px;">{label}</div>
                        <div style="color: {color}; font-size: 20px; font-weight: bold;">{value:.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # Monte Carlo Chart
            fig_mc = go.Figure()
            percentiles = ['P5', 'P25', 'Median', 'P75', 'P95']
            prices = [mc['percentile_5'], mc['percentile_25'], mc['median_price'],
                     mc['percentile_75'], mc['percentile_95']]
            colors = ['#f44336', '#ff9800', '#00d4ff', '#4caf50', '#00ff88']

            fig_mc.add_trace(go.Bar(x=percentiles, y=prices, marker_color=colors,
                                   text=[f"{p:.2f}" for p in prices], textposition='outside'))
            fig_mc.add_hline(y=prediction.current_price, line_dash="dash", line_color="white",
                            annotation_text=f"Current: {prediction.current_price:.2f}")
            fig_mc.update_layout(title="Monte Carlo Price Distribution", template='plotly_dark',
                                height=400, showlegend=False)
            st.plotly_chart(fig_mc, use_container_width=True, key="mc_chart")

        # Scenario Analysis
        if prediction.scenario_analysis:
            st.markdown("### 📋 Scenario Analysis")
            for scenario_name, scenario in prediction.scenario_analysis.items():
                with st.expander(f"{scenario_name.title()}: {scenario['description']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Target Price", f"{scenario['target']:.2f} EGP")
                    with col2:
                        st.metric("Probability", f"{scenario['probability']:.0%}")
                    st.write(f"**Rationale:** {scenario['rationale']}")

        # Feature Importance
        st.markdown("### 🧠 Feature Importance")
        features = prediction.features_importance
        feat_df = pd.DataFrame([
            {'Feature': k.replace('_', ' ').title(), 'Weight': v, 'Percentage': f"{v*100:.0f}%"}
            for k, v in features.items()
        ])

        fig_feat = go.Figure(go.Bar(
            x=list(features.values()),
            y=[k.replace('_', ' ').title() for k in features.keys()],
            orientation='h',
            marker_color='#00d4ff',
            text=[f"{v*100:.0f}%" for v in features.values()],
            textposition='outside'
        ))
        fig_feat.update_layout(template='plotly_dark', height=300, showlegend=False,
                              xaxis_title='Importance', yaxis_title='Feature')
        st.plotly_chart(fig_feat, use_container_width=True, key="feature_chart")

        # Save prediction
        if st.button("💾 Save Prediction", use_container_width=True):
            local_storage.save_prediction(symbol, {
                'direction': prediction.predicted_direction,
                'confidence': prediction.confidence,
                'target_price': prediction.target_price,
                'stop_loss': prediction.stop_loss,
                'horizon_days': prediction.horizon_days,
                'features': prediction.features_importance
            })
            st.success("Prediction saved!")
    else:
        st.warning("AI prediction unavailable. Try another symbol or period.")

# ═══════════════════════════════════════════════════════════════
# WATCHLIST PAGE
# ═══════════════════════════════════════════════════════════════
def render_watchlist():
    st.markdown("## 📋 My Watchlist")

    # Add to watchlist
    with st.expander("➕ Add Stock", expanded=True):
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        with col1:
            new_symbol = st.selectbox("Symbol", get_all_symbols(), key="wl_symbol")
        with col2:
            target = st.number_input("Target", min_value=0.0, value=0.0, step=0.1, key="wl_target")
        with col3:
            stop = st.number_input("Stop Loss", min_value=0.0, value=0.0, step=0.1, key="wl_stop")
        with col4:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Add", use_container_width=True):
                local_storage.add_to_watchlist(
                    new_symbol,
                    target_price=target if target > 0 else None,
                    stop_loss=stop if stop > 0 else None
                )
                st.success(f"Added {new_symbol} to watchlist!")
                st.rerun()

    # Watchlist Table
    st.markdown("### 📊 Watchlist")
    try:
        watchlist = local_storage.get_watchlist()
        if not watchlist.empty:
            enriched = []
            for _, row in watchlist.iterrows():
                sym = row['symbol']
                quote = market_engine.get_realtime_quote(sym)
                if quote:
                    enriched.append({
                        'Symbol': sym,
                        'Price': f"{quote['price']:.2f}",
                        'Change': f"{quote['change_pct']:+.2f}%",
                        'Volume': format_volume(quote['volume']),
                        'Target': f"{row['target_price']:.2f}" if pd.notna(row['target_price']) else 'N/A',
                        'Stop Loss': f"{row['stop_loss']:.2f}" if pd.notna(row['stop_loss']) else 'N/A',
                        'Added': str(row['added_at'])[:10] if pd.notna(row['added_at']) else 'N/A'
                    })

            if enriched:
                st.dataframe(pd.DataFrame(enriched), use_container_width=True, hide_index=True)

                # Quick Analysis for each
                st.markdown("### 📈 Quick Analysis")
                for item in enriched[:5]:
                    sym = item['Symbol']
                    try:
                        df = market_engine.fetch(sym, period='3mo', interval='1d')
                        if df is not None and not df.empty:
                            df = analysis_engine.compute_all(df)
                            summary = analysis_engine.get_summary(df)
                            signal = summary.get('final_signal', 'NEUTRAL')
                            color = get_signal_color(signal)

                            col1, col2, col3 = st.columns([1, 2, 1])
                            with col1:
                                st.markdown(f"<span style='color: #00d4ff; font-size: 18px; font-weight: bold;'>{sym}</span>", 
                                          unsafe_allow_html=True)
                            with col2:
                                st.markdown(f"""
                                <span style='background: {color}; color: white; padding: 4px 12px; 
                                            border-radius: 12px; font-size: 12px; font-weight: bold;'>
                                    {signal}
                                </span>
                                <span style='color: #888; font-size: 12px; margin-left: 10px;'>
                                    RSI: {summary.get('rsi', 0):.1f} | MACD: {summary.get('macd', 0):.4f}
                                </span>
                                """, unsafe_allow_html=True)
                            with col3:
                                if st.button("Remove", key=f"remove_{sym}"):
                                    local_storage.remove_from_watchlist(sym)
                                    st.rerun()
                    except Exception as e:
                        pass
        else:
            st.info("Your watchlist is empty. Add stocks above!")
    except Exception as e:
        st.info("Watchlist loading...")

# ═══════════════════════════════════════════════════════════════
# BACKTEST PAGE
# ═══════════════════════════════════════════════════════════════
def render_backtest():
    st.markdown("## 🧪 Strategy Backtest Lab")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        symbol = st.selectbox("Symbol", get_all_symbols(),
                             index=get_all_symbols().index(st.session_state.selected_symbol),
                             key="bt_symbol")
    with col2:
        period = st.selectbox("Period", ['6mo', '1y', '2y', '5y'],
                             index=1, key="bt_period")
    with col3:
        strategy = st.selectbox("Strategy", [
            "RSI Mean Reversion", "MACD Crossover", "EMA Crossover",
            "Bollinger Bands", "Trend Following", "Mean Reversion",
            "Breakout", "Composite Signal"
        ], key="bt_strategy")

    strategy_map = {
        "RSI Mean Reversion": "rsi", "MACD Crossover": "macd",
        "EMA Crossover": "ema", "Bollinger Bands": "bb",
        "Trend Following": "trend_following", "Mean Reversion": "mean_reversion",
        "Breakout": "breakout", "Composite Signal": "composite"
    }

    # Strategy Parameters
    with st.expander("⚙️ Strategy Parameters"):
        col1, col2, col3 = st.columns(3)
        with col1:
            initial_capital = st.number_input("Initial Capital (EGP)", 
                                             min_value=1000.0, value=100000.0, step=10000.0)
        with col2:
            commission = st.number_input("Commission (%)", 
                                        min_value=0.0, max_value=1.0, value=0.15, step=0.01) / 100
        with col3:
            risk_per_trade = st.slider("Risk per Trade", 0.05, 0.30, 0.10, 0.05)

    if st.button("🚀 Run Backtest", use_container_width=True, type="primary"):
        with st.spinner("Running backtest... This may take a moment."):
            df = market_engine.fetch(symbol, period=period, interval='1d')
            if df is None or df.empty:
                st.error("Failed to load data.")
                return

            df = analysis_engine.compute_all(df)
            result = backtest_engine.run_strategy(
                df, strategy_map[strategy], symbol=symbol,
                initial_capital=initial_capital,
                commission=commission,
                risk_per_trade=risk_per_trade
            )

            if result:
                # Save result
                local_storage.save_backtest(strategy, symbol, {
                    'total_return': result.total_return_pct,
                    'sharpe_ratio': result.sharpe_ratio,
                    'max_drawdown': result.max_drawdown_pct,
                    'win_rate': result.win_rate,
                    'total_trades': result.total_trades,
                    'params': {}
                })

                # Results Dashboard
                st.markdown("### 📊 Backtest Results")

                # Main Metrics
                col1, col2, col3, col4 = st.columns(4)
                metrics = [
                    ("Total Return", f"{result.total_return_pct:+.2f}%", 
                     "#4caf50" if result.total_return_pct > 0 else "#f44336"),
                    ("Sharpe Ratio", f"{result.sharpe_ratio:.3f}",
                     "#4caf50" if result.sharpe_ratio > 1 else "#ff9800"),
                    ("Max Drawdown", f"{result.max_drawdown_pct:.2f}%", "#f44336"),
                    ("Win Rate", f"{result.win_rate:.1f}%",
                     "#4caf50" if result.win_rate > 50 else "#f44336")
                ]
                for (label, value, color), col in zip(metrics, [col1, col2, col3, col4]):
                    with col:
                        st.markdown(f"""
                        <div class="metric-card" style="text-align: center;">
                            <div style="color: #888; font-size: 12px;">{label}</div>
                            <div style="color: {color}; font-size: 28px; font-weight: bold;">{value}</div>
                        </div>
                        """, unsafe_allow_html=True)

                # Secondary Metrics
                col1, col2, col3, col4 = st.columns(4)
                secondary = [
                    ("Sortino", f"{result.sortino_ratio:.3f}"),
                    ("Calmar", f"{result.calmar_ratio:.3f}"),
                    ("Profit Factor", f"{result.profit_factor:.3f}"),
                    ("Total Trades", str(result.total_trades))
                ]
                for (label, value), col in zip(secondary, [col1, col2, col3, col4]):
                    with col:
                        st.markdown(f"""
                        <div class="metric-card" style="text-align: center;">
                            <div style="color: #888; font-size: 12px;">{label}</div>
                            <div style="color: #00d4ff; font-size: 24px; font-weight: bold;">{value}</div>
                        </div>
                        """, unsafe_allow_html=True)

                # Equity Curve
                st.markdown("### 📈 Equity Curve")
                fig_eq = chart_engine.create_equity_curve(result.equity_curve)
                st.plotly_chart(fig_eq, use_container_width=True, key="equity_curve")

                # Drawdown
                st.markdown("### 📉 Drawdown Analysis")
                fig_dd = chart_engine.create_drawdown_chart(result.equity_curve)
                st.plotly_chart(fig_dd, use_container_width=True, key="drawdown_chart")

                # Trade History
                if result.trades:
                    st.markdown("### 📋 Trade History")
                    trade_df = pd.DataFrame([
                        {
                            'Entry': t.entry_date[:10] if t.entry_date else 'N/A',
                            'Exit': t.exit_date[:10] if t.exit_date else 'Open',
                            'Entry Price': f"{t.entry_price:.2f}",
                            'Exit Price': f"{t.exit_price:.2f}" if t.exit_price else 'N/A',
                            'P&L': f"{t.pnl:,.0f}" if t.pnl else 'N/A',
                            'Return %': f"{t.pnl_pct:.2f}%" if t.pnl_pct else 'N/A',
                            'Days': t.holding_days,
                            'Reason': t.exit_reason
                        }
                        for t in result.trades
                    ])
                    st.dataframe(trade_df, use_container_width=True, hide_index=True)
            else:
                st.error("Backtest failed. Check your parameters.")

    # Backtest History
    st.markdown("### 📜 Backtest History")
    try:
        history = local_storage.get_backtests(limit=10)
        if not history.empty:
            st.dataframe(history[['strategy_name', 'symbol', 'total_return', 'win_rate',
                                  'max_drawdown', 'sharpe_ratio', 'total_trades', 'created_at']],
                        use_container_width=True, hide_index=True)
        else:
            st.info("No backtest history yet.")
    except Exception as e:
        st.info("History loading...")

# ═══════════════════════════════════════════════════════════════
# MARKET OVERVIEW PAGE
# ═══════════════════════════════════════════════════════════════
def render_market():
    st.markdown("## 🏢 Market Overview")

    # Market Summary
    try:
        quotes = market_engine.get_market_overview(egx_config.TOP_STOCKS)
        if not quotes.empty:
            st.markdown("### 📊 Market Snapshot")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="metric-card" style="text-align: center;">
                    <div style="color: #888; font-size: 12px;">Total Stocks</div>
                    <div style="color: #00d4ff; font-size: 32px; font-weight: bold;">{len(quotes)}</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                gainers = (quotes['change_pct'] > 0).sum()
                st.markdown(f"""
                <div class="metric-card" style="text-align: center;">
                    <div style="color: #888; font-size: 12px;">Gainers</div>
                    <div style="color: #4caf50; font-size: 32px; font-weight: bold;">{gainers}</div>
                    <div style="color: #888; font-size: 12px;">{(gainers/len(quotes)*100):.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                losers = (quotes['change_pct'] < 0).sum()
                st.markdown(f"""
                <div class="metric-card" style="text-align: center;">
                    <div style="color: #888; font-size: 12px;">Losers</div>
                    <div style="color: #f44336; font-size: 32px; font-weight: bold;">{losers}</div>
                    <div style="color: #888; font-size: 12px;">{(losers/len(quotes)*100):.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                avg_change = quotes['change_pct'].mean()
                st.markdown(f"""
                <div class="metric-card" style="text-align: center;">
                    <div style="color: #888; font-size: 12px;">Avg Change</div>
                    <div style="color: {'#4caf50' if avg_change > 0 else '#f44336'}; 
                                font-size: 32px; font-weight: bold;">
                        {avg_change:+.2f}%
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Top Performers
            st.markdown("### 🏆 Top Performers")
            tabs = st.tabs(["Top Gainers", "Top Losers", "Most Active"])

            with tabs[0]:
                gainers_df = quotes.nlargest(15, 'change_pct')[['symbol', 'price', 'change_pct', 'volume']]
                gainers_df.columns = ['Symbol', 'Price', 'Change %', 'Volume']
                st.dataframe(gainers_df, use_container_width=True, hide_index=True)

            with tabs[1]:
                losers_df = quotes.nsmallest(15, 'change_pct')[['symbol', 'price', 'change_pct', 'volume']]
                losers_df.columns = ['Symbol', 'Price', 'Change %', 'Volume']
                st.dataframe(losers_df, use_container_width=True, hide_index=True)

            with tabs[2]:
                active_df = quotes.nlargest(15, 'volume')[['symbol', 'price', 'change_pct', 'volume']]
                active_df.columns = ['Symbol', 'Price', 'Change %', 'Volume']
                st.dataframe(active_df, use_container_width=True, hide_index=True)

            # Sector Performance
            st.markdown("### 🏭 Sector Performance")
            sector_perf = get_sector_performance(quotes)
            if not sector_perf.empty:
                fig_sector = chart_engine.create_sector_heatmap(
                    dict(zip(sector_perf['sector'], sector_perf['avg_change']))
                )
                st.plotly_chart(fig_sector, use_container_width=True, key="sector_heatmap")
    except Exception as e:
        st.warning(f"Market data loading: {e}")

    # Stock Comparison
    st.markdown("### 📈 Stock Comparison")
    comparison = st.multiselect("Select Stocks", egx_config.TOP_STOCKS,
                               default=st.session_state.comparison_symbols[:4],
                               max_selections=8, key="market_comparison")

    if comparison:
        st.session_state.comparison_symbols = comparison
        comp_data = {}
        for sym in comparison:
            df = market_engine.fetch(sym, period='1y', interval='1d')
            if df is not None and not df.empty:
                comp_data[sym] = df

        if comp_data:
            fig_comp = chart_engine.create_comparison_chart(comp_data, normalize=True)
            st.plotly_chart(fig_comp, use_container_width=True, key="market_comparison_chart")

            # Correlation Matrix
            if len(comp_data) >= 2:
                st.markdown("### 🔗 Correlation Matrix")
                corr_matrix = market_engine.get_correlation_matrix(list(comp_data.keys()), period='1y')
                if not corr_matrix.empty:
                    fig_corr = chart_engine.create_correlation_heatmap(corr_matrix)
                    st.plotly_chart(fig_corr, use_container_width=True, key="corr_heatmap")

# ═══════════════════════════════════════════════════════════════
# SETTINGS PAGE
# ═══════════════════════════════════════════════════════════════
def render_settings():
    st.markdown("## ⚙️ Settings")

    # About
    st.markdown("### ℹ️ About EGX Pro Terminal")
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.05); border-radius: 15px; padding: 20px; margin: 20px 0;">
        <div style="text-align: center;">
            <div style="font-size: 48px; margin-bottom: 10px;">📈</div>
            <div style="font-size: 28px; font-weight: bold; color: #00d4ff;">
                EGX Pro Terminal v{app_config.APP_VERSION}
            </div>
            <div style="color: #888; font-size: 16px; margin: 10px 0;">
                Codename: {app_config.APP_CODENAME}
            </div>
            <div style="color: #666; font-size: 14px;">
                {app_config.APP_DESCRIPTION}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Database Management
    st.markdown("### 🗄️ Database Management")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💾 Backup Database", use_container_width=True):
            with st.spinner("Creating backup..."):
                path = local_storage.backup()
                if path:
                    st.success(f"✅ Backup created: {path}")
                else:
                    st.error("❌ Backup failed")
    with col2:
        if st.button("🧹 Vacuum Database", use_container_width=True):
            with st.spinner("Optimizing..."):
                if local_storage.vacuum():
                    st.success("✅ Database optimized")
                else:
                    st.error("❌ Vacuum failed")
    with col3:
        if st.button("🗑️ Clear Old Data", use_container_width=True):
            with st.spinner("Clearing..."):
                if local_storage.clear_old_data(days=90):
                    st.success("✅ Old data cleared")
                else:
                    st.error("❌ Clear failed")

    # Database Statistics
    st.markdown("### 📊 Database Statistics")
    try:
        stats = local_storage.get_stats()
        if stats:
            col1, col2, col3, col4, col5 = st.columns(5)
            stat_data = [
                ("Watchlist", stats.get('watchlist', 0), "#00d4ff"),
                ("Alerts", stats.get('alerts', 0), "#ff9800"),
                ("Backtests", stats.get('backtest_results', 0), "#4caf50"),
                ("Predictions", stats.get('predictions', 0), "#ff69b4"),
                ("Size (MB)", stats.get('size_mb', 0), "#00ff88")
            ]
            for (label, value, color), col in zip(stat_data, [col1, col2, col3, col4, col5]):
                with col:
                    st.markdown(f"""
                    <div class="metric-card" style="text-align: center;">
                        <div style="color: #888; font-size: 12px;">{label}</div>
                        <div style="color: {color}; font-size: 28px; font-weight: bold;">{value}</div>
                    </div>
                    """, unsafe_allow_html=True)
    except Exception as e:
        st.info("Statistics loading...")

    # Features List
    st.markdown("### ✨ Features")
    features = [
        ("📊 Technical Analysis", "20+ indicators including RSI, MACD, Bollinger Bands, Ichimoku Cloud, ADX, Stochastic, and more"),
        ("🔍 Pattern Recognition", "20+ candlestick patterns with confidence scoring"),
        ("🤖 AI Predictions", "8-model ensemble with Monte Carlo simulation and scenario analysis"),
        ("🔔 Smart Alerts", "11 alert types with severity levels and cooldown system"),
        ("🧪 Backtest Lab", "8 strategies with walk-forward analysis and parameter optimization"),
        ("📈 Advanced Charts", "10+ chart types with professional Plotly visualization"),
        ("🏢 Market Overview", "Real-time sector performance and correlation analysis"),
        ("📋 Watchlist", "Portfolio tracking with targets and stop losses"),
    ]

    for icon_feature, description in features:
        with st.expander(icon_feature):
            st.write(description)

    # Disclaimer
    st.markdown("---")
    st.markdown("### ⚠️ Disclaimer")
    st.warning("""
    **This platform is for educational purposes only.**

    It does NOT constitute investment advice. Always consult a licensed financial 
    advisor before making investment decisions. Past performance does not guarantee 
    future results. Trading involves substantial risk of loss.

    **Data Sources:** Yahoo Finance (delayed, for educational use)
    **Market:** Egyptian Exchange (EGX)
    **Currency:** Egyptian Pound (EGP)
    """)

    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #666; font-size: 12px; padding: 20px 0;">
        <p>🇪🇬 Made in Egypt | EGX Pro Terminal v{app_config.APP_VERSION}</p>
        <p>Built with ❤️ for the Egyptian investment community</p>
        <p style="color: #444; font-size: 10px;">Not for commercial use. Educational purposes only.</p>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════
def main():
    render_sidebar()

    page = st.session_state.page

    if page == 'Dashboard':
        render_dashboard()
    elif page == 'Analysis':
        render_analysis()
    elif page == 'Charts':
        render_charts()
    elif page == 'Alerts':
        render_alerts()
    elif page == 'AI':
        render_ai()
    elif page == 'Watchlist':
        render_watchlist()
    elif page == 'Backtest':
        render_backtest()
    elif page == 'Market':
        render_market()
    elif page == 'Settings':
        render_settings()
    else:
        render_dashboard()

if __name__ == "__main__":
    main()
