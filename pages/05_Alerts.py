"""
EGX Pro Terminal - Alerts Page
"""

import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.egx_symbols import get_stock_info, get_all_symbols
from core.alerts import AlertEngine
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Alerts", page_icon="🔔", layout="wide")

alert_eng = AlertEngine()

st.title("🔔 Smart Alerts")

# Create Alert Section
st.subheader("➕ Create New Alert")

all_syms = get_all_symbols()[:50]
if "alert_symbol" not in st.session_state:
    st.session_state["alert_symbol"] = "COMI"

col1, col2, col3 = st.columns(3)
with col1:
    symbol = st.selectbox("Symbol", all_syms, 
                         index=all_syms.index(st.session_state["alert_symbol"]) if st.session_state["alert_symbol"] in all_syms else 0,
                         key="alert_sym_select")
    st.session_state["alert_symbol"] = symbol
with col2:
    alert_type = st.selectbox("Alert Type", [
        "PRICE_ABOVE", "PRICE_BELOW", "RSI_OVERBOUGHT", "RSI_OVERSOLD",
        "MACD_BULLISH", "MACD_BEARISH", "EMA_CROSSOVER", "VOLUME_SPIKE",
        "BOLLINGER_BREAKOUT", "SUPPORT_BREAK", "RESISTANCE_BREAK"
    ], key="alert_type")
with col3:
    if alert_type in ["PRICE_ABOVE", "PRICE_BELOW"]:
        target = st.number_input("Target Price", value=50.0, step=0.5, key="alert_target")
    else:
        target = st.number_input("Sensitivity", value=1.0, step=0.1, key="alert_sens")

severity = st.select_slider("Severity", options=["LOW", "MEDIUM", "HIGH", "CRITICAL"], value="MEDIUM", key="alert_severity")

if st.button("🚀 Create Alert", use_container_width=True):
    alert = {
        "id": f"alert_{datetime.now().strftime('%Y%m%d%H%M%S')}_{symbol}",
        "symbol": symbol,
        "type": alert_type,
        "target": target,
        "severity": severity,
        "created": datetime.now().isoformat(),
        "triggered": False,
        "triggered_at": None
    }
    if "alerts" not in st.session_state:
        st.session_state["alerts"] = []
    st.session_state["alerts"].append(alert)
    st.success(f"✅ Alert created for {symbol}: {alert_type}")

st.divider()

# Active Alerts
st.subheader("📋 Active Alerts")

if "alerts" not in st.session_state or not st.session_state["alerts"]:
    st.info("No active alerts. Create one above.")
else:
    alerts = st.session_state["alerts"]

    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        filter_status = st.selectbox("Filter by Status", ["ALL", "ACTIVE", "TRIGGERED"], key="alert_filter_status")
    with col2:
        filter_sym = st.selectbox("Filter by Symbol", ["ALL"] + list(set(a["symbol"] for a in alerts)), key="alert_filter_sym")

    filtered = alerts
    if filter_status == "ACTIVE":
        filtered = [a for a in filtered if not a["triggered"]]
    elif filter_status == "TRIGGERED":
        filtered = [a for a in filtered if a["triggered"]]
    if filter_sym != "ALL":
        filtered = [a for a in filtered if a["symbol"] == filter_sym]

    for alert in filtered:
        triggered = alert.get("triggered", False)
        severity_colors = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🟠", "CRITICAL": "🔴"}
        status_emoji = "🔴" if triggered else "🟢"
        sev_emoji = severity_colors.get(alert.get("severity", "MEDIUM"), "🟡")

        with st.container():
            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
            with col1:
                st.write(f"**{alert['symbol']}**")
            with col2:
                st.write(f"{alert['type']}")
            with col3:
                st.write(f"Target: {alert['target']}")
            with col4:
                st.write(f"{sev_emoji} {alert.get('severity', 'MEDIUM')}")
            with col5:
                st.write(f"{status_emoji}")

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(f"🗑️ Delete", key=f"del_{alert['id']}", use_container_width=True):
                    st.session_state["alerts"] = [a for a in st.session_state["alerts"] if a["id"] != alert["id"]]
                    st.rerun()
            with col2:
                if not triggered and st.button(f"🔔 Test", key=f"test_{alert['id']}", use_container_width=True):
                    st.toast(f"Test notification for {alert['symbol']}", icon="🔔")
        st.divider()

# Alert Statistics
if "alerts" in st.session_state and st.session_state["alerts"]:
    st.subheader("📊 Alert Statistics")
    total = len(st.session_state["alerts"])
    triggered = len([a for a in st.session_state["alerts"] if a["triggered"]])
    active = total - triggered

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Alerts", total)
    with col2:
        st.metric("Active", active)
    with col3:
        st.metric("Triggered", triggered)
