"""
EGX Pro Terminal - Fixed Version
React-DOM Safe | Stable Keys | Proper State Management
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ============ INITIALIZATION ============
def init_session_state():
    defaults = {
        "page": "dashboard",
        "alerts": [],
        "watchlist": ["COMI", "HRHO", "ETEL", "SWDY", "EAST"],
        "selected_symbol": "COMI",
        "selected_timeframe": "3M",
        "theme": "dark",
        "last_update": None,
        "news_filter": "all",
        "sector_filter": "all",
        "alert_symbol": "COMI",
        "backtest_strategy": "trend_following",
        "ai_model": "ensemble",
        "delete_alert_id": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_state()

# ============ NAVIGATION ============
def render_sidebar():
    with st.sidebar:
        st.title("🇪🇬 EGX Pro Terminal")
        st.caption("Professional EGX Analysis")
        
        pages = [
            ("dashboard", "📊 Dashboard"),
            ("technical", "📈 Technical"),
            ("ai_predictions", "🤖 AI Predictions"),
            ("backtest", "📊 Backtest"),
            ("alerts", "🔔 Alerts"),
            ("news", "📰 News"),
            ("settings", "⚙️ Settings"),
        ]
        
        st.divider()
        for key, label in pages:
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state["page"] = key
                st.rerun()
        
        st.divider()
        st.caption(f"Last update: {pd.Timestamp.now().strftime('%H:%M:%S')}")

# ============ DATA IMPORTS ============
from data.egx_symbols import get_stock_info, get_all_symbols, get_market_stats
from data.market_data import generate_mock_data
from data.news_dividends import news_engine, NewsCategory
from core.analysis import TechnicalAnalysis
from core.ai_engine import AIEngine
from core.alerts import AlertEngine
from core.backtest import BacktestEngine
from core.patterns import pattern_engine
from core.charts import ChartEngine

ta = TechnicalAnalysis()
ai = AIEngine()
alert_eng = AlertEngine()
bt = BacktestEngine()
charts = ChartEngine()

# ============ PAGES ============
def page_dashboard():
    st.title("🇪🇬 EGX Pro Terminal")
    
    # Market Stats
    stats = get_market_stats()
    cols = st.columns(6)
    metrics = [
        ("Companies", f"{stats['total_companies']}"),
        ("Market Cap", f"{stats['total_market_cap_egp_billions']:.1f}B EGP"),
        ("Avg P/E", f"{stats['avg_pe_ratio']}"),
        ("Avg Div Yield", f"{stats['avg_dividend_yield']:.1f}%"),
        ("Sectors", f"{stats['total_sectors']}"),
        ("Blue Chips", f"{stats['blue_chips']}"),
    ]
    for col, (label, value) in zip(cols, metrics):
        with col:
            st.metric(label, value)
    
    # Watchlist
    st.subheader("📌 Watchlist")
    symbols = st.session_state["watchlist"]
    watch_cols = st.columns(min(len(symbols), 5))
    for col, sym in zip(watch_cols, symbols):
        with col:
            df = generate_mock_data(sym, 30)
            info = get_stock_info(sym)
            last = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else last
            change = ((last["close"] - prev["close"]) / prev["close"]) * 100
            st.metric(sym, f"{last['close']:.2f}", f"{change:+.2f}%")
    
    # Quick Analysis
    st.subheader("🔍 Quick Analysis")
    all_syms = get_all_symbols()[:50]
    sel_idx = all_syms.index(st.session_state["selected_symbol"]) if st.session_state["selected_symbol"] in all_syms else 0
    selected = st.selectbox("Select Symbol", all_syms, index=sel_idx, key="dash_symbol")
    st.session_state["selected_symbol"] = selected
    
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📈 View Technical", key="dash_tech", use_container_width=True):
            st.session_state["page"] = "technical"
            st.rerun()
    with c2:
        if st.button("🔔 Add Alert", key="dash_alert", use_container_width=True):
            st.session_state["alert_symbol"] = selected
            st.session_state["page"] = "alerts"
            st.rerun()
    with c3:
        if st.button("⭐ Add to Watchlist", key="dash_watch", use_container_width=True):
            if selected not in st.session_state["watchlist"]:
                st.session_state["watchlist"].append(selected)
                st.toast(f"Added {selected} to watchlist!", icon="✅")

def page_technical():
    symbol = st.session_state.get("selected_symbol", "COMI")
    st.title(f"📈 Technical Analysis: {symbol}")
    
    timeframe = st.selectbox("Timeframe", ["1M", "3M", "6M", "1Y", "YTD"], index=1, key="tech_timeframe")
    days_map = {"1M": 22, "3M": 66, "6M": 132, "1Y": 252, "YTD": 180}
    days = days_map.get(timeframe, 90)
    
    df = generate_mock_data(symbol, days)
    info = get_stock_info(symbol)
    
    fig = charts.create_candlestick_chart(df, symbol, info.name if info else symbol)
    st.plotly_chart(fig, use_container_width=True, key="tech_chart")
    
    last = df.iloc[-1]
    indicators = ta.calculate_all_indicators(df)
    
    tech_cols = st.columns(6)
    tech_metrics = [
        ("RSI (14)", f"{indicators.get('rsi', 0):.1f}"),
        ("MACD", f"{indicators.get('macd', 0):.3f}"),
        ("Signal", f"{indicators.get('macd_signal', 0):.3f}"),
        ("MA20", f"{indicators.get('sma20', 0):.2f}"),
        ("MA50", f"{indicators.get('sma50', 0):.2f}"),
        ("Trend", "Bullish" if last["close"] > indicators.get("sma50", last["close"]) else "Bearish"),
    ]
    for col, (label, value) in zip(tech_cols, tech_metrics):
        with col:
            st.metric(label, value)

def page_ai():
    symbol = st.session_state.get("selected_symbol", "COMI")
    st.title(f"🤖 AI Predictions: {symbol}")
    
    df = generate_mock_data(symbol, 252)
    model = st.selectbox("AI Model", ["ensemble", "monte_carlo", "technical", "sentiment"], index=0, key="ai_model")
    
    if st.button("🚀 Generate Prediction", key="ai_run", use_container_width=True):
        with st.spinner("Running AI analysis..."):
            prediction = ai.predict(df, model_type=model)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Bullish", f"{prediction.get('bullish_prob', 0)*100:.1f}%")
            with col2:
                st.metric("Bearish", f"{prediction.get('bearish_prob', 0)*100:.1f}%")
            with col3:
                st.metric("Neutral", f"{prediction.get('neutral_prob', 0)*100:.1f}%")

def page_backtest():
    symbol = st.session_state.get("selected_symbol", "COMI")
    st.title(f"📊 Strategy Backtest: {symbol}")
    
    strategy = st.selectbox("Strategy", ["trend_following", "mean_reversion", "momentum", "breakout"], index=0, key="bt_strategy")
    col1, col2 = st.columns(2)
    with col1:
        initial_capital = st.number_input("Initial Capital (EGP)", value=100000, step=10000, key="bt_capital")
    with col2:
        days = st.number_input("Backtest Period (days)", value=252, step=30, key="bt_days")
    
    if st.button("▶️ Run Backtest", key="bt_run", use_container_width=True):
        with st.spinner("Running backtest..."):
            df = generate_mock_data(symbol, days)
            result = bt.run_backtest(df, strategy, initial_capital)
            st.json(result.get("summary", {}))

def add_alert(symbol, condition, price):
    alert = {
        "id": f"alert_{len(st.session_state['alerts'])}_{pd.Timestamp.now().strftime('%H%M%S')}",
        "symbol": symbol,
        "condition": condition,
        "target": price,
        "created": pd.Timestamp.now().isoformat(),
        "triggered": False
    }
    st.session_state["alerts"].append(alert)
    st.toast(f"Alert set: {symbol} {condition} @ {price:.2f}", icon="🔔")

def page_alerts():
    st.title("🔔 Price Alerts")
    
    # Handle deletion first
    if st.session_state.delete_alert_id:
        st.session_state["alerts"] = [a for a in st.session_state["alerts"] 
                                       if a["id"] != st.session_state.delete_alert_id]
        st.session_state.delete_alert_id = None
        st.rerun()
    
    # Create new alert
    st.subheader("Create New Alert")
    all_syms = get_all_symbols()[:50]
    sym = st.selectbox("Symbol", all_syms, key="alert_sym")
    col_type, col_price = st.columns(2)
    with col_type:
        cond = st.selectbox("Condition", ["ABOVE", "BELOW", "BULLISH", "BEARISH"], key="alert_cond")
    with col_price:
        price = st.number_input("Target Price", value=50.0, step=0.5, key="alert_price")
    
    if st.button("➕ Create Alert", key="alert_create", use_container_width=True):
        add_alert(sym, cond, price)
        st.rerun()
    
    # Active alerts
    st.divider()
    st.subheader("Active Alerts")
    alerts = st.session_state.get("alerts", [])
    if not alerts:
        st.info("No active alerts.")
    else:
        for alert in alerts:
            triggered = alert.get("triggered", False)
            status = "🔴 TRIGGERED" if triggered else "🟢 ACTIVE"
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{alert['symbol']}** — {alert['condition']} @ {alert['target']:.2f} | {status}")
            with col2:
                if st.button("🗑️", key=f"del_{alert['id']}"):
                    st.session_state.delete_alert_id = alert["id"]
                    st.rerun()

def page_news():
    st.title("📰 Market News & Dividends")
    tab1, tab2 = st.tabs(["📰 News", "💰 Dividends"])
    
    with tab1:
        st.subheader("Latest Market News")
        news_items = news_engine.get_all_news(20)
        for news in news_items[:5]:
            st.write(f"**{news.title}** | {news.source} | {news.category.value}")
    
    with tab2:
        st.subheader("💰 Dividend Distributions")
        dividends = news_engine.get_dividends()
        for div in dividends[:5]:
            st.write(f"**{div.symbol}**: {div.amount_per_share:.2f} {div.currency}")

def page_settings():
    st.title("⚙️ Settings")
    
    st.subheader("📌 Watchlist")
    current = st.session_state.get("watchlist", [])
    watch_text = st.text_area("Symbols (comma separated)", value=", ".join(current), key="set_watch")
    if st.button("💾 Save Watchlist", key="set_save_watch", use_container_width=True):
        new_list = [s.strip().upper() for s in watch_text.split(",") if s.strip()]
        st.session_state["watchlist"] = new_list
        st.toast(f"Watchlist updated: {len(new_list)} symbols", icon="💾")
    
    st.subheader("🎨 Appearance")
    theme = st.radio("Theme", ["dark", "light"], index=0, key="set_theme", horizontal=True)
    st.session_state["theme"] = theme
    
    st.subheader("⚠️ Danger Zone")
    if st.button("🗑️ Clear All Alerts", key="set_clear_alerts", use_container_width=True):
        st.session_state["alerts"] = []
        st.toast("All alerts cleared", icon="🗑️")
        st.rerun()
    
    if st.button("🏭 Reset to Defaults", key="set_reset", use_container_width=True):
        preserve = {"page", "_render_id", "_widget_counter"}
        keys_to_remove = [k for k in list(st.session_state.keys()) if k not in preserve]
        for k in keys_to_remove:
            del st.session_state[k]
        init_session_state()
        st.toast("Settings reset", icon="🏭")
        st.rerun()

# ============ MAIN ============
def main():
    render_sidebar()
    page = st.session_state.get("page", "dashboard")
    pages = {
        "dashboard": page_dashboard,
        "technical": page_technical,
        "ai_predictions": page_ai,
        "backtest": page_backtest,
        "alerts": page_alerts,
        "news": page_news,
        "settings": page_settings
    }
    page_func = pages.get(page, page_dashboard)
    page_func()

if __name__ == "__main__":
    main()
