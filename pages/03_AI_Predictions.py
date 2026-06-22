"""
EGX Pro Terminal - AI Predictions Page
"""

import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.egx_symbols import get_stock_info, get_all_symbols
from data.market_data import generate_mock_data
from core.ai_engine import AIEngine
import pandas as pd
import numpy as np

st.set_page_config(page_title="AI Predictions", page_icon="🤖", layout="wide")

ai = AIEngine()

st.title("🤖 AI-Powered Predictions")

all_syms = get_all_symbols()[:50]
if "selected_symbol" not in st.session_state:
    st.session_state["selected_symbol"] = "COMI"

symbol = st.selectbox("Select Symbol", all_syms,
                     index=all_syms.index(st.session_state["selected_symbol"]) if st.session_state["selected_symbol"] in all_syms else 0,
                     key="ai_symbol")
st.session_state["selected_symbol"] = symbol

model_type = st.selectbox("AI Model", ["ensemble", "monte_carlo", "technical", "sentiment", "hybrid"], key="ai_model")

if st.button("🚀 Generate Prediction", use_container_width=True):
    with st.spinner("Running advanced AI analysis..."):
        df = generate_mock_data(symbol, 252)
        prediction = ai.predict(df, model_type=model_type)

        st.success("Analysis Complete!")

        # Probability Gauges
        st.subheader("📊 Probability Distribution")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Bullish", f"{prediction.get('bullish_prob', 0)*100:.1f}%")
            st.progress(prediction.get('bullish_prob', 0))
        with col2:
            st.metric("Bearish", f"{prediction.get('bearish_prob', 0)*100:.1f}%")
            st.progress(prediction.get('bearish_prob', 0))
        with col3:
            st.metric("Neutral", f"{prediction.get('neutral_prob', 0)*100:.1f}%")
            st.progress(prediction.get('neutral_prob', 0))

        # Recommendation
        st.subheader("🎯 Trading Recommendation")
        rec = prediction.get("recommendation", "HOLD")
        confidence = prediction.get("confidence", 0.5)

        color_map = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡", "STRONG_BUY": "🟢🟢", "STRONG_SELL": "🔴🔴"}
        emoji = color_map.get(rec, "⚪")

        st.markdown(f"<h1 style='text-align:center'>{emoji} {rec}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center;font-size:1.2rem'>Confidence: {confidence*100:.1f}%</p>", unsafe_allow_html=True)

        # Signal Breakdown
        st.subheader("📋 Signal Breakdown")
        for signal in prediction.get("signals", []):
            st.write(f"• {signal}")

        # Feature Importance
        if "feature_importance" in prediction:
            st.subheader("🔍 Feature Importance")
            feat_imp = prediction["feature_importance"]
            for feat, imp in sorted(feat_imp.items(), key=lambda x: x[1], reverse=True):
                st.write(f"• {feat}: {imp*100:.1f}%")

        # Monte Carlo Simulation
        if model_type == "monte_carlo" and "monte_carlo" in prediction:
            st.subheader("🎲 Monte Carlo Simulation")
            mc = prediction["monte_carlo"]
            st.write(f"**Expected Price (30d):** {mc.get('expected_price', 0):.2f}")
            st.write(f"**95% CI Lower:** {mc.get('ci_lower', 0):.2f}")
            st.write(f"**95% CI Upper:** {mc.get('ci_upper', 0):.2f}")
            st.write(f"**Probability of Gain:** {mc.get('prob_gain', 0)*100:.1f}%")

        # Risk Metrics
        st.subheader("⚠️ Risk Metrics")
        risk = prediction.get("risk_metrics", {})
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Volatility", f"{risk.get('volatility', 0)*100:.1f}%")
        with col2:
            st.metric("VaR (95%)", f"{risk.get('var_95', 0)*100:.2f}%")
        with col3:
            st.metric("Max Drawdown", f"{risk.get('max_drawdown', 0)*100:.1f}%")
