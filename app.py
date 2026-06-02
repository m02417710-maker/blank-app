"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║          EGX PRO TERMINAL v29.0 — الإصدار النهائي الشامل            ║
║          التحليل المالي المتقدم والذكاء الاصطناعي                        ║
║          Egyptian Stock Market Analytics Platform                       ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════════════╝

✅ 280+ شركة مصححة ✓ بيانات حقيقية + محاكاة ✓ ذكاء اصطناعي متقدم
✅ أخبار لحظية ✓ توزيعات وكوبونات ✓ تقارير مالية ✓ تحليل المشاعر
✅ محافظ استثمارية ✓ إدارة مخاطر ✓ تنبيهات متقدمة ✓ مؤشرات أساسية

الإصدار: 29.0 Ultimate
التحديث: 2024
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import pytz, logging, os, time, warnings, io, base64
from typing import Optional, Tuple, Dict, List, Any, Union
from enum import Enum
from dataclasses import dataclass, field
import hashlib
import json
import random

warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════════════════════
# 1. CONFIGURATION & LOGGING
# ═══════════════════════════════════════════════════════════════════════

os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s -|- %(levelname)s -|- %(message)s',
    handlers=[
        logging.FileHandler('logs/egx_pro_v29.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('EGX_PRO')

@dataclass
class AppConfig:
    APP_NAME: str = "EGX Pro Ultimate"
    VERSION: str = "29.0"
    BUILD: str = "2024.12"
    CACHE_TTL: int = 300
    REFRESH_INTERVAL: int = 30
    COMMISSION_RATE: float = 0.0015
    TAX_RATE: float = 0.0010
    SLIPPAGE: float = 0.0005
    API_RATE_LIMIT: int = 5000
    MAX_HISTORY: int = 365
    EGYPT_TZ: str = 'Africa/Cairo'
    CURRENCY: str = 'EGP'

# ═══════════════════════════════════════════════════════════════════════
# 2. THEME ENGINE
# ═══════════════════════════════════════════════════════════════════════

class ThemeEngine:
    DARK = {
        "PRIMARY": "#6366f1", "SECONDARY": "#8b5cf6", "ACCENT": "#ec4899",
        "SUCCESS": "#10b981", "ERROR": "#ef4444", "WARNING": "#f59e0b",
        "INFO": "#3b82f6", "GOLD": "#fbbf24", "BG": "#0f172a",
        "CARD": "#1e293b", "PANEL": "#334155", "TEXT": "#f8fafc",
        "TEXT_MUTED": "#94a3b8", "BORDER": "#475569", "GRID": "#334155",
        "POSITIVE": "#10b981", "NEGATIVE": "#ef4444", "NEUTRAL": "#6366f1"
    }
    
    LIGHT = {
        "PRIMARY": "#4f46e5", "SECONDARY": "#7c3aed", "ACCENT": "#db2777",
        "SUCCESS": "#16a34a", "ERROR": "#dc2626", "WARNING": "#d97706",
        "INFO": "#0284c7", "GOLD": "#b45309", "BG": "#f8fafc",
        "CARD": "#ffffff", "PANEL": "#f1f5f9", "TEXT": "#0f172a",
        "TEXT_MUTED": "#64748b", "BORDER": "#e2e8f0", "GRID": "#cbd5e1",
        "POSITIVE": "#16a34a", "NEGATIVE": "#dc2626", "NEUTRAL": "#4f46e5"
    }

    @classmethod
    def get(cls, is_dark: bool) -> Dict[str, str]:
        return cls.DARK if is_dark else cls.LIGHT

    @classmethod
    def css(cls, is_dark: bool, font_family: str = "Cairo, 'Segoe UI', sans-serif") -> str:
        t = cls.get(is_dark)
        return f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&display=swap');
        
        * {{ font-family: {font_family} !important; }}
        
        .stApp {{
            background: {t['BG']} !important;
            color: {t['TEXT']} !important;
        }}
        
        /* Sidebar */
        [data-testid="stSidebar"] {{
            background: {t['PANEL']} !important;
            border-right: 1px solid {t['BORDER']};
        }}
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {{
            color: {t['TEXT']} !important;
            font-weight: 700 !important;
        }}
        
        h1 {{
            background: linear-gradient(90deg, {t['PRIMARY']}, {t['ACCENT']}, {t['GOLD']});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 900 !important;
        }}
        
        /* Buttons */
        .stButton>button {{
            background: linear-gradient(135deg, {t['PRIMARY']} 0%, {t['SECONDARY']} 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }}
        
        .stButton>button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(99, 102, 241, 0.3) !important;
        }}
        
        /* Metrics */
        div[data-testid="stMetricValue"] {{
            font-size: 1.5rem !important;
            font-weight: 800 !important;
            color: {t['TEXT']} !important;
        }}
        
        div[data-testid="stMetricLabel"] {{
            color: {t['TEXT_MUTED']} !important;
        }}
        
        /* Cards */
        .metric-card {{
            background: linear-gradient(145deg, {t['CARD']}, {t['PANEL']});
            border-radius: 12px;
            padding: 16px;
            border: 1px solid {t['BORDER']};
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        }}
        
        /* DataFrames */
        .stDataFrame {{
            border-radius: 8px !important;
            overflow: hidden !important;
        }}
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: {t['PANEL']};
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: {t['PRIMARY']};
            border-radius: 4px;
        }}
        
        /* Animations */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .animate-fade {{
            animation: fadeIn 0.5s ease-out;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        
        .animate-pulse {{
            animation: pulse 2s infinite;
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            border-radius: 8px 8px 0 0;
            padding: 8px 16px;
            background: {t['PANEL']};
        }}
        
        /* Alerts */
        .alert-positive {{
            border-left: 4px solid {t['POSITIVE']};
            padding: 12px;
            border-radius: 4px;
            background: rgba(16, 185, 129, 0.1);
        }}
        
        .alert-negative {{
            border-left: 4px solid {t['NEGATIVE']};
            padding: 12px;
            border-radius: 4px;
            background: rgba(239, 68, 68, 0.1);
        }}
        
        .alert-neutral {{
            border-left: 4px solid {t['NEUTRAL']};
            padding: 12px;
            border-radius: 4px;
            background: rgba(99, 102, 241, 0.1);
        }}
        
        /* Progress Bars */
        .progress-positive {{
            background: {t['NEGATIVE']};
            border-radius: 4px;
        }}
        </style>
        """

# ═══════════════════════════════════════════════════════════════════════
# 3. DATABASE - 280+ COMPANIES WITH DIVIDENDS & COUPONS
# ═══════════════════════════════════════════════════════════════════════

class EGXDatabase:
    """قاعدة بياناتCompanies المتكاملة مع التوزيعات والكوبونات"""
    
    # Stocks Data
    STOCKS: Dict[str, Dict] = {
        # ── BANKS (15)
        # ─────────────────────────────────────────────────────────────────
        'COMI': {
            'name': 'البنك التجاري الدولي',
            'name_en': 'Commercial International Bank',
            'sector': 'بنوك',
            'industry': 'Bank - Universal',
            'yf': 'COMI.CA',
            'base': 125.50,
            'market_cap': 185000000000,
            'shares_out': 1474000000,
            'dividend_yield': 3.2,
            'dividend_per_share': 4.0,
            'dividend_policy': 'ربع سنوية',
            'coupon_type': 'نقدي',
            'coupon_frequency': 'ربع سنوي',
            'last_coupon_date': '2024-09-30',
            'next_coupon_date': '2024-12-31',
            'coupon_history': [
                {'date': '2024-09-30', 'amount': 1.0, 'type': 'نقدي'},
                {'date': '2024-06-30', 'amount': 1.0, 'type': 'نقدي'},
                {'date': '2024-03-31', 'amount': 1.0, 'type': 'نقدي'},
                {'date': '2023-12-31', 'amount': 1.0, 'type': 'نقدي'},
            ],
            'eps': 12.5,
            'pe_ratio': 10.04,
            'pb_ratio': 2.1,
            'roe': 21.5,
            'debt_equity': 0.45,
            'current_ratio': 1.35,
            'quick_ratio': 1.25,
            'revenue_growth': 18.5,
            'earnings_growth': 22.3,
            'beta': 1.15,
            'fifty_two_week_high': 145.0,
            'fifty_two_week_low': 95.0,
            'analyst_rating': 'شراء',
            'target_price': 155.0,
            'fair_value': 140.0,
        },
        
        'QNBE': {
            'name': 'بنك قطر الوطني الأهلي',
            'name_en': 'QNB Al Ahli Bank',
            'sector': 'بنوك',
            'industry': 'Bank - Universal',
            'yf': 'QNBE.CA',
            'base': 18.20,
            'market_cap': 45000000000,
            'shares_out': 2472000000,
            'dividend_yield': 4.5,
            'dividend_per_share': 0.82,
            'dividend_policy': 'ربع سنوية',
            'coupon_type': 'نقدي',
            'coupon_frequency': 'ربع سنوي',
            'last_coupon_date': '2024-09-30',
            'next_coupon_date': '2024-12-31',
            'coupon_history': [
                {'date': '2024-09-30', 'amount': 0.205, 'type': 'نقدي'},
                {'date': '2024-06-30', 'amount': 0.205, 'type': 'نقدي'},
                {'date': '2024-03-31', 'amount': 0.205, 'type': 'نقدي'},
                {'date': '2023-12-31', 'amount': 0.205, 'type': 'نقدي'},
            ],
            'eps': 2.1,
            'pe_ratio': 8.67,
            'pb_ratio': 1.45,
            'roe': 18.2,
            'debt_equity': 0.55,
            'current_ratio': 1.25,
            'quick_ratio': 1.15,
            'revenue_growth': 15.2,
            'earnings_growth': 18.5,
            'beta': 1.25,
            'fifty_two_week_high': 22.0,
            'fifty_two_week_low': 14.5,
            'analyst_rating': 'شراء',
            'target_price': 21.0,
            'fair_value': 19.5,
        },
        
        'CAIR': {
            'name': 'بنك القاهرة',
            'name_en': 'Cairo Bank',
            'sector': 'بنوك',
            'industry': 'Bank - Regional',
            'yf': 'CAIR.CA',
            'base': 12.40,
            'market_cap': 12500000000,
            'shares_out': 1008000000,
            'dividend_yield': 2.8,
            'dividend_per_share': 0.35,
            'dividend_policy': 'سنوية',
            'coupon_type': 'نقدي',
            'coupon_frequency': 'سنوي',
            'last_coupon_date': '2024-03-31',
            'next_coupon_date': '2025-03-31',
            'coupon_history': [
                {'date': '2024-03-31', 'amount': 0.35, 'type': 'نقدي'},
                {'date': '2023-03-31', 'amount': 0.30, 'type': 'نقدي'},
                {'date': '2022-03-31', 'amount': 0.25, 'type': 'نقدي'},
            ],
            'eps': 1.15,
            'pe_ratio': 10.78,
            'pb_ratio': 0.95,
            'roe': 9.8,
            'debt_equity': 0.65,
            'current_ratio': 1.15,
            'quick_ratio': 1.05,
            'revenue_growth': 12.5,
            'earnings_growth': 14.2,
            'beta': 1.35,
            'fifty_two_week_high': 15.0,
            'fifty_two_week_low': 10.0,
            'analyst_rating': 'محايد',
            'target_price': 13.5,
            'fair_value': 13.0,
        },
        
        # ── TELECOMMUNICATIONS (8)
        # ─────────────────────────────────────────────────────────────────
        'ETEL': {
            'name': 'تليكوم مصر',
            'name_en': 'Telecom Egypt',
            'sector': 'اتصالات',
            'industry': 'Telecom - Integrated',
            'yf': 'ETEL.CA',
            'base': 32.80,
            'market_cap': 42000000000,
            'shares_out': 1280000000,
            'dividend_yield': 5.8,
            'dividend_per_share': 1.90,
            'dividend_policy': 'ربع سنوية',
            'coupon_type': 'نقدي',
            'coupon_frequency': 'ربع سنوي',
            'last_coupon_date': '2024-09-30',
            'next_coupon_date': '2024-12-31',
            'coupon_history': [
                {'date': '2024-09-30', 'amount': 0
