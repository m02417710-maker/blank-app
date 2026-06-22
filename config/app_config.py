"""
EGX Pro Terminal v34 - Streamlit App Configuration
"""

import streamlit as st
from config.settings import config

def setup_page_config():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title=config.APP_NAME,
        page_icon="🇪🇬",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "Get Help": "https://github.com/m02417710-maker/blank-app",
            "Report a bug": "https://github.com/m02417710-maker/blank-app/issues",
            "About": f"{config.APP_NAME} v{config.APP_VERSION} - Professional EGX Analysis Platform"
        }
    )

def inject_custom_css():
    """Inject custom CSS for EGX Pro Terminal."""
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
    .dividend-card { background: linear-gradient(145deg, #1e1e1e, #2a2a2a); border: 1px solid #333; border-radius: 10px; padding: 14px; margin-bottom: 8px; }
    .dividend-card .symbol { font-weight: 700; color: #4a9eff; }
    .dividend-card .amount { font-size: 1.2rem; font-weight: 600; color: #00d084; }
    .nav-btn { background: transparent; border: 1px solid #333; color: #ccc; padding: 8px 16px; border-radius: 8px; cursor: pointer; transition: all 0.2s; font-size: 0.9rem; }
    .nav-btn:hover, .nav-btn.active { background: #4a9eff; color: #fff; border-color: #4a9eff; }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
