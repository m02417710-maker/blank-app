"""
EGX Pro Terminal - Settings Page
"""

import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.egx_symbols import get_all_symbols, get_sector_list
import pandas as pd

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

st.title("⚙️ Settings & Configuration")

tab1, tab2, tab3, tab4 = st.tabs(["📌 Watchlist", "🎨 Appearance", "🔔 Notifications", "⚠️ Danger Zone"])

with tab1:
    st.subheader("📌 Your Watchlist")
    if "watchlist" not in st.session_state:
        st.session_state["watchlist"] = ["COMI", "HRHO", "ETEL", "SWDY", "EAST"]

    current = st.session_state["watchlist"]
    watch_text = st.text_area("Edit Watchlist (comma separated)", value=", ".join(current), key="set_watch_text")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Watchlist", use_container_width=True):
            new_list = [s.strip().upper() for s in watch_text.split(",") if s.strip()]
            st.session_state["watchlist"] = new_list
            st.success(f"✅ Watchlist updated: {len(new_list)} symbols")
    with col2:
        if st.button("🔄 Reset to Default", use_container_width=True):
            st.session_state["watchlist"] = ["COMI", "HRHO", "ETEL", "SWDY", "EAST"]
            st.success("✅ Watchlist reset to default")

    st.write("**Current Watchlist:**")
    st.write(", ".join(st.session_state["watchlist"]))

    # Quick add
    st.subheader("➕ Quick Add Symbols")
    all_syms = get_all_symbols()[:100]
    selected_to_add = st.multiselect("Select symbols to add", all_syms, key="set_quick_add")
    if st.button("➕ Add Selected", use_container_width=True):
        for sym in selected_to_add:
            if sym not in st.session_state["watchlist"]:
                st.session_state["watchlist"].append(sym)
        st.success(f"✅ Added {len(selected_to_add)} symbols")

with tab2:
    st.subheader("🎨 Appearance Settings")

    theme = st.radio("Theme", ["dark", "light"], 
                    index=0 if st.session_state.get("theme", "dark") == "dark" else 1,
                    key="set_theme", horizontal=True)
    st.session_state["theme"] = theme

    chart_style = st.selectbox("Chart Style", ["candlestick", "heikin_ashi", "line", "area"], key="set_chart_style")

    color_scheme = st.selectbox("Color Scheme", ["default", "green_red", "blue_orange", "monochrome"], key="set_colors")

    if st.button("💾 Save Appearance", use_container_width=True):
        st.success("✅ Appearance settings saved")

    st.subheader("📊 Default Timeframe")
    default_tf = st.select_slider("Default Chart Timeframe", 
                                  options=["1D", "1W", "1M", "3M", "6M", "1Y", "YTD", "MAX"],
                                  value="3M", key="set_default_tf")

with tab3:
    st.subheader("🔔 Notification Settings")

    st.write("**Alert Delivery Methods**")
    email_alerts = st.toggle("Email Alerts", value=False, key="set_email")
    telegram_alerts = st.toggle("Telegram Alerts", value=False, key="set_telegram")
    push_alerts = st.toggle("Browser Push Notifications", value=True, key="set_push")

    if email_alerts:
        st.text_input("Email Address", key="set_email_addr")

    if telegram_alerts:
        st.text_input("Telegram Bot Token", type="password", key="set_tg_token")
        st.text_input("Chat ID", key="set_tg_chat")

    st.write("**Alert Frequency**")
    alert_freq = st.select_slider("Check Frequency", 
                                 options=["1min", "5min", "15min", "30min", "1h", "4h", "1d"],
                                 value="15min", key="set_alert_freq")

    st.write("**Quiet Hours**")
    quiet_start = st.time_input("Quiet Hours Start", value=pd.Timestamp("22:00").time(), key="set_quiet_start")
    quiet_end = st.time_input("Quiet Hours End", value=pd.Timestamp("08:00").time(), key="set_quiet_end")

    if st.button("💾 Save Notification Settings", use_container_width=True):
        st.success("✅ Notification settings saved")

with tab4:
    st.subheader("⚠️ Danger Zone")
    st.warning("These actions cannot be undone!")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear All Alerts", use_container_width=True):
            if "alerts" in st.session_state:
                st.session_state["alerts"] = []
            st.success("✅ All alerts cleared")
    with col2:
        if st.button("🗑️ Clear Watchlist", use_container_width=True):
            st.session_state["watchlist"] = []
            st.success("✅ Watchlist cleared")

    st.divider()

    if st.button("🏭 Reset All Settings to Default", use_container_width=True):
        keys_to_keep = ["_render_id", "_widget_counter"]
        for k in list(st.session_state.keys()):
            if k not in keys_to_keep:
                del st.session_state[k]
        st.session_state["watchlist"] = ["COMI", "HRHO", "ETEL", "SWDY", "EAST"]
        st.session_state["alerts"] = []
        st.session_state["theme"] = "dark"
        st.success("✅ All settings reset to default")

    st.divider()

    st.subheader("📊 Data Management")
    if st.button("🔄 Clear Cache & Refresh", use_container_width=True):
        st.session_state["_render_id"] += 1
        st.session_state["_widget_counter"] = 0
        st.success("✅ Cache cleared and refreshed")

    if st.button("📥 Export All Data", use_container_width=True):
        st.info("Export feature will be available in the next update")
