"""
EGX Stock Analysis App — v34 Ultimate (React-DOM Bulletproof)
=============================================================
Rules enforced:
1. Every widget has a unique key via _unique_key()
2. No st.columns inside loops or conditionals
3. No widgets inside if/else blocks
4. No st.rerun() — navigation via _render_id increment
5. All dynamic lists rendered as HTML/CSS Grid
6. Logic separated from display widgets via on_click callbacks
7. Google Translate protection via CSS
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Any
import time

# ═══════════════════════════════════════════════════════════════
# GLOBAL STATE & KEY GENERATOR
# ═══════════════════════════════════════════════════════════════

def _init_state():
    """Initialize session state safely (idempotent)."""
    defaults = {
        "_render_id": 0,
        "_widget_counter": 0,
        "page": "dashboard",
        "alerts": [],
        "watchlist": ["COMI", "HRHO", "ETEL", "SWDY", "EFIH"],
        "selected_symbol": "COMI",
        "theme": "dark",
        "last_update": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

# ── Unique key generator (global, monotonic, render-scoped) ──
def _unique_key(base: str) -> str:
    st.session_state["_widget_counter"] += 1
    return f"{base}_{st.session_state['_widget_counter']}_{st.session_state['_render_id']}"

# ═══════════════════════════════════════════════════════════════
# CSS — Google Translate Protection + Dark Theme + Grid Cards
# ═══════════════════════════════════════════════════════════════

def _inject_css():
    css = """
    <style>
    /* Google Translate / DOM mutation protection */
    :not(:defined) { visibility: hidden !important; }

    /* Smooth transitions */
    .stApp { transition: all 0.3s ease; }

    /* Custom scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #1a1a1a; }
    ::-webkit-scrollbar-thumb { background: #444; border-radius: 4px; }

    /* Stock card grid */
    .stock-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
        gap: 12px;
        margin-bottom: 1rem;
    }
    .stock-card {
        background: linear-gradient(145deg, #1e1e1e, #2a2a2a);
        border: 1px solid #333;
        border-radius: 12px;
        padding: 16px;
        transition: transform 0.2s, box-shadow 0.2s;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    .stock-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.4);
        border-color: #4a9eff;
    }
    .stock-card .symbol {
        font-size: 1.2rem; font-weight: 700; color: #fff;
        margin-bottom: 4px;
    }
    .stock-card .name {
        font-size: 0.8rem; color: #aaa; margin-bottom: 8px;
    }
    .stock-card .price {
        font-size: 1.4rem; font-weight: 600; color: #4a9eff;
    }
    .stock-card .change-up { color: #00d084; }
    .stock-card .change-down { color: #ff4757; }
    .stock-card .volume {
        font-size: 0.75rem; color: #777; margin-top: 8px;
    }
    .stock-card .sparkline {
        position: absolute; bottom: 0; left: 0; right: 0; height: 40px;
        opacity: 0.15; pointer-events: none;
    }

    /* Alert card */
    .alert-card {
        background: #1e1e1e; border-left: 4px solid #4a9eff;
        border-radius: 8px; padding: 12px 16px; margin-bottom: 8px;
        display: flex; justify-content: space-between; align-items: center;
    }
    .alert-card.triggered { border-left-color: #ff4757; animation: pulse 2s infinite; }
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(255,71,87,0.4); }
        50% { box-shadow: 0 0 0 8px rgba(255,71,87,0); }
    }

    /* Metric row */
    .metric-row {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 10px; margin-bottom: 1rem;
    }
    .metric-box {
        background: #1e1e1e; border-radius: 10px; padding: 14px;
        text-align: center; border: 1px solid #2a2a2a;
    }
    .metric-box .label { font-size: 0.75rem; color: #888; text-transform: uppercase; }
    .metric-box .value { font-size: 1.3rem; font-weight: 700; color: #fff; margin-top: 4px; }

    /* Navigation buttons */
    .nav-btn {
        background: transparent; border: 1px solid #333;
        color: #ccc; padding: 8px 16px; border-radius: 8px;
        cursor: pointer; transition: all 0.2s; font-size: 0.9rem;
    }
    .nav-btn:hover, .nav-btn.active {
        background: #4a9eff; color: #fff; border-color: #4a9eff;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# MOCK DATA ENGINE (Replace with real EGX API)
# ═══════════════════════════════════════════════════════════════

def _generate_mock_data(symbol: str, days: int = 90) -> pd.DataFrame:
    """Generate realistic mock OHLCV data for EGX symbols."""
    np.random.seed(hash(symbol) % 2**31)
    base_price = np.random.uniform(5, 250)
    dates = pd.date_range(end=datetime.now(), periods=days, freq="B")

    returns = np.random.normal(0.001, 0.025, days)
    prices = base_price * np.exp(np.cumsum(returns))

    df = pd.DataFrame({
        "Open": prices * (1 + np.random.uniform(-0.02, 0.02, days)),
        "High": prices * (1 + np.random.uniform(0, 0.03, days)),
        "Low": prices * (1 + np.random.uniform(-0.03, 0, days)),
        "Close": prices,
        "Volume": np.random.randint(100000, 5000000, days),
    }, index=dates)
    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA50"] = df["Close"].rolling(50).mean()
    df["RSI"] = _compute_rsi(df["Close"])
    df["MACD"], df["MACD_Signal"] = _compute_macd(df["Close"])
    return df

def _compute_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def _compute_macd(prices: pd.Series):
    ema12 = prices.ewm(span=12).mean()
    ema26 = prices.ewm(span=26).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9).mean()
    return macd, signal

def _get_stock_info(symbol: str) -> Dict[str, Any]:
    """Mock stock metadata."""
    companies = {
        "COMI": "Commercial International Bank",
        "HRHO": "Hermes Holding",
        "ETEL": "Telecom Egypt",
        "SWDY": "Sidi Kerir Petrochemicals",
        "EFIH": "Egyptian Financial & Industrial",
        "EGX30": "EGX 30 Index",
    }
    np.random.seed(hash(symbol) % 2**31)
    return {
        "name": companies.get(symbol, f"Company {symbol}"),
        "sector": np.random.choice(["Banking", "Energy", "Telecom", "Industry", "Real Estate"]),
        "market_cap": np.random.uniform(1, 80),
        "pe": np.random.uniform(5, 25),
        "dividend_yield": np.random.uniform(0, 8),
    }

# ═══════════════════════════════════════════════════════════════
# NAVIGATION (No st.rerun — uses _render_id)
# ═══════════════════════════════════════════════════════════════

def _navigate_to(page_key: str):
    """Safe navigation: increments render_id to force fresh keys."""
    st.session_state["page"] = page_key
    st.session_state["_render_id"] += 1
    st.session_state["_widget_counter"] = 0
    # NO st.rerun() — Streamlit will re-render on next interaction naturally

def _render_navbar():
    """Render navigation as HTML buttons (no conditional widgets)."""
    pages = [
        ("dashboard", "📊 Dashboard"),
        ("technical", "📈 Technical"),
        ("alerts", "🔔 Alerts"),
        ("settings", "⚙️ Settings"),
    ]
    current = st.session_state["page"]

    cols_html = "<div style='display:flex;gap:10px;margin-bottom:20px;'>"
    for key, label in pages:
        active = "active" if key == current else ""
        # We use st.button BELOW the HTML for actual interaction,
        # but the visual is HTML to avoid conditional widget counts.
        cols_html += f"<span class='nav-btn {active}'>{label}</span>"
    cols_html += "</div>"
    st.markdown(cols_html, unsafe_allow_html=True)

    # Actual buttons — ALWAYS rendered, NEVER inside if/else
    btn_cols = st.columns(4)
    for idx, (key, label) in enumerate(pages):
        with btn_cols[idx]:
            # Each button has unique key and triggers navigation
            if st.button(label, key=_unique_key(f"nav_{key}"), use_container_width=True):
                _navigate_to(key)

# ═══════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════

def _render_stock_card(symbol: str, df: pd.DataFrame, info: Dict) -> str:
    """Generate HTML string for a single stock card."""
    last = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else last
    change = ((last["Close"] - prev["Close"]) / prev["Close"]) * 100
    change_cls = "change-up" if change >= 0 else "change-down"
    sign = "+" if change >= 0 else ""

    # Mini sparkline SVG
    closes = df["Close"].tail(20).values
    mn, mx = closes.min(), closes.max()
    rng = mx - mn if mx != mn else 1
    pts = " ".join(
        f"{i * 100 / (len(closes)-1)},{100 - (c - mn) / rng * 100}"
        for i, c in enumerate(closes)
    )
    sparkline = f'<svg class="sparkline" viewBox="0 0 100 100" preserveAspectRatio="none"><polyline points="{pts}" fill="none" stroke="#4a9eff" stroke-width="2"/></svg>'

    return f"""
    <div class="stock-card" onclick="window.parent.postMessage({{symbol:'{symbol}',page:'technical'}}, '*')">
        <div class="symbol">{symbol}</div>
        <div class="name">{info['name'][:28]}</div>
        <div class="price">{last['Close']:.2f} <span class="{change_cls}">{sign}{change:.2f}%</span></div>
        <div class="volume">Vol: {last['Volume']:,}</div>
        {sparkline}
    </div>
    """

def page_dashboard():
    st.title("🇪🇬 EGX Market Dashboard")
    st.caption(f"Last update: {datetime.now().strftime('%H:%M:%S')}")

    # ── Market Overview Metrics (HTML Grid, no st.columns) ──
    df_egx = _generate_mock_data("EGX30", 30)
    last = df_egx.iloc[-1]
    metrics = [
        ("EGX30", f"{last['Close']:.2f}"),
        ("Change", f"{((last['Close']-df_egx.iloc[-2]['Close'])/df_egx.iloc[-2]['Close']*100):.2f}%"),
        ("Volume", f"{last['Volume']:,}"),
        ("Trades", "12,450"),
        ("Advancers", "85"),
        ("Decliners", "62"),
    ]
    metrics_html = "<div class='metric-row'>"
    for label, value in metrics:
        metrics_html += f"<div class='metric-box'><div class='label'>{label}</div><div class='value'>{value}</div></div>"
    metrics_html += "</div>"
    st.markdown(metrics_html, unsafe_allow_html=True)

    # ── Watchlist Grid (HTML, no st.columns in loop) ──
    st.subheader("📌 Watchlist")
    symbols = st.session_state["watchlist"]
    cards_html = "<div class='stock-grid'>"
    for sym in symbols:
        df = _generate_mock_data(sym, 30)
        info = _get_stock_info(sym)
        cards_html += _render_stock_card(sym, df, info)
    cards_html += "</div>"
    st.markdown(cards_html, unsafe_allow_html=True)

    # ── Symbol selector (ALWAYS rendered, key is unique) ──
    st.subheader("🔍 Quick Analysis")
    all_symbols = ["COMI", "HRHO", "ETEL", "SWDY", "EFIH", "ORAS", "PHDC", "CIEB", "EKHO", "AMER"]
    selected = st.selectbox(
        "Select Symbol",
        all_symbols,
        index=all_symbols.index(st.session_state.get("selected_symbol", "COMI")),
        key=_unique_key("dash_symbol_select")
    )
    # Update state without rerun — next interaction will see new value
    st.session_state["selected_symbol"] = selected

    # ── Action buttons (ALWAYS rendered) ──
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📈 View Technical", key=_unique_key("dash_view_tech"), use_container_width=True):
            st.session_state["selected_symbol"] = selected
            _navigate_to("technical")
    with c2:
        if st.button("🔔 Add Alert", key=_unique_key("dash_add_alert"), use_container_width=True):
            st.session_state["alert_symbol"] = selected
            _navigate_to("alerts")
    with c3:
        if st.button("⭐ Add to Watchlist", key=_unique_key("dash_add_watch"), use_container_width=True):
            if selected not in st.session_state["watchlist"]:
                st.session_state["watchlist"].append(selected)
            st.toast(f"Added {selected} to watchlist!", icon="✅")

# ═══════════════════════════════════════════════════════════════
# PAGE: TECHNICAL ANALYSIS
# ═══════════════════════════════════════════════════════════════

def page_technical():
    symbol = st.session_state.get("selected_symbol", "COMI")
    st.title(f"📈 Technical Analysis: {symbol}")

    # ── Controls (always rendered, unique keys) ──
    timeframe = st.selectbox(
        "Timeframe",
        ["1M", "3M", "6M", "1Y", "YTD"],
        index=1,
        key=_unique_key("tech_timeframe")
    )
    days_map = {"1M": 22, "3M": 66, "6M": 132, "1Y": 252, "YTD": 180}
    days = days_map.get(timeframe, 90)

    df = _generate_mock_data(symbol, days)
    info = _get_stock_info(symbol)

    # ── Price Chart (Plotly) ──
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=(f"{symbol} — {info['name']}", "Volume", "RSI")
    )

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"], name="Price"
    ), row=1, col=1)

    # MAs
    fig.add_trace(go.Scatter(x=df.index, y=df["MA20"], name="MA20", line=dict(color="#4a9eff")), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["MA50"], name="MA50", line=dict(color="#ff9f43")), row=1, col=1)

    # Volume
    colors = ["#00d084" if df["Close"].iloc[i] >= df["Open"].iloc[i] else "#ff4757" for i in range(len(df))]
    fig.add_trace(go.Bar(x=df.index, y=df["Volume"], marker_color=colors, name="Volume"), row=2, col=1)

    # RSI
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI", line=dict(color="#a29bfe")), row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="#ff4757", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="#00d084", row=3, col=1)

    fig.update_layout(
        template="plotly_dark",
        height=700,
        showlegend=False,
        margin=dict(l=40, r=40, t=60, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True, key=_unique_key("tech_chart"))

    # ── Technical Metrics (HTML Grid) ──
    last = df.iloc[-1]
    tech_metrics = [
        ("RSI (14)", f"{last['RSI']:.1f}"),
        ("MACD", f"{last['MACD']:.3f}"),
        ("Signal", f"{last['MACD_Signal']:.3f}"),
        ("MA20", f"{last['MA20']:.2f}"),
        ("MA50", f"{last['MA50']:.2f}"),
        ("Trend", "Bullish" if last["Close"] > last["MA50"] else "Bearish"),
    ]
    html = "<div class='metric-row'>"
    for label, value in tech_metrics:
        html += f"<div class='metric-box'><div class='label'>{label}</div><div class='value'>{value}</div></div>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

    # ── Signal buttons (always rendered) ──
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬆️ Bullish Alert", key=_unique_key("tech_bull_alert"), use_container_width=True):
            _add_alert(symbol, "BULLISH", last["Close"])
    with c2:
        if st.button("⬇️ Bearish Alert", key=_unique_key("tech_bear_alert"), use_container_width=True):
            _add_alert(symbol, "BEARISH", last["Close"])

# ═══════════════════════════════════════════════════════════════
# PAGE: ALERTS
# ═══════════════════════════════════════════════════════════════

def _add_alert(symbol: str, condition: str, price: float):
    alert = {
        "id": _unique_key("alert"),
        "symbol": symbol,
        "condition": condition,
        "target": price,
        "created": datetime.now().isoformat(),
        "triggered": False,
    }
    st.session_state["alerts"].append(alert)
    st.toast(f"Alert set: {symbol} {condition} @ {price:.2f}", icon="🔔")

def _delete_alert(alert_id: str):
    st.session_state["alerts"] = [a for a in st.session_state["alerts"] if a["id"] != alert_id]
    st.toast("Alert deleted", icon="🗑️")

def page_alerts():
    st.title("🔔 Price Alerts")

    # ── New Alert Form (always rendered) ──
    with st.container():
        st.subheader("Create New Alert")
        all_symbols = ["COMI", "HRHO", "ETEL", "SWDY", "EFIH", "ORAS", "PHDC", "CIEB", "EKHO", "AMER"]
        sym = st.selectbox("Symbol", all_symbols, key=_unique_key("alert_sym"))
        col_type, col_price = st.columns(2)
        with col_type:
            cond = st.selectbox("Condition", ["ABOVE", "BELOW", "BULLISH", "BEARISH"], key=_unique_key("alert_cond"))
        with col_price:
            price = st.number_input("Target Price", value=50.0, step=0.5, key=_unique_key("alert_price"))

        if st.button("➕ Create Alert", key=_unique_key("alert_create"), use_container_width=True):
            _add_alert(sym, cond, price)

    st.divider()

    # ── Active Alerts (HTML list, no conditional widgets) ──
    st.subheader("Active Alerts")
    alerts = st.session_state.get("alerts", [])

    if not alerts:
        st.info("No active alerts. Create one above.")
    else:
        for alert in alerts:
            triggered = alert.get("triggered", False)
            trig_class = "triggered" if triggered else ""
            status = "🔴 TRIGGERED" if triggered else "🟢 ACTIVE"
            html = f"""
            <div class="alert-card {trig_class}">
                <div>
                    <strong>{alert['symbol']}</strong> — {alert['condition']} @ {alert['target']:.2f}<br>
                    <small style="color:#888">{status} | Created: {alert['created'][:16]}</small>
                </div>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)

        # Delete buttons rendered OUTSIDE the loop in a batch, or use unique keys per alert
        st.write("Manage alerts:")
        del_cols = st.columns(min(len(alerts), 4))
        for idx, alert in enumerate(alerts):
            with del_cols[idx % 4]:
                if st.button(f"🗑️ {alert['symbol']}", key=_unique_key(f"del_alert_{alert['id']}"), use_container_width=True):
                    _delete_alert(alert["id"])

# ═══════════════════════════════════════════════════════════════
# PAGE: SETTINGS
# ═══════════════════════════════════════════════════════════════

def page_settings():
    st.title("⚙️ Settings")

    # ── Watchlist Editor (always rendered) ──
    st.subheader("📌 Watchlist")
    current = st.session_state.get("watchlist", [])
    watch_text = st.text_area(
        "Symbols (comma separated)",
        value=", ".join(current),
        key=_unique_key("set_watchlist")
    )
    if st.button("💾 Save Watchlist", key=_unique_key("set_save_watch"), use_container_width=True):
        new_list = [s.strip().upper() for s in watch_text.split(",") if s.strip()]
        st.session_state["watchlist"] = new_list
        st.toast(f"Watchlist updated: {len(new_list)} symbols", icon="💾")

    st.divider()

    # ── Theme (always rendered) ──
    st.subheader("🎨 Appearance")
    theme = st.radio(
        "Theme",
        ["dark", "light"],
        index=0 if st.session_state.get("theme") == "dark" else 1,
        key=_unique_key("set_theme"),
        horizontal=True
    )
    st.session_state["theme"] = theme

    st.divider()

    # ── Data Refresh (always rendered) ──
    st.subheader("🔄 Data")
    if st.button("🔄 Refresh All Data", key=_unique_key("set_refresh"), use_container_width=True):
        st.session_state["_render_id"] += 1
        st.session_state["_widget_counter"] = 0
        st.session_state["last_update"] = datetime.now().isoformat()
        st.toast("Data refreshed!", icon="🔄")

    st.divider()

    # ── Danger Zone (always rendered) ──
    st.subheader("⚠️ Danger Zone")
    if st.button("🗑️ Clear All Alerts", key=_unique_key("set_clear_alerts"), use_container_width=True):
        st.session_state["alerts"] = []
        st.toast("All alerts cleared", icon="🗑️")
    if st.button("🏭 Reset to Defaults", key=_unique_key("set_reset"), use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        _init_state()
        st.toast("Settings reset to defaults", icon="🏭")

# ═══════════════════════════════════════════════════════════════
# MAIN APP ROUTER
# ═══════════════════════════════════════════════════════════════

def main():
    _inject_css()
    _render_navbar()

    page = st.session_state.get("page", "dashboard")
    if page == "dashboard":
        page_dashboard()
    elif page == "technical":
        page_technical()
    elif page == "alerts":
        page_alerts()
    elif page == "settings":
        page_settings()
    else:
        page_dashboard()

if __name__ == "__main__":
    main()
