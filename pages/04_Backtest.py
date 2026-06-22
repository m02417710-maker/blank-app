"""
EGX Pro Terminal - Backtesting Page
"""

import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.egx_symbols import get_stock_info, get_all_symbols
from data.market_data import generate_mock_data
from core.backtest import BacktestEngine
import pandas as pd

st.set_page_config(page_title="Backtest", page_icon="📊", layout="wide")

bt = BacktestEngine()

st.title("📊 Strategy Backtesting")

all_syms = get_all_symbols()[:50]
if "selected_symbol" not in st.session_state:
    st.session_state["selected_symbol"] = "COMI"

symbol = st.selectbox("Select Symbol", all_syms,
                     index=all_syms.index(st.session_state["selected_symbol"]) if st.session_state["selected_symbol"] in all_syms else 0,
                     key="bt_symbol")
st.session_state["selected_symbol"] = symbol

strategy = st.selectbox("Strategy", [
    "trend_following", "mean_reversion", "momentum", "breakout",
    "rsi_strategy", "macd_strategy", "bollinger_strategy", "ml_strategy"
], key="bt_strategy")

col1, col2, col3 = st.columns(3)
with col1:
    initial_capital = st.number_input("Initial Capital (EGP)", value=100000, step=10000, key="bt_capital")
with col2:
    days = st.number_input("Backtest Period (days)", value=252, step=30, key="bt_days")
with col3:
    position_size = st.slider("Position Size (%)", 10, 100, 50, key="bt_position")

if st.button("▶️ Run Backtest", use_container_width=True):
    with st.spinner("Running backtest simulation..."):
        df = generate_mock_data(symbol, days)
        result = bt.run_backtest(df, strategy, initial_capital)

        st.success("Backtest Complete!")

        # Performance Metrics
        st.subheader("📈 Performance Summary")
        metrics = result.get("summary", {})

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.metric("Total Return", f"{metrics.get('total_return', 0)*100:.2f}%")
        with col2:
            st.metric("Annual Return", f"{metrics.get('annual_return', 0)*100:.2f}%")
        with col3:
            st.metric("Sharpe Ratio", f"{metrics.get('sharpe_ratio', 0):.2f}")
        with col4:
            st.metric("Max Drawdown", f"{metrics.get('max_drawdown', 0)*100:.2f}%")
        with col5:
            st.metric("Win Rate", f"{metrics.get('win_rate', 0)*100:.1f}%")
        with col6:
            st.metric("Total Trades", f"{metrics.get('total_trades', 0)}")

        # Trade Statistics
        st.subheader("📋 Trade Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Winning Trades", metrics.get('winning_trades', 0))
        with col2:
            st.metric("Losing Trades", metrics.get('losing_trades', 0))
        with col3:
            st.metric("Avg Trade Return", f"{metrics.get('avg_trade_return', 0)*100:.2f}%")

        # Monthly Returns
        if "monthly_returns" in result:
            st.subheader("📅 Monthly Returns")
            monthly = result["monthly_returns"]
            st.bar_chart(monthly)

        # Trade Log
        if "trades" in result and result["trades"]:
            st.subheader("📝 Trade Log")
            trades_df = pd.DataFrame(result["trades"])
            st.dataframe(trades_df, use_container_width=True)
