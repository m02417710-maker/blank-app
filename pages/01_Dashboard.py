"""
EGX Pro Terminal - Dashboard Page
Streamlit Multi-Page: pages/01_Dashboard.py
"""

import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.egx_symbols import get_stock_info, get_all_symbols, get_market_stats, get_blue_chips, get_high_dividend
from data.market_data import generate_mock_data
from data.news_dividends import news_engine
import pandas as pd

st.set_page_config(page_title="EGX Dashboard", page_icon="📊", layout="wide")

def _render_stock_card(symbol, df, info):
    last = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else last
    change = ((last["close"] - prev["close"]) / prev["close"]) * 100
    change_cls = "change-up" if change >= 0 else "change-down"
    sign = "+" if change >= 0 else ""
    closes = df["close"].tail(20).values
    mn, mx = closes.min(), closes.max()
    rng = mx - mn if mx != mn else 1
    pts = " ".join(f"{i * 100 / (len(closes)-1)},{100 - (c - mn) / rng * 100}" for i, c in enumerate(closes))
    sparkline = f'<svg style="position:absolute;bottom:0;left:0;right:0;height:40px;opacity:0.15;pointer-events:none;" viewBox="0 0 100 100" preserveAspectRatio="none"><polyline points="{pts}" fill="none" stroke="#4a9eff" stroke-width="2"/></svg>'
    return f'<div class="stock-card" style="background:linear-gradient(145deg,#1e1e1e,#2a2a2a);border:1px solid #333;border-radius:12px;padding:16px;position:relative;overflow:hidden;margin-bottom:10px;"><div style="font-size:1.2rem;font-weight:700;color:#fff;margin-bottom:4px;">{symbol}</div><div style="font-size:0.8rem;color:#aaa;margin-bottom:8px;">{info.name[:28] if info else symbol}</div><div style="font-size:1.4rem;font-weight:600;color:#4a9eff;">{last["close"]:.2f} <span style="color:{"#00d084" if change >= 0 else "#ff4757"};">{sign}{change:.2f}%</span></div><div style="font-size:0.75rem;color:#777;margin-top:8px;">Vol: {last["volume"]:,}</div>{sparkline}</div>'

st.title("🇪🇬 EGX Pro Dashboard")
st.caption(f"Last update: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Market Overview
stats = get_market_stats()
col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    st.metric("Companies", stats['total_companies'])
with col2:
    st.metric("Market Cap", f"{stats['total_market_cap_egp_billions']:.1f}B EGP")
with col3:
    st.metric("Avg P/E", f"{stats['avg_pe_ratio']}")
with col4:
    st.metric("Avg Div Yield", f"{stats['avg_dividend_yield']:.1f}%")
with col5:
    st.metric("Sectors", stats['total_sectors'])
with col6:
    st.metric("Blue Chips", stats['blue_chips'])

st.divider()

# Market Indices
st.subheader("📈 Market Indices")
indices = ["EGX30", "EGX70", "EGX100", "EGX20"]
idx_cols = st.columns(4)
for idx, symbol in enumerate(indices):
    with idx_cols[idx]:
        df = generate_mock_data(symbol, 30)
        last = df.iloc[-1]
        prev = df.iloc[-2]
        change = ((last["close"] - prev["close"]) / prev["close"]) * 100
        st.metric(symbol, f"{last['close']:.2f}", f"{change:+.2f}%")

st.divider()

# Watchlist
st.subheader("📌 Your Watchlist")
if "watchlist" not in st.session_state:
    st.session_state["watchlist"] = ["COMI", "HRHO", "ETEL", "SWDY", "EAST"]

watchlist = st.session_state["watchlist"]
for i in range(0, len(watchlist), 4):
    cols = st.columns(4)
    for j, sym in enumerate(watchlist[i:i+4]):
        with cols[j]:
            df = generate_mock_data(sym, 30)
            info = get_stock_info(sym)
            st.markdown(_render_stock_card(sym, df, info), unsafe_allow_html=True)

st.divider()

# Top Performers
st.subheader("🏆 Top Performers (Today)")
all_syms = get_all_symbols()[:20]
performers = []
for sym in all_syms:
    df = generate_mock_data(sym, 5)
    if len(df) >= 2:
        change = ((df.iloc[-1]["close"] - df.iloc[-2]["close"]) / df.iloc[-2]["close"]) * 100
        performers.append((sym, change, df.iloc[-1]["close"]))

performers.sort(key=lambda x: x[1], reverse=True)
top_gainers = performers[:5]
top_losers = performers[-5:]

col1, col2 = st.columns(2)
with col1:
    st.write("**📈 Top Gainers**")
    for sym, change, price in top_gainers:
        st.write(f"**{sym}** | {price:.2f} | +{change:.2f}% 🟢")
with col2:
    st.write("**📉 Top Losers**")
    for sym, change, price in top_losers:
        st.write(f"**{sym}** | {price:.2f} | {change:.2f}% 🔴")

st.divider()

# High Dividend Stocks
st.subheader("💰 High Dividend Yield Stocks")
high_div = get_high_dividend()[:10]
for sym in high_div:
    info = get_stock_info(sym)
    if info and info.dividend_yield:
        st.write(f"**{sym}** ({info.name}) — Yield: {info.dividend_yield:.2f}%")

st.divider()

# Latest News
st.subheader("📰 Latest Market News")
news_items = news_engine.get_all_news(5)
for news in news_items:
    with st.expander(f"{news.title} [{news.priority.value.upper()}]"):
        st.write(news.content)
        st.caption(f"{news.source} | {news.published_at.strftime('%Y-%m-%d %H:%M')}")
