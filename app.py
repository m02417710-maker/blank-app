"""
EGX Pro Terminal v35 - Fixed Version
React-DOM Safe | Stable Keys | Proper State Management
No HTML+Button mixing | No dynamic keys | No state mutation during render
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ============ CRITICAL: PAGE CONFIG MUST BE FIRST ============
st.set_page_config(
    page_title="EGX Pro Terminal",
    page_icon="🇪🇬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/m02417710-maker/blank-app',
        'Report a bug': 'https://github.com/m02417710-maker/blank-app/issues',
        'About': 'EGX Pro Terminal - Professional Egyptian Stock Market Analysis Platform'
    }
)

# ============ SESSION STATE INITIALIZATION ============
def init_session_state():
    """Initialize all session state variables with defaults"""
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
        "reset_triggered": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ============ CSS INJECTION (SAFE - NO EMPTY CSS) ============
def inject_css():
    """Inject custom CSS styles"""
    css = """
    <style>
    /* Main app background */
    .stApp {
        background-color: #0e1117;
    }

    /* Sidebar styling */
    .stSidebar {
        background-color: #161b22;
    }

    /* Button styling */
    .stButton > button {
        background-color: #1f6feb;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 500;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background-color: #388bfd;
        transform: translateY(-1px);
    }

    /* Metric cards */
    .stMetric {
        background-color: #161b22;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #30363d;
    }

    /* Alert cards */
    .alert-card {
        background-color: #161b22;
        padding: 12px;
        border-radius: 6px;
        border-left: 3px solid #1f6feb;
        margin-bottom: 8px;
    }
    .alert-card.triggered {
        border-left-color: #ff4444;
    }
    .alert-card.active {
        border-left-color: #00ff88;
    }

    /* News cards */
    .news-card {
        background-color: #161b22;
        padding: 10px;
        border-radius: 6px;
        margin-bottom: 8px;
        border-left: 3px solid #ffaa00;
    }

    /* Dividend cards */
    .dividend-card {
        background-color: #161b22;
        padding: 10px;
        border-radius: 6px;
        margin-bottom: 8px;
        border-left: 3px solid #00ff88;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0e1117;
    }
    ::-webkit-scrollbar-thumb {
        background: #30363d;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #484f58;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

inject_css()

# ============ STABLE KEY GENERATOR ============
def get_key(base: str) -> str:
    """
    Generate stable widget key based on current page.
    CRITICAL: Keys must be stable across renders to prevent React DOM errors.
    """
    page = st.session_state.get("page", "dashboard")
    return f"{page}_{base}"

# ============ SAFE NAVIGATION (NO HTML MIXING) ============
def render_sidebar():
    """
    Render navigation sidebar using ONLY Streamlit native components.
    NEVER mix HTML with Streamlit widgets - this causes React DOM errors.
    """
    with st.sidebar:
        st.title("🇪🇬 EGX Pro")
        st.caption("Professional EGX Analysis")
        st.divider()

        pages = [
            ("dashboard", "📊 Dashboard"),
            ("technical", "📈 Technical"),
            ("ai_predictions", "🤖 AI"),
            ("backtest", "📊 Backtest"),
            ("alerts", "🔔 Alerts"),
            ("news", "📰 News"),
            ("settings", "⚙️ Settings"),
        ]

        for key, label in pages:
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state["page"] = key
                st.rerun()

        st.divider()
        st.caption(f"Last update: {pd.Timestamp.now().strftime('%H:%M:%S')}")

        # Quick symbol selector in sidebar
        st.divider()
        st.subheader("🔍 Quick Symbol")
        from data.egx_symbols import get_all_symbols
        all_syms = get_all_symbols()[:20]
        current_sym = st.session_state.get("selected_symbol", "COMI")
        sym_idx = all_syms.index(current_sym) if current_sym in all_syms else 0
        selected = st.selectbox("Symbol", all_syms, index=sym_idx, key="sidebar_symbol")
        if selected != current_sym:
            st.session_state["selected_symbol"] = selected

# ============ DATA IMPORTS ============
from data.egx_symbols import get_stock_info, get_all_symbols, get_market_stats, get_sector_performance
from data.market_data import generate_mock_data, get_realtime_quote
from data.news_dividends import news_engine, NewsCategory
from core.analysis import TechnicalAnalysis
from core.ai_engine import AIEngine
from core.alerts import AlertEngine
from core.backtest import BacktestEngine
from core.patterns import pattern_engine
from core.charts import ChartEngine
from utils.formatters import format_number, format_percentage, format_volume
from utils.helpers import time_ago

ta = TechnicalAnalysis()
ai = AIEngine()
alert_eng = AlertEngine()
bt = BacktestEngine()
charts = ChartEngine()

# ============ PAGE: DASHBOARD ============
def page_dashboard():
    st.title("🇪🇬 EGX Pro Terminal")
    st.caption("Professional Egyptian Stock Market Analysis Platform")

    # Market Overview Stats
    stats = get_market_stats()
    cols = st.columns(6)
    metrics = [
        ("Companies", f"{stats['total_companies']}", None),
        ("Market Cap", f"{stats['total_market_cap_egp_billions']:.1f}B EGP", None),
        ("Avg P/E", f"{stats['avg_pe_ratio']}", None),
        ("Avg Div Yield", f"{stats['avg_dividend_yield']:.1f}%", None),
        ("Sectors", f"{stats['total_sectors']}", None),
        ("Blue Chips", f"{stats['blue_chips']}", None),
    ]
    for col, (label, value, delta) in zip(cols, metrics):
        with col:
            if delta:
                st.metric(label, value, delta)
            else:
                st.metric(label, value)

    st.divider()

    # Watchlist Section
    st.subheader("📌 Watchlist")
    symbols = st.session_state.get("watchlist", [])
    if symbols:
        # Display watchlist as metrics in columns
        watch_cols = st.columns(min(len(symbols), 5))
        for col, sym in zip(watch_cols, symbols):
            with col:
                try:
                    df = generate_mock_data(sym, 30)
                    last = df.iloc[-1]
                    prev = df.iloc[-2] if len(df) > 1 else last
                    change = ((last["close"] - prev["close"]) / prev["close"]) * 100
                    st.metric(sym, f"{last['close']:.2f}", f"{change:+.2f}%")
                except Exception:
                    st.metric(sym, "N/A", "0%")

    st.divider()

    # Quick Analysis Section
    st.subheader("🔍 Quick Analysis")
    all_syms = get_all_symbols()[:50]
    current_sym = st.session_state.get("selected_symbol", "COMI")
    sel_idx = all_syms.index(current_sym) if current_sym in all_syms else 0
    selected = st.selectbox("Select Symbol", all_syms, index=sel_idx, key=get_key("dash_symbol"))

    if selected != current_sym:
        st.session_state["selected_symbol"] = selected

    # Quick action buttons
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📈 View Technical", key=get_key("dash_tech"), use_container_width=True):
            st.session_state["page"] = "technical"
            st.rerun()
    with c2:
        if st.button("🔔 Add Alert", key=get_key("dash_alert"), use_container_width=True):
            st.session_state["alert_symbol"] = selected
            st.session_state["page"] = "alerts"
            st.rerun()
    with c3:
        if st.button("⭐ Add to Watchlist", key=get_key("dash_watch"), use_container_width=True):
            watchlist = st.session_state.get("watchlist", [])
            if selected not in watchlist:
                watchlist.append(selected)
                st.session_state["watchlist"] = watchlist
                st.toast(f"Added {selected} to watchlist!", icon="✅")

    # Sector Performance
    st.divider()
    st.subheader("📊 Sector Performance")
    sector_perf = get_sector_performance()
    sector_data = {k: v for k, v in sorted(sector_perf.items(), key=lambda x: x[1], reverse=True)}
    sector_cols = st.columns(min(len(sector_data), 6))
    for col, (sector, perf) in zip(sector_cols, list(sector_data.items())[:6]):
        with col:
            color = "🟢" if perf > 0 else "🔴" if perf < 0 else "⚪"
            st.metric(f"{color} {sector}", f"{perf:+.2f}%")

# ============ PAGE: TECHNICAL ============
def page_technical():
    symbol = st.session_state.get("selected_symbol", "COMI")
    st.title(f"📈 Technical Analysis: {symbol}")

    # Timeframe selector
    timeframe = st.selectbox(
        "Timeframe", 
        ["1M", "3M", "6M", "1Y", "YTD"], 
        index=1, 
        key=get_key("tech_timeframe")
    )
    days_map = {"1M": 22, "3M": 66, "6M": 132, "1Y": 252, "YTD": 180}
    days = days_map.get(timeframe, 90)

    # Generate data and display chart
    df = generate_mock_data(symbol, days)
    info = get_stock_info(symbol)

    fig = charts.create_candlestick_chart(df, symbol, info.name if info else symbol)
    st.plotly_chart(fig, use_container_width=True, key=get_key("tech_chart"))

    # Technical indicators
    last = df.iloc[-1]
    indicators = ta.calculate_all_indicators(df)

    st.subheader("📊 Technical Indicators")
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

    # Pattern detection
    patterns = pattern_engine.get_pattern_summary(df)
    if patterns.get("total", 0) > 0:
        st.subheader("🔍 Pattern Detection")
        st.write(f"Bullish: {patterns['bullish_count']} | Bearish: {patterns['bearish_count']} | Latest: {patterns['latest_signal']}")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("⬆️ Bullish Alert", key=get_key("tech_bull"), use_container_width=True):
                st.toast(f"Bullish alert set for {symbol}", icon="📈")
        with c2:
            if st.button("⬇️ Bearish Alert", key=get_key("tech_bear"), use_container_width=True):
                st.toast(f"Bearish alert set for {symbol}", icon="📉")

    # Support/Resistance
    st.divider()
    sr = ta.get_support_resistance(df)
    sr_cols = st.columns(3)
    with sr_cols[0]:
        st.metric("Support", f"{sr['nearest_support']:.2f}")
    with sr_cols[1]:
        st.metric("Current", f"{last['close']:.2f}")
    with sr_cols[2]:
        st.metric("Resistance", f"{sr['nearest_resistance']:.2f}")

# ============ PAGE: AI PREDICTIONS ============
def page_ai():
    symbol = st.session_state.get("selected_symbol", "COMI")
    st.title(f"🤖 AI Predictions: {symbol}")

    df = generate_mock_data(symbol, 252)
    model = st.selectbox(
        "AI Model", 
        ["ensemble", "monte_carlo", "technical", "sentiment"], 
        index=0, 
        key=get_key("ai_model")
    )

    if st.button("🚀 Generate Prediction", key=get_key("ai_run"), use_container_width=True):
        with st.spinner("Running AI analysis..."):
            prediction = ai.predict(df, model_type=model)

            # Display probabilities
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Bullish Probability", f"{prediction.get('bullish_prob', 0)*100:.1f}%")
            with col2:
                st.metric("Bearish Probability", f"{prediction.get('bearish_prob', 0)*100:.1f}%")
            with col3:
                st.metric("Neutral Probability", f"{prediction.get('neutral_prob', 0)*100:.1f}%")

            # Signal breakdown
            st.subheader("📊 Signal Breakdown")
            for signal in prediction.get("signals", []):
                st.write(f"• {signal}")

            # Recommendation
            st.subheader("🎯 Recommendation")
            rec = prediction.get("recommendation", "HOLD")
            color_map = {"BUY": "#00ff88", "SELL": "#ff4444", "HOLD": "#ffaa00"}
            color = color_map.get(rec, "#888888")
            st.markdown(
                f"<h2 style='color:{color};text-align:center;padding:20px;background-color:#161b22;border-radius:8px;'>"
                f"{rec}</h2>", 
                unsafe_allow_html=True
            )

            # Price targets
            st.subheader("🎯 Price Targets")
            target_cols = st.columns(3)
            with target_cols[0]:
                st.metric("Current Price", f"{prediction.get('current_price', 0):.2f}")
            with target_cols[1]:
                st.metric("Target Price", f"{prediction.get('target_price', 0):.2f}")
            with target_cols[2]:
                st.metric("Stop Loss", f"{prediction.get('stop_loss', 0):.2f}")

            # Monte Carlo results
            if prediction.get('monte_carlo'):
                st.subheader("🎲 Monte Carlo Simulation")
                mc = prediction['monte_carlo']
                mc_cols = st.columns(5)
                mc_metrics = [
                    ("5th Percentile", f"{mc.get('percentile_5', 0):.2f}"),
                    ("25th Percentile", f"{mc.get('percentile_25', 0):.2f}"),
                    ("Median", f"{mc.get('median_price', 0):.2f}"),
                    ("75th Percentile", f"{mc.get('percentile_75', 0):.2f}"),
                    ("95th Percentile", f"{mc.get('percentile_95', 0):.2f}"),
                ]
                for col, (label, value) in zip(mc_cols, mc_metrics):
                    with col:
                        st.metric(label, value)

# ============ PAGE: BACKTEST ============
def page_backtest():
    symbol = st.session_state.get("selected_symbol", "COMI")
    st.title(f"📊 Strategy Backtest: {symbol}")

    strategy = st.selectbox(
        "Strategy", 
        ["trend_following", "mean_reversion", "momentum", "breakout", 
         "rsi_strategy", "macd_strategy", "bollinger_strategy", "ml_strategy"], 
        index=0, 
        key=get_key("bt_strategy")
    )

    col1, col2 = st.columns(2)
    with col1:
        initial_capital = st.number_input(
            "Initial Capital (EGP)", 
            value=100000, 
            step=10000, 
            key=get_key("bt_capital")
        )
    with col2:
        days = st.number_input(
            "Backtest Period (days)", 
            value=252, 
            step=30, 
            key=get_key("bt_days")
        )

    if st.button("▶️ Run Backtest", key=get_key("bt_run"), use_container_width=True):
        with st.spinner("Running backtest..."):
            df = generate_mock_data(symbol, days)
            result = bt.run_backtest(df, strategy, initial_capital)

            st.subheader("📈 Performance Summary")
            metrics = result.get("summary", {})

            perf_cols = st.columns(6)
            perf_metrics = [
                ("Total Return", f"{metrics.get('total_return', 0)*100:.2f}%"),
                ("Annual Return", f"{metrics.get('annual_return', 0)*100:.2f}%"),
                ("Sharpe Ratio", f"{metrics.get('sharpe_ratio', 0):.2f}"),
                ("Max Drawdown", f"{metrics.get('max_drawdown', 0)*100:.2f}%"),
                ("Win Rate", f"{metrics.get('win_rate', 0)*100:.1f}%"),
                ("Trades", f"{metrics.get('total_trades', 0)}"),
            ]
            for col, (label, value) in zip(perf_cols, perf_metrics):
                with col:
                    st.metric(label, value)

            # Equity curve
            equity_curve = result.get("equity_curve", [])
            if equity_curve:
                st.subheader("📈 Equity Curve")
                fig = charts.create_equity_curve(equity_curve)
                st.plotly_chart(fig, use_container_width=True, key=get_key("bt_equity"))

            # Trade list
            trades = result.get("trades", [])
            if trades:
                st.subheader("📋 Trade History")
                trade_df = pd.DataFrame(trades[:10])  # Show first 10 trades
                st.dataframe(trade_df, use_container_width=True)

# ============ SAFE ALERT MANAGEMENT ============
def add_alert(symbol: str, condition: str, price: float):
    """Add new alert safely"""
    alert = {
        "id": f"alert_{len(st.session_state.get('alerts', []))}_{pd.Timestamp.now().strftime('%H%M%S')}",
        "symbol": symbol,
        "condition": condition,
        "target": price,
        "created": pd.Timestamp.now().isoformat(),
        "triggered": False
    }
    alerts = st.session_state.get("alerts", [])
    alerts.append(alert)
    st.session_state["alerts"] = alerts
    st.toast(f"Alert set: {symbol} {condition} @ {price:.2f}", icon="🔔")

def mark_alert_for_deletion(alert_id: str):
    """Mark alert for deletion (will be processed on next render)"""
    st.session_state["delete_alert_id"] = alert_id

# ============ PAGE: ALERTS ============
def page_alerts():
    st.title("🔔 Price Alerts")

    # CRITICAL: Process deletions BEFORE rendering
    # This prevents React DOM errors from modifying state during render
    delete_id = st.session_state.get("delete_alert_id")
    if delete_id:
        alerts = st.session_state.get("alerts", [])
        st.session_state["alerts"] = [a for a in alerts if a["id"] != delete_id]
        st.session_state["delete_alert_id"] = None
        st.toast("Alert deleted", icon="🗑️")
        st.rerun()

    # Create new alert section
    st.subheader("➕ Create New Alert")
    all_syms = get_all_symbols()[:50]
    sym = st.selectbox("Symbol", all_syms, key=get_key("alert_sym"))

    col_type, col_price = st.columns(2)
    with col_type:
        cond = st.selectbox(
            "Condition", 
            ["ABOVE", "BELOW", "BULLISH", "BEARISH"], 
            key=get_key("alert_cond")
        )
    with col_price:
        price = st.number_input(
            "Target Price", 
            value=50.0, 
            step=0.5, 
            key=get_key("alert_price")
        )

    if st.button("➕ Create Alert", key=get_key("alert_create"), use_container_width=True):
        add_alert(sym, cond, price)
        st.rerun()

    # Active alerts section
    st.divider()
    st.subheader("📋 Active Alerts")

    alerts = st.session_state.get("alerts", [])
    if not alerts:
        st.info("No active alerts. Create one above.")
    else:
        for alert in alerts:
            triggered = alert.get("triggered", False)
            status = "🔴 TRIGGERED" if triggered else "🟢 ACTIVE"
            card_class = "triggered" if triggered else "active"

            # Use columns for layout - NO nested HTML with buttons
            col1, col2, col3 = st.columns([3, 2, 1])

            with col1:
                st.write(f"**{alert['symbol']}**")
                st.caption(f"{alert['condition']} @ {alert['target']:.2f}")

            with col2:
                st.write(f"{status}")
                st.caption(f"Created: {alert['created'][:16]}")

            with col3:
                # CRITICAL: Use mark_alert_for_deletion instead of direct deletion
                if st.button("🗑️", key=f"del_{alert['id']}"):
                    mark_alert_for_deletion(alert["id"])
                    st.rerun()

            st.divider()

# ============ PAGE: NEWS & DIVIDENDS ============
def page_news():
    st.title("📰 Market News & Dividends")

    tab1, tab2 = st.tabs(["📰 News", "💰 Dividends"])

    with tab1:
        st.subheader("Latest Market News")

        filter_cat = st.selectbox(
            "Filter by Category", 
            ["all", "earnings", "dividend", "ipo", "market_update", "economic"], 
            key=get_key("news_filter")
        )

        news_items = news_engine.get_all_news(20)
        if filter_cat != "all":
            cat_map = {
                "earnings": NewsCategory.EARNINGS, 
                "dividend": NewsCategory.DIVIDEND, 
                "ipo": NewsCategory.IPO, 
                "market_update": NewsCategory.MARKET_UPDATE, 
                "economic": NewsCategory.ECONOMIC
            }
            news_items = [n for n in news_items if n.category == cat_map.get(filter_cat)]

        for news in news_items[:10]:
            priority_class = news.priority.value
            time_ago_str = time_ago(news.published_at)

            with st.container():
                st.markdown(f"""
                <div style="padding:12px; background-color:#161b22; border-radius:8px; margin-bottom:10px; border-left:3px solid {'#ff4444' if priority_class=='high' else '#ffaa00' if priority_class=='medium' else '#00ff88'};">
                    <strong>{news.title}</strong><br>
                    <small>{news.source} • {time_ago_str} • {news.category.value}</small><br>
                    {news.content[:200]}...
                </div>
                """, unsafe_allow_html=True)

    with tab2:
        st.subheader("💰 Dividend Distributions")

        dividends = news_engine.get_dividends()
        for div in dividends[:10]:
            status_color = {"announced": "🟡", "approved": "🟢", "distributed": "🔵"}.get(div.status, "⚪")

            with st.container():
                st.markdown(f"""
                <div style="padding:12px; background-color:#161b22; border-radius:8px; margin-bottom:10px; border-left:3px solid #00ff88;">
                    <strong>{div.symbol}</strong> {status_color} {div.amount_per_share:.2f} {div.currency}<br>
                    <small>Record: {div.record_date.strftime('%Y-%m-%d')} | Distribution: {div.distribution_date.strftime('%Y-%m-%d')}</small><br>
                    Type: {div.dividend_type} | Status: {div.status}
                </div>
                """, unsafe_allow_html=True)

        st.subheader("📅 Dividend Calendar")
        calendar = news_engine.get_dividend_calendar()
        for month, divs in sorted(calendar.items()):
            with st.expander(f"📅 {month} ({len(divs)} distributions)"):
                for div in divs:
                    st.write(f"• **{div.symbol}**: {div.amount_per_share:.2f} {div.currency} on {div.distribution_date.strftime('%Y-%m-%d')}")

# ============ PAGE: SETTINGS ============
def page_settings():
    st.title("⚙️ Settings")

    # Watchlist management
    st.subheader("📌 Watchlist")
    current = st.session_state.get("watchlist", [])
    watch_text = st.text_area(
        "Symbols (comma separated)", 
        value=", ".join(current), 
        key=get_key("set_watch")
    )
    if st.button("💾 Save Watchlist", key=get_key("set_save_watch"), use_container_width=True):
        new_list = [s.strip().upper() for s in watch_text.split(",") if s.strip()]
        st.session_state["watchlist"] = new_list
        st.toast(f"Watchlist updated: {len(new_list)} symbols", icon="💾")

    st.divider()

    # Theme settings
    st.subheader("🎨 Appearance")
    theme = st.radio(
        "Theme", 
        ["dark", "light"], 
        index=0 if st.session_state.get("theme") == "dark" else 1, 
        key=get_key("set_theme"), 
        horizontal=True
    )
    st.session_state["theme"] = theme

    st.divider()

    # Data refresh
    st.subheader("🔄 Data")
    if st.button("🔄 Refresh All Data", key=get_key("set_refresh"), use_container_width=True):
        st.session_state["last_update"] = pd.Timestamp.now().isoformat()
        st.toast("Data refreshed!", icon="🔄")

    st.divider()

    # Danger zone - SAFE reset
    st.subheader("⚠️ Danger Zone")

    if st.button("🗑️ Clear All Alerts", key=get_key("set_clear_alerts"), use_container_width=True):
        st.session_state["alerts"] = []
        st.toast("All alerts cleared", icon="🗑️")
        st.rerun()

    # CRITICAL: Safe reset - only delete user keys, preserve system keys
    if st.button("🏭 Reset to Defaults", key=get_key("set_reset"), use_container_width=True):
        # Preserve system keys that Streamlit needs
        preserve_keys = {
            "page", "_render_id", "_widget_counter", 
            "_st_session_state_initialized", "_streamlit_script_run_context"
        }

        # Only remove user-defined keys
        keys_to_remove = [
            k for k in list(st.session_state.keys()) 
            if k not in preserve_keys and not k.startswith("_")
        ]

        for k in keys_to_remove:
            del st.session_state[k]

        # Re-initialize defaults
        init_session_state()

        st.toast("Settings reset to defaults", icon="🏭")
        st.rerun()

# ============ MAIN APPLICATION ============
def main():
    """Main application entry point"""
    render_sidebar()

    # Route to current page
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
