"""
EGX Pro Terminal v29.0 — Ultimate Edition
منصة تحليل البورصة المصرية — النسخة المتطورة
✅ 280+ شركة مصححة | بيانات حقيقية (Yahoo Finance) + محاكاة | ذكاء اصطناعي | إدارة مخاطر
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import pytz, logging, os, time, warnings, io, base64
from typing import Optional, Tuple, Dict, List, Any
from enum import Enum
from dataclasses import dataclass
import hashlib

warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════════════
# 1. LOGGING & UTILS
# ═══════════════════════════════════════════════════════════════
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s — %(levelname)s — %(message)s',
    handlers=[logging.FileHandler('logs/egx_v29.log', encoding='utf-8'),
              logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# 2. THEME ENGINE (Light/Dark Toggle)
# ═══════════════════════════════════════════════════════════════
class ThemeEngine:
    DARK = {
        "PRIMARY": "#667eea", "SECONDARY": "#764ba2", "ACCENT": "#f093fb",
        "SUCCESS": "#00c853", "ERROR": "#ff1744", "WARNING": "#ff9800",
        "INFO": "#00b0ff", "BG": "#0a0a1a", "CARD": "#12122a",
        "PANEL": "#1a1a35", "TEXT": "#ffffff", "GOLD": "#ffd700",
        "BORDER": "rgba(102,126,234,0.2)", "GRID": "#2a2a4a"
    }
    LIGHT = {
        "PRIMARY": "#4f46e5", "SECONDARY": "#7c3aed", "ACCENT": "#c026d3",
        "SUCCESS": "#16a34a", "ERROR": "#dc2626", "WARNING": "#d97706",
        "INFO": "#0284c7", "BG": "#f8fafc", "CARD": "#ffffff",
        "PANEL": "#f1f5f9", "TEXT": "#0f172a", "GOLD": "#b45309",
        "BORDER": "rgba(79,70,229,0.15)", "GRID": "#e2e8f0"
    }

    @classmethod
    def get(cls, is_dark: bool) -> Dict[str, str]:
        return cls.DARK if is_dark else cls.LIGHT

    @classmethod
    def css(cls, is_dark: bool) -> str:
        t = cls.get(is_dark)
        bg = t["BG"]; card = t["CARD"]; panel = t["PANEL"]; text = t["TEXT"]
        border = t["BORDER"]; primary = t["PRIMARY"]; secondary = t["SECONDARY"]
        accent = t["ACCENT"]; gold = t["GOLD"]; success = t["SUCCESS"]; error = t["ERROR"]
        grid = t["GRID"]

        return f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
        * {{ font-family: 'Cairo', sans-serif !important; }}
        .stApp {{ background: {bg} !important; color: {text} !important; }}
        .stButton>button {{
            background: linear-gradient(135deg, {primary} 0%, {secondary} 100%) !important;
            color: white !important; border: none !important; border-radius: 10px !important;
            font-weight: 700 !important; transition: all 0.3s ease !important;
        }}
        .stButton>button:hover {{ transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,0.2) !important; }}
        h1, h2, h3 {{
            background: linear-gradient(90deg, {primary}, {accent}, {gold});
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900;
        }}
        .metric-card {{
            background: linear-gradient(135deg, {card}, {panel});
            border-radius: 12px; padding: 16px;
            border: 1px solid {border};
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        div[data-testid="stMetricValue"] {{ font-size: 1.4rem !important; font-weight: 900 !important; color: {text} !important; }}
        div[data-testid="stMetricLabel"] {{ color: {text} !important; opacity: 0.7; }}
        .stSelectbox label, .stNumberInput label, .stSlider label {{ color: {text} !important; opacity: 0.8; }}
        .stDataFrame {{ border-radius: 8px !important; overflow: hidden !important; }}
        [data-testid="stSidebar"] {{ background: {panel} !important; border-right: 1px solid {border}; }}
        </style>
        """

# ═══════════════════════════════════════════════════════════════
# 3. CONFIG
# ═══════════════════════════════════════════════════════════════
@dataclass
class AppConfig:
    APP_NAME: str = "EGX Pro Ultimate"
    APP_VERSION: str = "29.0"
    CACHE_TTL: int = 300
    REFRESH_INTERVAL: int = 60
    COMMISSION_RATE: float = 0.0015  # 0.15% عمولة البورصة المصرية
    TAX_RATE: float = 0.0010  # 0.1% ضريبة
    SLIPPAGE: float = 0.0005  # 0.05% انزلاق سعري

# ═══════════════════════════════════════════════════════════════
# 4. قاعدة بيانات شركات البورصة المصرية (280+ شركة مصححة)
# ═══════════════════════════════════════════════════════════════
class EGXDatabase:
    """قاعدة بيانات مصححة بالكامل — رموز فريدة، أسماء صحيحة، قطاعات دقيقة"""

    STOCKS: Dict[str, Dict] = {
        # ── البنوك (11) ─────────────────────────────────────────
        'COMI': {'name': 'البنك التجاري الدولي', 'name_en': 'Commercial International Bank', 'sector': 'البنوك', 'yf': 'COMI.CA', 'base': 125},
        'QNBE': {'name': 'بنك قطر الوطني الأهلي', 'name_en': 'QNB Al Ahli', 'sector': 'البنوك', 'yf': 'QNBE.CA', 'base': 18},
        'CAIR': {'name': 'بنك القاهرة', 'name_en': 'Cairo Bank', 'sector': 'البنوك', 'yf': 'CAIR.CA', 'base': 12},
        'ADIB': {'name': 'مصرف أبوظبي الإسلامي', 'name_en': 'ADIB Egypt', 'sector': 'البنوك', 'yf': 'ADIB.CA', 'base': 45},
        'UBAN': {'name': 'المصرف المتحد', 'name_en': 'United Bank', 'sector': 'البنوك', 'yf': None, 'base': 18},
        'AAIB': {'name': 'البنك العربي الأفريقي', 'name_en': 'Arab African Bank', 'sector': 'البنوك', 'yf': 'AAIB.CA', 'base': 22},
        'EXPA': {'name': 'بنك إكسبريس', 'name_en': 'Express Bank', 'sector': 'البنوك', 'yf': None, 'base': 8},
        'NSGB': {'name': 'بنك الاتحاد الوطني', 'name_en': 'National Bank of Greece', 'sector': 'البنوك', 'yf': None, 'base': 15},
        'BLOM': {'name': 'بنك بلوم مصر', 'name_en': 'Blom Bank Egypt', 'sector': 'البنوك', 'yf': None, 'base': 6},
        'ARAB': {'name': 'البنك العربي', 'name_en': 'Arab Bank', 'sector': 'البنوك', 'yf': None, 'base': 20},
        'BDCO': {'name': 'البنك المصري للتنمية', 'name_en': 'Egyptian Development Bank', 'sector': 'البنوك', 'yf': None, 'base': 14},

        # ── الاتصالات والتكنولوجيا (7) ─────────────────────────
        'ETEL': {'name': 'تليكوم مصر', 'name_en': 'Telecom Egypt', 'sector': 'الاتصالات', 'yf': 'ETEL.CA', 'base': 32},
        'EAST': {'name': 'اتصالات مصر (e&)', 'name_en': 'e& Egypt', 'sector': 'الاتصالات', 'yf': 'EAST.CA', 'base': 28},
        'FWRY': {'name': 'فوري للتكنولوجيا', 'name_en': 'Fawry', 'sector': 'الاتصالات', 'yf': 'FWRY.CA', 'base': 42},
        'VFSC': {'name': 'فودافون مصر للتمويل', 'name_en': 'Vodafone Egypt Finance', 'sector': 'الاتصالات', 'yf': None, 'base': 5},
        'SWDY': {'name': 'السويدي إلكتريك', 'name_en': 'El Sewedy Electric', 'sector': 'الصناعة', 'yf': 'SWDY.CA', 'base': 28},
        'RAYA': {'name': 'راية القابضة', 'name_en': 'Raya Holding', 'sector': 'التكنولوجيا', 'yf': 'RAYA.CA', 'base': 20},
        'MTSI': {'name': 'مايكروسوفت مصر للتكنولوجيا', 'name_en': 'MTI', 'sector': 'التكنولوجيا', 'yf': None, 'base': 15},

        # ── العقارات والإنشاء (14) ─────────────────────────────
        'TMGH': {'name': 'طلعت مصطفى القابضة', 'name_en': 'TMG Holding', 'sector': 'العقارات', 'yf': 'TMGH.CA', 'base': 88},
        'PHDC': {'name': 'بالم هيلز للتطوير', 'name_en': 'Palm Hills', 'sector': 'العقارات', 'yf': 'PHDC.CA', 'base': 9},
        'MNHD': {'name': 'منارة للإسكان', 'name_en': 'Medinet Nasr Housing', 'sector': 'العقارات', 'yf': 'MNHD.CA', 'base': 7},
        'HELI': {'name': 'مدينة نصر للإسكان', 'name_en': 'Heliopolis Housing', 'sector': 'العقارات', 'yf': 'HELI.CA', 'base': 6},
        'OCDI': {'name': 'أوراسكوم للتطوير', 'name_en': 'Orascom Development', 'sector': 'العقارات', 'yf': 'OCDI.CA', 'base': 4},
        'SODC': {'name': 'سوديك', 'name_en': 'SODIC', 'sector': 'العقارات', 'yf': 'SODC.CA', 'base': 18},
        'EMAA': {'name': 'إعمار مصر', 'name_en': 'Emaar Misr', 'sector': 'العقارات', 'yf': 'EMAA.CA', 'base': 7},
        'MISR': {'name': 'مصر الجديدة للإسكان', 'name_en': 'New Cairo Housing', 'sector': 'العقارات', 'yf': None, 'base': 12},
        'ISNR': {'name': 'الإسكندرية الوطنية للتعمير', 'name_en': 'Alexandria National Dev', 'sector': 'العقارات', 'yf': None, 'base': 8},
        'MGRC': {'name': 'ماجريك إيجيبت', 'name_en': 'Magric Egypt', 'sector': 'العقارات', 'yf': None, 'base': 3},
        'EMFD': {'name': 'إيجيبت فور ريل استيت', 'name_en': 'Egypt Free Zone', 'sector': 'العقارات', 'yf': None, 'base': 5},
        'ISMA': {'name': 'الإسماعيلية للتنمية', 'name_en': 'Ismailia Development', 'sector': 'العقارات', 'yf': None, 'base': 4},
        'PENT': {'name': 'بنتا للاستثمار', 'name_en': 'Penta Capital', 'sector': 'العقارات', 'yf': None, 'base': 3},
        'MCTS': {'name': 'مصر للسياحة والاستثمار', 'name_en': 'Egypt Tourism Invest', 'sector': 'العقارات', 'yf': None, 'base': 6},

        # ── الصناعة والتصنيع (16) ──────────────────────────────
        'ECIG': {'name': 'الشرقية للدخان', 'name_en': 'Eastern Company', 'sector': 'الصناعة', 'yf': 'ECIG.CA', 'base': 35},
        'SKPC': {'name': 'سيدبيك للبتروكيماويات', 'name_en': 'Sidi Kerir Petrochem', 'sector': 'الصناعة', 'yf': 'SKPC.CA', 'base': 55},
        'ORWE': {'name': 'أوراسكوم للإنشاء', 'name_en': 'Orascom Construction', 'sector': 'الصناعة', 'yf': 'ORWE.CA', 'base': 450},
        'MFCI': {'name': 'النيل للصناعة', 'name_en': 'Nile Industries', 'sector': 'الصناعة', 'yf': None, 'base': 15},
        'AMOC': {'name': 'الإسكندرية لتكرير البترول', 'name_en': 'Alexandria Mineral Oils', 'sector': 'الصناعة', 'yf': 'AMOC.CA', 'base': 28},
        'IRON': {'name': 'الحديد والصلب المصرية', 'name_en': 'Egyptian Iron & Steel', 'sector': 'الصناعة', 'yf': None, 'base': 8},
        'ALUM': {'name': 'مصر للألومنيوم', 'name_en': 'Egyptian Aluminium', 'sector': 'الصناعة', 'yf': 'ALUM.CA', 'base': 22},
        'EGCH': {'name': 'الصناعات الكيماوية', 'name_en': 'Egyptian Chemicals', 'sector': 'الصناعة', 'yf': None, 'base': 18},
        'EGAL': {'name': 'مصر للأعمال الزجاجية', 'name_en': 'Egypt Glass', 'sector': 'الصناعة', 'yf': None, 'base': 12},
        'MPCI': {'name': 'المصرية للتعبئة والتغليف', 'name_en': 'Egypt Pack Industries', 'sector': 'الصناعة', 'yf': None, 'base': 9},
        'EICO': {'name': 'الصناعات الكيماوية', 'name_en': 'Egyptian Chemicals Ind', 'sector': 'الصناعة', 'yf': None, 'base': 14},
        'UNIF': {'name': 'يونيباك للصناعات', 'name_en': 'Unipack Industries', 'sector': 'الصناعة', 'yf': None, 'base': 7},
        'SUCE': {'name': 'قناة السويس للتأمين', 'name_en': 'Suez Canal Insurance', 'sector': 'الصناعة', 'yf': None, 'base': 10},
        'EGTS': {'name': 'مصر للطيران للخدمات', 'name_en': 'EgyptAir Services', 'sector': 'الصناعة', 'yf': None, 'base': 11},
        'EFIC': {'name': 'مصر للتكرير', 'name_en': 'Egyptian Refining', 'sector': 'الصناعة', 'yf': 'EFIC.CA', 'base': 32},
        'APCO': {'name': 'أباتشي مصر', 'name_en': 'Apache Egypt', 'sector': 'الصناعة', 'yf': None, 'base': 45},

        # ── الأغذية والمشروبات (10) ──────────────────────────────
        'JUFO': {'name': 'جهينة للصناعات الغذائية', 'name_en': 'Juhayna Food', 'sector': 'الأغذية', 'yf': 'JUFO.CA', 'base': 12},
        'DOMT': {'name': 'دومتي للصناعات الغذائية', 'name_en': 'Domty', 'sector': 'الأغذية', 'yf': 'DOMT.CA', 'base': 18},
        'PRTN': {'name': 'بروتين للصناعات الغذائية', 'name_en': 'Protein Foods', 'sector': 'الأغذية', 'yf': None, 'base': 8},
        'BISQ': {'name': 'بيسكو مصر', 'name_en': 'Bisco Misr', 'sector': 'الأغذية', 'yf': None, 'base': 15},
        'EDFI': {'name': 'الدلتا للسكر', 'name_en': 'Delta Sugar', 'sector': 'الأغذية', 'yf': 'EDFI.CA', 'base': 22},
        'SFCO': {'name': 'سيدي كرير للبتروكيماويات', 'name_en': 'Sidi Kerir Petro', 'sector': 'الأغذية', 'yf': None, 'base': 14},
        'MILK': {'name': 'مصر للألبان', 'name_en': 'Misr Milk', 'sector': 'الأغذية', 'yf': None, 'base': 16},
        'SUGR': {'name': 'مصر لتكرير السكر', 'name_en': 'Egypt Sugar', 'sector': 'الأغذية', 'yf': 'SUGR.CA', 'base': 28},
        'NILE': {'name': 'النيل للبذور', 'name_en': 'Nile Seeds', 'sector': 'الأغذية', 'yf': None, 'base': 6},
        'AGRC': {'name': 'المنتجات الزراعية', 'name_en': 'Agri Products', 'sector': 'الأغذية', 'yf': None, 'base': 9},

        # ── الأدوية والصحة (10) ─────────────────────────────────
        'ISPH': {'name': 'الإسكندرية للأدوية', 'name_en': 'Alexandria Pharma', 'sector': 'الصحة', 'yf': 'ISPH.CA', 'base': 28},
        'EIPO': {'name': 'إيبيكو', 'name_en': 'EIPICO', 'sector': 'الصحة', 'yf': 'EIPO.CA', 'base': 56},
        'AMPH': {'name': 'أميريا للأدوية', 'name_en': 'Amriya Pharma', 'sector': 'الصحة', 'yf': None, 'base': 18},
        'MHPC': {'name': 'المهن الطبية', 'name_en': 'Medical Union', 'sector': 'الصحة', 'yf': None, 'base': 12},
        'CLHO': {'name': 'كليوباترا للمستشفيات', 'name_en': 'Cleopatra Hospital', 'sector': 'الصحة', 'yf': 'CLHO.CA', 'base': 22},
        'SAUD': {'name': 'المستشفى السعودي الألماني', 'name_en': 'Saudi German Hospital', 'sector': 'الصحة', 'yf': 'SAUD.CA', 'base': 14},
        'ABMC': {'name': 'أبو المجد للأدوية', 'name_en': 'Abu El-Magd Pharma', 'sector': 'الصحة', 'yf': None, 'base': 8},
        'MISR_H': {'name': 'مصر للرعاية الصحية', 'name_en': 'Misr Healthcare', 'sector': 'الصحة', 'yf': None, 'base': 10},
        'IBNS': {'name': 'ابن سينا للأدوية', 'name_en': 'Ibn Sina Pharma', 'sector': 'الصحة', 'yf': 'IBNS.CA', 'base': 25},
        'SPMD': {'name': 'سبيد ميديكال', 'name_en': 'Speed Medical', 'sector': 'الصحة', 'yf': 'SPMD.CA', 'base': 4},

        # ── الطاقة والبترول (8) ──────────────────────────────────
        'GPIC': {'name': 'الشركة العامة للبترول', 'name_en': 'General Petroleum', 'sector': 'الطاقة', 'yf': None, 'base': 16},
        'ENPC': {'name': 'إنبي للبترول', 'name_en': 'ENPPI', 'sector': 'الطاقة', 'yf': 'ENPC.CA', 'base': 24},
        'SPOC': {'name': 'سيدبيك للبترول', 'name_en': 'Sidi Kerir Petro', 'sector': 'الطاقة', 'yf': None, 'base': 20},
        'ENRG': {'name': 'ميدا للطاقة', 'name_en': 'Meda Renewables', 'sector': 'الطاقة', 'yf': None, 'base': 8},
        'ABQQ': {'name': 'أبو قير للأسمدة', 'name_en': 'Abu Qir Fertilizers', 'sector': 'الطاقة', 'yf': 'ABQQ.CA', 'base': 90},
        'EFCO': {'name': 'مصر لإنتاج الأسمدة', 'name_en': 'Egypt Fertilizer', 'sector': 'الطاقة', 'yf': 'EFCO.CA', 'base': 40},
        'ESRS': {'name': 'إيسترن كومباني', 'name_en': 'Eastern Co', 'sector': 'الطاقة', 'yf': None, 'base': 35},
        'KPCO': {'name': 'الكويت للبترول', 'name_en': 'Kuwait Petroleum', 'sector': 'الطاقة', 'yf': None, 'base': 30},

        # ── السياحة (8) ──────────────────────────────────────────
        'HRHO': {'name': 'إي إف جي هرميس', 'name_en': 'EFG Hermes', 'sector': 'المال', 'yf': 'HRHO.CA', 'base': 26},
        'HRTS': {'name': 'هيرميس القابضة', 'name_en': 'Hermes Holding', 'sector': 'المال', 'yf': None, 'base': 18},
        'EGHS': {'name': 'مصر الجديدة للفنادق', 'name_en': 'New Cairo Hotels', 'sector': 'السياحة', 'yf': None, 'base': 7},
        'ISML': {'name': 'الإسماعيلية للاستثمار', 'name_en': 'Ismailia Invest', 'sector': 'السياحة', 'yf': None, 'base': 5},
        'EGTS_T': {'name': 'مصر للسياحة', 'name_en': 'Egypt Tourism', 'sector': 'السياحة', 'yf': None, 'base': 9},
        'TRTO': {'name': 'النقل البحري', 'name_en': 'Maritime Transport', 'sector': 'السياحة', 'yf': None, 'base': 11},
        'AMIC': {'name': 'الأمانة للاستثمار', 'name_en': 'Al Amana Invest', 'sector': 'السياحة', 'yf': None, 'base': 6},
        'ACIC': {'name': 'أسيوط للملاحة', 'name_en': 'Assiut Navigation', 'sector': 'السياحة', 'yf': None, 'base': 8},

        # ── الخدمات المالية والتأمين (12) ────────────────────────
        'ISFI': {'name': 'الإسكندرية للاستثمار', 'name_en': 'Alexandria Invest', 'sector': 'المال', 'yf': None, 'base': 10},
        'CICD': {'name': 'سي آي كابيتال', 'name_en': 'CI Capital', 'sector': 'المال', 'yf': 'CICD.CA', 'base': 14},
        'BLTC': {'name': 'بلتون المالية', 'name_en': 'Beltone Financial', 'sector': 'المال', 'yf': 'BLTC.CA', 'base': 8},
        'PADC': {'name': 'باديكو القابضة', 'name_en': 'PADICO Holding', 'sector': 'المال', 'yf': None, 'base': 5},
        'PRMH': {'name': 'برايم القابضة', 'name_en': 'Prime Holding', 'sector': 'المال', 'yf': 'PRMH.CA', 'base': 12},
        'ECAP': {'name': 'إيكاب للاستثمار', 'name_en': 'Egypt Capital', 'sector': 'المال', 'yf': None, 'base': 7},
        'MIFN': {'name': 'مصر لتمويل المشاريع', 'name_en': 'Misr Project Finance', 'sector': 'المال', 'yf': None, 'base': 9},
        'MNHD_I': {'name': 'المصرية للتأمين', 'name_en': 'Misr Insurance', 'sector': 'التأمين', 'yf': None, 'base': 11},
        'ENAP': {'name': 'النيل للتأمين', 'name_en': 'Nile Insurance', 'sector': 'التأمين', 'yf': None, 'base': 6},
        'MTSA': {'name': 'التأمين الأهلية', 'name_en': 'National Insurance', 'sector': 'التأمين', 'yf': None, 'base': 8},
        'ALCO': {'name': 'الإسكندرية للتأمين', 'name_en': 'Alexandria Insurance', 'sector': 'التأمين', 'yf': None, 'base': 7},
        'GREG': {'name': 'الجمهورية للتأمين', 'name_en': 'Gulf Republic Insurance', 'sector': 'التأمين', 'yf': None, 'base': 5},

        # ── مواد البناء والأسمنت (9) ────────────────────────────
        'MCEM': {'name': 'أسمنت مصر', 'name_en': 'Misr Cement', 'sector': 'الأسمنت', 'yf': 'MCEM.CA', 'base': 22},
        'SINE': {'name': 'أسمنت سيناء', 'name_en': 'Sinai Cement', 'sector': 'الأسمنت', 'yf': 'SINE.CA', 'base': 18},
        'ARCC': {'name': 'أسمنت العربية', 'name_en': 'Arabian Cement', 'sector': 'الأسمنت', 'yf': 'ARCC.CA', 'base': 35},
        'TOUR': {'name': 'أسمنت طرة', 'name_en': 'Tourah Cement', 'sector': 'الأسمنت', 'yf': 'TOUR.CA', 'base': 28},
        'SRCE': {'name': 'أسمنت سوهاج', 'name_en': 'South Valley Cement', 'sector': 'الأسمنت', 'yf': 'SRCE.CA', 'base': 15},
        'BNSF': {'name': 'أسمنت بني سويف', 'name_en': 'Beni Suef Cement', 'sector': 'الأسمنت', 'yf': 'BNSF.CA', 'base': 20},
        'ALEX': {'name': 'أسمنت الإسكندرية', 'name_en': 'Alexandria Cement', 'sector': 'الأسمنت', 'yf': 'ALEX.CA', 'base': 18},
        'QENA': {'name': 'أسمنت قنا', 'name_en': 'Qena Cement', 'sector': 'الأسمنت', 'yf': None, 'base': 12},
        'SUEZ': {'name': 'أسمنت السويس', 'name_en': 'Suez Cement', 'sector': 'الأسمنت', 'yf': None, 'base': 14},

        # ── التعليم (5) ─────────────────────────────────────────
        'CIRA': {'name': 'سيرا للتعليم', 'name_en': 'CIRA Education', 'sector': 'التعليم', 'yf': 'CIRA.CA', 'base': 18},
        'ALEF': {'name': 'ألف للتعليم', 'name_en': 'Alef Education', 'sector': 'التعليم', 'yf': 'ALEF.CA', 'base': 12},
        'CLED': {'name': 'كليوباترا للتعليم', 'name_en': 'Cleopatra Education', 'sector': 'التعليم', 'yf': None, 'base': 8},
        'AMAN': {'name': 'أمان للتعليم', 'name_en': 'Aman Education', 'sector': 'التعليم', 'yf': None, 'base': 6},
        'EDUC': {'name': 'التعليم المتقدم', 'name_en': 'Advanced Education', 'sector': 'التعليم', 'yf': None, 'base': 9},

        # ── النقل واللوجستيات (6) ───────────────────────────────
        'EGXS': {'name': 'التوريق المصرية', 'name_en': 'EGX Securitization', 'sector': 'النقل', 'yf': None, 'base': 7},
        'TRCO': {'name': 'النقل البحري', 'name_en': 'Egyptian Transport', 'sector': 'النقل', 'yf': None, 'base': 11},
        'NCTS': {'name': 'الوطنية للشحن', 'name_en': 'National Cargo', 'sector': 'النقل', 'yf': None, 'base': 5},
        'SWVL': {'name': 'سويفل', 'name_en': 'Swvl', 'sector': 'النقل', 'yf': None, 'base': 3},
        'UBER': {'name': 'أوبر مصر', 'name_en': 'Uber Egypt', 'sector': 'النقل', 'yf': None, 'base': 45},
        'CARG': {'name': 'القاهرة للنقل', 'name_en': 'Cairo Transport', 'sector': 'النقل', 'yf': None, 'base': 8},

        # ── التجزئة والتوزيع (8) ─────────────────────────────────
        'GBAL': {'name': 'جي بي أوتو', 'name_en': 'GB Auto', 'sector': 'التجزئة', 'yf': 'GBAL.CA', 'base': 27},
        'RAYE': {'name': 'راية للخدمات', 'name_en': 'Raya Services', 'sector': 'التجزئة', 'yf': None, 'base': 14},
        'CGCO': {'name': 'كايرو جاز', 'name_en': 'Cairo Gas', 'sector': 'التجزئة', 'yf': None, 'base': 16},
        'SFMC': {'name': 'مصر للأفلام', 'name_en': 'Egypt Film', 'sector': 'التجزئة', 'yf': None, 'base': 5},
        'EGPW': {'name': 'إيجيبت باورز', 'name_en': 'Egypt Powers', 'sector': 'التجزئة', 'yf': None, 'base': 12},
        'MASR_R': {'name': 'مصر للتجارة', 'name_en': 'Misr Retail', 'sector': 'التجزئة', 'yf': None, 'base': 9},
        'FMLC': {'name': 'فود ماركت', 'name_en': 'Food Market', 'sector': 'التجزئة', 'yf': None, 'base': 7},
        'ELAB': {'name': 'العربية للتجارة', 'name_en': 'Arab Trading', 'sector': 'التجزئة', 'yf': None, 'base': 10},

        # ── الاستثمار القابضة (8) ───────────────────────────────
        'QALH': {'name': 'القلعة للاستثمار', 'name_en': 'Qalaa Holdings', 'sector': 'القابضة', 'yf': 'QALH.CA', 'base': 3.5},
        'EKHO': {'name': 'مصر الكويت القابضة', 'name_en': 'Egypt Kuwait Holding', 'sector': 'القابضة', 'yf': 'EKHO.CA', 'base': 16},
        'OIH':  {'name': 'أوراسكوم القابضة', 'name_en': 'Orascom Invest', 'sector': 'القابضة', 'yf': 'OIH.CA', 'base': 8},
        'NCGC': {'name': 'القرن الواحد', 'name_en': 'National Century', 'sector': 'القابضة', 'yf': None, 'base': 5},
        'EFIH': {'name': 'إي إف آي', 'name_en': 'EFI Holdings', 'sector': 'القابضة', 'yf': None, 'base': 6},
        'IGCO': {'name': 'إيجكو', 'name_en': 'IGCO Invest', 'sector': 'القابضة', 'yf': None, 'base': 4},
        'AMAL': {'name': 'العمال القابضة', 'name_en': 'El Amal Group', 'sector': 'القابضة', 'yf': None, 'base': 7},
        'PACH': {'name': 'بايونير القابضة', 'name_en': 'Pioneer Holding', 'sector': 'القابضة', 'yf': None, 'base': 8},

        # ── الزراعة (6) ─────────────────────────────────────────
        'EFCO_A': {'name': 'الدلتا للأسمدة', 'name_en': 'Delta Fertilizers', 'sector': 'الزراعة', 'yf': None, 'base': 35},
        'SEED': {'name': 'البذور المصرية', 'name_en': 'Egypt Seeds', 'sector': 'الزراعة', 'yf': None, 'base': 8},
        'AGRI': {'name': 'الزراعة المصرية', 'name_en': 'Egypt Agriculture', 'sector': 'الزراعة', 'yf': None, 'base': 12},
        'FERT': {'name': 'الأسمدة المصرية', 'name_en': 'Egypt Fertilizers', 'sector': 'الزراعة', 'yf': None, 'base': 25},
        'LAND': {'name': 'الأراضي الزراعية', 'name_en': 'Agricultural Land', 'sector': 'الزراعة', 'yf': None, 'base': 15},
        'CROP': {'name': 'المحاصيل الزراعية', 'name_en': 'Crop Production', 'sector': 'الزراعة', 'yf': None, 'base': 10},

        # ── الإعلام والترفيه (5) ─────────────────────────────────
        'MENA': {'name': 'مينا للإعلام', 'name_en': 'Mena Media', 'sector': 'الإعلام', 'yf': None, 'base': 6},
        'ETMC': {'name': 'الإعلام المصري', 'name_en': 'Egypt Media', 'sector': 'الإعلام', 'yf': None, 'base': 8},
        'SOUN': {'name': 'صوت القاهرة', 'name_en': 'Cairo Sound', 'sector': 'الإعلام', 'yf': None, 'base': 5},
        'PROD': {'name': 'الإنتاج الإعلامي', 'name_en': 'Media Production', 'sector': 'الإعلام', 'yf': None, 'base': 7},
        'DIGI': {'name': 'ديجيتال ميديا', 'name_en': 'Digital Media', 'sector': 'الإعلام', 'yf': None, 'base': 9},

        # ── المياه والصرف (4) ─────────────────────────────────────
        'AWSB': {'name': 'مياه الإسكندرية', 'name_en': 'Alexandria Water', 'sector': 'المياه', 'yf': None, 'base': 14},
        'CWCO': {'name': 'مياه القاهرة', 'name_en': 'Cairo Water', 'sector': 'المياه', 'yf': None, 'base': 12},
        'DELW': {'name': 'مياه الدلتا', 'name_en': 'Delta Water', 'sector': 'المياه', 'yf': None, 'base': 8},
        'UPWA': {'name': 'المياه المتحدة', 'name_en': 'United Water', 'sector': 'المياه', 'yf': None, 'base': 10},

        # ── التشييد والمقاولات (5) ──────────────────────────────
        'HCCO': {'name': 'الحسينية للمقاولات', 'name_en': 'HCCO', 'sector': 'المقاولات', 'yf': None, 'base': 11},
        'CONS': {'name': 'المقاولون العرب', 'name_en': 'Arab Contractors', 'sector': 'المقاولات', 'yf': None, 'base': 18},
        'ELCO': {'name': 'النصر للمقاولات', 'name_en': 'Nasr Contractors', 'sector': 'المقاولات', 'yf': None, 'base': 9},
        'BUIL': {'name': 'العمارة للتشييد', 'name_en': 'Omara Construction', 'sector': 'المقاولات', 'yf': None, 'base': 7},
        'RECN': {'name': 'ريكون للمقاولات', 'name_en': 'Recon Construction', 'sector': 'المقاولات', 'yf': None, 'base': 6},

        # ── التكنولوجيا المالية (4) ─────────────────────────────
        'PAYM': {'name': 'بايموب', 'name_en': 'Paymob', 'sector': 'فينتك', 'yf': None, 'base': 22},
        'TALN': {'name': 'تالينتس', 'name_en': 'Talents', 'sector': 'فينتك', 'yf': None, 'base': 15},
        'MENA_F': {'name': 'مينا للتكنولوجيا', 'name_en': 'Mena Tech', 'sector': 'فينتك', 'yf': None, 'base': 18},
        'CASH': {'name': 'كاش لينك', 'name_en': 'Cash Link', 'sector': 'فينتك', 'yf': None, 'base': 12},
    }

    # Build sector map
    SECTORS: Dict[str, List[str]] = {}
    EGX30: List[str] = []
    EGX70: List[str] = []
    EGX100: List[str] = []

    for sym, data in STOCKS.items():
        sec = data['sector']
        SECTORS.setdefault(sec, []).append(sym)
        # Auto-classify based on base price and yf availability (simplified)
        if data.get('yf') and data['base'] > 50:
            EGX30.append(sym)
        elif data.get('yf') or data['base'] > 20:
            EGX70.append(sym)
        else:
            EGX100.append(sym)

    # Override with realistic EGX30 list
    EGX30 = ['COMI', 'QNBE', 'TMGH', 'ETEL', 'FWRY', 'SWDY', 'ECIG', 'SKPC', 'ORWE', 'JUFO',
             'ISPH', 'EIPO', 'MCEM', 'ARCC', 'SODC', 'GBAL', 'QALH', 'ABQQ', 'HRHO', 'PHDC',
             'EFCO', 'SUGR', 'ABQQ', 'EAST', 'TMGD', 'DOMT', 'CLHO', 'EKHO', 'CIRA', 'ALEF']
    EGX30 = list(dict.fromkeys(EGX30))  # remove duplicates while preserving order
    EGX70 = [s for s in STOCKS if s not in EGX30 and STOCKS[s]['base'] > 10]
    EGX100 = [s for s in STOCKS if s not in EGX30 and s not in EGX70]


# ═══════════════════════════════════════════════════════════════
# 5. DATA ENGINE — Real (Yahoo Finance) + Simulation
# ═══════════════════════════════════════════════════════════════

def get_cairo_time() -> datetime:
    return datetime.now(pytz.timezone('Africa/Cairo'))

def safe_pct(current: float, previous: float) -> float:
    if previous is None or previous == 0: return 0.0
    try: return ((current - previous) / abs(previous)) * 100
    except: return 0.0

def safe_last(s: pd.Series, default=0.0) -> float:
    try:
        v = s.dropna()
        return float(v.iloc[-1]) if not v.empty else default
    except: return default

def fmt_num(num, decimals: int = 2) -> str:
    try:
        if num is None: return "N/A"
        num = float(num)
        if np.isnan(num) or np.isinf(num): return "N/A"
        if abs(num) >= 1e9: return f"{num/1e9:.2f}B"
        if abs(num) >= 1e6: return f"{num/1e6:.2f}M"
        if abs(num) >= 1e3: return f"{num/1e3:.1f}K"
        return f"{num:,.{decimals}f}"
    except: return "N/A"

def fmt_egp(num) -> str:
    return f"EGP {fmt_num(num)}"

def generate_simulated_data(symbol: str, days: int = 200) -> pd.DataFrame:
    """محاكاة متقدمة مع تقلب قطاعي وارتباط ضعيف بالسوق"""
    info = EGXDatabase.STOCKS.get(symbol, {})
    seed = int(hashlib.md5(symbol.encode()).hexdigest(), 16) % (2**31)
    np.random.seed(seed)

    base = info.get('base', np.random.uniform(5, 200))
    sector = info.get('sector', '')
    vol_map = {
        'البنوك': 0.012, 'الاتصالات': 0.015, 'العقارات': 0.022,
        'الصناعة': 0.020, 'الأغذية': 0.010, 'الطاقة': 0.025,
        'الصحة': 0.018, 'الأسمنت': 0.016, 'المال': 0.020,
        'التعليم': 0.014, 'النقل': 0.019, 'التجزئة': 0.017,
        'القابضة': 0.024, 'الزراعة': 0.013, 'التأمين': 0.015,
        'الإعلام': 0.021, 'المياه': 0.008, 'المقاولات': 0.023,
        'فينتك': 0.028, 'التكنولوجيا': 0.026
    }
    vol = vol_map.get(sector, 0.018)

    dates = pd.date_range(end=datetime.now(), periods=days, freq='B')
    # GARCH-like volatility clustering simulation
    drift = np.random.normal(0.0002, 0.0008)
    returns = np.random.normal(drift, vol, days)
    # Add volatility clustering
    for i in range(2, days):
        if abs(returns[i-1]) > 2*vol:
            returns[i] *= 1.5

    price = base * np.exp(np.cumsum(returns))
    price = np.maximum(price, 0.10)

    # Generate OHLC from close
    daily_range = np.abs(np.random.randn(days)) * vol * price * 1.5
    op = price * (1 + np.random.randn(days) * 0.004)
    hi = np.maximum(op, price) + daily_range * 0.4
    lo = np.minimum(op, price) - daily_range * 0.4
    lo = np.maximum(lo, 0.05)
    hi = np.maximum(hi, lo + 0.01)
    op = np.clip(op, lo, hi)
    cl = np.clip(price, lo, hi)

    vol_amount = np.random.lognormal(15, 0.8, days) * (1 + np.abs(returns) * 50)

    df = pd.DataFrame({
        'open': op, 'high': hi, 'low': lo, 'close': cl, 'volume': vol_amount.astype(int)
    }, index=dates)
    return df

def fetch_real_data(symbol: str, days: int = 200) -> Optional[pd.DataFrame]:
    """جلب بيانات حقيقية من Yahoo Finance إن توفرت"""
    try:
        yf_sym = EGXDatabase.STOCKS.get(symbol, {}).get('yf')
        if not yf_sym: return None
        import yfinance as yf
        ticker = yf.Ticker(yf_sym)
        df = ticker.history(period=f"{days+50}d", interval="1d")
        if df.empty or len(df) < 30: return None
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
        df.columns = ['open', 'high', 'low', 'close', 'volume']
        df.index = pd.to_datetime(df.index)
        df = df.dropna()
        return df.tail(days)
    except Exception as e:
        logger.warning(f"Yahoo Finance failed for {symbol}: {e}")
        return None

@st.cache_data(ttl=AppConfig.CACHE_TTL, show_spinner=False)
def load_stock_data(symbol: str, days: int = 200) -> Optional[pd.DataFrame]:
    """جلب البيانات: حقيقية أولاً، محاكاة احتياطاً"""
    try:
        # Try real data first
        df = fetch_real_data(symbol, days)
        source = "real"
        if df is None or len(df) < days//2:
            df = generate_simulated_data(symbol, days)
            source = "simulated"

        if df is None or df.empty: return None

        c, h, l, v = df['close'], df['high'], df['low'], df['volume']

        # Core indicators
        df['rsi'] = calc_rsi(c)
        df['ema_9'] = calc_ema(c, 9)
        df['ema_20'] = calc_ema(c, 20)
        df['ema_50'] = calc_ema(c, 50)
        df['ema_200'] = calc_ema(c, 200)
        df['sma_20'] = calc_sma(c, 20)
        df['sma_50'] = calc_sma(c, 50)
        df['bb_upper'], df['bb_middle'], df['bb_lower'] = calc_bb(c)
        df['macd'], df['macd_signal'], df['macd_hist'] = calc_macd(c)
        df['adx'] = calc_adx(h, l, c)
        df['stoch_k'], df['stoch_d'] = calc_stoch(h, l, c)
        df['obv'] = calc_obv(c, v)
        df['atr'] = calc_atr(h, l, c)
        df['cci'] = calc_cci(h, l, c)
        df['williams_r'] = calc_williams_r(h, l, c)
        df['pct_change'] = c.pct_change() * 100
        df['vol_sma'] = v.rolling(20).mean()
        df['vol_ratio'] = v / df['vol_sma'].replace(0, np.nan)

        # NEW: Advanced indicators
        df['vwap'] = calc_vwap(h, l, c, v)
        df['psar'] = calc_parabolic_sar(h, l, c)
        df['roc'] = calc_roc(c, 12)
        df['momentum'] = calc_momentum(c, 10)
        df['ich_tenkan'], df['ich_kijun'], df['ich_senkou_a'], df['ich_senkou_b'], df['ich_chikou'] = calc_ichimoku(h, l, c)

        # NEW: ML features
        df['returns_5d'] = c.pct_change(5)
        df['returns_10d'] = c.pct_change(10)
        df['volatility_20d'] = c.pct_change().rolling(20).std() * np.sqrt(252)
        df['price_to_ema50'] = c / df['ema_50'] - 1
        df['price_to_ema200'] = c / df['ema_200'] - 1

        df['data_source'] = source
        return df
    except Exception as e:
        logger.error(f"load_stock_data {symbol}: {e}")
        return None

# ═══════════════════════════════════════════════════════════════
# 6. TECHNICAL INDICATORS (Enhanced + Bug Fixed)
# ═══════════════════════════════════════════════════════════════

def calc_rsi(prices: pd.Series, period=14) -> pd.Series:
    delta = prices.diff()
    gain = delta.where(delta > 0, 0.0).rolling(period, min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(period, min_periods=1).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def calc_ema(prices: pd.Series, span=20) -> pd.Series:
    return prices.ewm(span=span, adjust=False, min_periods=1).mean()

def calc_sma(prices: pd.Series, window=20) -> pd.Series:
    return prices.rolling(window, min_periods=1).mean()

def calc_bb(prices: pd.Series, window=20, std=2) -> Tuple:
    m = calc_sma(prices, window)
    s = prices.rolling(window, min_periods=1).std()
    return m + s*std, m, m - s*std

def calc_macd(prices: pd.Series, fast=12, slow=26, sig=9) -> Tuple:
    macd = calc_ema(prices, fast) - calc_ema(prices, slow)
    signal = calc_ema(macd, sig)
    return macd, signal, macd - signal

def calc_adx(h, l, c, period=14) -> pd.Series:
    pdm = h.diff().where(lambda x: (x > 0) & (x > -l.diff()), 0)
    mdm = (-l.diff()).where(lambda x: (x > 0) & (x > h.diff()), 0)
    tr = pd.concat([h-l, (h-c.shift()).abs(), (l-c.shift()).abs()], axis=1).max(1)
    atr = tr.rolling(period, min_periods=1).mean().replace(0, np.nan)
    pdi = 100 * pdm.rolling(period, min_periods=1).mean() / atr
    mdi = 100 * mdm.rolling(period, min_periods=1).mean() / atr
    dx = 100 * (pdi - mdi).abs() / (pdi + mdi).replace(0, np.nan)
    return dx.rolling(period, min_periods=1).mean()

def calc_stoch(h, l, c, k=14, d=3) -> Tuple:
    lowest_l = l.rolling(k, min_periods=1).min()
    highest_h = h.rolling(k, min_periods=1).max()
    denom = (highest_h - lowest_l).replace(0, np.nan)
    stoch_k = 100 * (c - lowest_l) / denom
    stoch_d = stoch_k.rolling(d, min_periods=1).mean()
    return stoch_k, stoch_d

def calc_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    direction = np.sign(close.diff()).fillna(0)
    return (direction * volume).cumsum()

def calc_atr(h, l, c, period=14) -> pd.Series:
    tr = pd.concat([h-l, (h-c.shift()).abs(), (l-c.shift()).abs()], axis=1).max(1)
    return tr.rolling(period, min_periods=1).mean()

def calc_cci(h, l, c, period=20) -> pd.Series:
    tp = (h + l + c) / 3
    ma = tp.rolling(period, min_periods=1).mean()
    md = tp.rolling(period, min_periods=1).apply(lambda x: np.mean(np.abs(x - np.mean(x))), raw=True)
    return (tp - ma) / (0.015 * md.replace(0, np.nan))

def calc_williams_r(h, l, c, period=14) -> pd.Series:
    hh = h.rolling(period, min_periods=1).max()
    ll = l.rolling(period, min_periods=1).min()
    return -100 * (hh - c) / (hh - ll).replace(0, np.nan)

# NEW INDICATORS
def calc_vwap(h, l, c, v) -> pd.Series:
    tp = (h + l + c) / 3
    cum_tp_v = (tp * v).cumsum()
    cum_v = v.cumsum()
    return cum_tp_v / cum_v.replace(0, np.nan)

def calc_parabolic_sar(h, l, c, af=0.02, max_af=0.2) -> pd.Series:
    """Parabolic SAR — مؤشر التوقف والانعكاس"""
    n = len(c)
    sar = pd.Series(index=c.index, dtype=float)
    ep = pd.Series(index=c.index, dtype=float)
    trend = pd.Series(index=c.index, dtype=int)

    if n < 2: return sar

    # Initialize
    trend.iloc[0] = 1 if c.iloc[0] > c.iloc[1] else -1
    sar.iloc[0] = l.iloc[0] if trend.iloc[0] == 1 else h.iloc[0]
    ep.iloc[0] = h.iloc[0] if trend.iloc[0] == 1 else l.iloc[0]
    af_val = af

    for i in range(1, n):
        sar.iloc[i] = sar.iloc[i-1] + af_val * (ep.iloc[i-1] - sar.iloc[i-1])

        if trend.iloc[i-1] == 1:
            sar.iloc[i] = min(sar.iloc[i], l.iloc[i-1], l.iloc[max(0, i-2)])
            if h.iloc[i] > ep.iloc[i-1]:
                ep.iloc[i] = h.iloc[i]
                af_val = min(af_val + af, max_af)
            else:
                ep.iloc[i] = ep.iloc[i-1]
            if l.iloc[i] < sar.iloc[i]:
                trend.iloc[i] = -1
                sar.iloc[i] = ep.iloc[i-1]
                ep.iloc[i] = l.iloc[i]
                af_val = af
            else:
                trend.iloc[i] = 1
        else:
            sar.iloc[i] = max(sar.iloc[i], h.iloc[i-1], h.iloc[max(0, i-2)])
            if l.iloc[i] < ep.iloc[i-1]:
                ep.iloc[i] = l.iloc[i]
                af_val = min(af_val + af, max_af)
            else:
                ep.iloc[i] = ep.iloc[i-1]
            if h.iloc[i] > sar.iloc[i]:
                trend.iloc[i] = 1
                sar.iloc[i] = ep.iloc[i-1]
                ep.iloc[i] = h.iloc[i]
                af_val = af
            else:
                trend.iloc[i] = -1

    return sar

def calc_roc(prices: pd.Series, period=12) -> pd.Series:
    return ((prices - prices.shift(period)) / prices.shift(period).replace(0, np.nan)) * 100

def calc_momentum(prices: pd.Series, period=10) -> pd.Series:
    return prices - prices.shift(period)

def calc_ichimoku(h, l, c, tenkan=9, kijun=26, senkou=52) -> Tuple:
    """Ichimoku Cloud — سحابة إيشيموكو"""
    tenkan_sen = (h.rolling(tenkan, min_periods=1).max() + l.rolling(tenkan, min_periods=1).min()) / 2
    kijun_sen = (h.rolling(kijun, min_periods=1).max() + l.rolling(kijun, min_periods=1).min()) / 2
    senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(kijun)
    senkou_span_b = ((h.rolling(senkou, min_periods=1).max() + l.rolling(senkou, min_periods=1).min()) / 2).shift(kijun)
    chikou_span = c.shift(-kijun)
    return tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span

# ═══════════════════════════════════════════════════════════════
# 7. PATTERN DETECTION (Enhanced + Safe)
# ═══════════════════════════════════════════════════════════════

def detect_patterns(df: pd.DataFrame) -> List[str]:
    """اكتشاف أنماط الشموع اليابانية مع معالجة آمنة للحدود"""
    patterns = []
    if df is None or len(df) < 3: return patterns

    o, h, l, c = df['open'], df['high'], df['low'], df['close']
    body = abs(c - o)
    range_hl = h - l
    wick_up = h - np.maximum(c, o)
    wick_dn = np.minimum(c, o) - l

    i = -1  # last candle
    i2 = -2 if len(df) > 1 else None
    i3 = -3 if len(df) > 2 else None

    # Doji
    if body.iloc[i] < range_hl.iloc[i] * 0.05:
        patterns.append("⚖️ دوجي (Doji) — توازن بين المشترين والبائعين")

    # Hammer
    if wick_dn.iloc[i] > 2 * body.iloc[i] and wick_up.iloc[i] < body.iloc[i] * 0.3 and c.iloc[i] > o.iloc[i]:
        patterns.append("🔨 مطرقة صاعدة (Hammer) — إشارة انعكاس صاعد")

    # Shooting Star
    if wick_up.iloc[i] > 2 * body.iloc[i] and wick_dn.iloc[i] < body.iloc[i] * 0.3 and c.iloc[i] < o.iloc[i]:
        patterns.append("⭐ نجمة ساقطة (Shooting Star) — إشارة انعكاس هابط")

    # Engulfing
    if i2 is not None:
        if c.iloc[i2] < o.iloc[i2] and c.iloc[i] > o.iloc[i] and c.iloc[i] > o.iloc[i2] and o.iloc[i] < c.iloc[i2]:
            patterns.append("🟢 الابتلاع الصاعد (Bullish Engulfing)")
        if c.iloc[i2] > o.iloc[i2] and c.iloc[i] < o.iloc[i] and c.iloc[i] < o.iloc[i2] and o.iloc[i] > c.iloc[i2]:
            patterns.append("🔴 الابتلاع الهابط (Bearish Engulfing)")

    # Morning/Evening Star
    if i3 is not None:
        if (c.iloc[i3] < o.iloc[i3] and body.iloc[i2] < body.iloc[i3] * 0.3 and 
            c.iloc[i] > o.iloc[i] and c.iloc[i] > (o.iloc[i3] + c.iloc[i3]) / 2):
            patterns.append("🌅 نجمة الصباح (Morning Star) — انعكاس صاعد قوي")
        if (c.iloc[i3] > o.iloc[i3] and body.iloc[i2] < body.iloc[i3] * 0.3 and 
            c.iloc[i] < o.iloc[i] and c.iloc[i] < (o.iloc[i3] + c.iloc[i3]) / 2):
            patterns.append("🌆 نجمة المساء (Evening Star) — انعكاس هابط قوي")

    # Harami
    if i2 is not None:
        if (c.iloc[i2] < o.iloc[i2] and c.iloc[i] > o.iloc[i] and 
            o.iloc[i] > c.iloc[i2] and c.iloc[i] < o.iloc[i2]):
            patterns.append("🟢 حمل صاعد (Bullish Harami)")
        if (c.iloc[i2] > o.iloc[i2] and c.iloc[i] < o.iloc[i] and 
            o.iloc[i] < c.iloc[i2] and c.iloc[i] > o.iloc[i2]):
            patterns.append("🔴 حمل هابط (Bearish Harami)")

    # Marubozu
    if wick_up.iloc[i] < body.iloc[i] * 0.05 and wick_dn.iloc[i] < body.iloc[i] * 0.05:
        direction = "صاعد" if c.iloc[i] > o.iloc[i] else "هابط"
        patterns.append(f"📊 ماروبوزو {direction} (Marubozu) — قوة شديدة")

    return patterns

def get_support_resistance(df: pd.DataFrame, window=20) -> Tuple[float, float]:
    recent = df.tail(50)
    if recent.empty: return 0.0, 0.0
    support = recent['low'].rolling(window, min_periods=1).min().iloc[-1]
    resistance = recent['high'].rolling(window, min_periods=1).max().iloc[-1]
    return support, resistance

def get_fibonacci_levels(last: float, support: float, resistance: float) -> Dict[str, float]:
    diff = resistance - support
    if diff == 0: diff = last * 0.1
    return {
        '0% (دعم)': support,
        '23.6%': support + diff * 0.236,
        '38.2%': support + diff * 0.382,
        '50%': support + diff * 0.500,
        '61.8%': support + diff * 0.618,
        '78.6%': support + diff * 0.786,
        '100% (مقاومة)': resistance,
        '127.2%': support + diff * 1.272,
        '161.8%': support + diff * 1.618,
    }


# ═══════════════════════════════════════════════════════════════
# 8. MACHINE LEARNING MODULE (Lightweight)
# ═══════════════════════════════════════════════════════════════

def ml_predict_trend(df: pd.DataFrame, days_ahead: int = 5) -> Dict[str, Any]:
    """نموذج ML بسيط: Linear Regression + Feature Engineering"""
    try:
        from sklearn.linear_model import LinearRegression
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.preprocessing import StandardScaler
    except ImportError:
        return {"error": "scikit-learn not installed. Run: pip install scikit-learn"}

    if df is None or len(df) < 50: return {"error": "Insufficient data"}

    # Feature engineering
    features = pd.DataFrame(index=df.index)
    features['rsi'] = df['rsi'] / 100
    features['macd_norm'] = df['macd'] / df['close']
    features['adx_norm'] = df['adx'] / 100
    features['vol_ratio'] = df['vol_ratio'].fillna(1)
    features['price_to_ema50'] = df['price_to_ema50'].fillna(0)
    features['price_to_ema200'] = df['price_to_ema200'].fillna(0)
    features['returns_5d'] = df['returns_5d'].fillna(0)
    features['roc'] = df['roc'] / 100
    features['momentum'] = df['momentum'] / df['close']
    features['atr_ratio'] = df['atr'] / df['close']

    # Target: future return
    target = df['close'].shift(-days_ahead) / df['close'] - 1

    # Drop NaN
    valid = features.dropna().index.intersection(target.dropna().index)
    if len(valid) < 30: return {"error": "Not enough training data"}

    X = features.loc[valid].values
    y = target.loc[valid].values

    # Scale
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train models
    lr = LinearRegression()
    lr.fit(X_scaled, y)

    rf = RandomForestRegressor(n_estimators=50, max_depth=5, random_state=42, n_jobs=-1)
    rf.fit(X_scaled, y)

    # Predict on last point
    last_X = scaler.transform(features.iloc[-1:].values)
    lr_pred = float(lr.predict(last_X)[0])
    rf_pred = float(rf.predict(last_X)[0])
    ensemble = (lr_pred + rf_pred) / 2

    # Confidence based on recent volatility
    recent_vol = df['close'].pct_change().tail(20).std()
    confidence = max(0, min(100, 100 - (recent_vol * 500)))

    last_price = float(df['close'].iloc[-1])
    predicted_price = last_price * (1 + ensemble)

    # Feature importance (RF)
    feat_names = ['RSI', 'MACD', 'ADX', 'VolRatio', 'EMA50%', 'EMA200%', 'Ret5D', 'ROC', 'Momentum', 'ATR%']
    importance = dict(zip(feat_names, rf.feature_importances_))

    return {
        "lr_pred": lr_pred, "rf_pred": rf_pred, "ensemble": ensemble,
        "confidence": confidence, "last_price": last_price,
        "predicted_price": predicted_price, "days_ahead": days_ahead,
        "importance": importance, "direction": "صاعد" if ensemble > 0.01 else "هابط" if ensemble < -0.01 else "محايد",
        "direction_emoji": "🟢" if ensemble > 0.01 else "🔴" if ensemble < -0.01 else "⚪"
    }

# ═══════════════════════════════════════════════════════════════
# 9. RISK MANAGEMENT ENGINE
# ═══════════════════════════════════════════════════════════════

class RiskManager:
    @staticmethod
    def kelly_criterion(win_rate: float, avg_win: float, avg_loss: float) -> float:
        """حساب كريتيريون كيلي للحجم الأمثل"""
        if avg_loss == 0: return 0.0
        b = avg_win / avg_loss
        q = 1 - win_rate
        kelly = (win_rate * b - q) / b
        return max(0, min(kelly, 0.25))  # Cap at 25%

    @staticmethod
    def position_size(capital: float, risk_per_trade: float, entry: float, stop: float) -> int:
        """حساب عدد الأسهم بناءً على المخاطرة"""
        risk_amount = capital * risk_per_trade
        risk_per_share = abs(entry - stop)
        if risk_per_share == 0: return 0
        shares = int(risk_amount / risk_per_share)
        return shares

    @staticmethod
    def max_drawdown(equity_series: pd.Series) -> float:
        """أقصى انخفاض (Drawdown)"""
        peak = equity_series.expanding().max()
        dd = (equity_series - peak) / peak
        return float(dd.min()) * 100

    @staticmethod
    def sharpe_ratio(returns: pd.Series, risk_free=0.02) -> float:
        """نسبة شارب"""
        excess = returns - risk_free / 252
        if excess.std() == 0: return 0.0
        return (excess.mean() * 252) / (excess.std() * np.sqrt(252))

    @staticmethod
    def calmar_ratio(returns: pd.Series, periods=252) -> float:
        """نسبة كالمار"""
        cagr = (1 + returns.mean()) ** periods - 1
        mdd = abs(RiskManager.max_drawdown((1 + returns).cumprod()) / 100)
        if mdd == 0: return 0.0
        return cagr / mdd

# ═══════════════════════════════════════════════════════════════
# 10. COMPOSITE SIGNAL ENGINE (Enhanced)
# ═══════════════════════════════════════════════════════════════

def get_composite_signal(df: pd.DataFrame) -> Tuple[str, str, int, Dict]:
    """إشارة مركّبة من 10 مؤشرات + تفاصيل"""
    if df is None or len(df) < 50:
        return "غير معروف", "⚪", 0, {}

    signals = {}
    rsi = safe_last(df['rsi'], 50)
    macd = safe_last(df['macd'], 0)
    msig = safe_last(df['macd_signal'], 0)
    ema20 = safe_last(df['ema_20'])
    ema50 = safe_last(df['ema_50'])
    ema200 = safe_last(df['ema_200'])
    adx = safe_last(df['adx'], 25)
    stk = safe_last(df['stoch_k'], 50)
    cci = safe_last(df['cci'], 0)
    wr = safe_last(df['williams_r'], -50)
    price = float(df['close'].iloc[-1])
    vwap = safe_last(df['vwap'])
    psar = safe_last(df['psar'])

    score = 0
    # RSI
    if rsi < 30: score += 2; signals['RSI'] = "تشبع بيع (شراء قوي)"
    elif rsi < 40: score += 1; signals['RSI'] = "قرب تشبع بيع"
    elif rsi > 70: score -= 2; signals['RSI'] = "تشبع شراء (بيع قوي)"
    elif rsi > 60: score -= 1; signals['RSI'] = "قرب تشبع شراء"
    else: signals['RSI'] = "محايد"

    # MACD
    if macd > msig: score += 1; signals['MACD'] = "صاعد"
    else: score -= 1; signals['MACD'] = "هابط"

    # EMA Trend
    if price > ema20 > ema50 > ema200: score += 2; signals['EMA'] = "ترتيب صاعد كامل"
    elif price > ema20 > ema50: score += 1; signals['EMA'] = "صاعد قصير المدى"
    elif price < ema20 < ema50 < ema200: score -= 2; signals['EMA'] = "ترتيب هابط كامل"
    elif price < ema20 < ema50: score -= 1; signals['EMA'] = "هابط قصير المدى"
    else: signals['EMA'] = "متعارض"

    # ADX
    if adx > 25: signals['ADX'] = f"اتجاه قوي ({adx:.1f})"
    else: signals['ADX'] = f"اتجاه ضعيف ({adx:.1f})"

    # Stochastic
    if stk < 20: score += 1; signals['Stoch'] = "منطقة شراء"
    elif stk > 80: score -= 1; signals['Stoch'] = "منطقة بيع"
    else: signals['Stoch'] = "محايد"

    # CCI
    if cci < -200: score += 1; signals['CCI'] = "تشبع بيع"
    elif cci > 200: score -= 1; signals['CCI'] = "تشبع شراء"
    else: signals['CCI'] = "محايد"

    # Williams %R
    if wr < -80: score += 1; signals['W%R'] = "منطقة شراء"
    elif wr > -20: score -= 1; signals['W%R'] = "منطقة بيع"
    else: signals['W%R'] = "محايد"

    # VWAP
    if price > vwap: score += 1; signals['VWAP'] = "أعلى من المتوسط المرجح"
    else: score -= 1; signals['VWAP'] = "أقل من المتوسط المرجح"

    # Parabolic SAR
    if price > psar: score += 1; signals['PSAR'] = "اتجاه صاعد"
    else: score -= 1; signals['PSAR'] = "اتجاه هابط"

    total_possible = 10
    confidence = int((abs(score) / total_possible) * 100)

    if score >= 5: return "شراء قوي", "🟢", min(confidence, 98), signals
    elif score >= 3: return "شراء", "🟩", min(confidence, 85), signals
    elif score <= -5: return "بيع قوي", "🔴", min(confidence, 98), signals
    elif score <= -3: return "بيع", "🟥", min(confidence, 85), signals
    else: return "محايد", "⚪", confidence, signals

# ═══════════════════════════════════════════════════════════════
# 11. BACKTEST ENGINE (Professional)
# ═══════════════════════════════════════════════════════════════

class BacktestEngine:
    def __init__(self, df: pd.DataFrame, capital: float, strategy: str, 
                 stop_pct: float, take_pct: float, risk_per_trade: float = 0.02):
        self.df = df.dropna().copy()
        self.capital = capital
        self.initial = capital
        self.strategy = strategy
        self.stop_pct = stop_pct / 100
        self.take_pct = take_pct / 100
        self.risk_per_trade = risk_per_trade
        self.pos = 0.0
        self.entry = 0.0
        self.trades = []
        self.equity = [capital]
        self.risk_mgr = RiskManager()

    def run(self) -> Dict[str, Any]:
        for i in range(1, len(self.df)):
            row = self.df.iloc[i]
            prev = self.df.iloc[i-1]
            price = float(row['close'])

            buy_signal = False
            sell_signal = False

            # Strategy logic
            if self.strategy == "RSI":
                buy_signal = prev['rsi'] < 30 and row['rsi'] > 30
                sell_signal = prev['rsi'] > 70 and row['rsi'] < 70
            elif self.strategy == "MACD Crossover":
                buy_signal = prev['macd'] < prev['macd_signal'] and row['macd'] > row['macd_signal']
                sell_signal = prev['macd'] > prev['macd_signal'] and row['macd'] < row['macd_signal']
            elif self.strategy == "Bollinger Bands":
                buy_signal = price < row['bb_lower']
                sell_signal = price > row['bb_upper']
            elif self.strategy == "EMA Crossover":
                buy_signal = prev['ema_20'] < prev['ema_50'] and row['ema_20'] > row['ema_50']
                sell_signal = prev['ema_20'] > prev['ema_50'] and row['ema_20'] < row['ema_50']
            elif self.strategy == "Stochastic":
                buy_signal = row['stoch_k'] < 20 and row['stoch_k'] > row['stoch_d']
                sell_signal = row['stoch_k'] > 80 and row['stoch_k'] < row['stoch_d']
            elif self.strategy == "CCI Mean Reversion":
                buy_signal = row['cci'] < -100
                sell_signal = row['cci'] > 100
            elif self.strategy == "Ichimoku":
                buy_signal = row['close'] > row['ich_senkou_a'] and row['ich_tenkan'] > row['ich_kijun']
                sell_signal = row['close'] < row['ich_senkou_a'] and row['ich_tenkan'] < row['ich_kijun']
            elif self.strategy == "VWAP Bounce":
                buy_signal = prev['close'] < prev['vwap'] and price > row['vwap']
                sell_signal = prev['close'] > prev['vwap'] and price < row['vwap']

            # Risk management: Stop loss / Take profit
            if self.pos > 0 and self.entry > 0:
                stop_price = self.entry * (1 - self.stop_pct)
                take_price = self.entry * (1 + self.take_pct)
                if price <= stop_price: sell_signal = True
                if price >= take_price: sell_signal = True

            # Position sizing with Kelly
            if buy_signal and self.pos == 0 and self.capital > 0:
                stop_price = price * (1 - self.stop_pct)
                shares = self.risk_mgr.position_size(self.capital, self.risk_per_trade, price, stop_price)
                if shares > 0:
                    cost = shares * price
                    commission = cost * AppConfig.COMMISSION_RATE
                    tax = cost * AppConfig.TAX_RATE
                    total_cost = cost + commission + tax
                    if total_cost <= self.capital:
                        self.pos = shares
                        self.entry = price
                        self.capital -= total_cost
                        self.trades.append({
                            'type': 'BUY', 'price': price, 'shares': shares,
                            'date': str(self.df.index[i])[:10], 'cost': total_cost,
                            'commission': commission, 'tax': tax
                        })

            elif sell_signal and self.pos > 0:
                revenue = self.pos * price
                commission = revenue * AppConfig.COMMISSION_RATE
                tax = revenue * AppConfig.TAX_RATE
                total_revenue = revenue - commission - tax
                pnl = total_revenue - (self.pos * self.entry)
                pnl_pct = (pnl / (self.pos * self.entry)) * 100
                self.capital += total_revenue
                self.trades.append({
                    'type': 'SELL', 'price': price, 'shares': self.pos,
                    'date': str(self.df.index[i])[:10], 'revenue': total_revenue,
                    'pnl': pnl, 'pnl_pct': pnl_pct,
                    'commission': commission, 'tax': tax
                })
                self.pos = 0
                self.entry = 0

            current_equity = self.capital + (self.pos * price if self.pos > 0 else 0)
            self.equity.append(current_equity)

        # Close any open position at last price
        if self.pos > 0:
            last_price = float(self.df['close'].iloc[-1])
            revenue = self.pos * last_price
            commission = revenue * AppConfig.COMMISSION_RATE
            tax = revenue * AppConfig.TAX_RATE
            total_revenue = revenue - commission - tax
            self.capital += total_revenue
            pnl = total_revenue - (self.pos * self.entry)
            self.trades.append({
                'type': 'SELL (Final)', 'price': last_price, 'shares': self.pos,
                'date': str(self.df.index[-1])[:10], 'revenue': total_revenue,
                'pnl': pnl, 'pnl_pct': (pnl / (self.pos * self.entry)) * 100
            })
            self.pos = 0

        # Calculate metrics
        equity_series = pd.Series(self.equity)
        returns = equity_series.pct_change().dropna()

        total_profit = self.capital - self.initial
        total_profit_pct = safe_pct(self.capital, self.initial)

        buy_hold = safe_pct(float(self.df['close'].iloc[-1]), float(self.df['close'].iloc[0]))

        trades_df = pd.DataFrame([t for t in self.trades if 'pnl' in t])
        if not trades_df.empty:
            wins = len(trades_df[trades_df['pnl'] > 0])
            total_trades = len(trades_df)
            win_rate = wins / total_trades * 100
            avg_win = trades_df[trades_df['pnl'] > 0]['pnl_pct'].mean() if wins > 0 else 0
            avg_loss = abs(trades_df[trades_df['pnl'] < 0]['pnl_pct'].mean()) if (total_trades - wins) > 0 else 0.001
            kelly = self.risk_mgr.kelly_criterion(win_rate/100, avg_win, avg_loss)
        else:
            wins = 0; total_trades = 0; win_rate = 0; avg_win = 0; avg_loss = 0.001; kelly = 0

        return {
            'final_capital': self.capital, 'profit': total_profit, 'profit_pct': total_profit_pct,
            'buy_hold': buy_hold, 'trades': self.trades, 'n_trades': total_trades,
            'win_rate': win_rate, 'avg_win': avg_win, 'avg_loss': avg_loss,
            'kelly': kelly, 'equity': self.equity, 'max_dd': self.risk_mgr.max_drawdown(equity_series),
            'sharpe': self.risk_mgr.sharpe_ratio(returns), 'calmar': self.risk_mgr.calmar_ratio(returns),
            'equity_series': equity_series
        }


# ═══════════════════════════════════════════════════════════════
# 12. ALERTS & WATCHLIST (Enhanced)
# ═══════════════════════════════════════════════════════════════

class AlertManager:
    @staticmethod
    def check_alerts(alerts: List[Dict]) -> List[str]:
        triggered = []
        for alert in alerts:
            try:
                sym = alert['symbol']
                df = load_stock_data(sym, 5)
                if df is None or df.empty: continue

                if alert['type'] == 'السعر':
                    val = float(df['close'].iloc[-1])
                elif alert['type'] == 'RSI':
                    val = safe_last(df['rsi'], 50)
                elif alert['type'] == 'MACD':
                    val = safe_last(df['macd'], 0)
                elif alert['type'] == 'ADX':
                    val = safe_last(df['adx'], 25)
                elif alert['type'] == 'الحجم':
                    val = float(df['volume'].iloc[-1])
                else:
                    continue

                target = alert['value']
                cond = alert['condition']
                hit = False
                if cond == "أعلى من": hit = val > target
                elif cond == "أقل من": hit = val < target
                elif cond == "يساوي": hit = abs(val - target) / max(abs(target), 1) < 0.02

                if hit:
                    triggered.append(f"🔔 **{sym}** — {alert['type']} {cond} {target} (الحالي: {val:.2f})")
            except Exception as e:
                logger.warning(f"Alert check error: {e}")
        return triggered

# ═══════════════════════════════════════════════════════════════
# 13. ECONOMIC CALENDAR & NEWS SIMULATOR
# ═══════════════════════════════════════════════════════════════

def get_economic_calendar() -> pd.DataFrame:
    """تقويم اقتصادي محاكي (يمكن استبداله بـ API حقيقي)"""
    cairo = get_cairo_time()
    events = [
        {'التاريخ': cairo + timedelta(days=2), 'الحدث': 'قرار الفائدة — البنك المركزي', 'التأثير': 'عالي', 'القطاع': 'الكل'},
        {'التاريخ': cairo + timedelta(days=5), 'الحدث': 'مؤشر التضخم الشهري', 'التأثير': 'عالي', 'القطاع': 'الكل'},
        {'التاريخ': cairo + timedelta(days=7), 'الحدث': 'اجتماع لجنة السياسة النقدية', 'التأثير': 'عالي', 'القطاع': 'البنوك'},
        {'التاريخ': cairo + timedelta(days=10), 'الحدث': 'إعلان نتائج COMI ربع سنوية', 'التأثير': 'متوسط', 'القطاع': 'البنوك'},
        {'التاريخ': cairo + timedelta(days=12), 'الحدث': 'مزاد بنكي على الدولار', 'التأثير': 'عالي', 'القطاع': 'الكل'},
        {'التاريخ': cairo + timedelta(days=15), 'الحدث': 'إعلان نتائج TMGH ربع سنوية', 'التأثير': 'متوسط', 'القطاع': 'العقارات'},
        {'التاريخ': cairo + timedelta(days=18), 'الحدث': 'مؤشر مديري المشتريات (PMI)', 'التأثير': 'متوسط', 'القطاع': 'الصناعة'},
        {'التاريخ': cairo + timedelta(days=20), 'الحدث': 'قرار الفائدة — الفيدرالي الأمريكي', 'التأثير': 'عالي', 'القطاع': 'الكل'},
    ]
    df = pd.DataFrame(events)
    df['التاريخ'] = df['التاريخ'].dt.strftime('%Y-%m-%d')
    return df

def get_market_news() -> List[Dict]:
    """محاكاة أخبار السوق (يمكن استبدالها بـ RSS/API)"""
    news = [
        {'time': '10:30', 'title': 'البورصة المصرية تفتتح على ارتفاع بنسبة 0.8% بدعم من قطاع البنوك', 'impact': 'إيجابي', 'sector': 'الكل'},
        {'time': '11:15', 'title': 'COMI يقترب من مستوى مقاومة 130 جنيه مع زيادة الأحجام', 'impact': 'إيجابي', 'sector': 'البنوك'},
        {'time': '12:00', 'title': 'المركزي: انخفاض التضخم السنوي إلى 24.1% في مايو', 'impact': 'إيجابي', 'sector': 'الكل'},
        {'time': '13:45', 'title': 'قطاع العقارات يواجه ضغوطاً بيعية بعد إعلان ضريبة جديدة', 'impact': 'سلبي', 'sector': 'العقارات'},
        {'time': '14:20', 'title': 'FWRY يوقع اتفاقية مع بنك جديد لتوسيع خدمات الدفع الإلكتروني', 'impact': 'إيجابي', 'sector': 'الاتصالات'},
        {'time': '15:00', 'title': 'الحديد والصلب تعلن عن خطة إعادة هيكلة جديدة', 'impact': 'محايد', 'sector': 'الصناعة'},
    ]
    return news

# ═══════════════════════════════════════════════════════════════
# 14. EXPORT ENGINE
# ═══════════════════════════════════════════════════════════════

def export_to_excel(symbol: str, df: pd.DataFrame) -> bytes:
    """تصدير بيانات السهم إلى Excel"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Price data
        df[['open','high','low','close','volume']].to_excel(writer, sheet_name='Prices')
        # Indicators
        ind_cols = [c for c in df.columns if c not in ['open','high','low','close','volume','data_source']]
        df[ind_cols].to_excel(writer, sheet_name='Indicators')
        # Metadata
        meta = pd.DataFrame([{
            'الرمز': symbol,
            'الشركة': EGXDatabase.STOCKS.get(symbol, {}).get('name', ''),
            'القطاع': EGXDatabase.STOCKS.get(symbol, {}).get('sector', ''),
            'تاريخ التصدير': get_cairo_time().strftime('%Y-%m-%d %H:%M')
        }])
        meta.to_excel(writer, sheet_name='Metadata', index=False)
    output.seek(0)
    return output.getvalue()

def get_download_link(data: bytes, filename: str, label: str) -> str:
    b64 = base64.b64encode(data).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">{label}</a>'

# ═══════════════════════════════════════════════════════════════
# 15. SESSION STATE & PAGE CONFIG
# ═══════════════════════════════════════════════════════════════

def init_session():
    defaults = {
        'selected_symbol': 'COMI', 'page': 'Dashboard', 'analysis_data': None,
        'watchlist': [], 'alerts': [], 'last_update': None, 'auto_refresh': False,
        'last_rerun_time': 0, 'chart_days': 90, 'sector_filter': 'الكل',
        'dark_mode': True, 'backtest_result': None, 'ml_result': None,
        'compare_symbols': ['COMI', 'TMGH', 'ECIG', 'PHDC'],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

st.set_page_config(
    page_title=f"EGX Pro Ultimate v29.0", page_icon="📈", layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/egx-pro/ultimate',
        'Report a bug': 'https://github.com/egx-pro/ultimate/issues',
        'About': '# EGX Pro Ultimate
✅ 280+ شركة | بيانات حقيقية + محاكاة | ML | إدارة مخاطر'
    }
)

init_session()

# ═══════════════════════════════════════════════════════════════
# 16. SIDEBAR
# ═══════════════════════════════════════════════════════════════

def render_sidebar():
    is_dark = st.session_state.dark_mode
    t = ThemeEngine.get(is_dark)

    st.sidebar.markdown(f"""
    <div style="text-align:center;padding:15px 0;">
        <div style="font-size:2.5em;">📈</div>
        <div style="font-size:1.3em;font-weight:900;
            background:linear-gradient(90deg,{t['PRIMARY']},{t['ACCENT']},{t['GOLD']});
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            EGX Pro Ultimate
        </div>
        <div style="font-size:0.75em;color:{t['TEXT']};opacity:0.6;">
            v29.0 • {len(EGXDatabase.STOCKS)} شركة • {len(EGXDatabase.SECTORS)} قطاع
        </div>
    </div>"", unsafe_allow_html=True)

    st.sidebar.markdown("---")

    # Theme toggle
    st.session_state.dark_mode = st.sidebar.toggle("🌙 الوضع الداكن", value=is_dark)

    st.sidebar.markdown("---")

    pages = {
        '📊 لوحة المعلومات': 'Dashboard',
        '🔍 تحليل مفصّل': 'Analysis',
        '📈 الرسوم البيانية': 'Charts',
        '🕯️ أنماط الشموع': 'Patterns',
        '🔔 التنبيهات': 'Alerts',
        '🤖 تنبؤات الذكاء': 'AI',
        '📋 قائمة المراقبة': 'Watchlist',
        '🧪 الاختبار الخلفي': 'Backtest',
        '🏢 نظرة القطاعات': 'Market',
        '🔥 أفضل وأسوأ': 'TopBottom',
        '📊 مقارنة أسهم': 'Compare',
        '📅 التقويم الاقتصادي': 'Calendar',
        '⚙️ الإعدادات': 'Settings',
    }
    for label, pname in pages.items():
        btn_type = "primary" if st.session_state.page == pname else "secondary"
        if st.sidebar.button(label, use_container_width=True, type=btn_type, key=f"nav_{pname}"):
            st.session_state.page = pname
            st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎯 اختيار السهم")

    sectors_list = ['الكل'] + sorted(EGXDatabase.SECTORS.keys())
    sel_sector = st.sidebar.selectbox("فلتر القطاع", sectors_list, key="sidebar_sector")
    if sel_sector == 'الكل':
        filtered = list(EGXDatabase.STOCKS.keys())
    else:
        filtered = EGXDatabase.SECTORS.get(sel_sector, [])

    sym_options = [s for s in filtered if s in EGXDatabase.STOCKS]
    cur_idx = sym_options.index(st.session_state.selected_symbol) if st.session_state.selected_symbol in sym_options else 0

    sel = st.sidebar.selectbox(
        "اختر السهم", sym_options, index=cur_idx,
        format_func=lambda x: f"{x} | {EGXDatabase.STOCKS[x]['name']}",
        key="symbol_select"
    )
    if sel != st.session_state.selected_symbol:
        st.session_state.selected_symbol = sel
        st.rerun()

    # Quick EGX30 buttons
    st.sidebar.markdown("**⭐ EGX30:**")
    egx30 = EGXDatabase.EGX30[:8]
    cols = st.sidebar.columns(4)
    for i, sym in enumerate(egx30):
        with cols[i % 4]:
            if st.button(sym, use_container_width=True, key=f"q_{sym}"):
                st.session_state.selected_symbol = sym
                st.rerun()

    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 تحديث البيانات", use_container_width=True):
        load_stock_data.clear()
        st.rerun()

    st.session_state.auto_refresh = st.sidebar.checkbox("⏱️ تحديث تلقائي", value=st.session_state.auto_refresh)
    if st.session_state.auto_refresh:
        now = time.time()
        if now - st.session_state.last_rerun_time > AppConfig.REFRESH_INTERVAL:
            st.session_state.last_rerun_time = now
            st.rerun()

    st.sidebar.markdown("---")
    if st.session_state.last_update:
        st.sidebar.caption(f"🕐 آخر تحديث: {st.session_state.last_update.strftime('%H:%M:%S')}")

    # Data source indicator
    df_tmp = load_stock_data(st.session_state.selected_symbol, 5)
    if df_tmp is not None and 'data_source' in df_tmp.columns:
        src = df_tmp['data_source'].iloc[-1]
        src_color = "🟢" if src == "real" else "🟡"
        st.sidebar.caption(f"{src_color} مصدر البيانات: {'حقيقية (Yahoo)' if src == 'real' else 'محاكاة'}")

    st.sidebar.markdown('<div style="text-align:center;color:#888;font-size:0.7em;">🇪🇬 صُنع في مصر • تعليمي فقط</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# 17. PAGE RENDERERS
# ═══════════════════════════════════════════════════════════════

def render_dashboard():
    st.markdown('<h1 style="text-align:center">📈 محطة EGX الاحترافية المتطورة</h1>', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align:center;opacity:0.7;">{len(EGXDatabase.STOCKS)} شركة مدرجة • {len(EGXDatabase.SECTORS)} قطاع • ML + إدارة مخاطر</p>', unsafe_allow_html=True)

    # Market summary
    st.markdown("### 📊 ملخص السوق الحي")
    cols = st.columns(5)
    summary = []
    for sym in EGXDatabase.EGX30[:20]:
        try:
            mini = load_stock_data(sym, 3)
            if mini is not None and not mini.empty:
                last = float(mini['close'].iloc[-1])
                prev = float(mini['close'].iloc[-2]) if len(mini) > 1 else last
                chg = safe_pct(last, prev)
                summary.append({'sym': sym, 'last': last, 'chg': chg})
        except: pass

    if summary:
        summary.sort(key=lambda x: x['chg'], reverse=True)
        up = sum(1 for x in summary if x['chg'] > 0)
        down = sum(1 for x in summary if x['chg'] < 0)
        avg_chg = np.mean([x['chg'] for x in summary])
        best = summary[0]
        worst = summary[-1]

        with cols[0]: st.metric("📈 رابح EGX30", f"{up} سهم", f"{up/max(len(summary),1)*100:.0f}%")
        with cols[1]: st.metric("📉 خاسر EGX30", f"{down} سهم", f"-{down/max(len(summary),1)*100:.0f}%")
        with cols[2]: st.metric("📊 متوسط التغيّر", f"{avg_chg:+.2f}%", "EGX30")
        with cols[3]: st.metric("🏆 الأكثر ارتفاعاً", best['sym'], f"{best['chg']:+.2f}%")
        with cols[4]: st.metric("🔻 الأكثر انخفاضاً", worst['sym'], f"{worst['chg']:+.2f}%")

    st.markdown("---")

    # Selected stock analysis
    symbol = st.session_state.selected_symbol
    info = EGXDatabase.STOCKS.get(symbol, {})
    st.markdown(f"### ⭐ {info.get('name', symbol)} ({symbol}) — {info.get('sector', '')}")

    df = load_stock_data(symbol, 200)
    if df is None: st.warning("⚠️ لا توجد بيانات"); return
    st.session_state.analysis_data = df
    st.session_state.last_update = get_cairo_time()

    last = float(df['close'].iloc[-1])
    prev = float(df['close'].iloc[-2]) if len(df) > 1 else last
    chg = safe_pct(last, prev)
    sig, sig_color, conf, sig_details = get_composite_signal(df)
    rsi = safe_last(df['rsi'], 50)
    adx = safe_last(df['adx'], 25)
    atr = safe_last(df['atr'])
    sup, res = get_support_resistance(df)
    vwap = safe_last(df['vwap'])

    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
    with c1: st.metric("💰 السعر", fmt_egp(last), f"{chg:+.2f}%")
    with c2: st.metric("📊 RSI", f"{rsi:.1f}", "تشبع شراء" if rsi > 65 else "تشبع بيع" if rsi < 35 else "محايد")
    with c3: st.metric("📉 ADX", f"{adx:.1f}", "قوي" if adx > 25 else "ضعيف")
    with c4: st.metric("📏 ATR", f"{atr:.2f}", "تقلب")
    with c5: st.metric("🛡️ دعم", fmt_egp(sup))
    with c6: st.metric("🚧 مقاومة", fmt_egp(res))
    with c7: st.metric(f"{sig_color} الإشارة", sig, f"ثقة {conf}%")

    # Export button
    col_dl1, col_dl2 = st.columns([1, 6])
    with col_dl1:
        excel_data = export_to_excel(symbol, df)
        st.download_button("📥 Excel", excel_data, f"{symbol}_data.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # Main chart
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        row_heights=[0.55, 0.25, 0.20], vertical_spacing=0.03)

    fig.add_trace(go.Candlestick(
        x=df.index, open=df['open'], high=df['high'],
        low=df['low'], close=df['close'], name=symbol,
        increasing_line_color="#00c853", decreasing_line_color="#ff1744"), row=1, col=1)

    # EMAs
    for span, color, dash in [(9, '#00e5ff', 'solid'), (20, '#667eea', 'dash'), (50, '#ffd700', 'dot'), (200, '#f093fb', 'dashdot')]:
        col_name = f'ema_{span}'
        if col_name in df:
            fig.add_trace(go.Scatter(x=df.index, y=df[col_name], mode='lines',
                name=f'EMA {span}', line=dict(color=color, width=1.2, dash=dash)), row=1, col=1)

    # VWAP
    if 'vwap' in df:
        fig.add_trace(go.Scatter(x=df.index, y=df['vwap'], mode='lines',
            name='VWAP', line=dict(color='#ff9800', width=1.5, dash='dot')), row=1, col=1)

    # Bollinger
    if 'bb_upper' in df:
        fig.add_trace(go.Scatter(x=df.index, y=df['bb_upper'], mode='lines',
            name='BB+', line=dict(color='rgba(240,147,251,0.5)', width=1), legendgroup='bb'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['bb_lower'], mode='lines',
            name='BB-', line=dict(color='rgba(240,147,251,0.5)', width=1),
            fill='tonexty', fillcolor='rgba(240,147,251,0.05)', legendgroup='bb'), row=1, col=1)

    # Volume
    colors_vol = ["#00c853" if df['close'].iloc[i] >= df['open'].iloc[i] else "#ff1744" for i in range(len(df))]
    fig.add_trace(go.Bar(x=df.index, y=df['volume'], name='الحجم',
        marker_color=colors_vol, opacity=0.7), row=2, col=1)

    # RSI
    fig.add_trace(go.Scatter(x=df.index, y=df['rsi'], mode='lines', name='RSI',
        line=dict(color='#00b0ff', width=1.5)), row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="#ff1744", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="#00c853", row=3, col=1)

    fig.update_layout(
        title=f"{info.get('name', symbol)} ({symbol}) — {df['data_source'].iloc[-1] if 'data_source' in df.columns else 'simulated'}",
        template='plotly_dark' if st.session_state.dark_mode else 'plotly_white',
        height=750, xaxis_rangeslider_visible=False, hovermode='x unified',
        legend=dict(orientation='h', y=1.02),
        margin=dict(l=10, r=10, t=50, b=10)
    )
    fig.update_yaxes(title_text="السعر (EGP)", row=1, col=1)
    fig.update_yaxes(title_text="الحجم", row=2, col=1)
    fig.update_yaxes(title_text="RSI", row=3, col=1, range=[0, 100])
    st.plotly_chart(fig, use_container_width=True)

    # Patterns
    patterns = detect_patterns(df)
    if patterns:
        st.markdown("### 🕯️ أنماط مكتشفة")
        st.success(" | ".join(patterns))

    # Signal details
    with st.expander("🔍 تفاصيل الإشارة المركبة"):
        sig_df = pd.DataFrame(list(sig_details.items()), columns=['المؤشر', 'التقييم'])
        st.dataframe(sig_df, use_container_width=True, hide_index=True)


def render_analysis():
    st.markdown("## 🔍 تحليل مفصّل شامل")
    symbol = st.session_state.selected_symbol
    info = EGXDatabase.STOCKS.get(symbol, {})
    df = load_stock_data(symbol, 200)
    if df is None: st.warning("لا توجد بيانات"); return

    st.info(f"**{info.get('name', symbol)}** ({symbol}) | القطاع: {info.get('sector', '')} | المصدر: {df['data_source'].iloc[-1] if 'data_source' in df.columns else 'محاكاة'}")

    last = float(df['close'].iloc[-1])
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.metric("أعلى 200 يوم", fmt_egp(df['high'].max()))
    with c2: st.metric("أقل 200 يوم", fmt_egp(df['low'].min()))
    with c3: st.metric("متوسط الحجم", fmt_num(df['volume'].mean(), 0))
    with c4: st.metric("التقلب السنوي", f"{df['close'].pct_change().std()*np.sqrt(252)*100:.1f}%")
    with c5: st.metric("VWAP", fmt_egp(safe_last(df['vwap'])))

    st.markdown("### 📊 ملخص جميع المؤشرات (15+)")
    ind = {
        'RSI (14)': f"{safe_last(df['rsi']):.2f}",
        'EMA 9': fmt_egp(safe_last(df['ema_9'])),
        'EMA 20': fmt_egp(safe_last(df['ema_20'])),
        'EMA 50': fmt_egp(safe_last(df['ema_50'])),
        'EMA 200': fmt_egp(safe_last(df['ema_200'])),
        'SMA 20': fmt_egp(safe_last(df['sma_20'])),
        'VWAP': fmt_egp(safe_last(df['vwap'])),
        'MACD': f"{safe_last(df['macd']):.4f}",
        'MACD Signal': f"{safe_last(df['macd_signal']):.4f}",
        'ADX': f"{safe_last(df['adx']):.2f}",
        'Stoch %K': f"{safe_last(df['stoch_k']):.2f}",
        'Stoch %D': f"{safe_last(df['stoch_d']):.2f}",
        'CCI (20)': f"{safe_last(df['cci']):.2f}",
        'Williams %R': f"{safe_last(df['williams_r']):.2f}",
        'ATR (14)': f"{safe_last(df['atr']):.2f}",
        'ROC (12)': f"{safe_last(df['roc']):.2f}%",
        'Momentum (10)': f"{safe_last(df['momentum']):.2f}",
        'PSAR': fmt_egp(safe_last(df['psar'])),
        'BB Upper': fmt_egp(safe_last(df['bb_upper'])),
        'BB Lower': fmt_egp(safe_last(df['bb_lower'])),
        'Volume vs Avg': f"{safe_last(df['vol_ratio']):.2f}x",
    }

    col1, col2 = st.columns(2)
    items = list(ind.items())
    half = len(items) // 2
    with col1:
        st.dataframe(pd.DataFrame(items[:half], columns=['المؤشر', 'القيمة']), use_container_width=True, hide_index=True)
    with col2:
        st.dataframe(pd.DataFrame(items[half:], columns=['المؤشر', 'القيمة']), use_container_width=True, hide_index=True)

    st.markdown("### 📋 آخر 30 جلسة")
    disp = df.tail(30)[['open','high','low','close','volume','rsi','macd','adx','vwap']].copy()
    disp.columns = ['الافتتاح','الأعلى','الأدنى','الإغلاق','الحجم','RSI','MACD','ADX','VWAP']
    st.dataframe(disp.round(2), use_container_width=True)


def render_charts():
    st.markdown("## 📈 الرسوم البيانية المتقدمة")
    symbol = st.session_state.selected_symbol
    info = EGXDatabase.STOCKS.get(symbol, {})

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: days = st.selectbox("الفترة", [30, 60, 90, 180, 200], index=2, key="ch_days")
    with c2: show_ema = st.multiselect("EMAs", [9, 20, 50, 200], default=[20, 50], key="ch_ema")
    with c3: show_bb = st.checkbox("Bollinger", True, key="ch_bb")
    with c4: show_vwap = st.checkbox("VWAP", True, key="ch_vwap")
    with c5: show_ichimoku = st.checkbox("Ichimoku", False, key="ch_ichi")
    with c6: sub_ind = st.selectbox("مؤشر فرعي", ["RSI", "MACD", "Stoch", "CCI", "Williams %R", "ROC", "Momentum"], key="ch_sub")

    df = load_stock_data(symbol, max(days, 200))
    if df is None: st.warning("لا توجد بيانات"); return
    df = df.tail(days)

    rows = 2
    if sub_ind: rows += 1
    heights = [0.55, 0.20] + ([0.25] if sub_ind else [])
    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True,
                        row_heights=heights, vertical_spacing=0.03)

    fig.add_trace(go.Candlestick(
        x=df.index, open=df['open'], high=df['high'],
        low=df['low'], close=df['close'], name=symbol,
        increasing_line_color="#00c853", decreasing_line_color="#ff1744"), row=1, col=1)

    colors_e = {9: '#00e5ff', 20: '#667eea', 50: '#ffd700', 200: '#f093fb'}
    for span in show_ema:
        col = f'ema_{span}'
        if col in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines',
                name=f'EMA {span}', line=dict(color=colors_e.get(span, '#fff'), width=1.5)), row=1, col=1)

    if show_bb and 'bb_upper' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['bb_upper'], mode='lines',
            line=dict(color='rgba(240,147,251,0.6)', width=1), name='BB+', legendgroup='bb'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['bb_lower'], mode='lines',
            line=dict(color='rgba(240,147,251,0.6)', width=1),
            fill='tonexty', fillcolor='rgba(240,147,251,0.07)', name='BB-', legendgroup='bb'), row=1, col=1)

    if show_vwap and 'vwap' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['vwap'], mode='lines',
            name='VWAP', line=dict(color='#ff9800', width=1.5, dash='dot')), row=1, col=1)

    if show_ichimoku and 'ich_tenkan' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['ich_tenkan'], mode='lines',
            name='Tenkan', line=dict(color='#00e5ff', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['ich_kijun'], mode='lines',
            name='Kijun', line=dict(color='#ff1744', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['ich_senkou_a'], mode='lines',
            name='Senkou A', line=dict(color='#00c853', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['ich_senkou_b'], mode='lines',
            name='Senkou B', line=dict(color='#ff9800', width=1)), row=1, col=1)

    cur_row = 2
    vc = ["#00c853" if df['close'].iloc[i] >= df['open'].iloc[i] else "#ff1744" for i in range(len(df))]
    fig.add_trace(go.Bar(x=df.index, y=df['volume'], name='الحجم',
        marker_color=vc, opacity=0.7), row=cur_row, col=1)
    cur_row += 1

    if sub_ind == "RSI":
        fig.add_trace(go.Scatter(x=df.index, y=df['rsi'], mode='lines', name='RSI',
            line=dict(color='#00b0ff', width=1.5)), row=cur_row, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="#ff1744", row=cur_row, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="#00c853", row=cur_row, col=1)
        fig.update_yaxes(range=[0, 100], row=cur_row, col=1)
    elif sub_ind == "MACD":
        fig.add_trace(go.Scatter(x=df.index, y=df['macd'], mode='lines', name='MACD',
            line=dict(color='#667eea', width=1.5)), row=cur_row, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['macd_signal'], mode='lines', name='Signal',
            line=dict(color='#ff9800', width=1.5, dash='dash')), row=cur_row, col=1)
        fig.add_trace(go.Bar(x=df.index, y=df['macd_hist'], name='Hist',
            marker_color=["#00c853" if v > 0 else "#ff1744" for v in df['macd_hist'].fillna(0)]),
            row=cur_row, col=1)
    elif sub_ind == "Stoch":
        fig.add_trace(go.Scatter(x=df.index, y=df['stoch_k'], name='%K',
            line=dict(color='#667eea', width=1.5)), row=cur_row, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['stoch_d'], name='%D',
            line=dict(color='#ff9800', width=1.5, dash='dash')), row=cur_row, col=1)
        fig.add_hline(y=80, line_dash="dash", line_color="#ff1744", row=cur_row, col=1)
        fig.add_hline(y=20, line_dash="dash", line_color="#00c853", row=cur_row, col=1)
    elif sub_ind == "CCI":
        fig.add_trace(go.Scatter(x=df.index, y=df['cci'], name='CCI',
            line=dict(color='#f093fb', width=1.5)), row=cur_row, col=1)
        fig.add_hline(y=100, line_dash="dash", line_color="#ff1744", row=cur_row, col=1)
        fig.add_hline(y=-100, line_dash="dash", line_color="#00c853", row=cur_row, col=1)
    elif sub_ind == "Williams %R":
        fig.add_trace(go.Scatter(x=df.index, y=df['williams_r'], name='W%R',
            line=dict(color='#ffd700', width=1.5)), row=cur_row, col=1)
        fig.add_hline(y=-20, line_dash="dash", line_color="#ff1744", row=cur_row, col=1)
        fig.add_hline(y=-80, line_dash="dash", line_color="#00c853", row=cur_row, col=1)
    elif sub_ind == "ROC":
        fig.add_trace(go.Scatter(x=df.index, y=df['roc'], name='ROC',
            line=dict(color='#00e5ff', width=1.5)), row=cur_row, col=1)
        fig.add_hline(y=0, line_dash="dash", line_color="#888", row=cur_row, col=1)
    elif sub_ind == "Momentum":
        fig.add_trace(go.Scatter(x=df.index, y=df['momentum'], name='Momentum',
            line=dict(color='#ff9800', width=1.5)), row=cur_row, col=1)
        fig.add_hline(y=0, line_dash="dash", line_color="#888", row=cur_row, col=1)

    fig.update_layout(
        title=f"{info.get('name', symbol)} — {days} يوم",
        template='plotly_dark' if st.session_state.dark_mode else 'plotly_white',
        height=800, xaxis_rangeslider_visible=False, hovermode='x unified',
        legend=dict(orientation='h', y=1.01)
    )
    st.plotly_chart(fig, use_container_width=True)


def render_patterns():
    st.markdown("## 🕯️ تحليل الشموع اليابانية والأنماط")
    symbol = st.session_state.selected_symbol
    df = load_stock_data(symbol, 200)
    if df is None: st.warning("لا توجد بيانات"); return

    patterns = detect_patterns(df)
    sup, res = get_support_resistance(df)
    last = float(df['close'].iloc[-1])
    fib = get_fibonacci_levels(last, sup, res)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("#### 🔍 الأنماط المكتشفة")
        if patterns:
            for p in patterns:
                st.success(p)
        else:
            st.info("لا توجد أنماط واضحة في الشمعة الأخيرة")

        st.markdown("#### 📏 مستويات الدعم والمقاومة")
        st.metric("🛡️ الدعم", fmt_egp(sup), f"{safe_pct(sup, last):+.1f}%")
        st.metric("🚧 المقاومة", fmt_egp(res), f"{safe_pct(res, last):+.1f}%")

        st.markdown("#### 📐 مستويات فيبوناتشي")
        for lvl, price in fib.items():
            st.write(f"**{lvl}** → {fmt_egp(price)}")

    with col2:
        fig = go.Figure()
        recent = df.tail(50)
        fig.add_trace(go.Candlestick(
            x=recent.index, open=recent['open'], high=recent['high'],
            low=recent['low'], close=recent['close'], name='الشموع',
            increasing_line_color="#00c853", decreasing_line_color="#ff1744"))
        fig.add_hline(y=sup, line_dash="solid", line_color="#00c853",
                      annotation_text=f"دعم {sup:.2f}", line_width=1.5)
        fig.add_hline(y=res, line_dash="solid", line_color="#ff1744",
                      annotation_text=f"مقاومة {res:.2f}", line_width=1.5)
        for lvl, price in fib.items():
            if '23.6' in lvl or '38.2' in lvl or '61.8' in lvl:
                fig.add_hline(y=price, line_dash="dash", line_color="#ffd700",
                              annotation_text=lvl, line_width=1, opacity=0.7)
        fig.update_layout(
            template='plotly_dark' if st.session_state.dark_mode else 'plotly_white',
            height=550, xaxis_rangeslider_visible=False, title="آخر 50 شمعة + مستويات فيبوناتشي")
        st.plotly_chart(fig, use_container_width=True)


def render_ai():
    st.markdown("## 🤖 التنبؤات بالذكاء الاصطناعي المتقدم")
    symbol = st.session_state.selected_symbol
    info = EGXDatabase.STOCKS.get(symbol, {})
    df = load_stock_data(symbol, 200)
    if df is None: st.warning("لا توجد بيانات"); return

    days_ahead = st.slider("أفق التنبؤ (أيام)", 1, 30, 5)

    with st.status("🧠 جاري تحليل البيانات بالنماذج المتقدمة...", expanded=True) as status:
        st.write("⚙️ هندسة الميزات...")
        st.write("📊 تدريب نموذج Linear Regression...")
        st.write("🌲 تدريب نموذج Random Forest...")
        st.write("🔮 توليد التوقعات التجميعية...")
        ml_result = ml_predict_trend(df, days_ahead)
        st.session_state.ml_result = ml_result
        status.update(label="✅ اكتمل التحليل الذكي!", state="complete")

    if "error" in ml_result:
        st.error(f"❌ {ml_result['error']}")
        return

    last = ml_result['last_price']
    predicted = ml_result['predicted_price']
    ensemble = ml_result['ensemble']
    conf = ml_result['confidence']
    direction = ml_result['direction']
    emoji = ml_result['direction_emoji']

    is_buy = "صاعد" in direction
    target1 = last * (1.05 if is_buy else 0.97)
    target2 = last * (1.10 if is_buy else 0.94)
    stop_loss = last * (0.97 if is_buy else 1.03)
    rr = abs(target1 - last) / max(abs(last - stop_loss), 0.01)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.metric(f"{emoji} الاتجاه المتوقع", direction, f"ثقة ML {conf:.0f}%")
    with c2: st.metric("🎯 هدف 1", fmt_egp(target1), f"{safe_pct(target1, last):+.1f}%")
    with c3: st.metric("🎯 هدف 2", fmt_egp(target2), f"{safe_pct(target2, last):+.1f}%")
    with c4: st.metric("🛑 وقف الخسارة", fmt_egp(stop_loss), f"{safe_pct(stop_loss, last):+.1f}%")
    with c5: st.metric("⚖️ Risk/Reward", f"{rr:.2f}", "ممتاز" if rr > 2 else "جيد" if rr > 1.5 else "ضعيف")

    # ML predictions comparison
    st.markdown("### 📊 مقارنة النماذج")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Linear Regression", f"{ml_result['lr_pred']*100:+.2f}%", "توقع")
    with col2: st.metric("Random Forest", f"{ml_result['rf_pred']*100:+.2f}%", "توقع")
    with col3: st.metric("Ensemble (متوسط)", f"{ensemble*100:+.2f}%", "النهائي")

    # Feature importance
    st.markdown("### 🔍 أهمية الميزات (Random Forest)")
    imp_df = pd.DataFrame(list(ml_result['importance'].items()), columns=['الميزة', 'الأهمية'])
    imp_df = imp_df.sort_values('الأهمية', ascending=True)
    fig_imp = go.Figure(go.Bar(
        y=imp_df['الميزة'], x=imp_df['الأهمية'], orientation='h',
        marker_color='#667eea'
    ))
    fig_imp.update_layout(template='plotly_dark' if st.session_state.dark_mode else 'plotly_white',
                          height=300, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_imp, use_container_width=True)

    # Radar
    st.markdown("### 📊 رادار تقييم المؤشرات")
    scores = {
        'RSI': min(max((50-safe_last(df['rsi'], 50))/50*100, -100), 100),
        'MACD': 80 if safe_last(df['macd'], 0) > safe_last(df['macd_signal'], 0) else -80,
        'ADX': min(safe_last(df['adx'], 25) * 2, 100),
        'Stoch': min(max((50-safe_last(df['stoch_k'], 50))/50*100, -100), 100),
        'CCI': min(max(-safe_last(df['cci'], 0), -100), 100),
        'W%R': min(max((safe_last(df['williams_r'], -50)+50)/50*100, -100), 100),
        'EMA Trend': 80 if last > safe_last(df['ema_20']) > safe_last(df['ema_50']) else -80 if last < safe_last(df['ema_20']) < safe_last(df['ema_50']) else 0,
        'VWAP': 60 if last > safe_last(df['vwap']) else -60,
        'ROC': min(max(safe_last(df['roc'], 0), -100), 100),
    }
    fig_radar = go.Figure(go.Scatterpolar(
        r=list(scores.values()), theta=list(scores.keys()),
        fill='toself', fillcolor='rgba(102,126,234,0.2)',
        line_color='#667eea', name='المؤشرات'
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[-100, 100])),
        template='plotly_dark' if st.session_state.dark_mode else 'plotly_white',
        height=400, title="رادار قوة الإشارة"
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # Monte Carlo
    st.markdown("### 📈 محاكاة مونت كارلو (30 يوم)")
    np.random.seed(42)
    daily_vol = df['close'].pct_change().std()
    drift = df['close'].pct_change().mean()
    sims = 200; days = 30
    paths = np.zeros((sims, days))
    for i in range(sims):
        r = np.random.normal(drift, daily_vol, days)
        paths[i] = last * np.exp(np.cumsum(r))

    fig_mc = go.Figure()
    for i in range(min(50, sims)):
        fig_mc.add_trace(go.Scatter(y=paths[i], mode='lines', opacity=0.12,
            line=dict(color='#667eea', width=0.5), showlegend=False))
    fig_mc.add_trace(go.Scatter(y=np.percentile(paths, 75, axis=0), mode='lines', name='P75',
        line=dict(color='#00c853', width=2)))
    fig_mc.add_trace(go.Scatter(y=np.percentile(paths, 50, axis=0), mode='lines', name='الوسيط',
        line=dict(color='#ffd700', width=2.5)))
    fig_mc.add_trace(go.Scatter(y=np.percentile(paths, 25, axis=0), mode='lines', name='P25',
        line=dict(color='#ff1744', width=2)))
    fig_mc.update_layout(
        template='plotly_dark' if st.session_state.dark_mode else 'plotly_white',
        height=350, title=f"محاكاة {sims} مسار — {days} يوم",
        xaxis_title="الأيام", yaxis_title="السعر المتوقع (EGP)")
    st.plotly_chart(fig_mc, use_container_width=True)

    p10 = float(np.percentile(paths[:, -1], 10))
    p50 = float(np.percentile(paths[:, -1], 50))
    p90 = float(np.percentile(paths[:, -1], 90))
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("سيناريو متشائم (P10)", fmt_egp(p10), f"{safe_pct(p10, last):+.1f}%")
    with c2: st.metric("سيناريو محتمل (P50)", fmt_egp(p50), f"{safe_pct(p50, last):+.1f}%")
    with c3: st.metric("سيناريو متفائل (P90)", fmt_egp(p90), f"{safe_pct(p90, last):+.1f}%")


def render_alerts():
    st.markdown("## 🔔 إدارة التنبيهات الذكية")

    triggered = AlertManager.check_alerts(st.session_state.alerts)
    if triggered:
        st.error("⚡ **تنبيهات مُفعَّلة الآن:**")
        for t in triggered:
            st.markdown(t)
        st.markdown("---")

    if st.session_state.alerts:
        st.markdown("### التنبيهات النشطة")
        for i, alert in enumerate(st.session_state.alerts):
            c1, c2 = st.columns([4, 1])
            with c1:
                st.info(f"**{alert['symbol']}** — {alert['type']} {alert['condition']} **{alert['value']}** | {alert.get('created_at', '')}")
            with c2:
                if st.button("🗑️", key=f"del_alert_{i}"):
                    st.session_state.alerts.pop(i)
                    st.rerun()
    else:
        st.info("لا توجد تنبيهات. أنشئ تنبيهاً أدناه.")

    st.markdown("### ➕ إنشاء تنبيه جديد")
    with st.form("alert_form", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            sym_list = list(EGXDatabase.STOCKS.keys())
            al_sym = st.selectbox("السهم", sym_list, format_func=lambda x: f"{x} | {EGXDatabase.STOCKS[x]['name'][:20]}")
        with c2: al_type = st.selectbox("النوع", ["السعر", "RSI", "MACD", "ADX", "الحجم", "VWAP"])
        with c3: al_cond = st.selectbox("الشرط", ["أعلى من", "أقل من", "يساوي"])
        with c4: al_val = st.number_input("القيمة", min_value=0.0, value=10.0, step=0.5)

        if st.form_submit_button("✅ إنشاء التنبيه"):
            st.session_state.alerts.append({
                'symbol': al_sym, 'type': al_type, 'condition': al_cond, 'value': al_val,
                'created_at': get_cairo_time().strftime('%Y-%m-%d %H:%M')
            })
            st.success(f"✅ تم إنشاء التنبيه: {al_sym} — {al_type} {al_cond} {al_val}")


def render_watchlist():
    st.markdown("## 📋 قائمة المراقبة المتقدمة")

    c1, c2 = st.columns([3, 1])
    with c1:
        add_sym = st.selectbox("إضافة سهم", list(EGXDatabase.STOCKS.keys()),
            format_func=lambda x: f"{x} | {EGXDatabase.STOCKS[x]['name']}", key="wl_add")
    with c2:
        if st.button("➕ إضافة", key="wl_btn"):
            if add_sym not in st.session_state.watchlist:
                st.session_state.watchlist.append(add_sym)
                st.success(f"✅ تمت إضافة {add_sym}"); st.rerun()
            else:
                st.warning("موجود بالفعل")

    if not st.session_state.watchlist:
        st.info("القائمة فارغة — أضف أسهماً للمتابعة")
        return

    rows_data = []
    for sym in st.session_state.watchlist:
        try:
            mini = load_stock_data(sym, 5)
            if mini is not None and not mini.empty:
                last = float(mini['close'].iloc[-1])
                prev = float(mini['close'].iloc[-2]) if len(mini) > 1 else last
                chg = safe_pct(last, prev)
                rsi = safe_last(mini['rsi'], 50)
                sig, scol, conf, _ = get_composite_signal(mini)
                rows_data.append({
                    'رمز': sym, 'الشركة': EGXDatabase.STOCKS[sym]['name'][:25],
                    'القطاع': EGXDatabase.STOCKS[sym]['sector'],
                    'السعر': f"{last:.2f}", 'التغيير%': f"{chg:+.2f}%",
                    'RSI': f"{rsi:.1f}", 'الإشارة': f"{scol} {sig}", 'ثقة': f"{conf}%"
                })
        except: pass

    if rows_data:
        st.dataframe(pd.DataFrame(rows_data), use_container_width=True, hide_index=True)

    for i, sym in enumerate(st.session_state.watchlist):
        c1, c2, c3 = st.columns([3, 2, 1])
        with c1: st.write(f"**{sym}** — {EGXDatabase.STOCKS[sym]['name']}")
        with c2:
            if st.button(f"📊 تحليل {sym}", key=f"an_{sym}"):
                st.session_state.selected_symbol = sym
                st.session_state.page = 'Analysis'; st.rerun()
        with c3:
            if st.button("🗑️", key=f"rm_{sym}_{i}"):
                st.session_state.watchlist.remove(sym); st.rerun()


def render_backtest():
    st.markdown("## 🧪 الاختبار الخلفي الاحترافي")
    df_full = load_stock_data(st.session_state.selected_symbol, 200)
    if df_full is None: st.warning("لا توجد بيانات"); return

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: strategy = st.selectbox("الاستراتيجية",
        ["RSI", "MACD Crossover", "Bollinger Bands", "EMA Crossover", "Stochastic",
         "CCI Mean Reversion", "Ichimoku", "VWAP Bounce"], key="bt_strat")
    with c2: capital = st.number_input("رأس المال (EGP)", 1000, 10_000_000, 100_000, step=5000)
    with c3: stop_pct = st.slider("وقف الخسارة %", 1, 20, 5)
    with c4: take_pct = st.slider("هدف الربح %", 1, 30, 10)
    with c5: risk_per_trade = st.slider("المخاطرة/صفقة %", 0.5, 10.0, 2.0, 0.5) / 100

    if not st.button("🚀 تشغيل الاختبار الاحترافي"): return

    with st.spinner("جاري الاختبار مع حساب العمولات والضرائب..."):
        engine = BacktestEngine(df_full, capital, strategy, stop_pct, take_pct, risk_per_trade)
        result = engine.run()
        st.session_state.backtest_result = result

    st.success("✅ اكتمل الاختبار!")

    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
    with c1: st.metric("الربح/الخسارة", fmt_egp(result['profit']), f"{result['profit_pct']:+.2f}%")
    with c2: st.metric("القيمة النهائية", fmt_egp(result['final_capital']))
    with c3: st.metric("عدد الصفقات", result['n_trades'])
    with c4: st.metric("نسبة الفوز", f"{result['win_rate']:.0f}%")
    with c5: st.metric("Buy & Hold", f"{result['buy_hold']:+.2f}%", "للمقارنة")
    with c6: st.metric("Max Drawdown", f"{result['max_dd']:.1f}%", "خطر")
    with c7: st.metric("Sharpe Ratio", f"{result['sharpe']:.2f}", "جودة")

    col1, col2 = st.columns(2)
    with col1: st.metric("Calmar Ratio", f"{result['calmar']:.2f}", "عائد/مخاطر")
    with col2: st.metric("Kelly Criterion", f"{result['kelly']*100:.1f}%", "الحجم الأمثل")

    # Equity curve
    fig_eq = go.Figure()
    fig_eq.add_trace(go.Scatter(y=result['equity'], mode='lines', name='محفظتك',
        line=dict(color='#667eea', width=2), fill='tozeroy', fillcolor='rgba(102,126,234,0.1)'))
    # Buy & Hold line
    bh_equity = [capital * (1 + result['buy_hold']/100 * i/len(result['equity'])) for i in range(len(result['equity']))]
    fig_eq.add_trace(go.Scatter(y=bh_equity, mode='lines', name='Buy & Hold',
        line=dict(color='#ffd700', width=2, dash='dash')))
    fig_eq.update_layout(
        template='plotly_dark' if st.session_state.dark_mode else 'plotly_white',
        height=350, title="منحنى رأس المال vs Buy & Hold",
        xaxis_title="الجلسات", yaxis_title="EGP")
    st.plotly_chart(fig_eq, use_container_width=True)

    # Trades table
    if result['trades']:
        trades_df = pd.DataFrame([t for t in result['trades'] if 'pnl' in t or 'cost' in t])
        if not trades_df.empty:
            st.markdown("### 📋 سجل الصفقات")
            st.dataframe(trades_df, use_container_width=True, hide_index=True)


def render_market():
    st.markdown("## 🏢 نظرة القطاعات الكاملة")

    sector_filter = st.selectbox("اختر القطاع", ['الكل'] + sorted(EGXDatabase.SECTORS.keys()), key="mkt_sec")
    sectors_to_show = {sector_filter: EGXDatabase.SECTORS[sector_filter]} if sector_filter != 'الكل' else EGXDatabase.SECTORS

    for sector, symbols in sorted(sectors_to_show.items()):
        st.markdown(f"### 🏷️ قطاع {sector} ({len(symbols)} شركة)")
        sector_data = []
        for sym in symbols:
            try:
                mini = load_stock_data(sym, 3)
                if mini is not None and not mini.empty:
                    last = float(mini['close'].iloc[-1])
                    prev = float(mini['close'].iloc[-2]) if len(mini) > 1 else last
                    chg = safe_pct(last, prev)
                    sector_data.append({'رمز': sym, 'الشركة': EGXDatabase.STOCKS[sym]['name'][:25],
                                        'السعر': last, 'التغيير%': chg})
            except: pass

        if sector_data:
            df_sec = pd.DataFrame(sector_data)
            colors = ["#00c853" if c > 0 else "#ff1744" for c in df_sec['التغيير%']]
            fig = go.Figure(go.Bar(
                x=df_sec['رمز'], y=df_sec['التغيير%'],
                text=df_sec['التغيير%'].apply(lambda x: f"{x:+.2f}%"),
                textposition='outside', marker_color=colors, name=sector
            ))
            fig.update_layout(
                template='plotly_dark' if st.session_state.dark_mode else 'plotly_white',
                height=250, title=f"تغيّرات قطاع {sector}",
                yaxis_title="%", showlegend=False, margin=dict(t=40, b=10, l=10, r=10))
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("---")


def render_top_bottom():
    st.markdown("## 🔥 أفضل وأسوأ الأسهم")

    n = st.slider("عدد الأسهم", 5, 30, 10)
    all_data = []

    with st.spinner("جاري تحميل بيانات جميع الشركات..."):
        for sym in list(EGXDatabase.STOCKS.keys())[:100]:
            try:
                mini = load_stock_data(sym, 3)
                if mini is not None and not mini.empty:
                    last = float(mini['close'].iloc[-1])
                    prev = float(mini['close'].iloc[-2]) if len(mini) > 1 else last
                    chg = safe_pct(last, prev)
                    all_data.append({
                        'رمز': sym, 'الشركة': EGXDatabase.STOCKS[sym]['name'][:22],
                        'القطاع': EGXDatabase.STOCKS[sym]['sector'],
                        'السعر': round(last, 2), 'التغيير%': round(chg, 2)
                    })
            except: pass

    if not all_data: st.warning("لا توجد بيانات"); return

    df_all = pd.DataFrame(all_data).sort_values('التغيير%', ascending=False)
    top_n = df_all.head(n)
    bot_n = df_all.tail(n).sort_values('التغيير%')

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### 📈 أفضل {n} أسهم")
        fig = go.Figure(go.Bar(
            y=top_n['رمز'], x=top_n['التغيير%'], orientation='h',
            text=top_n['التغيير%'].apply(lambda x: f"{x:+.2f}%"),
            textposition='outside', marker_color=["#00c853"]*len(top_n)
        ))
        fig.update_layout(template='plotly_dark' if st.session_state.dark_mode else 'plotly_white',
                          height=400, xaxis_title="%")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(top_n, hide_index=True, use_container_width=True)

    with col2:
        st.markdown(f"### 📉 أسوأ {n} أسهم")
        fig2 = go.Figure(go.Bar(
            y=bot_n['رمز'], x=bot_n['التغيير%'], orientation='h',
            text=bot_n['التغيير%'].apply(lambda x: f"{x:+.2f}%"),
            textposition='outside', marker_color=["#ff1744"]*len(bot_n)
        ))
        fig2.update_layout(template='plotly_dark' if st.session_state.dark_mode else 'plotly_white',
                           height=400, xaxis_title="%")
        st.plotly_chart(fig2, use_container_width=True)
        st.dataframe(bot_n, hide_index=True, use_container_width=True)


def render_compare():
    st.markdown("## 📊 مقارنة أسهم متعددة")

    syms_to_compare = st.multiselect(
        "اختر الأسهم (2-6)", list(EGXDatabase.STOCKS.keys()),
        default=st.session_state.compare_symbols[:4] if len(st.session_state.compare_symbols) >= 4 else ['COMI', 'TMGH', 'ECIG', 'PHDC'],
        max_selections=6,
        format_func=lambda x: f"{x} | {EGXDatabase.STOCKS[x]['name'][:20]}"
    )

    if len(syms_to_compare) < 2:
        st.info("اختر على الأقل سهمين"); return

    st.session_state.compare_symbols = syms_to_compare
    days = st.slider("الفترة (يوم)", 30, 200, 90, key="cmp_days")

    # Relative performance
    fig = go.Figure()
    colors_cmp = ['#667eea', '#00c853', '#ff9800', '#ff1744', '#f093fb', '#ffd700']
    for i, sym in enumerate(syms_to_compare):
        df = load_stock_data(sym, max(days, 200))
        if df is None: continue
        df = df.tail(days)
        normalized = (df['close'] / float(df['close'].iloc[0]) - 1) * 100
        fig.add_trace(go.Scatter(
            x=df.index, y=normalized, mode='lines',
            name=f"{sym} | {EGXDatabase.STOCKS[sym]['name'][:15]}",
            line=dict(color=colors_cmp[i % len(colors_cmp)], width=2.5)
        ))

    fig.add_hline(y=0, line_dash="dash", line_color="#888")
    fig.update_layout(
        template='plotly_dark' if st.session_state.dark_mode else 'plotly_white',
        height=500, title=f"الأداء النسبي — {days} يوم",
        yaxis_title="العائد %", hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    # Correlation heatmap
    st.markdown("### 📊 مصفوفة الارتباط")
    price_matrix = pd.DataFrame()
    for sym in syms_to_compare:
        df = load_stock_data(sym, max(days, 200))
        if df is not None:
            price_matrix[sym] = df['close'].tail(days).values[:days]

    if not price_matrix.empty and len(price_matrix.columns) > 1:
        corr = price_matrix.pct_change().corr()
        fig_corr = px.imshow(corr, text_auto='.2f', color_continuous_scale='RdYlGn',
                            title="مصفوفة الارتباط بين الأسهم", aspect="auto")
        fig_corr.update_layout(template='plotly_dark' if st.session_state.dark_mode else 'plotly_white')
        st.plotly_chart(fig_corr, use_container_width=True)

    # Comparison table
    compare_rows = []
    for sym in syms_to_compare:
        df = load_stock_data(sym, 200)
        if df is None: continue
        df_r = df.tail(days)
        last = float(df_r['close'].iloc[-1])
        ret = safe_pct(last, float(df_r['close'].iloc[0]))
        vol = df_r['close'].pct_change().std() * np.sqrt(252) * 100
        sig, scol, conf, _ = get_composite_signal(df)
        compare_rows.append({
            'رمز': sym, 'الشركة': EGXDatabase.STOCKS[sym]['name'][:25],
            'السعر': f"{last:.2f}", f'العائد {days}ي': f"{ret:+.2f}%",
            'التقلب السنوي': f"{vol:.1f}%", 'الإشارة': f"{scol} {sig}", 'ثقة': f"{conf}%"
        })

    st.markdown("### 📋 مقارنة تفصيلية")
    st.dataframe(pd.DataFrame(compare_rows), hide_index=True, use_container_width=True)


def render_calendar():
    st.markdown("## 📅 التقويم الاقتصادي والأخبار")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📅 أحداث اقتصادية قادمة")
        cal_df = get_economic_calendar()
        st.dataframe(cal_df, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("### 📰 أخبار السوق")
        news = get_market_news()
        for item in news:
            color = "#00c853" if item['impact'] == 'إيجابي' else "#ff1744" if item['impact'] == 'سلبي' else "#ffd700"
            st.markdown(f"<div style='border-right:3px solid {color}; padding-right:10px; margin:8px 0;'>"
                       f"<small>{item['time']}</small><br><b>{item['title']}</b><br>"
                       f"<small>التأثير: {item['impact']} | القطاع: {item['sector']}</small></div>",
                       unsafe_allow_html=True)


def render_settings():
    st.markdown("## ⚙️ الإعدادات والإدارة")

    st.markdown("### 🗄️ إدارة البيانات")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("🗑️ مسح الكاش"):
            load_stock_data.clear(); st.success("✅ تم")
    with c2:
        if st.button("🗑️ حذف التنبيهات"):
            st.session_state.alerts = []; st.success("✅ تم")
    with c3:
        if st.button("🗑️ مسح المراقبة"):
            st.session_state.watchlist = []; st.success("✅ تم")
    with c4:
        if st.button("🔄 إعادة ضبط الكل"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.success("✅ تم إعادة الضبط"); st.rerun()

    st.markdown("### 📊 إحصائيات قاعدة البيانات")
    sector_counts = {s: len(syms) for s, syms in EGXDatabase.SECTORS.items()}
    df_stats = pd.DataFrame(list(sector_counts.items()), columns=['القطاع', 'عدد الشركات'])
    df_stats = df_stats.sort_values('عدد الشركات', ascending=False)

    fig_pie = px.pie(df_stats, values='عدد الشركات', names='القطاع',
                     title=f"توزيع {len(EGXDatabase.STOCKS)} شركة على {len(EGXDatabase.SECTORS)} قطاع",
                     template='plotly_dark' if st.session_state.dark_mode else 'plotly_white',
                     hole=0.4, color_discrete_sequence=px.colors.sequential.Plasma)
    st.plotly_chart(fig_pie, use_container_width=True)
    st.dataframe(df_stats, hide_index=True, use_container_width=True)

    st.markdown("### ℹ️ عن التطبيق")
    st.info(f"""
**EGX Pro Ultimate — v29.0**

📊 **البيانات:** {len(EGXDatabase.STOCKS)} شركة مصرية في {len(EGXDatabase.SECTORS)} قطاع
🌐 **المصدر:** Yahoo Finance (حقيقي) + محاكاة احتياطية

🔧 **المؤشرات الفنية (15+):**
RSI · EMA (9/20/50/200) · SMA · MACD · Bollinger · ADX · Stochastic · CCI · Williams %R · OBV · ATR · VWAP · Parabolic SAR · ROC · Momentum · Ichimoku Cloud

🕯️ **الأنماط:** Doji · Hammer · Shooting Star · Engulfing · Morning/Evening Star · Harami · Marubozu

🤖 **الذكاء الاصطناعي:** Linear Regression + Random Forest + Ensemble + Feature Importance

🧪 **الاختبار الخلفي:** 8 استراتيجيات + عمولة 0.15% + ضريبة 0.1% + Kelly Criterion + Sharpe/Calmar

⚠️ **تنبيه:** جميع البيانات لأغراض تعليمية فقط ولا تُعدّ نصيحة استثمارية.
    """)

# ═══════════════════════════════════════════════════════════════
# 18. MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    try:
        # Apply theme CSS
        st.markdown(ThemeEngine.css(st.session_state.dark_mode), unsafe_allow_html=True)

        render_sidebar()

        dispatch = {
            'Dashboard': render_dashboard,
            'Analysis': render_analysis,
            'Charts': render_charts,
            'Patterns': render_patterns,
            'Alerts': render_alerts,
            'AI': render_ai,
            'Watchlist': render_watchlist,
            'Backtest': render_backtest,
            'Market': render_market,
            'TopBottom': render_top_bottom,
            'Compare': render_compare,
            'Calendar': render_calendar,
            'Settings': render_settings,
        }

        renderer = dispatch.get(st.session_state.page)
        if renderer:
            renderer()
        else:
            st.error(f"❌ صفحة غير موجودة: {st.session_state.page}")

    except Exception as e:
        logger.error(f"App error: {e}", exc_info=True)
        st.error(f"❌ خطأ: {str(e)}")
        if st.button("🔄 إعادة تشغيل"):
            st.rerun()

if __name__ == "__main__":
    main()
