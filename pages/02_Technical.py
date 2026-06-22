"""
EGX Pro Terminal - Technical Analysis Page
"""

import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.egx_symbols import get_stock_info, get_all_symbols
from data.market_data import generate_mock_data
from core.analysis import TechnicalAnalysis
from core.patterns import pattern_engine
from core.charts import ChartEngine
import pandas as pd

st.set_page_config(page_title="Technical Analysis", page_icon="📈", layout="wide")

ta = TechnicalAnalysis()
charts = ChartEngine()

st.title("📈 Technical Analysis")

all_syms = get_all_symbols()[:50]
if "selected_symbol" not in st.session_state:
    st.session_state["selected_symbol"] = "COMI"

symbol = st.selectbox("Select Symbol", all_syms, 
                     index=all_syms.index(st.session_state["selected_symbol"]) if st.session_state["selected_symbol"] in all_syms else 0,
                     key="tech_symbol")
st.session_state["selected_symbol"] = symbol

timeframe = st.select_slider("Timeframe", options=["1M", "3M", "6M", "1Y", "YTD", "MAX"], value="3M")
days_map = {"1M": 22, "3M": 66, "6M": 132, "1Y": 252, "YTD": 180, "MAX": 500}
days = days_map.get(timeframe, 90)

df = generate_mock_data(symbol, days)
info = get_stock_info(symbol)

# Main Chart
fig = charts.create_candlestick_chart(df, symbol, info.name if info else symbol)
st.plotly_chart(fig, use_container_width=True, use_container_height=True)

# Technical Indicators Table
st.subheader("📊 Technical Indicators")
indicators = ta.calculate_all_indicators(df)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("RSI (14)", f"{indicators.get('rsi', 0):.1f}")
    st.metric("MACD", f"{indicators.get('macd', 0):.3f}")
    st.metric("MACD Signal", f"{indicators.get('macd_signal', 0):.3f}")
with col2:
    st.metric("SMA 20", f"{indicators.get('sma20', 0):.2f}")
    st.metric("SMA 50", f"{indicators.get('sma50', 0):.2f}")
    st.metric("SMA 200", f"{indicators.get('sma200', 0):.2f}")
with col3:
    st.metric("EMA 9", f"{indicators.get('ema9', 0):.2f}")
    st.metric("EMA 21", f"{indicators.get('ema21', 0):.2f}")
    st.metric("VWAP", f"{indicators.get('vwap', 0):.2f}")
with col4:
    st.metric("BB Upper", f"{indicators.get('bb_upper', 0):.2f}")
    st.metric("BB Middle", f"{indicators.get('bb_middle', 0):.2f}")
    st.metric("BB Lower", f"{indicators.get('bb_lower', 0):.2f}")

# Pattern Detection
st.subheader("🔍 Candlestick Patterns")
patterns = pattern_engine.get_pattern_summary(df)
if patterns["total"] > 0:
    st.write(f"**Total Patterns Detected:** {patterns['total']}")
    st.write(f"**Bullish:** {patterns['bullish_count']} | **Bearish:** {patterns['bearish_count']}")
    st.write(f"**Latest Signal:** {patterns['latest_signal']}")

    if patterns['bullish_patterns']:
        st.write("**Bullish Patterns:**")
        for p in patterns['bullish_patterns']:
            st.write(f"• {p['pattern']} (Confidence: {p['confidence']*100:.0f}%)")
    if patterns['bearish_patterns']:
        st.write("**Bearish Patterns:**")
        for p in patterns['bearish_patterns']:
            st.write(f"• {p['pattern']} (Confidence: {p['confidence']*100:.0f}%)")
else:
    st.info("No significant patterns detected in the current timeframe.")

# Support/Resistance
st.subheader("🎯 Support & Resistance Levels")
sr_levels = ta.find_support_resistance(df)
st.write(f"**Support Levels:** {', '.join([f'{l:.2f}' for l in sr_levels['support'][:3]])}")
st.write(f"**Resistance Levels:** {', '.join([f'{l:.2f}' for l in sr_levels['resistance'][:3]])}")
st.write(f"**Pivot Point:** {sr_levels['pivot']:.2f}")

# Volume Analysis
st.subheader("📊 Volume Analysis")
vol_metrics = ta.volume_analysis(df)
st.write(f"**Average Volume:** {vol_metrics['avg_volume']:,.0f}")
st.write(f"**Volume Trend:** {vol_metrics['volume_trend']}")
st.write(f"**OBV:** {vol_metrics['obv']:,.0f}")
st.write(f"**Money Flow Index:** {vol_metrics['mfi']:.1f}")
