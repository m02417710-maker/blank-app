"""
EGX Pro Terminal v34 Ultimate
Main Streamlit Application Entry Point
React-DOM Safe | No st.rerun | Unique Keys
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def _init_session_state():
    defaults = {
        "_render_id": 0,
        "_widget_counter": 0,
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
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_session_state()

def _unique_key(base: str) -> str:
    st.session_state["_widget_counter"] += 1
    return f"{base}_{st.session_state['_widget_counter']}_{st.session_state['_render_id']}"

def _inject_css():
    css = """
    <style>
    :not(:defined) { visibility: hidden !important; }
    .stApp { transition: all 0.3s ease; }
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #1a1a1a; }
    ::-webkit-scrollbar-thumb { background: #444; border-radius: 4px; }
    .stock-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; margin-bottom: 1rem; }
    .stock-card { background: linear-gradient(145deg, #1e1e1e, #2a2a2a); border: 1px solid #333; border-radius: 12px; padding: 16px; transition: transform 0.2s, box-shadow 0.2s; cursor: pointer; position: relative; overflow: hidden; }
    .stock-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,0.4); border-color: #4a9eff; }
    .stock-card .symbol { font-size: 1.2rem; font-weight: 700; color: #fff; margin-bottom: 4px; }
    .stock-card .name { font-size: 0.8rem; color: #aaa; margin-bottom: 8px; }
    .stock-card .price { font-size: 1.4rem; font-weight: 600; color: #4a9eff; }
    .stock-card .change-up { color: #00d084; }
    .stock-card .change-down { color: #ff4757; }
    .stock-card .volume { font-size: 0.75rem; color: #777; margin-top: 8px; }
    .metric-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; margin-bottom: 1rem; }
    .metric-box { background: #1e1e1e; border-radius: 10px; padding: 14px; text-align: center; border: 1px solid #2a2a2a; }
    .metric-box .label { font-size: 0.75rem; color: #888; text-transform: uppercase; }
    .metric-box .value { font-size: 1.3rem; font-weight: 700; color: #fff; margin-top: 4px; }
    .alert-card { background: #1e1e1e; border-left: 4px solid #4a9eff; border-radius: 8px; padding: 12px 16px; margin-bottom: 8px; }
    .alert-card.triggered { border-left-color: #ff4757; }
    .news-card { background: #1e1e1e; border-radius: 10px; padding: 16px; margin-bottom: 10px; border-left: 3px solid #4a9eff; }
    .news-card.high { border-left-color: #ff4757; }
    .news-card.medium { border-left-color: #ffa502; }
    .news-card.low { border-left-color: #2ed573; }
    .news-card .title { font-size: 1rem; font-weight: 600; color: #fff; margin-bottom: 4px; }
    .news-card .meta { font-size: 0.75rem; color: #888; }
    .news-card .content { font-size: 0.85rem; color: #ccc; margin-top: 8px; }
    .dividend-card { background: linear-gradient(145deg, #1e1e1e, #2a2a2a); border: 1px solid #333; border-radius: 10px; padding: 14px; margin-bottom: 8px; }
    .dividend-card .symbol { font-weight: 700; color: #4a9eff; }
    .dividend-card .amount { font-size: 1.2rem; font-weight: 600; color: #00d084; }
    .dividend-card .date { font-size: 0.8rem; color: #888; }
    .nav-btn { background: transparent; border: 1px solid #333; color: #ccc; padding: 8px 16px; border-radius: 8px; cursor: pointer; transition: all 0.2s; font-size: 0.9rem; }
    .nav-btn:hover, .nav-btn.active { background: #4a9eff; color: #fff; border-color: #4a9eff; }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def _navigate_to(page_key: str):
    st.session_state["page"] = page_key
    st.session_state["_render_id"] += 1
    st.session_state["_widget_counter"] = 0

def _render_navbar():
    pages = [
        ("dashboard", "📊 Dashboard"),
        ("technical", "📈 Technical"),
        ("ai_predictions", "🤖 AI"),
        ("backtest", "📊 Backtest"),
        ("alerts", "🔔 Alerts"),
        ("news", "📰 News"),
        ("settings", "⚙️ Settings"),
    ]
    current = st.session_state["page"]
    cols_html = "<div style='display:flex;gap:10px;margin-bottom:20px;'>"
    for key, label in pages:
        active = "active" if key == current else ""
        cols_html += f"<span class='nav-btn {active}'>{label}</span>"
    cols_html += "</div>"
    st.markdown(cols_html, unsafe_allow_html=True)
    btn_cols = st.columns(7)
    for idx, (key, label) in enumerate(pages):
        with btn_cols[idx]:
            if st.button(label, key=_unique_key(f"nav_{key}"), use_container_width=True):
                _navigate_to(key)

import pandas as pd
import numpy as np
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
    return f'''<div class="stock-card"><div class="symbol">{symbol}</div><div class="name">{info.name[:28] if info else symbol}</div><div class="price">{last['close']:.2f} <span class="{change_cls}">{sign}{change:.2f}%</span></div><div class="volume">Vol: {last['volume']:,}</div>{sparkline}</div>'''

def page_dashboard():
    st.title("🇪🇬 EGX Pro Terminal")
    st.caption(f"Last update: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    stats = get_market_stats()
    metrics = [
        ("Companies", f"{stats['total_companies']}"),
        ("Market Cap", f"{stats['total_market_cap_egp_billions']:.1f}B EGP"),
        ("Avg P/E", f"{stats['avg_pe_ratio']}"),
        ("Avg Div Yield", f"{stats['avg_dividend_yield']:.1f}%"),
        ("Sectors", f"{stats['total_sectors']}"),
        ("Blue Chips", f"{stats['blue_chips']}"),
    ]
    html = "<div class='metric-row'>"
    for label, value in metrics:
        html += f"<div class='metric-box'><div class='label'>{label}</div><div class='value'>{value}</div></div>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)
    st.subheader("📌 Watchlist")
    symbols = st.session_state["watchlist"]
    cards_html = "<div class='stock-grid'>"
    for sym in symbols:
        df = generate_mock_data(sym, 30)
        info = get_stock_info(sym)
        cards_html += _render_stock_card(sym, df, info)
    cards_html += "</div>"
    st.markdown(cards_html, unsafe_allow_html=True)
    st.subheader("🔍 Quick Analysis")
    all_syms = get_all_symbols()[:50]
    sel_idx = all_syms.index(st.session_state["selected_symbol"]) if st.session_state["selected_symbol"] in all_syms else 0
    selected = st.selectbox("Select Symbol", all_syms, index=sel_idx, key=_unique_key("dash_symbol"))
    st.session_state["selected_symbol"] = selected
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📈 View Technical", key=_unique_key("dash_tech"), use_container_width=True):
            _navigate_to("technical")
    with c2:
        if st.button("🔔 Add Alert", key=_unique_key("dash_alert"), use_container_width=True):
            st.session_state["alert_symbol"] = selected
            _navigate_to("alerts")
    with c3:
        if st.button("⭐ Add to Watchlist", key=_unique_key("dash_watch"), use_container_width=True):
            if selected not in st.session_state["watchlist"]:
                st.session_state["watchlist"].append(selected)
            st.toast(f"Added {selected} to watchlist!", icon="✅")

def page_technical():
    symbol = st.session_state.get("selected_symbol", "COMI")
    st.title(f"📈 Technical Analysis: {symbol}")
    timeframe = st.selectbox("Timeframe", ["1M", "3M", "6M", "1Y", "YTD"], index=1, key=_unique_key("tech_timeframe"))
    days_map = {"1M": 22, "3M": 66, "6M": 132, "1Y": 252, "YTD": 180}
    days = days_map.get(timeframe, 90)
    df = generate_mock_data(symbol, days)
    info = get_stock_info(symbol)
    fig = charts.create_candlestick_chart(df, symbol, info.name if info else symbol)
    st.plotly_chart(fig, use_container_width=True, key=_unique_key("tech_chart"))
    last = df.iloc[-1]
    indicators = ta.calculate_all_indicators(df)
    tech_metrics = [
        ("RSI (14)", f"{indicators.get('rsi', 0):.1f}"),
        ("MACD", f"{indicators.get('macd', 0):.3f}"),
        ("Signal", f"{indicators.get('macd_signal', 0):.3f}"),
        ("MA20", f"{indicators.get('sma20', 0):.2f}"),
        ("MA50", f"{indicators.get('sma50', 0):.2f}"),
        ("Trend", "Bullish" if last["close"] > indicators.get("sma50", last["close"]) else "Bearish"),
    ]
    html = "<div class='metric-row'>"
    for label, value in tech_metrics:
        html += f"<div class='metric-box'><div class='label'>{label}</div><div class='value'>{value}</div></div>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)
    patterns = pattern_engine.get_pattern_summary(df)
    if patterns["total"] > 0:
        st.subheader("🔍 Pattern Detection")
        st.write(f"Bullish: {patterns['bullish_count']} | Bearish: {patterns['bearish_count']} | Latest: {patterns['latest_signal']}")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬆️ Bullish Alert", key=_unique_key("tech_bull"), use_container_width=True):
            st.toast(f"Bullish alert set for {symbol}", icon="📈")
    with c2:
        if st.button("⬇️ Bearish Alert", key=_unique_key("tech_bear"), use_container_width=True):
            st.toast(f"Bearish alert set for {symbol}", icon="📉")

def page_ai():
    symbol = st.session_state.get("selected_symbol", "COMI")
    st.title(f"🤖 AI Predictions: {symbol}")
    df = generate_mock_data(symbol, 252)
    model = st.selectbox("AI Model", ["ensemble", "monte_carlo", "technical", "sentiment"], index=0, key=_unique_key("ai_model"))
    if st.button("🚀 Generate Prediction", key=_unique_key("ai_run"), use_container_width=True):
        with st.spinner("Running AI analysis..."):
            prediction = ai.predict(df, model_type=model)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Bullish Probability", f"{prediction.get('bullish_prob', 0)*100:.1f}%")
            with col2:
                st.metric("Bearish Probability", f"{prediction.get('bearish_prob', 0)*100:.1f}%")
            with col3:
                st.metric("Neutral Probability", f"{prediction.get('neutral_prob', 0)*100:.1f}%")
            st.subheader("📊 Signal Breakdown")
            for signal in prediction.get("signals", []):
                st.write(f"• {signal}")
            st.subheader("🎯 Recommendation")
            rec = prediction.get("recommendation", "HOLD")
            color = {"BUY": "green", "SELL": "red", "HOLD": "orange"}.get(rec, "gray")
            st.markdown(f"<h2 style='color:{color};text-align:center'>{rec}</h2>", unsafe_allow_html=True)

def page_backtest():
    symbol = st.session_state.get("selected_symbol", "COMI")
    st.title(f"📊 Strategy Backtest: {symbol}")
    strategy = st.selectbox("Strategy", ["trend_following", "mean_reversion", "momentum", "breakout", "rsi_strategy", "macd_strategy", "bollinger_strategy", "ml_strategy"], index=0, key=_unique_key("bt_strategy"))
    col1, col2 = st.columns(2)
    with col1:
        initial_capital = st.number_input("Initial Capital (EGP)", value=100000, step=10000, key=_unique_key("bt_capital"))
    with col2:
        days = st.number_input("Backtest Period (days)", value=252, step=30, key=_unique_key("bt_days"))
    if st.button("▶️ Run Backtest", key=_unique_key("bt_run"), use_container_width=True):
        with st.spinner("Running backtest..."):
            df = generate_mock_data(symbol, days)
            result = bt.run_backtest(df, strategy, initial_capital)
            st.subheader("📈 Performance Summary")
            metrics = result.get("summary", {})
            perf_html = "<div class='metric-row'>"
            perf_metrics = [
                ("Total Return", f"{metrics.get('total_return', 0)*100:.2f}%"),
                ("Annual Return", f"{metrics.get('annual_return', 0)*100:.2f}%"),
                ("Sharpe Ratio", f"{metrics.get('sharpe_ratio', 0):.2f}"),
                ("Max Drawdown", f"{metrics.get('max_drawdown', 0)*100:.2f}%"),
                ("Win Rate", f"{metrics.get('win_rate', 0)*100:.1f}%"),
                ("Trades", f"{metrics.get('total_trades', 0)}"),
            ]
            for label, value in perf_metrics:
                perf_html += f"<div class='metric-box'><div class='label'>{label}</div><div class='value'>{value}</div></div>"
            perf_html += "</div>"
            st.markdown(perf_html, unsafe_allow_html=True)
            st.info("Equity curve visualization available in full version")

def _add_alert(symbol, condition, price):
    alert = {"id": _unique_key("alert"), "symbol": symbol, "condition": condition, "target": price, "created": pd.Timestamp.now().isoformat(), "triggered": False}
    st.session_state["alerts"].append(alert)
    st.toast(f"Alert set: {symbol} {condition} @ {price:.2f}", icon="🔔")

def _delete_alert(alert_id):
    st.session_state["alerts"] = [a for a in st.session_state["alerts"] if a["id"] != alert_id]
    st.toast("Alert deleted", icon="🗑️")

def page_alerts():
    st.title("🔔 Price Alerts")
    st.subheader("Create New Alert")
    all_syms = get_all_symbols()[:50]
    sym = st.selectbox("Symbol", all_syms, key=_unique_key("alert_sym"))
    col_type, col_price = st.columns(2)
    with col_type:
        cond = st.selectbox("Condition", ["ABOVE", "BELOW", "BULLISH", "BEARISH"], key=_unique_key("alert_cond"))
    with col_price:
        price = st.number_input("Target Price", value=50.0, step=0.5, key=_unique_key("alert_price"))
    if st.button("➕ Create Alert", key=_unique_key("alert_create"), use_container_width=True):
        _add_alert(sym, cond, price)
    st.divider()
    st.subheader("Active Alerts")
    alerts = st.session_state.get("alerts", [])
    if not alerts:
        st.info("No active alerts. Create one above.")
    else:
        for alert in alerts:
            triggered = alert.get("triggered", False)
            trig_class = "triggered" if triggered else ""
            status = "🔴 TRIGGERED" if triggered else "🟢 ACTIVE"
            html = f'''<div class="alert-card {trig_class}"><div><strong>{alert['symbol']}</strong> — {alert['condition']} @ {alert['target']:.2f}<br><small style="color:#888">{status} | Created: {alert['created'][:16]}</small></div></div>'''
            st.markdown(html, unsafe_allow_html=True)
        st.write("Manage alerts:")
        del_cols = st.columns(min(len(alerts), 4))
        for idx, alert in enumerate(alerts):
            with del_cols[idx % 4]:
                if st.button(f"🗑️ {alert['symbol']}", key=_unique_key(f"del_alert_{alert['id']}"), use_container_width=True):
                    _delete_alert(alert["id"])

def _time_ago(dt):
    from datetime import datetime
    diff = datetime.now() - dt
    if diff.days > 0:
        return f"{diff.days}d ago"
    hours = diff.seconds // 3600
    if hours > 0:
        return f"{hours}h ago"
    return f"{(diff.seconds % 3600) // 60}m ago"

def page_news():
    st.title("📰 Market News & Dividends")
    tab1, tab2 = st.tabs(["📰 News", "💰 Dividends"])
    with tab1:
        st.subheader("Latest Market News")
        filter_cat = st.selectbox("Filter by Category", ["all", "earnings", "dividend", "ipo", "market_update", "economic"], key=_unique_key("news_filter"))
        news_items = news_engine.get_all_news(20)
        if filter_cat != "all":
            cat_map = {"earnings": NewsCategory.EARNINGS, "dividend": NewsCategory.DIVIDEND, "ipo": NewsCategory.IPO, "market_update": NewsCategory.MARKET_UPDATE, "economic": NewsCategory.ECONOMIC}
            news_items = [n for n in news_items if n.category == cat_map.get(filter_cat)]
        for news in news_items:
            priority_class = news.priority.value
            time_ago = _time_ago(news.published_at)
            html = f'''<div class="news-card {priority_class}"><div class="title">{news.title}</div><div class="meta">{news.source} • {time_ago} • {news.category.value}</div><div class="content">{news.content[:200]}...</div></div>'''
            st.markdown(html, unsafe_allow_html=True)
    with tab2:
        st.subheader("💰 Dividend Distributions")
        dividends = news_engine.get_dividends()
        for div in dividends:
            status_color = {"announced": "🟡", "approved": "🟢", "distributed": "🔵"}.get(div.status, "⚪")
            html = f'''<div class="dividend-card"><div style="display:flex;justify-content:space-between;align-items:center"><span class="symbol">{div.symbol}</span><span class="amount">{status_color} {div.amount_per_share:.2f} {div.currency}</span></div><div class="date">Record: {div.record_date.strftime('%Y-%m-%d')} | Distribution: {div.distribution_date.strftime('%Y-%m-%d')}</div><div style="font-size:0.8rem;color:#888">Type: {div.dividend_type} | Status: {div.status}</div></div>'''
            st.markdown(html, unsafe_allow_html=True)
        st.subheader("📅 Dividend Calendar")
        calendar = news_engine.get_dividend_calendar()
        for month, divs in sorted(calendar.items()):
            with st.expander(f"📅 {month} ({len(divs)} distributions)"):
                for div in divs:
                    st.write(f"• **{div.symbol}**: {div.amount_per_share:.2f} {div.currency} on {div.distribution_date.strftime('%Y-%m-%d')}")

def page_settings():
    st.title("⚙️ Settings")
    st.subheader("📌 Watchlist")
    current = st.session_state.get("watchlist", [])
    watch_text = st.text_area("Symbols (comma separated)", value=", ".join(current), key=_unique_key("set_watch"))
    if st.button("💾 Save Watchlist", key=_unique_key("set_save_watch"), use_container_width=True):
        new_list = [s.strip().upper() for s in watch_text.split(",") if s.strip()]
        st.session_state["watchlist"] = new_list
        st.toast(f"Watchlist updated: {len(new_list)} symbols", icon="💾")
    st.divider()
    st.subheader("🎨 Appearance")
    theme = st.radio("Theme", ["dark", "light"], index=0 if st.session_state.get("theme") == "dark" else 1, key=_unique_key("set_theme"), horizontal=True)
    st.session_state["theme"] = theme
    st.divider()
    st.subheader("🔄 Data")
    if st.button("🔄 Refresh All Data", key=_unique_key("set_refresh"), use_container_width=True):
        st.session_state["_render_id"] += 1
        st.session_state["_widget_counter"] = 0
        st.session_state["last_update"] = pd.Timestamp.now().isoformat()
        st.toast("Data refreshed!", icon="🔄")
    st.divider()
    st.subheader("⚠️ Danger Zone")
    if st.button("🗑️ Clear All Alerts", key=_unique_key("set_clear_alerts"), use_container_width=True):
        st.session_state["alerts"] = []
        st.toast("All alerts cleared", icon="🗑️")
    if st.button("🏭 Reset to Defaults", key=_unique_key("set_reset"), use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        _init_session_state()
        st.toast("Settings reset to defaults", icon="🏭")

def main():
    _inject_css()
    _render_navbar()
    page = st.session_state.get("page", "dashboard")
    pages = {"dashboard": page_dashboard, "technical": page_technical, "ai_predictions": page_ai, "backtest": page_backtest, "alerts": page_alerts, "news": page_news, "settings": page_settings}
    page_func = pages.get(page, page_dashboard)
    page_func()

if __name__ == "__main__":
    main()
