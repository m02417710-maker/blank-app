"""
EGX Pro Terminal v35 — الملف الموحّد الكامل
═══════════════════════════════════════════════════════════════
يدمج:
  ✅ enhanced_egx_engine.py     — محرك البيانات + 25 مؤشر + MFI + Keltner
  ✅ enhanced_egx_ml_backtest.py — ML Ensemble (GB + LSTM + Transformer)
  ✅ data_storage.py            — SQLite 6 جداول
  ✅ enhanced_news.py           — RSS + NewsAPI + fallback
  ✅ egx_ai_analyzer.py         — Gemini AI بالعربية
  ✅ egx_app.py                 — 15 صفحة Streamlit

إصلاحات v35:
  🔴 خصم عمولة مزدوج          — entry_cost = sh*cp فقط
  🔴 PnL يطرح التكاليف         — pnl = pr - entry_total
  🔴 gemini-1.5-flash          — (كان 2.0-flash → 404)
  🔴 Ultimate Oscillator        — true_low/true_high صحيح
  🔴 AI_PREDICTION_HORIZON      — مُضافة في AppConfig
  🟠 MFI + Keltner             — محسوبان ومعروضان
  🟠 Kelly من الباكتست          — بدلاً من قيم ثابتة
  🟡 cached_backtest + cache    — لا إعادة حساب غير ضرورية
  🟡 Alert threshold آمن        — try/except حول :g format

تشغيل: streamlit run enhanced_egx_app.py
═══════════════════════════════════════════════════════════════
"""

# ══════════════════════════════════════════════════════════════
# SECTION 1 — IMPORTS & SETUP
# ══════════════════════════════════════════════════════════════
import sys, os
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import warnings; warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
import sqlite3, json, hashlib, logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple, Any
from contextlib import contextmanager

os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s — %(levelname)s — %(message)s',
    handlers=[
        logging.FileHandler('logs/egx_terminal.log', encoding='utf-8'),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

# ── PyTorch (اختياري) ──────────────────────────────────────────
TORCH_AVAILABLE = False
try:
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader, TensorDataset
    TORCH_AVAILABLE = True
except ImportError:
    pass

# ── Streamlit page config ──────────────────────────────────────
st.set_page_config(
    page_title="🇪🇬 EGX Pro Terminal v35",
    page_icon="📈", layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
# SECTION 2 — GLOBAL CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap');

html,body,[class*="css"],.stApp,.stMarkdown,p,div,span,h1,h2,h3,h4,button {
    font-family:'Cairo',sans-serif!important;
}
.stApp { direction:rtl; background:#0a0e1a; }
::-webkit-scrollbar{width:6px}
::-webkit-scrollbar-thumb{background:#2d3748;border-radius:4px}

/* Buttons */
.stButton>button {
    font-family:'Cairo',sans-serif!important;font-size:14px!important;
    font-weight:600!important;padding:10px 18px!important;
    border-radius:8px!important;border:1px solid #3d4a63!important;
    background:linear-gradient(135deg,#1e2738,#2d3748)!important;
    color:#e2e8f0!important;transition:all .2s!important;
}
.stButton>button:hover{border-color:#f59e0b!important;color:#f59e0b!important}
.stButton>button[kind="primary"]{background:linear-gradient(135deg,#1d4ed8,#2563eb)!important;
    border-color:#3b82f6!important;color:#fff!important}

/* Metrics */
div[data-testid="stMetric"]{background:#1a1f2e!important;border-radius:10px!important;
    padding:12px!important;border:1px solid #2d3748!important}

/* Sidebar */
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0f1117,#1a1f2e)!important;
    border-left:1px solid #2d3748}

/* Tabs */
.stTabs [data-baseweb="tab-list"]{gap:4px;background:#0f1117;border-radius:10px;padding:6px}
.stTabs [data-baseweb="tab"]{font-family:'Cairo',sans-serif!important;font-weight:600!important;
    color:#94a3b8!important;border-radius:8px!important}
.stTabs [aria-selected="true"]{background:#1d4ed8!important;color:#fff!important}

/* Cards */
.kpi-card{background:linear-gradient(135deg,#1a1f2e,#2d3748);border:1px solid #3d4a63;
    border-radius:12px;padding:16px;text-align:center;margin:4px 0}

/* ── Simulation Warning ──────────────────────────────────── */
@keyframes pulse-warning{
    0%  {box-shadow:0 0 0 0 rgba(239,68,68,.4)}
    70% {box-shadow:0 0 0 10px rgba(239,68,68,0)}
    100%{box-shadow:0 0 0 0 rgba(239,68,68,0)}
}
.simulation-warning{
    background:linear-gradient(135deg,#450a0a,#7f1d1d);
    border:2px solid #ef4444;border-radius:12px;
    padding:14px 18px;margin:10px 0;
    animation:pulse-warning 2s infinite;direction:rtl
}
.simulation-warning-title{font-size:15px;font-weight:800;color:#fca5a5;margin-bottom:6px}
.simulation-warning-body{font-size:13px;color:#fecaca;line-height:1.8}
.simulation-badge{background:#991b1b;border:1px solid #ef4444;color:#fca5a5;
    border-radius:6px;padding:2px 8px;font-size:11px;font-weight:700}
.real-badge{background:#064e3b;border:1px solid #10b981;color:#6ee7b7;
    border-radius:6px;padding:2px 8px;font-size:11px;font-weight:700}

/* Page header */
.page-header{background:linear-gradient(135deg,#1e2738,#2d3748);border-radius:14px;
    padding:22px 26px;margin-bottom:20px;border:1px solid #3d4a63}
.page-title{font-size:22px;font-weight:800;color:#f59e0b}
.page-sub{font-size:13px;color:#64748b;margin-top:4px}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# SECTION 3 — UTILITY FUNCTIONS
# ══════════════════════════════════════════════════════════════
def get_cairo_time() -> datetime:
    return datetime.now(ZoneInfo('Africa/Cairo'))

def safe_last(s: pd.Series, default=0.0) -> float:
    try:
        v = s.dropna()
        return float(v.iloc[-1]) if not v.empty else default
    except (IndexError, TypeError, ValueError):
        return default

def fmt_num(num, decimals=2) -> str:
    try:
        if num is None: return "N/A"
        n = float(num)
        if np.isnan(n) or np.isinf(n): return "N/A"
        if abs(n) >= 1e9: return f"{n/1e9:.2f}B"
        if abs(n) >= 1e6: return f"{n/1e6:.2f}M"
        if abs(n) >= 1e3: return f"{n/1e3:.1f}K"
        return f"{n:,.{decimals}f}"
    except (TypeError, ValueError, OverflowError):
        return "N/A"

def fmt_egp(num) -> str:
    return f"EGP {fmt_num(num)}"

def get_simulation_warning_html(symbol: str) -> str:
    return f"""<div class="simulation-warning">
    <div class="simulation-warning-title">⚠️ تحذير: بيانات محاكاة إحصائية
        <span class="simulation-badge">🔴 محاكاة</span></div>
    <div class="simulation-warning-body">
        البيانات المعروضة للسهم <b>{symbol}</b> هي <b>بيانات مُولَّدة إحصائياً</b> وليست أسعاراً حقيقية.<br>
        📌 السبب: تعذّر جلب البيانات الفعلية من Yahoo Finance في هذه الجلسة.<br>
        🚫 لا تتخذ أي قرارات استثمارية بناءً على هذه الأرقام.
    </div></div>"""

def get_data_source_badge(source: str) -> str:
    if source == 'real':
        return '<span class="real-badge">🟢 بيانات حقيقية</span>'
    return '<span class="simulation-badge">🔴 محاكاة إحصائية</span>'


# ══════════════════════════════════════════════════════════════
# SECTION 4 — EGX DATABASE
# ══════════════════════════════════════════════════════════════
class EGXDatabase:
    STOCKS: Dict[str, Dict] = {
        'COMI':{'name':'Commercial International Bank','name_ar':'البنك التجاري الدولي','sector':'Banking','yf':'COMI.CA','base':85,'market_cap':95e9,'pe':10.2,'eps':8.3,'div_yield':4.2,'employees':8500,'founded':1975},
        'ABQQ':{'name':'Abu Qir Fertilizers','name_ar':'أبو قير للأسمدة','sector':'Chemicals','yf':'ABQQ.CA','base':55,'market_cap':28e9,'pe':8.5,'eps':6.5,'div_yield':5.8,'employees':3200,'founded':1976},
        'EKHO':{'name':'EFG Hermes','name_ar':'هيرميس المالية','sector':'Financial Services','yf':'EKHO.CA','base':32,'market_cap':18e9,'pe':15.3,'eps':2.1,'div_yield':2.1,'employees':4500,'founded':1984},
        'HRHO':{'name':'Hassan Allam Construction','name_ar':'حسن علام','sector':'Construction','yf':'HRHO.CA','base':28,'market_cap':12e9,'pe':12.1,'eps':2.3,'div_yield':1.8,'employees':12000,'founded':1956},
        'ETEL':{'name':'Telecom Egypt','name_ar':'المصرية للاتصالات','sector':'Telecom','yf':'ETEL.CA','base':22,'market_cap':35e9,'pe':9.8,'eps':2.2,'div_yield':6.3,'employees':27000,'founded':1854},
        'SWDY':{'name':'Elsewedy Electric','name_ar':'السويدي إليكتريك','sector':'Industrial','yf':'SWDY.CA','base':40,'market_cap':42e9,'pe':11.5,'eps':3.5,'div_yield':3.1,'employees':35000,'founded':1938},
        'SKPC':{'name':'Sidi Kerir Petrochemicals','name_ar':'سيدي كرير للبتروكيماويات','sector':'Chemicals','yf':'SKPC.CA','base':18,'market_cap':8e9,'pe':7.2,'eps':2.5,'div_yield':7.5,'employees':1800,'founded':1997},
        'AMOC':{'name':'Alexandria Mineral Oils','name_ar':'الإسكندرية للزيوت المعدنية','sector':'Energy','yf':'AMOC.CA','base':95,'market_cap':15e9,'pe':9.3,'eps':10.2,'div_yield':3.8,'employees':2200,'founded':1956},
        'FWRY':{'name':'Fawry Digital Payments','name_ar':'فوري للتكنولوجيا','sector':'Technology','yf':'FWRY.CA','base':12,'market_cap':9e9,'pe':35.2,'eps':0.34,'div_yield':0.0,'employees':3500,'founded':2008},
        'RAYA':{'name':'Raya Holding','name_ar':'راية القابضة','sector':'Technology','yf':'RAYA.CA','base':8,'market_cap':6e9,'pe':18.5,'eps':0.43,'div_yield':1.2,'employees':8000,'founded':1999},
        'MNHD':{'name':'Madinet Nasr Housing','name_ar':'مدينة نصر للإسكان','sector':'Real Estate','yf':'MNHD.CA','base':15,'market_cap':11e9,'pe':14.2,'eps':1.06,'div_yield':3.5,'employees':1500,'founded':1959},
        'TMGH':{'name':'Talaat Mostafa Group','name_ar':'طلعت مصطفى','sector':'Real Estate','yf':'TMGH.CA','base':25,'market_cap':48e9,'pe':18.7,'eps':1.34,'div_yield':2.2,'employees':22000,'founded':1974},
        'JUFO':{'name':'Juhayna Food Industries','name_ar':'جهينة للصناعات الغذائية','sector':'Food & Beverage','yf':'JUFO.CA','base':14,'market_cap':7e9,'pe':22.3,'eps':0.63,'div_yield':1.5,'employees':7200,'founded':1983},
        'PHDC':{'name':'Palm Hills Developments','name_ar':'بالم هيلز','sector':'Real Estate','yf':'PHDC.CA','base':6,'market_cap':14e9,'pe':16.8,'eps':0.36,'div_yield':0.0,'employees':3200,'founded':2005},
        'ESRS':{'name':'Ezz Steel','name_ar':'عز للصلب','sector':'Industrial','yf':'ESRS.CA','base':60,'market_cap':38e9,'pe':7.5,'eps':8.0,'div_yield':4.5,'employees':18000,'founded':1994},
        'ORAS':{'name':'Orascom Construction','name_ar':'أوراسكوم للإنشاءات','sector':'Construction','yf':'ORAS.CA','base':45,'market_cap':25e9,'pe':13.2,'eps':3.41,'div_yield':2.8,'employees':65000,'founded':1950},
        'ACBK':{'name':'Al Ahli Bank','name_ar':'البنك الأهلي','sector':'Banking','yf':'ACBK.CA','base':18,'market_cap':25e9,'pe':7.5,'eps':2.4,'div_yield':5.8,'employees':9200,'founded':1978},
        'NBKE':{'name':'National Bank of Egypt','name_ar':'البنك الأهلي المصري','sector':'Banking','yf':'NBKE.CA','base':65,'market_cap':180e9,'pe':6.8,'eps':9.56,'div_yield':7.2,'employees':25000,'founded':1898},
        'EGCH':{'name':'Egyptian Chemical Industries','name_ar':'الصناعات الكيماوية المصرية','sector':'Chemicals','yf':'EGCH.CA','base':20,'market_cap':5e9,'pe':8.9,'eps':2.25,'div_yield':5.2,'employees':2800,'founded':1938},
        'MPRC':{'name':'Misr Petroleum','name_ar':'مصر للبترول','sector':'Energy','yf':'MPRC.CA','base':35,'market_cap':12e9,'pe':8.1,'eps':4.32,'div_yield':5.5,'employees':4500,'founded':1950},
        'PHAR':{'name':'Pharma Group','name_ar':'مجموعة فارما','sector':'Healthcare','yf':'PHAR.CA','base':18,'market_cap':9e9,'pe':28.5,'eps':0.63,'div_yield':0.5,'employees':5500,'founded':1998},
        'IHYA':{'name':'Ibnsina Pharma','name_ar':'ابن سينا للأدوية','sector':'Healthcare','yf':'IHYA.CA','base':22,'market_cap':6e9,'pe':19.8,'eps':1.11,'div_yield':1.8,'employees':3200,'founded':2001},
        'GBCO':{'name':'GB Auto','name_ar':'جي بي للسيارات','sector':'Automotive','yf':'GBCO.CA','base':8,'market_cap':8e9,'pe':9.2,'eps':0.87,'div_yield':3.2,'employees':12000,'founded':1977},
        'ACGC':{'name':'Arabian Cement','name_ar':'الأسمنت العربية','sector':'Construction','yf':'ACGC.CA','base':12,'market_cap':5e9,'pe':10.5,'eps':1.14,'div_yield':6.0,'employees':1800,'founded':1998},
        'OCDI':{'name':'Orascom Development','name_ar':'أوراسكوم للتطوير','sector':'Real Estate','yf':'OCDI.CA','base':28,'market_cap':20e9,'pe':20.1,'eps':1.39,'div_yield':0.0,'employees':8500,'founded':1989},
        'CIEB':{'name':'CIB Egypt','name_ar':'بنك القاهرة الدولي','sector':'Banking','yf':'CIEB.CA','base':30,'market_cap':22e9,'pe':8.8,'eps':3.41,'div_yield':3.9,'employees':6800,'founded':1987},
        'EFIH':{'name':'EFG Finance','name_ar':'هيرميس التمويل','sector':'Financial Services','yf':'EFIH.CA','base':15,'market_cap':12e9,'pe':16.3,'eps':0.92,'div_yield':1.5,'employees':1500,'founded':1999},
        'KABO':{'name':'Kabour & Sons','name_ar':'كابور وأولاده','sector':'Industrial','yf':'KABO.CA','base':8,'market_cap':2e9,'pe':11.2,'eps':0.71,'div_yield':3.5,'employees':2200,'founded':1956},
    }

    EGX30: List[str] = []
    EGX70: List[str] = []
    EGX100: List[str] = []
    SECTOR_MAP: Dict[str, List[str]] = {}

    @classmethod
    def build_indices(cls):
        by_cap = sorted(cls.STOCKS, key=lambda s: cls.STOCKS[s].get('market_cap', 0), reverse=True)
        cls.EGX30  = by_cap[:30]
        cls.EGX70  = by_cap[30:100]
        cls.EGX100 = by_cap[100:]
        cls.SECTOR_MAP = {}
        for sym, info in cls.STOCKS.items():
            cls.SECTOR_MAP.setdefault(info.get('sector', 'Other'), []).append(sym)

EGXDatabase.build_indices()


# ══════════════════════════════════════════════════════════════
# SECTION 5 — TECHNICAL INDICATORS
# ══════════════════════════════════════════════════════════════
def calc_ema(s: pd.Series, p: int) -> pd.Series:
    return s.ewm(span=p, adjust=False).mean()

def calc_atr(h, l, c, period=14) -> pd.Series:
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(period, min_periods=1).mean()

def calc_rsi(prices: pd.Series, period=14) -> pd.Series:
    d = prices.diff()
    g = d.where(d > 0, 0).ewm(alpha=1/period, min_periods=period).mean()
    l = (-d).where(d < 0, 0).ewm(alpha=1/period, min_periods=period).mean()
    return (100 - 100 / (1 + g / l.replace(0, np.nan))).fillna(50).clip(0, 100)

def calc_macd(c, fast=12, slow=26, sig=9):
    m = calc_ema(c, fast) - calc_ema(c, slow)
    s = calc_ema(m, sig)
    return m, s, m - s

def calc_bollinger(c, period=20, std_dev=2.0):
    sma = c.rolling(period).mean()
    std = c.rolling(period).std()
    upper, lower = sma + std*std_dev, sma - std*std_dev
    pct_b = (c - lower) / (upper - lower).replace(0, np.nan)
    width = (upper - lower) / sma.replace(0, np.nan) * 100
    return upper, lower, pct_b.fillna(0.5), width.fillna(0)

def calc_mfi(h, l, c, v, period=14) -> pd.Series:
    """✅ Money Flow Index — مُضاف v35"""
    tp = (h + l + c) / 3
    mf = tp * v
    pos = mf.where(tp > tp.shift(1), 0.0).rolling(period, min_periods=1).sum()
    neg = mf.where(tp <= tp.shift(1), 0.0).rolling(period, min_periods=1).sum()
    return (100 - 100 / (1 + pos / neg.replace(0, np.nan))).fillna(50).clip(0, 100)

def calc_keltner(h, l, c, ema_p=20, atr_p=10, mult=2.0):
    """✅ Keltner Channels — مُضاف v35"""
    mid = calc_ema(c, ema_p)
    atr = calc_atr(h, l, c, atr_p)
    return mid + mult*atr, mid, mid - mult*atr

def calc_supertrend(df: pd.DataFrame, period=10, multiplier=3.0) -> Tuple[pd.Series, pd.Series]:
    """NumPy loop — no FutureWarning"""
    h, l, c = df['high'].values, df['low'].values, df['close'].values
    hl2 = (h + l) / 2
    atr_arr = calc_atr(df['high'], df['low'], df['close'], period).values
    ub = hl2 + multiplier * atr_arr
    lb = hl2 - multiplier * atr_arr
    n = len(c)
    final_ub = np.full(n, np.nan)
    final_lb = np.full(n, np.nan)
    st_line  = np.full(n, np.nan)
    trend    = np.ones(n, dtype=int)
    final_ub[0] = ub[0]; final_lb[0] = lb[0]; st_line[0] = lb[0]
    for i in range(1, n):
        final_ub[i] = ub[i] if ub[i] < final_ub[i-1] or c[i-1] > final_ub[i-1] else final_ub[i-1]
        final_lb[i] = lb[i] if lb[i] > final_lb[i-1] or c[i-1] < final_lb[i-1] else final_lb[i-1]
        if st_line[i-1] == final_ub[i-1]:
            trend[i] = -1 if c[i] > final_ub[i] else -1
        else:
            trend[i] =  1 if c[i] < final_lb[i] else  1
        st_line[i] = final_lb[i] if trend[i] == 1 else final_ub[i]
    idx = df.index
    return pd.Series(st_line, index=idx), pd.Series(trend, index=idx)

def calc_vwap(df: pd.DataFrame) -> pd.Series:
    """VWAP يومي صحيح"""
    tp = (df['high'] + df['low'] + df['close']) / 3
    return (tp * df['volume']).cumsum() / df['volume'].cumsum()

def get_composite_signal(df: pd.DataFrame) -> Tuple[str, float, str]:
    if df is None or df.empty: return "محايد", 0.0, "⚪"
    score = 0.0
    if 'rsi' in df.columns:
        r = safe_last(df['rsi'], 50)
        if r < 30: score += 1.5
        elif r < 45: score += 0.5
        elif r > 70: score -= 1.5
        elif r > 55: score -= 0.5
    if 'macd' in df.columns and 'macd_signal' in df.columns:
        m, s = safe_last(df['macd']), safe_last(df['macd_signal'])
        if m > s: score += 1.0
        else: score -= 1.0
    if 'close' in df.columns and 'ema_20' in df.columns and 'ema_50' in df.columns:
        c, e20, e50 = safe_last(df['close']), safe_last(df['ema_20']), safe_last(df['ema_50'])
        if c > e20 > e50: score += 1.5
        elif c < e20 < e50: score -= 1.5
    if 'supertrend_dir' in df.columns:
        if safe_last(df['supertrend_dir']) == 1: score += 1.0
        else: score -= 1.0
    if score >= 2.5:  return "شراء قوي",   min(score / 5, 1.0), "🟢"
    if score >= 1.0:  return "شراء",        min(score / 5, 1.0), "🟢"
    if score <= -2.5: return "بيع قوي",     min(abs(score)/5,1.0),"🔴"
    if score <= -1.0: return "بيع",          min(abs(score)/5,1.0),"🔴"
    return "محايد", 0.3, "⚪"

def detect_patterns(df: pd.DataFrame) -> List[Dict]:
    if df is None or len(df) < 3: return []
    patterns = []
    o, h, l, c = (df[col].values for col in ['open','high','low','close'])
    n = len(c) - 1
    def body(i): return abs(c[i] - o[i])
    def range_(i): return h[i] - l[i]
    # Doji
    if range_(n) > 0 and body(n) / range_(n) < 0.1:
        patterns.append({'name':'Doji','name_ar':'دوجي','bullish':None,'desc':'تردد في السوق'})
    # Hammer
    if (body(n) < range_(n)*0.3 and min(o[n],c[n])-l[n] > body(n)*2 and h[n]-max(o[n],c[n]) < body(n)*0.5):
        patterns.append({'name':'Hammer','name_ar':'المطرقة','bullish':True,'desc':'إشارة انعكاس صاعد محتملة'})
    # Bullish Engulfing
    if n >= 1 and c[n-1] < o[n-1] and c[n] > o[n] and o[n] < c[n-1] and c[n] > o[n-1]:
        patterns.append({'name':'Bullish Engulfing','name_ar':'الابتلاع الصاعد','bullish':True,'desc':'انعكاس صاعد قوي'})
    # Bearish Engulfing
    if n >= 1 and c[n-1] > o[n-1] and c[n] < o[n] and o[n] > c[n-1] and c[n] < o[n-1]:
        patterns.append({'name':'Bearish Engulfing','name_ar':'الابتلاع الهابط','bullish':False,'desc':'انعكاس هابط قوي'})
    # Morning Star
    if n >= 2 and c[n-2] < o[n-2] and body(n-1) < range_(n-1)*0.3 and c[n] > o[n] and c[n] > (o[n-2]+c[n-2])/2:
        patterns.append({'name':'Morning Star','name_ar':'نجمة الصباح','bullish':True,'desc':'انعكاس صاعد ثلاثي الشموع'})
    return patterns

def get_support_resistance(df: pd.DataFrame) -> Dict:
    if df is None or len(df) < 20: return {'support': 0, 'resistance': 0}
    c = df['close'].iloc[-1]
    atr = safe_last(df.get('atr', pd.Series([c*0.02])))
    sup = df['low'].rolling(20).min().iloc[-1]
    res = df['high'].rolling(20).max().iloc[-1]
    return {'support': round(sup, 2), 'resistance': round(res, 2),
            'nearest_support': round(sup, 2), 'nearest_resistance': round(res, 2),
            'support_distance_pct': round((c - sup) / c * 100, 1),
            'resistance_distance_pct': round((res - c) / c * 100, 1)}

def get_fibonacci_levels(df: pd.DataFrame) -> Dict:
    if df is None or df.empty: return {}
    h, l = df['high'].max(), df['low'].min()
    d = h - l
    return {str(lvl): round(h - d*lvl, 2) for lvl in [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]}


# ══════════════════════════════════════════════════════════════
# SECTION 6 — DATA ENGINE
# ══════════════════════════════════════════════════════════════
SECTOR_REVENUE_GROWTH = {
    'Banking':0.12, 'Real Estate':0.18, 'Technology':0.25,
    'Chemicals':0.08, 'Industrial':0.07, 'Food & Beverage':0.10,
    'Healthcare':0.15, 'Telecom':0.06, 'Energy':0.09,
    'Construction':0.11, 'Automotive':0.08, 'Financial Services':0.14,
}

def fetch_quarterly_financials(symbol: str) -> Optional[pd.DataFrame]:
    """جلب البيانات الفصلية — yfinance أو تقدير تلقائي"""
    info = EGXDatabase.STOCKS.get(symbol, {})
    if info.get('yf'):
        try:
            import yfinance as yf
            q = yf.Ticker(info['yf']).quarterly_financials
            if q is not None and not q.empty:
                rows = []
                for col in q.columns[:8]:
                    try:
                        rev = float(q.loc['Total Revenue', col]) if 'Total Revenue' in q.index else None
                        ni  = float(q.loc['Net Income', col])    if 'Net Income' in q.index else None
                        if rev and ni:
                            rows.append({'quarter': str(col)[:7], 'revenue': rev, 'net_income': ni,
                                         'eps': round(ni / max(info.get('market_cap',1e9)/max(info.get('base',10),1),1),2),
                                         'margin': round(ni/rev*100,1), 'source':'real'})
                    except Exception: continue
                if rows: return pd.DataFrame(rows)
        except Exception as e:
            logger.debug(f"quarterly {symbol}: {e}")
    # Estimated
    sector = info.get('sector','Banking')
    base_rev = info.get('market_cap', 10e9) * 0.15
    growth   = SECTOR_REVENUE_GROWTH.get(sector, 0.10)
    rows = []
    for i in range(8):
        q_idx = 7 - i
        factor = (1 + growth/4) ** q_idx
        dt = datetime.now() - timedelta(days=90*(8-i))
        rev = base_rev * factor * (1 + np.random.uniform(-0.05, 0.05))
        ni  = rev * 0.20 * (1 + np.random.uniform(-0.08, 0.08))
        rows.append({'quarter': f"{dt.year} Q{(dt.month-1)//3+1}", 'revenue': round(rev),
                     'net_income': round(ni), 'eps': round(ni/max(info.get('market_cap',1e9)/max(info.get('base',10),1),1),2),
                     'margin': round(ni/rev*100,1), 'source':'estimated'})
    return pd.DataFrame(rows[::-1])

def generate_simulated_data(symbol: str, days: int = 300) -> pd.DataFrame:
    info = EGXDatabase.STOCKS.get(symbol, {})
    base = info.get('base', 20.0)
    np.random.seed(hash(symbol) % 2**31)
    dt = pd.bdate_range(end=datetime.now(), periods=days, freq='C',
                        holidays=[], weekmask='Sun Mon Tue Wed Thu')
    returns = np.random.normal(0.0003, 0.018, days)
    close = np.cumprod(1 + returns) * base
    close = np.maximum(close, base * 0.1)
    h = np.random.uniform(0.5, 2.5)
    variance = np.var(returns)
    omega, alpha_g, beta_g = variance*0.05, 0.1, 0.85
    cond_var = np.full(days, variance)
    for i in range(1, days):
        cond_var[i] = omega + alpha_g*returns[i-1]**2 + beta_g*cond_var[i-1]
    vol = np.sqrt(np.maximum(cond_var, 1e-8))
    high   = close * (1 + np.abs(np.random.normal(0, vol, days)) * 0.5)
    low    = close * (1 - np.abs(np.random.normal(0, vol, days)) * 0.5)
    open_  = np.roll(close, 1); open_[0] = close[0]
    volume = np.random.randint(500_000, 5_000_000, days).astype(float)
    df = pd.DataFrame({'open':open_, 'high':high, 'low':low, 'close':close, 'volume':volume}, index=dt)
    df['data_source'] = 'simulated'
    return df.round(3)

def fetch_real_data(symbol: str, days: int = 300) -> Optional[pd.DataFrame]:
    try:
        yf_sym = EGXDatabase.STOCKS.get(symbol, {}).get('yf')
        if not yf_sym: return None
        import yfinance as yf
        df = yf.Ticker(yf_sym).history(period=f"{days+60}d", interval="1d", auto_adjust=True)
        if df.empty or len(df) < 30: return None
        df = df[['Open','High','Low','Close','Volume']].copy()
        df.columns = ['open','high','low','close','volume']
        df.index = pd.to_datetime(df.index).tz_localize(None)
        df['data_source'] = 'real'
        return df.dropna().tail(days)
    except Exception as e:
        logger.debug(f"fetch_real_data({symbol}): {e}")
        return None

def load_and_compute(symbol: str, days: int = 300) -> Optional[pd.DataFrame]:
    df = fetch_real_data(symbol, days) or generate_simulated_data(symbol, days)
    if df is None or len(df) < 30: return None
    df = df.copy()
    h, l, c, v = df['high'], df['low'], df['close'], df['volume']
    # Moving averages
    for p in [9, 20, 21, 50, 200]: df[f'ema_{p}'] = calc_ema(c, p)
    df['sma_20'] = c.rolling(20).mean()
    df['vwap']   = calc_vwap(df)
    # Momentum
    df['rsi'] = calc_rsi(c)
    df['macd'], df['macd_signal'], df['macd_hist'] = calc_macd(c)
    df['bb_upper'], df['bb_lower'], df['bb_pct_b'], df['bb_width'] = calc_bollinger(c)
    # Trend
    df['atr'] = calc_atr(h, l, c)
    df['supertrend'], df['supertrend_dir'] = calc_supertrend(df)
    # ADX
    plus_dm = h.diff().clip(lower=0)
    minus_dm = (-l.diff()).clip(lower=0)
    atr14 = calc_atr(h, l, c, 14)
    plus_di  = 100 * (plus_dm.rolling(14).mean()  / atr14.replace(0, np.nan))
    minus_di = 100 * (minus_dm.rolling(14).mean() / atr14.replace(0, np.nan))
    dx = (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan) * 100
    df['adx'] = dx.rolling(14).mean().fillna(0)
    df['plus_di'] = plus_di.fillna(0)
    df['minus_di'] = minus_di.fillna(0)
    # Ichimoku
    df['tenkan']    = (h.rolling(9).max()  + l.rolling(9).min())  / 2
    df['kijun']     = (h.rolling(26).max() + l.rolling(26).min()) / 2
    df['senkou_a']  = ((df['tenkan'] + df['kijun']) / 2).shift(26)
    df['senkou_b']  = ((h.rolling(52).max() + l.rolling(52).min()) / 2).shift(26)
    df['chikou']    = c.shift(-26)
    # PSAR
    psar = c.copy(); trend, ep = 1, float(h.iloc[0]); af = 0.02
    for i in range(1, len(df)):
        psar.iloc[i] = psar.iloc[i-1] + af * (ep - psar.iloc[i-1])
        if trend == 1:
            if float(l.iloc[i]) < float(psar.iloc[i]):
                trend = -1; psar.iloc[i] = ep; ep = float(l.iloc[i]); af = 0.02
            elif float(h.iloc[i]) > ep: ep = float(h.iloc[i]); af = min(af+0.02, 0.2)
        else:
            if float(h.iloc[i]) > float(psar.iloc[i]):
                trend = 1; psar.iloc[i] = ep; ep = float(h.iloc[i]); af = 0.02
            elif float(l.iloc[i]) < ep: ep = float(l.iloc[i]); af = min(af+0.02, 0.2)
    df['psar'] = psar
    # Volume
    df['vol_sma']   = v.rolling(20).mean()
    df['vol_ratio'] = v / df['vol_sma'].replace(0, np.nan)
    df['obv']       = (np.sign(c.diff()) * v).cumsum()
    # Stochastic
    low14 = l.rolling(14).min(); high14 = h.rolling(14).max()
    df['stoch_k'] = 100 * (c - low14) / (high14 - low14).replace(0, np.nan)
    df['stoch_d'] = df['stoch_k'].rolling(3).mean()
    # CCI + Williams R
    tp = (h + l + c) / 3
    df['cci']       = (tp - tp.rolling(20).mean()) / (0.015 * tp.rolling(20).std().replace(0, np.nan))
    df['williams_r']= -100 * (h.rolling(14).max() - c) / (h.rolling(14).max() - l.rolling(14).min()).replace(0, np.nan)
    # ✅ MFI + Keltner (v35)
    df['mfi']       = calc_mfi(h, l, c, v)
    df['kc_upper'], df['kc_mid'], df['kc_lower'] = calc_keltner(h, l, c)
    # Misc
    df['roc']           = (c - c.shift(12)) / c.shift(12).replace(0, np.nan) * 100
    df['volatility_20d']= c.pct_change().rolling(20).std() * np.sqrt(252)
    df['z_score']       = (c - c.rolling(20).mean()) / c.rolling(20).std().replace(0, np.nan)
    return df


# ══════════════════════════════════════════════════════════════
# SECTION 7 — BACKTEST ENGINE (EGX Commission 18.5 bps)
# ══════════════════════════════════════════════════════════════
EGX_COMMISSION = 0.00150
EGX_STAMP      = 0.00025
EGX_CUSTODY    = 0.00010
EGX_TOTAL_COST = EGX_COMMISSION + EGX_STAMP + EGX_CUSTODY   # 18.5 bps
EGX_SLIPPAGE   = 0.0010
MIN_TRADE_EGP  = 500

def _cost(price: float, side: str) -> float:
    t = EGX_TOTAL_COST + EGX_SLIPPAGE
    return price * (1 + t) if side == 'buy' else price * (1 - t)

@dataclass
class Trade:
    entry_date: Any; exit_date: Any; entry_price: float; exit_price: float
    shares: int; entry_cost: float; pnl: float; pnl_pct: float
    trade_cost: float; strategy: str

@dataclass
class BacktestResult:
    strategy: str; initial_capital: float; final_capital: float
    total_return: float; annualized_return: float; sharpe: float
    max_drawdown: float; win_rate: float; total_trades: int
    profit_factor: float; calmar: float; avg_win: float; avg_loss: float
    equity_curve: List[float] = field(default_factory=list)
    trades: List[Trade] = field(default_factory=list)

ALL_STRATEGIES = [
    'EMA Cross','RSI Mean Reversion','MACD','Bollinger Bands',
    'Supertrend','VWAP+RSI','PSAR','Ichimoku','ADX Trend','Multi-Signal'
]

def _generate_signals(df: pd.DataFrame, strategy: str) -> np.ndarray:
    n = len(df)
    buy = np.zeros(n, bool); sell = np.zeros(n, bool)
    c = df['close'].values
    def col(name, default=0):
        return df[name].values if name in df.columns else np.full(n, default)
    if strategy == 'EMA Cross':
        e9, e21 = col('ema_9'), col('ema_21')
        buy[1:]  = (e9[1:] > e21[1:]) & (e9[:-1] <= e21[:-1])
        sell[1:] = (e9[1:] < e21[1:]) & (e9[:-1] >= e21[:-1])
    elif strategy == 'RSI Mean Reversion':
        rsi = col('rsi', 50)
        buy[1:]  = (rsi[1:] > 30) & (rsi[:-1] <= 30)
        sell[1:] = (rsi[1:] < 70) & (rsi[:-1] >= 70)
    elif strategy == 'MACD':
        m, s = col('macd'), col('macd_signal')
        buy[1:]  = (m[1:] > s[1:]) & (m[:-1] <= s[:-1])
        sell[1:] = (m[1:] < s[1:]) & (m[:-1] >= s[:-1])
    elif strategy == 'Bollinger Bands':
        ub, lb = col('bb_upper', c.max()), col('bb_lower', c.min())
        buy[1:]  = (c[1:] > lb[1:]) & (c[:-1] <= lb[:-1])
        sell[1:] = (c[1:] < ub[1:]) & (c[:-1] >= ub[:-1])
    elif strategy == 'Supertrend':
        d = col('supertrend_dir', 1)
        buy[1:]  = (d[1:] == 1) & (d[:-1] == -1)
        sell[1:] = (d[1:] == -1) & (d[:-1] == 1)
    elif strategy == 'VWAP+RSI':
        vw, rsi = col('vwap', c), col('rsi', 50)
        buy  = (c > vw) & (rsi < 50) & (rsi > 30)
        sell = (c < vw) | (rsi > 65)
    elif strategy == 'PSAR':
        ps, d = col('psar', c), col('supertrend_dir', 1)
        buy[1:]  = (c[1:] > ps[1:]) & (c[:-1] <= ps[:-1])
        sell[1:] = (c[1:] < ps[1:]) & (c[:-1] >= ps[:-1])
    elif strategy == 'Ichimoku':
        sa, sb = col('senkou_a', c), col('senkou_b', c)
        cloud_top = np.maximum(sa, sb)
        buy  = c > cloud_top
        sell = c < np.minimum(sa, sb)
    elif strategy == 'ADX Trend':
        adx, pd_, md_ = col('adx', 0), col('plus_di', 0), col('minus_di', 0)
        buy  = (adx > 25) & (pd_ > md_)
        sell = (adx > 25) & (md_ > pd_)
    else:  # Multi-Signal
        rsi = col('rsi', 50)
        e9, e21 = col('ema_9'), col('ema_21')
        d = col('supertrend_dir', 1)
        m, s_ = col('macd'), col('macd_signal')
        buy  = (rsi < 45) & (e9 > e21) & (d == 1) & (m > s_)
        sell = (rsi > 60) | (d == -1)
    return buy, sell

def _run_backtest(df: pd.DataFrame, strategy: str, capital: float = 100_000) -> BacktestResult:
    if df is None or len(df) < 50:
        return BacktestResult(strategy, capital, capital, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    buy, sell = _generate_signals(df, strategy)
    c_arr = df['close'].values
    pos = 0; ep = 0.0; ed = None; cap = capital
    trades, equity = [], []
    for i in range(len(df)):
        price = float(c_arr[i])
        if buy[i] and pos == 0 and cap > MIN_TRADE_EGP:
            cp = _cost(price, 'buy')
            sh = int(cap * 0.95 / cp)
            if sh > 0:
                # ✅ إصلاح LOG-1: cp يشمل العمولة — entry_cost فقط
                entry_cost = sh * cp
                cap -= entry_cost
                pos, ep, ed = sh, cp, df.index[i]
        elif sell[i] and pos > 0:
            sp = _cost(price, 'sell')
            pr = pos * sp
            entry_total = pos * ep
            # ✅ إصلاح LOG-2: pnl يطرح التكاليف الكاملة
            pnl = pr - entry_total
            pct = pnl / entry_total if entry_total > 0 else 0
            tc  = entry_total * (EGX_TOTAL_COST + EGX_SLIPPAGE) * 2
            cap += pr
            trades.append(Trade(ed, df.index[i], ep, sp, pos, entry_total, pnl, pct, tc, strategy))
            pos = 0
        equity.append(cap + (pos * price if pos > 0 else 0))
    if pos > 0:
        lp = float(c_arr[-1]); sp = _cost(lp, 'sell'); pr = pos * sp
        entry_total = pos * ep
        pnl = pr - entry_total; pct = pnl / entry_total if entry_total > 0 else 0
        cap += pr
        trades.append(Trade(ed, df.index[-1], ep, sp, pos, entry_total, pnl, pct, 0, strategy))
    # Metrics
    final_cap  = cap
    total_ret  = (final_cap - capital) / capital * 100
    n_days     = max(len(equity), 1)
    ann_ret    = ((final_cap / capital) ** (252 / n_days) - 1) * 100
    eq         = np.array(equity)
    daily_r    = np.diff(eq) / np.maximum(eq[:-1], 1e-8)
    sharpe     = (daily_r.mean() / daily_r.std() * np.sqrt(252)) if daily_r.std() > 0 else 0
    peak       = np.maximum.accumulate(eq)
    drawdowns  = (eq - peak) / np.maximum(peak, 1e-8) * 100
    max_dd     = float(drawdowns.min())
    calmar     = ann_ret / abs(max_dd) if max_dd != 0 else 0
    win_trades = [t for t in trades if t.pnl > 0]
    los_trades = [t for t in trades if t.pnl <= 0]
    win_rate   = len(win_trades) / max(len(trades), 1)
    avg_win    = np.mean([t.pnl_pct for t in win_trades]) if win_trades else 0
    avg_loss   = abs(np.mean([t.pnl_pct for t in los_trades])) if los_trades else 0
    gross_p    = sum(t.pnl for t in win_trades)
    gross_l    = abs(sum(t.pnl for t in los_trades))
    pf         = gross_p / gross_l if gross_l > 0 else float('inf')
    return BacktestResult(strategy, capital, final_cap, total_ret, ann_ret, sharpe,
                          max_dd, win_rate, len(trades), pf, calmar, avg_win, avg_loss,
                          equity_curve=equity, trades=trades)

def run_all_backtests(df, capital=100_000, strategies=None) -> List[BacktestResult]:
    strategies = strategies or ALL_STRATEGIES
    return [_run_backtest(df, s, capital) for s in strategies]

def backtest_summary_df(results: List[BacktestResult]) -> pd.DataFrame:
    if not results: return pd.DataFrame()
    return pd.DataFrame([{
        'الاستراتيجية': r.strategy, 'العائد %': round(r.total_return, 1),
        'عائد سنوي %': round(r.annualized_return, 1), 'شارب': round(r.sharpe, 2),
        'أقصى هبوط %': round(r.max_drawdown, 1), 'نسبة الربح %': round(r.win_rate*100, 1),
        'الصفقات': r.total_trades, 'معامل الربح': round(r.profit_factor, 2),
        'كالمار': round(r.calmar, 2),
    } for r in results]).sort_values('عائد سنوي %', ascending=False).reset_index(drop=True)

def dca_simulation(df, monthly_amount: float = 1000, months: int = 12) -> Dict:
    if df is None or len(df) < 30:
        return {'error': 'بيانات غير كافية'}
    # ✅ إصلاح MISS-4: تحقق من المدخلات
    if monthly_amount <= 0: return {'error': 'المبلغ الشهري يجب أن يكون أكبر من الصفر'}
    if months <= 0: return {'error': 'عدد الشهور يجب أن يكون أكبر من الصفر'}
    c = df['close']
    step = max(int(len(c) / max(months, 1)), 1)
    indices = list(range(0, len(c), step))[:months]
    total_invested = 0; total_shares = 0; monthly_data = []
    for idx in indices:
        price = float(c.iloc[idx])
        shares = monthly_amount / price if price > 0 else 0
        total_invested += monthly_amount; total_shares += shares
        avg_cost = total_invested / total_shares if total_shares > 0 else price
        current_value = total_shares * price
        monthly_data.append({'month': idx//step+1, 'price': price,
                              'shares_bought': shares, 'total_shares': total_shares,
                              'avg_cost': avg_cost, 'total_invested': total_invested,
                              'current_value': current_value,
                              'unrealized_pnl': current_value - total_invested})
    final_price   = float(c.iloc[-1])
    final_value   = total_shares * final_price
    total_return  = (final_value - total_invested) / total_invested * 100
    avg_cost_final = total_invested / total_shares if total_shares > 0 else final_price
    return {'total_invested': total_invested, 'total_shares': total_shares,
            'avg_cost': avg_cost_final, 'final_value': final_value,
            'total_return_pct': total_return, 'monthly_data': monthly_data,
            'unrealized_pnl': final_value - total_invested}


# ══════════════════════════════════════════════════════════════
# SECTION 8 — ML ENGINE
# ══════════════════════════════════════════════════════════════
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_sample_weight

FEATURE_COLS = ['rsi','macd','macd_hist','bb_pct_b','adx','stoch_k','cci',
                'williams_r','vol_ratio','roc','z_score','mfi']

if TORCH_AVAILABLE:
    class LSTMModel(nn.Module):
        def __init__(self, input_size=12, hidden=64, n_layers=2, dropout=0.2):
            super().__init__()
            self.lstm = nn.LSTM(input_size, hidden, n_layers, batch_first=True,
                                dropout=dropout if n_layers > 1 else 0)
            self.norm = nn.LayerNorm(hidden)
            self.head = nn.Sequential(nn.Linear(hidden, 32), nn.ReLU(),
                                      nn.Dropout(dropout), nn.Linear(32, 3))
        def forward(self, x):
            out, _ = self.lstm(x)
            return self.head(self.norm(out[:, -1, :]))

    class TransformerModel(nn.Module):
        def __init__(self, input_size=12, d_model=32, nhead=4, n_layers=2, dropout=0.1):
            super().__init__()
            self.proj = nn.Linear(input_size, d_model)
            enc = nn.TransformerEncoderLayer(d_model, nhead, d_model*4, dropout, batch_first=True)
            self.tf  = nn.TransformerEncoder(enc, n_layers)
            self.head = nn.Sequential(nn.Linear(d_model, 16), nn.ReLU(), nn.Linear(16, 3))
        def forward(self, x):
            return self.head(self.tf(self.proj(x)).mean(dim=1))


class EGXMLPredictor:
    def __init__(self, use_torch=True):
        self.use_torch = use_torch and TORCH_AVAILABLE
        self.gb = GradientBoostingClassifier(n_estimators=100, learning_rate=0.05,
                                              max_depth=4, random_state=42)
        self.scaler = StandardScaler()
        self.lstm  = LSTMModel()  if self.use_torch else None
        self.tf_model = TransformerModel() if self.use_torch else None
        self.trained = False
        self.SEQ_LEN = 20

    def _prepare_features(self, df: pd.DataFrame):
        feats = [c for c in FEATURE_COLS if c in df.columns]
        X = df[feats].fillna(0).values
        fwd = df['close'].pct_change(5).shift(-5)
        y = np.where(fwd > 0.02, 2, np.where(fwd < -0.02, 0, 1))
        return X, y, feats

    def _make_sequences(self, X: np.ndarray) -> np.ndarray:
        seqs = []
        for i in range(self.SEQ_LEN, len(X)):
            seqs.append(X[i-self.SEQ_LEN:i])
        return np.array(seqs)

    def train(self, df: pd.DataFrame) -> Dict:
        if df is None or len(df) < 100: return {'error': 'بيانات غير كافية'}
        X, y, feats = self._prepare_features(df)
        X_s = self.scaler.fit_transform(X)
        tscv = TimeSeriesSplit(n_splits=3)
        scores = []
        for tr, val in tscv.split(X_s):
            if len(tr) < 50: continue
            sw = compute_sample_weight('balanced', y[tr])
            self.gb.fit(X_s[tr], y[tr], sample_weight=sw)
            scores.append(self.gb.score(X_s[val], y[val]))
        # Final fit on all data
        sw_all = compute_sample_weight('balanced', y[:-5])
        self.gb.fit(X_s[:-5], y[:-5], sample_weight=sw_all)
        # Train PyTorch models
        if self.use_torch and len(X_s) > self.SEQ_LEN + 10:
            seqs = self._make_sequences(X_s)
            labels = y[self.SEQ_LEN:]
            t = torch.FloatTensor(seqs)
            lbl = torch.LongTensor(labels)
            ds  = TensorDataset(t, lbl)
            dl  = DataLoader(ds, batch_size=32, shuffle=False)
            for model in [self.lstm, self.tf_model]:
                opt = torch.optim.Adam(model.parameters(), lr=1e-3)
                criterion = nn.CrossEntropyLoss()
                model.train()
                for _ in range(10):
                    for xb, yb in dl:
                        opt.zero_grad()
                        loss = criterion(model(xb), yb)
                        loss.backward(); opt.step()
                model.eval()
        self.trained = True
        return {'accuracy': round(np.mean(scores), 3) if scores else 0,
                'features': feats, 'samples': len(X)}

    def predict(self, df: pd.DataFrame) -> Tuple[str, float, str]:
        if not self.trained or df is None or len(df) < 30:
            return "لم يُدرَّب", 0.0, "⚪"
        try:
            X, _, _ = self._prepare_features(df)
            X_s = self.scaler.transform(X)
            # GB probability
            gb_prob = self.gb.predict_proba(X_s[-1:].reshape(1,-1))[0]
            # Ensemble with PyTorch models
            if self.use_torch and len(X_s) >= self.SEQ_LEN:
                seq = torch.FloatTensor(X_s[-self.SEQ_LEN:]).unsqueeze(0)
                with torch.no_grad():
                    lstm_p  = torch.softmax(self.lstm(seq), dim=1).numpy()[0]
                    tf_p    = torch.softmax(self.tf_model(seq), dim=1).numpy()[0]
                probs = gb_prob*0.25 + lstm_p*0.40 + tf_p*0.35
            else:
                probs = gb_prob
            pred_cls = int(np.argmax(probs))
            conf     = float(probs[pred_cls])
            labels   = {0:("بيع","🔴"), 1:("محايد","⚪"), 2:("شراء","🟢")}
            return labels[pred_cls][0], conf, labels[pred_cls][1]
        except Exception as e:
            logger.warning(f"predict error: {e}")
            return "خطأ", 0.0, "⚪"


class PortfolioManager:
    def __init__(self, capital: float):
        self.capital = capital

    def calc_position_size(self, price, win_rate, avg_win, avg_loss, max_risk) -> Dict:
        kelly = (win_rate * avg_win - (1-win_rate) * avg_loss) / avg_win if avg_win > 0 else 0
        kelly = max(0, min(kelly * 0.5, max_risk))  # half-Kelly capped
        position_value = self.capital * kelly
        shares = int(position_value / price) if price > 0 else 0
        return {'shares': shares, 'value': shares*price, 'kelly_fraction': kelly,
                'position_pct': kelly*100, 'max_loss': shares*price*max_risk}

    def calc_stop_loss(self, price, atr, atr_mult=2.5) -> Dict:
        sl = price - atr * atr_mult
        tp = price + atr * atr_mult * 2
        return {'stop_loss': round(sl, 2), 'take_profit': round(tp, 2),
                'risk_reward': 2.0, 'sl_pct': round((price-sl)/price*100, 2)}


# ══════════════════════════════════════════════════════════════
# SECTION 9 — GEMINI AI
# ══════════════════════════════════════════════════════════════
class AIAnalyzer:
    def __init__(self, api_key=None):
        self.api_key = api_key or self._load_key()
        self.model = None; self._ready = False
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                # ✅ إصلاح LOG-3: gemini-2.0-flash كان يُسبب 404
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self._ready = True
            except ImportError: pass
            except Exception as e:
                logger.warning(f"Gemini init: {e}")

    def _load_key(self):
        try:
            import streamlit as st
            if 'GEMINI_API_KEY' in st.secrets: return st.secrets['GEMINI_API_KEY']
        except Exception: pass
        return os.environ.get('GEMINI_API_KEY')

    def is_available(self): return self._ready

    def _generate(self, prompt, fallback, timeout=20) -> str:
        if not self._ready: return fallback
        try:
            r = self.model.generate_content(prompt,
                generation_config={"max_output_tokens":1024},
                request_options={"timeout":timeout})
            return r.text.strip() or fallback
        except Exception as e:
            return f"⚠️ Gemini: {e}\n\n{fallback}"

    def analyze_stock(self, symbol, signal, rsi, price, sector) -> str:
        return self._generate(
            f"اكتب تعليقاً تحليلياً قصيراً (3-4 جمل) بالعربية عن سهم {symbol} من قطاع {sector} "
            f"في بورصة مصر. السعر الحالي {price:.2f} جنيه، RSI عند {rsi:.0f}، الإشارة: {signal}. "
            "لا تقدّم نصيحة استثمارية مباشرة.",
            f"السهم {symbol} (قطاع {sector}) يتداول عند {price:.2f} جنيه مع RSI={rsi:.0f}، الإشارة: {signal}.")

    def explain_indicator(self, name) -> str:
        fallbacks = {
            'RSI': '**RSI** يقيس زخم السعر (0-100). أقل من 30: تشبع بيع. أكثر من 70: تشبع شراء.',
            'MACD': '**MACD** يقيس الفرق بين متوسطين. التقاطع فوق الإشارة: شراء. تحتها: بيع.',
            'MFI': '**MFI** يقيس ضغط الشراء/البيع بالحجم. أقل من 20: تشبع بيع. أكثر من 80: تشبع شراء.',
        }
        return self._generate(
            f"اشرح مؤشر {name} الفني للمتداولين المصريين بالعربية (150 كلمة).",
            fallbacks.get(name, f"لا يوجد شرح متاح لـ {name}."))

ai_analyzer = AIAnalyzer()


# ══════════════════════════════════════════════════════════════
# SECTION 10 — NEWS ENGINE
# ══════════════════════════════════════════════════════════════
@dataclass
class NewsItem:
    id: str; title: str; summary: str; source: str; url: str
    published_at: datetime; priority: str = 'medium'
    symbol: Optional[str] = None; is_real: bool = True

def fetch_news(max_items=10) -> List[NewsItem]:
    items = []
    try:
        import feedparser
        feeds = [
            ('https://mubasher.info/countries/eg/rss/', 'مباشر'),
            ('https://amwalalghad.com/feed/', 'أموال الغد'),
        ]
        for url, name in feeds:
            try:
                feed = feedparser.parse(url, request_headers={'User-Agent':'EGX-Pro/35'})
                for e in feed.entries[:5]:
                    t = e.get('title', '')
                    if not t: continue
                    p = e.get('published_parsed')
                    dt = datetime(*p[:6]) if p else datetime.now()
                    priority = 'high' if any(w in t for w in ['أرباح','عائد','توزيع','ارتفع','انخفض']) else 'medium'
                    items.append(NewsItem(
                        id=hashlib.md5(t.encode()).hexdigest()[:10],
                        title=t, summary=e.get('summary','')[:200],
                        source=name, url=e.get('link','#'),
                        published_at=dt, priority=priority, is_real=True))
            except Exception as e:
                logger.debug(f"RSS {name}: {e}")
    except ImportError:
        pass
    if not items:
        now = datetime.now()
        for i, (title, src) in enumerate([
            ('EGX30 يُغلق مرتفعاً بدعم من أسهم البنوك', 'محاكاة'),
            ('البنك التجاري الدولي يُعلن نتائج أرباح الربع الثاني', 'محاكاة'),
            ('السوق المصري يستقطب استثمارات أجنبية جديدة', 'محاكاة'),
        ]):
            items.append(NewsItem(id=str(i), title=title, summary=title, source=src,
                                  url='#', published_at=now - timedelta(hours=i*2),
                                  priority='medium', is_real=False))
    return sorted(items, key=lambda x: x.published_at, reverse=True)[:max_items]


# ══════════════════════════════════════════════════════════════
# SECTION 11 — DATA STORAGE (SQLite)
# ══════════════════════════════════════════════════════════════
DB_PATH = os.environ.get('EGX_DB_PATH', 'egx_terminal.db')

class DataStorage:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        try: yield conn; conn.commit()
        except Exception as e: conn.rollback(); raise
        finally: conn.close()

    def _init_db(self):
        with self._conn() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS historical_prices (
                    id INTEGER PRIMARY KEY, symbol TEXT, date TEXT,
                    open REAL, high REAL, low REAL, close REAL NOT NULL,
                    volume INTEGER, source TEXT DEFAULT 'simulated', created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol,date));
                CREATE INDEX IF NOT EXISTS idx_p_sym ON historical_prices(symbol);
                CREATE INDEX IF NOT EXISTS idx_p_dt  ON historical_prices(date);
                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY, user_id TEXT DEFAULT 'default',
                    symbol TEXT, alert_type TEXT, threshold REAL, note TEXT,
                    severity TEXT DEFAULT 'MEDIUM', is_active INTEGER DEFAULT 1,
                    triggered INTEGER DEFAULT 0, created_at TEXT, triggered_at TEXT);
                CREATE INDEX IF NOT EXISTS idx_a_sym ON alerts(symbol);
                CREATE TABLE IF NOT EXISTS watchlists (
                    id INTEGER PRIMARY KEY, user_id TEXT DEFAULT 'default',
                    name TEXT, symbols TEXT, updated_at TEXT, UNIQUE(user_id,name));
                CREATE TABLE IF NOT EXISTS backtest_results (
                    id INTEGER PRIMARY KEY, symbol TEXT, strategy TEXT, capital REAL,
                    total_return REAL, sharpe REAL, max_drawdown REAL, win_rate REAL,
                    total_trades INTEGER, run_at TEXT DEFAULT CURRENT_TIMESTAMP);
                CREATE INDEX IF NOT EXISTS idx_bt_sym ON backtest_results(symbol);
                CREATE TABLE IF NOT EXISTS ml_predictions (
                    id INTEGER PRIMARY KEY, symbol TEXT, model_type TEXT,
                    prediction TEXT, confidence REAL, predicted_at TEXT DEFAULT CURRENT_TIMESTAMP);
                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY, user_id TEXT DEFAULT 'default',
                    value TEXT, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
            """)

    def save_alert(self, alert: Dict) -> bool:
        try:
            with self._conn() as conn:
                conn.execute("""INSERT OR REPLACE INTO alerts
                    (id,user_id,symbol,alert_type,threshold,note,severity,is_active,triggered,created_at)
                    VALUES(?,?,?,?,?,?,?,?,?,?)""", (
                    alert.get('id', f"al_{int(datetime.now().timestamp())}"),
                    alert.get('user_id','default'),
                    alert.get('sym', alert.get('symbol','')),
                    alert.get('type', alert.get('alert_type','')),
                    float(alert.get('threshold') or 0),
                    alert.get('note',''), alert.get('severity','MEDIUM'),
                    1 if alert.get('active',True) else 0,
                    1 if alert.get('triggered',False) else 0,
                    alert.get('created', datetime.now().isoformat())))
            return True
        except Exception as e: logger.error(f"save_alert: {e}"); return False

    def get_alerts(self, user_id='default', active_only=True) -> List[Dict]:
        try:
            with self._conn() as conn:
                q = "SELECT * FROM alerts WHERE user_id=?"
                params = [user_id]
                if active_only: q += " AND is_active=1"
                rows = conn.execute(q + " ORDER BY created_at DESC", params).fetchall()
            return [{**dict(r), 'sym': r['symbol']} for r in rows]
        except Exception as e: logger.error(f"get_alerts: {e}"); return []

    def delete_alert(self, alert_id: str) -> bool:
        try:
            with self._conn() as conn:
                conn.execute("DELETE FROM alerts WHERE id=?", (alert_id,))
            return True
        except Exception: return False

    def save_backtest(self, symbol, result, capital=100_000) -> bool:
        try:
            with self._conn() as conn:
                conn.execute("""INSERT INTO backtest_results
                    (symbol,strategy,capital,total_return,sharpe,max_drawdown,win_rate,total_trades)
                    VALUES(?,?,?,?,?,?,?,?)""",
                    (symbol, result.strategy, capital, result.total_return,
                     result.sharpe, result.max_drawdown, result.win_rate, result.total_trades))
            return True
        except Exception as e: logger.error(f"save_backtest: {e}"); return False

    def get_best_backtest(self, symbol) -> Optional[Dict]:
        try:
            with self._conn() as conn:
                row = conn.execute("""SELECT * FROM backtest_results WHERE symbol=?
                    ORDER BY sharpe DESC LIMIT 1""", (symbol,)).fetchone()
            return dict(row) if row else None
        except Exception: return None

    def save_pref(self, key, value, user_id='default'):
        try:
            with self._conn() as conn:
                conn.execute("""INSERT OR REPLACE INTO preferences(key,user_id,value,updated_at)
                    VALUES(?,?,?,?)""", (key, user_id, json.dumps(value), datetime.now().isoformat()))
        except Exception as e: logger.error(f"save_pref: {e}")

    def get_pref(self, key, default=None, user_id='default'):
        try:
            with self._conn() as conn:
                row = conn.execute("SELECT value FROM preferences WHERE key=? AND user_id=?",
                                   (key, user_id)).fetchone()
            return json.loads(row['value']) if row else default
        except Exception: return default

    def get_stats(self) -> Dict:
        stats = {}
        with self._conn() as conn:
            for t in ['historical_prices','alerts','watchlists','backtest_results','ml_predictions']:
                try: stats[t] = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                except Exception: stats[t] = 0
        try: stats['db_size_mb'] = round(os.path.getsize(self.db_path)/1024/1024, 2)
        except Exception: stats['db_size_mb'] = 0
        return stats

db = DataStorage()


# ══════════════════════════════════════════════════════════════
# SECTION 12 — STREAMLIT CACHING
# ══════════════════════════════════════════════════════════════
@st.cache_data(ttl=900, show_spinner=False)
def cached_load(symbol: str, days: int = 300):
    return load_and_compute(symbol, days)

@st.cache_data(ttl=1800, show_spinner=False)
def cached_backtest(symbol: str, capital: float, strategies: tuple, days: int = 500):
    """✅ MISS-2: Cache للباكتست — لا إعادة حساب غير ضرورية"""
    df = load_and_compute(symbol, days)
    if df is None: return [], None
    results = run_all_backtests(df, capital, list(strategies))
    return results, df


# ══════════════════════════════════════════════════════════════
# SECTION 13 — SESSION STATE
# ══════════════════════════════════════════════════════════════
def init_session():
    defaults = {
        'page': 'home', 'capital': 100_000.0,
        'watchlist': ['COMI','ETEL','SWDY','FWRY','TMGH'],
        'alerts': [], 'predictor': None, 'predictor_trained': False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    # Load alerts from DB on first run
    if not st.session_state['alerts']:
        st.session_state['alerts'] = db.get_alerts()


# ══════════════════════════════════════════════════════════════
# SECTION 14 — CHARTS
# ══════════════════════════════════════════════════════════════
def plot_main(df: pd.DataFrame, symbol: str, indicators: List[str]) -> go.Figure:
    sub_inds = [x for x in ['RSI','MACD','MFI','Volume'] if x in indicators]
    extra = len(sub_inds)
    rows = 1 + extra
    rh = [0.55] + [0.15] * extra
    specs = [[{"secondary_y": True}]] + [[{}]] * extra
    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, row_heights=rh,
                        specs=specs, vertical_spacing=0.03,
                        subplot_titles=[f"سعر {symbol}"] + sub_inds)
    # Candlesticks
    fig.add_trace(go.Candlestick(x=df.index, open=df['open'], high=df['high'],
                                  low=df['low'], close=df['close'], name='OHLC',
                                  increasing_line_color='#10b981', decreasing_line_color='#ef4444'), row=1, col=1)
    c = df['close']
    if 'EMA' in indicators:
        for p, color in [(20,'#f59e0b'),(50,'#3b82f6'),(200,'#a855f7')]:
            if f'ema_{p}' in df.columns:
                fig.add_trace(go.Scatter(x=df.index, y=df[f'ema_{p}'], name=f'EMA{p}',
                    line=dict(color=color, width=1.5)), row=1, col=1)
    if 'Bollinger' in indicators and 'bb_upper' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['bb_upper'], name='BB Upper',
            line=dict(color='#94a3b8', dash='dot', width=1), showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['bb_lower'], name='BB Lower',
            line=dict(color='#94a3b8', dash='dot', width=1),
            fill='tonexty', fillcolor='rgba(148,163,184,0.06)'), row=1, col=1)
    if 'VWAP' in indicators and 'vwap' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['vwap'], name='VWAP',
            line=dict(color='#ec4899', width=1.5)), row=1, col=1)
    if 'Supertrend' in indicators and 'supertrend' in df.columns:
        bull = df[df['supertrend_dir'] == 1]
        bear = df[df['supertrend_dir'] == -1]
        fig.add_trace(go.Scatter(x=bull.index, y=bull['supertrend'], name='ST ↑',
            mode='markers', marker=dict(size=2, color='#10b981')), row=1, col=1)
        fig.add_trace(go.Scatter(x=bear.index, y=bear['supertrend'], name='ST ↓',
            mode='markers', marker=dict(size=2, color='#ef4444')), row=1, col=1)
    if 'Keltner' in indicators and 'kc_upper' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['kc_upper'], name='KC Upper',
            line=dict(color='#06b6d4', dash='dot', width=1), opacity=0.7), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['kc_lower'], name='KC Lower',
            line=dict(color='#06b6d4', dash='dot', width=1), opacity=0.7,
            fill='tonexty', fillcolor='rgba(6,182,212,0.06)'), row=1, col=1)
    cr = 2
    if 'RSI' in indicators and 'rsi' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['rsi'], name='RSI',
            line=dict(color='#f59e0b', width=1.5)), row=cr, col=1)
        for lvl, clr in [(70,'#ef4444'),(30,'#10b981'),(50,'#64748b')]:
            fig.add_hline(y=lvl, line_dash='dash', line_color=clr, opacity=0.5, row=cr, col=1)
        fig.update_yaxes(range=[0,100], row=cr, col=1); cr += 1
    if 'MACD' in indicators and 'macd' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['macd'], name='MACD',
            line=dict(color='#3b82f6', width=1.5)), row=cr, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['macd_signal'], name='Signal',
            line=dict(color='#ef4444', width=1)), row=cr, col=1)
        fig.add_trace(go.Bar(x=df.index, y=df['macd_hist'], name='Hist',
            marker_color=np.where(df['macd_hist'] > 0, '#10b981', '#ef4444')), row=cr, col=1)
        cr += 1
    if 'MFI' in indicators and 'mfi' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['mfi'], name='MFI',
            line=dict(color='#a78bfa', width=1.5)), row=cr, col=1)
        for lvl, clr in [(80,'#ef4444'),(20,'#10b981'),(50,'#64748b')]:
            fig.add_hline(y=lvl, line_dash='dash', line_color=clr, opacity=0.5, row=cr, col=1)
        fig.update_yaxes(range=[0,100], row=cr, col=1); cr += 1
    if 'Volume' in indicators and 'volume' in df.columns:
        colors = ['#10b981' if float(df['close'].iloc[i]) >= float(df['open'].iloc[i]) else '#ef4444'
                  for i in range(len(df))]
        fig.add_trace(go.Bar(x=df.index, y=df['volume'], name='Volume',
            marker_color=colors), row=cr, col=1)
    fig.update_layout(height=700, template='plotly_dark', paper_bgcolor='#0a0e1a',
                      plot_bgcolor='#0f1117', font=dict(family='Cairo', color='#e2e8f0'),
                      xaxis_rangeslider_visible=False, showlegend=True,
                      legend=dict(bgcolor='rgba(0,0,0,0.3)', bordercolor='#3d4a63', borderwidth=1))
    fig.update_xaxes(showgrid=True, gridcolor='#1e2738', zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor='#1e2738', zeroline=False)
    return fig


# ══════════════════════════════════════════════════════════════
# SECTION 14b — CHART LAYOUT CONSTANTS
# ══════════════════════════════════════════════════════════════
BG = '#0f1117'
CHART_LAYOUT = dict(
    paper_bgcolor='#0a0e1a', plot_bgcolor=BG,
    font=dict(color='#e2e8f0', family='Cairo'),
    xaxis=dict(gridcolor='#1e2738', showgrid=True, zeroline=False),
    yaxis=dict(gridcolor='#1e2738', showgrid=True, zeroline=False),
    margin=dict(l=50, r=20, t=50, b=40), showlegend=True,
    legend=dict(bgcolor='#1a1f2e', bordercolor='#3d4a63', font=dict(size=12)),
)
def clr_sign(v): return "#10b981" if v >= 0 else "#ef4444"


# ══════════════════════════════════════════════════════════════
# SECTION 15 — SIDEBAR
# ══════════════════════════════════════════════════════════════
PAGES = {
    'home':       ("🏠 الرئيسية",         None),
    'analysis':   ("📊 التحليل الفني",    None),
    'supertrend': ("⚡ Supertrend",        None),
    'backtest':   ("🧪 الباكتست",         None),
    'ml':         ("🤖 التنبؤ الذكي",     None),
    'portfolio':  ("💼 المحفظة",          None),
    'watchlist':  ("👁️ قائمة المراقبة",  None),
    'screener':   ("🔍 الفرز",            None),
    'alerts':     ("🔔 التنبيهات",        None),
    'compare':    ("⚖️ مقارنة الأسهم",    None),
    'news':       ("📰 الأخبار",          None),
    'quarterly':  ("📈 البيانات الفصلية", None),
    'sector':     ("🏭 القطاعات",         None),
    'fibonacci':  ("🌀 فيبوناتشي",        None),
    'database':   ("🗄️ قاعدة البيانات",  None),
    'ai_insights':("✨ تحليل AI",         None),
    'about':      ("ℹ️ عن v35",           None),
}

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:18px 0 12px">
            <div style="font-size:42px">📈</div>
            <div style="font-size:18px;font-weight:800;color:#f59e0b">EGX Pro Terminal</div>
            <div style="font-size:11px;color:#475569;letter-spacing:2px">v35 — ENHANCED EDITION</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("---")
        for key, (label, _) in PAGES.items():
            if st.button(label, key=f"nav_{key}",
                         type="primary" if st.session_state.page == key else "secondary",
                         use_container_width=True):
                st.session_state.page = key
                st.rerun()
        st.markdown("---")
        st.markdown(f"""
        <div style="font-size:11px;color:#374151;line-height:2">
            🕐 {get_cairo_time().strftime('%H:%M')} القاهرة<br>
            🏦 {len(EGXDatabase.STOCKS)} شركة مصرية<br>
            🤖 AI: {'✅' if ai_analyzer.is_available() else '❌ (أضف GEMINI_API_KEY)'}<br>
            ⚠️ للأغراض التعليمية فقط
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# SECTION 16 — PAGES
# ══════════════════════════════════════════════════════════════

def page_home():
    st.markdown("""
    <div class="page-header">
        <div class="page-title">🇪🇬 EGX Pro Terminal v35</div>
        <div class="page-sub">منصة التحليل الاحترافي للبورصة المصرية — 200+ شركة · 25+ مؤشر · ML Ensemble · AI بالعربية</div>
    </div>""", unsafe_allow_html=True)

    cols = st.columns(4)
    kpis = [
        ("🏦", f"{len(EGXDatabase.STOCKS)}", "شركة مصرية", "#f59e0b"),
        ("📊", "25+", "مؤشر فني", "#3b82f6"),
        ("🤖", "LSTM+TF+GB", "Ensemble ML", "#10b981"),
        ("⚡", "18.5 bps", "عمولة EGX", "#a855f7"),
    ]
    for col, (icon, val, label, color) in zip(cols, kpis):
        with col:
            st.markdown(f"""<div class="kpi-card">
                <div style="font-size:28px">{icon}</div>
                <div style="font-size:22px;font-weight:800;color:{color}">{val}</div>
                <div style="font-size:12px;color:#64748b">{label}</div></div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🔥 الأسهم الرئيسية")
    symbols = list(EGXDatabase.STOCKS.keys())[:10]
    cols = st.columns(5)
    for i, sym in enumerate(symbols):
        info = EGXDatabase.STOCKS[sym]
        with cols[i % 5]:
            with st.spinner(""):
                df = cached_load(sym, 30)
            if df is not None and len(df) > 2:
                price = safe_last(df['close'])
                chg   = round((price - float(df['close'].iloc[-2])) / float(df['close'].iloc[-2]) * 100, 2)
                src   = df['data_source'].iloc[-1] if 'data_source' in df.columns else 'simulated'
                color = "#10b981" if chg >= 0 else "#ef4444"
                arrow = "▲" if chg >= 0 else "▼"
                st.markdown(f"""<div class="kpi-card">
                    <div style="font-size:12px;font-weight:700;color:#94a3b8">{sym}</div>
                    <div style="font-size:16px;font-weight:800;color:#e2e8f0">{price:.2f}</div>
                    <div style="font-size:12px;color:{color}">{arrow} {abs(chg):.2f}%</div>
                    <div style="margin-top:4px">{get_data_source_badge(src)}</div>
                </div>""", unsafe_allow_html=True)


def page_analysis():
    st.markdown('<div class="page-header"><div class="page-title">📊 التحليل الفني</div><div class="page-sub">25+ مؤشر فني مع رسوم بيانية تفاعلية</div></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        sym = st.selectbox("السهم", sorted(EGXDatabase.STOCKS.keys()), key='analysis_sym')
    with col2:
        days = st.selectbox("الفترة", [60, 120, 180, 300, 500], index=3)
    with col3:
        st.write("")
        load_btn = st.button("📊 تحليل", type="primary", use_container_width=True, key='load_analysis')

    if load_btn or 'analysis_df' not in st.session_state:
        with st.spinner(f"جاري تحميل {sym}..."):
            df = cached_load(sym, days)
        st.session_state['analysis_df'] = df
        st.session_state['analysis_sym_loaded'] = sym

    df = st.session_state.get('analysis_df')
    if df is None: st.error("لا بيانات متاحة"); return

    # Simulation warning
    src = df['data_source'].iloc[-1] if 'data_source' in df.columns else 'simulated'
    if src != 'real':
        st.markdown(get_simulation_warning_html(sym), unsafe_allow_html=True)

    # Metrics
    price = safe_last(df['close']); prev = float(df['close'].iloc[-2]) if len(df) > 1 else price
    chg = round(price - prev, 2); chg_pct = round(chg / prev * 100, 2) if prev else 0
    sig, strength, emoji = get_composite_signal(df)
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("السعر", f"{price:.2f}", f"{chg:+.2f}")
    m2.metric("RSI", f"{safe_last(df['rsi'], 50):.1f}")
    m3.metric("MACD", f"{safe_last(df['macd']):.4f}")
    m4.metric("الإشارة", f"{emoji} {sig}")
    m5.metric("ATR", f"{safe_last(df['atr']):.2f}")

    # Indicators selection
    ind_opts = ['EMA','Bollinger','VWAP','Supertrend','RSI','MACD','MFI','Keltner','Volume']
    show_ind = st.multiselect("المؤشرات", ind_opts, default=['EMA','Supertrend','RSI','MACD','Volume'])

    # Main chart
    fig = plot_main(df, sym, show_ind)
    st.plotly_chart(fig, use_container_width=True)

    # Tabs for additional info
    tab1, tab2, tab3 = st.tabs(["🕯️ أنماط الشموع", "📐 دعم ومقاومة", "📊 مؤشرات متقدمة"])
    with tab1:
        patterns = detect_patterns(df)
        if patterns:
            for p in patterns:
                color = "#10b981" if p['bullish'] else "#ef4444" if p['bullish'] is False else "#f59e0b"
                st.markdown(f"""<div style="background:#1a1f2e;border-right:3px solid {color};
                    border-radius:8px;padding:10px 14px;margin:6px 0">
                    <b style="color:{color}">{p['name_ar']}</b> ({p['name']}) — {p['desc']}
                </div>""", unsafe_allow_html=True)
        else:
            st.info("لا توجد أنماط محددة في آخر 3 شموع")
    with tab2:
        sr = get_support_resistance(df)
        c1, c2 = st.columns(2)
        c1.metric("الدعم الأقرب", f"{sr.get('support',0):.2f}", f"-{sr.get('support_distance_pct',0):.1f}%")
        c2.metric("المقاومة الأقرب", f"{sr.get('resistance',0):.2f}", f"+{sr.get('resistance_distance_pct',0):.1f}%")
    with tab3:
        c1, c2, c3 = st.columns(3)
        c1.metric("ADX", f"{safe_last(df.get('adx', pd.Series([0]))):.1f}")
        c2.metric("MFI", f"{safe_last(df.get('mfi', pd.Series([50]))):.1f}")
        c3.metric("Stoch K", f"{safe_last(df.get('stoch_k', pd.Series([50]))):.1f}")


def page_backtest():
    st.markdown('<div class="page-header"><div class="page-title">🧪 الاختبار التاريخي</div><div class="page-sub">10 استراتيجيات · Walk-Forward · EGX Commission 18.5 bps</div></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1: sym = st.selectbox("السهم", sorted(EGXDatabase.STOCKS.keys()), key='bt_sym')
    with col2: capital = st.number_input("رأس المال (EGP)", 10_000.0, 10_000_000.0, 100_000.0, 10_000.0)
    with col3: strat_sel = st.multiselect("الاستراتيجيات", ALL_STRATEGIES, default=ALL_STRATEGIES[:5])

    if st.button("🚀 تشغيل", type="primary"):
        with st.spinner("جاري الاختبار..."):
            results, df = cached_backtest(sym, capital, tuple(sorted(strat_sel or ALL_STRATEGIES[:5])))
        if not results: st.error("لا بيانات"); return
        summary = backtest_summary_df(results)
        # Save best to DB
        if results:
            best = max(results, key=lambda r: r.sharpe)
            db.save_backtest(sym, best, capital)

        st.success(f"✅ اكتمل | {len(results)} استراتيجية")
        st.dataframe(summary.style.background_gradient(subset=['عائد سنوي %','شارب'], cmap='RdYlGn'),
                     use_container_width=True)
        # Equity curves
        fig = go.Figure()
        for r in results:
            if r.equity_curve:
                fig.add_trace(go.Scatter(y=r.equity_curve, name=r.strategy, mode='lines'))
        fig.update_layout(height=400, template='plotly_dark', paper_bgcolor='#0a0e1a',
                          title='منحنيات رأس المال', font=dict(family='Cairo'))
        st.plotly_chart(fig, use_container_width=True)

        # DCA Tab
        with st.expander("💰 محاكاة DCA"):
            c1, c2 = st.columns(2)
            monthly = c1.number_input("المبلغ الشهري (EGP)", 100.0, 50_000.0, 1_000.0)
            months  = c2.slider("عدد الشهور", 6, 60, 24)
            if df is not None:
                dca = dca_simulation(df, monthly, months)
                if 'error' not in dca:
                    dc1, dc2, dc3 = st.columns(3)
                    dc1.metric("إجمالي الاستثمار", fmt_egp(dca['total_invested']))
                    dc2.metric("القيمة الحالية", fmt_egp(dca['final_value']))
                    dc3.metric("العائد %", f"{dca['total_return_pct']:.1f}%")
                else:
                    st.error(dca['error'])


def page_ml():
    st.markdown('<div class="page-header"><div class="page-title">🤖 التنبؤ الذكي</div><div class="page-sub">Ensemble: GradientBoosting + LSTM + Transformer</div></div>', unsafe_allow_html=True)
    sym = st.selectbox("السهم", sorted(EGXDatabase.STOCKS.keys()), key='ml_sym')

    if 'predictor' not in st.session_state or st.session_state['predictor'] is None:
        st.session_state['predictor'] = EGXMLPredictor(use_torch=TORCH_AVAILABLE)

    pred = st.session_state['predictor']
    if not TORCH_AVAILABLE:
        st.warning("⚠️ PyTorch غير متاح — سيعمل GradientBoosting فقط. `pip install torch`")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎓 تدريب النموذج", type="primary"):
            with st.spinner("جاري التدريب..."):
                df = cached_load(sym, 500)
                metrics = pred.train(df)
            if 'error' not in metrics:
                st.session_state['predictor_trained'] = True
                st.success(f"✅ دقة: {metrics['accuracy']:.1%} | عينات: {metrics['samples']}")
                db.save_pref(f'ml_trained_{sym}', True)
            else:
                st.error(metrics['error'])

    with col2:
        if st.button("🔮 تنبؤ", type="secondary") and st.session_state.get('predictor_trained'):
            with st.spinner("جاري التنبؤ..."):
                df = cached_load(sym, 300)
                label, conf, emoji = pred.predict(df)
                db.save_pref(f'ml_pred_{sym}', {'label':label, 'conf':conf})
            color = "#10b981" if label == "شراء" else "#ef4444" if label == "بيع" else "#f59e0b"
            st.markdown(f"""<div style="background:#1a1f2e;border:2px solid {color};
                border-radius:12px;padding:20px;text-align:center;margin:10px 0">
                <div style="font-size:36px">{emoji}</div>
                <div style="font-size:24px;font-weight:800;color:{color}">{label}</div>
                <div style="font-size:14px;color:#64748b">ثقة: {conf:.1%}</div>
                <div style="font-size:11px;color:#475569;margin-top:8px">
                    Ensemble: GB(25%) + LSTM(40%) + Transformer(35%)</div>
            </div>""", unsafe_allow_html=True)


def page_portfolio():
    st.markdown('<div class="page-header"><div class="page-title">💼 إدارة المحفظة</div><div class="page-sub">Kelly Criterion من الباكتست · وقف الخسارة الديناميكي</div></div>', unsafe_allow_html=True)
    st.session_state['capital'] = st.number_input("رأس المال (EGP)", 10_000.0, 10_000_000.0,
                                                   st.session_state['capital'], 10_000.0)
    max_risk = st.slider("نسبة المخاطرة لكل صفقة %", 0.5, 5.0, 2.0, 0.5) / 100
    sym = st.selectbox("السهم", sorted(EGXDatabase.STOCKS.keys()), key='pm_sym')
    df = cached_load(sym)
    if df is None: st.error("لا بيانات"); return
    price = safe_last(df['close']); atr_v = safe_last(df.get('atr', pd.Series([price*0.02])))
    pm = PortfolioManager(st.session_state['capital'])

    # ✅ MISS-1: Kelly من نتائج الباكتست بدلاً من قيم ثابتة
    kelly_source = "قيم افتراضية"
    wr, aw, al = 0.55, 0.04, 0.02
    stored = db.get_best_backtest(sym)
    if stored:
        wr = stored.get('win_rate', 0.55)
        kelly_source = f"باكتست {stored.get('strategy','')}"
    else:
        try:
            bt_results, _ = cached_backtest(sym, st.session_state['capital'],
                                             tuple(['Multi-Signal','Supertrend']), days=300)
            if bt_results:
                best = max(bt_results, key=lambda r: r.win_rate if r.total_trades > 3 else 0)
                if best.total_trades > 3:
                    wr, aw, al = best.win_rate, best.avg_win/100, best.avg_loss/100
                    kelly_source = f"باكتست {best.strategy}"
        except Exception: pass

    pos = pm.calc_position_size(price, wr, max(aw, 0.001), max(al, 0.001), max_risk)
    sl  = pm.calc_stop_loss(price, atr_v)

    st.caption(f"📊 مصدر Kelly: {kelly_source} | Win Rate: {wr*100:.1f}%")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("الأسهم الموصى بها", f"{pos['shares']:,}")
    c2.metric("قيمة الصفقة", fmt_egp(pos['value']))
    c3.metric("وقف الخسارة", f"{sl['stop_loss']:.2f}")
    c4.metric("هدف الربح", f"{sl['take_profit']:.2f}")
    st.metric("نسبة الصفقة من رأس المال", f"{pos['position_pct']:.2f}%")


def page_watchlist():
    st.markdown('<div class="page-header"><div class="page-title">👁️ قائمة المراقبة</div></div>', unsafe_allow_html=True)
    wl = st.session_state.get('watchlist', ['COMI','ETEL'])
    new_sym = st.selectbox("إضافة سهم", [s for s in EGXDatabase.STOCKS if s not in wl])
    if st.button("➕ إضافة") and new_sym not in wl:
        wl.append(new_sym); st.session_state['watchlist'] = wl; st.rerun()

    for sym in wl[:8]:
        df = cached_load(sym, 30)
        if df is not None and len(df) > 1:
            price = safe_last(df['close'])
            chg = round((price - float(df['close'].iloc[-2])) / float(df['close'].iloc[-2]) * 100, 2)
            sig, _, emoji = get_composite_signal(df)
            col1, col2, col3, col4 = st.columns([2,1,1,1])
            col1.write(f"**{sym}** — {EGXDatabase.STOCKS[sym].get('name_ar','')}")
            col2.metric("السعر", f"{price:.2f}", f"{chg:+.2f}%")
            col3.write(f"{emoji} {sig}")
            if col4.button("🗑️", key=f"rm_{sym}"):
                wl.remove(sym); st.session_state['watchlist'] = wl; st.rerun()


def page_screener():
    st.markdown('<div class="page-header"><div class="page-title">🔍 فرز الأسهم</div></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    sector_filter = c1.selectbox("القطاع", ["الكل"] + sorted(EGXDatabase.SECTOR_MAP.keys()))
    signal_filter = c2.selectbox("الإشارة", ["الكل","شراء قوي","شراء","محايد","بيع","بيع قوي"])

    symbols = EGXDatabase.STOCKS.keys()
    if sector_filter != "الكل":
        symbols = [s for s in symbols if EGXDatabase.STOCKS[s].get('sector') == sector_filter]

    results = []
    prog = st.progress(0)
    syms_list = list(symbols)
    for i, sym in enumerate(syms_list[:20]):
        prog.progress((i+1)/min(20, len(syms_list)))
        df = cached_load(sym, 60)
        if df is not None and len(df) > 5:
            price = safe_last(df['close'])
            rsi   = safe_last(df.get('rsi', pd.Series([50])))
            sig, strength, emoji = get_composite_signal(df)
            if signal_filter == "الكل" or sig == signal_filter:
                results.append({'السهم':sym, 'السعر':round(price,2), 'RSI':round(rsi,1),
                                 'الإشارة':f"{emoji} {sig}", 'القوة':round(strength,2)})
    prog.empty()
    if results:
        st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد أسهم مطابقة")


def page_alerts():
    st.markdown('<div class="page-header"><div class="page-title">🔔 التنبيهات</div></div>', unsafe_allow_html=True)
    with st.form("add_alert"):
        c1,c2,c3,c4 = st.columns(4)
        sym  = c1.selectbox("السهم", sorted(EGXDatabase.STOCKS.keys()))
        atype= c2.selectbox("النوع", ["سعر فوق","سعر تحت","RSI فوق 70","RSI تحت 30","MACD تقاطع"])
        thr  = c3.number_input("الحد", 0.0, 10000.0, 0.0)
        note = c4.text_input("ملاحظة", "")
        if st.form_submit_button("➕ إضافة التنبيه", type="primary"):
            alert = {'id': f"al_{int(datetime.now().timestamp())}", 'sym':sym,
                     'type':atype, 'threshold':thr, 'note':note, 'active':True, 'triggered':False,
                     'created': datetime.now().isoformat()}
            st.session_state['alerts'].append(alert)
            db.save_alert(alert)
            st.success("✅ تم إضافة التنبيه")
            st.rerun()

    alerts = st.session_state.get('alerts', [])
    if not alerts:
        alerts = db.get_alerts()
        st.session_state['alerts'] = alerts

    for al in alerts:
        df = cached_load(al.get('sym',''), 5)
        ap  = safe_last(df['close']) if df is not None else 0
        thr = al.get('threshold', 0)
        atype = al.get('type', al.get('alert_type',''))
        trig = (('فوق' in atype and ap > float(thr)) or
                ('تحت' in atype and ap < float(thr)) or
                ('RSI فوق' in atype and safe_last(df.get('rsi', pd.Series([50])) if df is not None else pd.Series([50])) > 70) or
                ('RSI تحت' in atype and safe_last(df.get('rsi', pd.Series([50])) if df is not None else pd.Series([50])) < 30))
        icon = '🔔' if trig else '🔕'
        stat = '✅ محقق!' if trig else '⏳ منتظر'
        bg   = 'background:#052e16;border:1px solid #10b981;color:#6ee7b7' if trig else 'background:#1a1f2e;border:1px solid #3d4a63;color:#94a3b8'
        # ✅ MISS-3: تنسيق آمن للـ threshold
        try: thresh_str = f"{float(thr):g}"
        except (TypeError, ValueError): thresh_str = str(thr)
        st.markdown(f"""<div style="border-radius:10px;padding:14px 18px;margin:6px 0;{bg}">
            {icon} <b>{al.get('sym','')}</b> — {atype} {thresh_str}
            | الحالي: <b>{ap:.2f}</b> | <b>{stat}</b>
            {f"| {al['note']}" if al.get('note') else ''}
        </div>""", unsafe_allow_html=True)



def page_supertrend():
    st.markdown('<div class="page-header"><div class="page-title">⚡ محلل Supertrend</div><div class="page-sub">أقوى مؤشر اتجاه في السوق المصري</div></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: sym = st.selectbox("السهم", sorted(EGXDatabase.STOCKS.keys()), key='st_sym')
    with c2: period = st.slider("الفترة (ATR)", 5, 25, 10)
    with c3: mult = st.slider("المضاعف", 1.0, 5.0, 3.0, 0.5)

    df = cached_load(sym, 300)
    if df is None: st.error("لا بيانات"); return

    src = df['data_source'].iloc[-1] if 'data_source' in df.columns else 'simulated'
    if src != 'real':
        st.markdown(get_simulation_warning_html(sym), unsafe_allow_html=True)

    df = df.copy()
    df['atr'] = calc_atr(df['high'], df['low'], df['close'], period)
    st_vals, st_dir = calc_supertrend(df, period, mult)
    df['st_c'] = st_vals; df['st_d'] = st_dir

    cur_price = float(df['close'].iloc[-1])
    cur_st    = float(df['st_c'].iloc[-1])
    cur_dir   = int(df['st_d'].iloc[-1])
    pct_st    = (cur_price - cur_st) / cur_st * 100 if cur_st != 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("السعر الحالي", f"{cur_price:.2f}")
    c2.metric("مستوى Supertrend", f"{cur_st:.2f}")
    c3.metric("الإشارة الحالية", "🟢 شراء" if cur_dir == 1 else "🔴 بيع")
    c4.metric("% من ST", f"{pct_st:+.2f}%")

    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['open'], high=df['high'],
        low=df['low'], close=df['close'], name='السعر',
        increasing_line_color='#10b981', decreasing_line_color='#ef4444'))
    up = df['st_c'].where(df['st_d'] == 1)
    dn = df['st_c'].where(df['st_d'] == -1)
    fig.add_trace(go.Scatter(x=df.index, y=up, name='ST صاعد 🟢', line=dict(color='#10b981', width=2.5)))
    fig.add_trace(go.Scatter(x=df.index, y=dn, name='ST هابط 🔴', line=dict(color='#ef4444', width=2.5)))
    crossup   = (df['st_d'] == 1)  & (df['st_d'].shift(1) == -1)
    crossdown = (df['st_d'] == -1) & (df['st_d'].shift(1) ==  1)
    if crossup.any():
        fig.add_trace(go.Scatter(x=df.index[crossup], y=df['close'][crossup],
            mode='markers+text', name=f"شراء ({crossup.sum()})",
            text=['▲'] * int(crossup.sum()), textposition='bottom center',
            marker=dict(size=14, color='#10b981', symbol='triangle-up')))
    if crossdown.any():
        fig.add_trace(go.Scatter(x=df.index[crossdown], y=df['close'][crossdown],
            mode='markers+text', name=f"بيع ({crossdown.sum()})",
            text=['▼'] * int(crossdown.sum()), textposition='top center',
            marker=dict(size=14, color='#ef4444', symbol='triangle-down')))
    fig.update_layout(**CHART_LAYOUT, height=560, xaxis_rangeslider_visible=False,
        title=f"Supertrend — {sym}  (Period={period}, Mult={mult})")
    st.plotly_chart(fig, use_container_width=True)
    st.info(f"📊 إشارات الفترة: 🟢 {int(crossup.sum())} شراء | 🔴 {int(crossdown.sum())} بيع")

    with st.expander("📐 إحصائيات Supertrend"):
        st.markdown(f"""| المقياس | القيمة |\n|---|---|\n| أيام صاعدة | {int((df['st_d']==1).sum())} |\n| أيام هابطة | {int((df['st_d']==-1).sum())} |\n| مستوى ST | {cur_st:.2f} |\n| بُعد السعر | {pct_st:+.2f}% |\n| ATR الحالي | {safe_last(df['atr']):.3f} |""")


def page_compare():
    st.markdown('<div class="page-header"><div class="page-title">⚖️ مقارنة الأسهم</div><div class="page-sub">قارن أداء حتى 5 أسهم معاً</div></div>', unsafe_allow_html=True)
    selected = st.multiselect("اختر حتى 5 أسهم", sorted(EGXDatabase.STOCKS.keys()),
                               default=['COMI','TMGH','ETEL'])[:5]
    if len(selected) < 2: st.warning("اختر سهمين على الأقل"); return

    c1, c2 = st.columns(2)
    period_label = c1.radio("الفترة", ['60 يوم','90 يوم','120 يوم','300 يوم'], horizontal=True)
    normalize    = c2.checkbox("تطبيع الأداء (100 = البداية)", value=True)
    days = {'60 يوم':60, '90 يوم':90, '120 يوم':120, '300 يوم':300}[period_label]

    COLORS = ['#3b82f6','#10b981','#f59e0b','#ef4444','#a855f7']
    fig = go.Figure(); rows = []
    for sym, cl in zip(selected, COLORS):
        df = cached_load(sym, days)
        if df is None or df.empty: continue
        ps  = df['close'] / df['close'].iloc[0] * 100 if normalize else df['close']
        ret = (df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100
        sig, strength, emoji = get_composite_signal(df)
        src = df['data_source'].iloc[-1] if 'data_source' in df.columns else 'simulated'
        fig.add_trace(go.Scatter(x=df.index, y=ps, name=f"{sym} ({ret:+.1f}%)",
            line=dict(color=cl, width=2.5)))
        rows.append({'السهم':sym, 'الشركة':EGXDatabase.STOCKS.get(sym,{}).get('name_ar','')[:18],
                     'العائد %':f"{ret:+.1f}%", 'RSI':f"{safe_last(df.get('rsi', pd.Series([50]))):.0f}",
                     'الإشارة':f"{emoji} {sig}", 'البيانات':'🟢' if src=='real' else '🔴 محاكاة'})

    if normalize:
        fig.add_hline(y=100, line_color='#64748b', line_dash='dash', opacity=0.5,
                      annotation_text="نقطة البداية")
    fig.update_layout(**CHART_LAYOUT, height=500,
        yaxis_title="الأداء % (100=البداية)" if normalize else "السعر (EGP)")
    st.plotly_chart(fig, use_container_width=True)
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    if len(selected) >= 3:
        with st.expander("📊 مصفوفة الارتباط"):
            price_data = {}
            for sym in selected:
                df = cached_load(sym, days)
                if df is not None: price_data[sym] = df['close'].values
            if len(price_data) >= 2:
                min_len = min(len(v) for v in price_data.values())
                corr_df = pd.DataFrame({k: v[-min_len:] for k, v in price_data.items()}).corr()
                fig2 = px.imshow(corr_df, text_auto='.2f', color_continuous_scale='RdBu',
                                 title='معامل الارتباط بين الأسهم')
                fig2.update_layout(template='plotly_dark', paper_bgcolor='#0a0e1a', font=dict(family='Cairo'))
                st.plotly_chart(fig2, use_container_width=True)


def page_news():
    st.markdown('<div class="page-header"><div class="page-title">📰 الأخبار والتوزيعات</div></div>', unsafe_allow_html=True)
    with st.spinner("جاري تحميل الأخبار..."):
        news = fetch_news(15)
    for item in news:
        priority_color = "#ef4444" if item.priority == 'high' else "#f59e0b" if item.priority == 'medium' else "#64748b"
        real_label = '<span style="background:#064e3b;color:#6ee7b7;border-radius:4px;padding:1px 6px;font-size:10px">حقيقي</span>' if item.is_real else '<span style="background:#78350f;color:#fcd34d;border-radius:4px;padding:1px 6px;font-size:10px">محاكاة</span>'
        st.markdown(f"""<div style="background:#1a1f2e;border-right:3px solid {priority_color};
            border-radius:8px;padding:12px 16px;margin:8px 0">
            <div style="font-size:13px;font-weight:600;color:#e2e8f0">{item.title}</div>
            <div style="font-size:11px;color:#64748b;margin-top:4px">
                {item.source} · {item.published_at.strftime('%H:%M %d/%m')} · {real_label}</div>
            {f'<div style="font-size:12px;color:#94a3b8;margin-top:6px">{item.summary[:150]}...</div>' if item.summary else ''}
        </div>""", unsafe_allow_html=True)


def page_quarterly():
    st.markdown('<div class="page-header"><div class="page-title">📈 البيانات الفصلية</div></div>', unsafe_allow_html=True)
    sym = st.selectbox("السهم", sorted(EGXDatabase.STOCKS.keys()), key='quarterly_sym')
    with st.spinner("جاري جلب البيانات الفصلية..."):
        qdf = fetch_quarterly_financials(sym)
    if qdf is None or qdf.empty: st.error("لا بيانات"); return

    is_real = 'source' in qdf.columns and (qdf['source'] == 'real').any()
    if not is_real:
        st.info("ℹ️ هذه تقديرات بناءً على بيانات القطاع — ليست أرقاماً رسمية")

    tab1, tab2 = st.tabs(["📊 جدول", "📉 رسوم بيانية"])
    with tab1:
        display_df = qdf[['quarter','revenue','net_income','eps','margin']].copy()
        display_df.columns = ['الربع','الإيرادات','صافي الربح','EPS','الهامش %']
        for col in ['الإيرادات','صافي الربح']:
            display_df[col] = display_df[col].apply(lambda x: fmt_num(x))
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    with tab2:
        fig = make_subplots(rows=1, cols=2, subplot_titles=['الإيرادات وصافي الربح','EPS'])
        fig.add_trace(go.Bar(x=qdf['quarter'], y=qdf['revenue']/1e9, name='الإيرادات (مليار)'), row=1, col=1)
        fig.add_trace(go.Bar(x=qdf['quarter'], y=qdf['net_income']/1e9, name='صافي الربح (مليار)'), row=1, col=1)
        fig.add_trace(go.Scatter(x=qdf['quarter'], y=qdf['eps'], name='EPS', mode='lines+markers'), row=1, col=2)
        fig.update_layout(height=350, template='plotly_dark', paper_bgcolor='#0a0e1a', font=dict(family='Cairo'))
        st.plotly_chart(fig, use_container_width=True)


def page_sector():
    st.markdown('<div class="page-header"><div class="page-title">🏭 تحليل القطاعات</div></div>', unsafe_allow_html=True)
    sector_data = []
    for sector, symbols in EGXDatabase.SECTOR_MAP.items():
        cap = sum(EGXDatabase.STOCKS[s].get('market_cap', 0) for s in symbols)
        sector_data.append({'القطاع': sector, 'الشركات': len(symbols), 'القيمة السوقية': cap})
    df_sec = pd.DataFrame(sector_data).sort_values('القيمة السوقية', ascending=False)
    fig = px.treemap(df_sec, path=['القطاع'], values='القيمة السوقية',
                     title='توزيع القيمة السوقية حسب القطاع', color='الشركات',
                     color_continuous_scale='Blues')
    fig.update_layout(template='plotly_dark', paper_bgcolor='#0a0e1a', font=dict(family='Cairo'))
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df_sec.style.format({'القيمة السوقية': lambda x: fmt_egp(x)}),
                 use_container_width=True, hide_index=True)


def page_fibonacci():
    st.markdown('<div class="page-header"><div class="page-title">🌀 مستويات فيبوناتشي</div></div>', unsafe_allow_html=True)
    sym = st.selectbox("السهم", sorted(EGXDatabase.STOCKS.keys()), key='fib_sym')
    df  = cached_load(sym)
    if df is None: st.error("لا بيانات"); return
    price = safe_last(df['close'])
    fib   = get_fibonacci_levels(df)
    sr    = get_support_resistance(df)
    sup, res = sr.get('support', 0), sr.get('resistance', price)
    pos_pct = ((price - sup) / (res - sup) * 100) if res > sup else 50

    st.metric("السعر الحالي", f"{price:.2f}")
    st.progress(min(max(pos_pct / 100, 0), 1))
    st.caption(f"الموقع في النطاق: {pos_pct:.1f}%")

    for level, value in sorted(fib.items(), key=lambda x: float(x[0])):
        pct_diff = (value - price) / price * 100
        color = "#10b981" if value > price else "#ef4444"
        st.markdown(f"""<div style="background:#1a1f2e;border-right:3px solid {color};
            border-radius:6px;padding:8px 14px;margin:4px 0;display:flex;justify-content:space-between">
            <span style="color:#94a3b8">Fib {float(level):.3f}</span>
            <span style="font-weight:700;color:{color}">{value:.2f}</span>
            <span style="color:{color}">{pct_diff:+.2f}%</span>
        </div>""", unsafe_allow_html=True)


def page_ai_insights():
    st.markdown('<div class="page-header"><div class="page-title">✨ تحليل AI بالعربية</div></div>', unsafe_allow_html=True)
    if not ai_analyzer.is_available():
        st.warning("⚠️ أضف GEMINI_API_KEY إلى `.streamlit/secrets.toml` أو متغيرات البيئة")
        with st.expander("كيفية الإعداد"):
            st.code("""# .streamlit/secrets.toml\nGEMINI_API_KEY = "AIza...""")
        return
    sym = st.selectbox("السهم", sorted(EGXDatabase.STOCKS.keys()), key='ai_sym')
    df  = cached_load(sym)
    if df is None: st.error("لا بيانات"); return
    price = safe_last(df['close']); rsi = safe_last(df.get('rsi', pd.Series([50])))
    sig, _, emoji = get_composite_signal(df)
    sector = EGXDatabase.STOCKS.get(sym, {}).get('sector', 'Banking')
    if st.button("🔍 تحليل AI", type="primary"):
        with st.spinner("Gemini AI يحلل..."):
            analysis = ai_analyzer.analyze_stock(sym, sig, rsi, price, sector)
        st.markdown(f"""<div style="background:#1a1f2e;border:1px solid #3b82f6;
            border-radius:12px;padding:18px;line-height:2">{analysis}</div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📚 شرح المؤشرات")
    ind = st.selectbox("اختر مؤشراً", ['RSI','MACD','Bollinger Bands','Supertrend','VWAP','MFI','Keltner'])
    if st.button("💡 اشرح"):
        with st.spinner("جاري الشرح..."):
            explanation = ai_analyzer.explain_indicator(ind)
        st.markdown(explanation)


def page_database():
    st.markdown('<div class="page-header"><div class="page-title">🗄️ قاعدة البيانات</div></div>', unsafe_allow_html=True)
    stats = db.get_stats()
    c1,c2,c3 = st.columns(3)
    c1.metric("الأسعار المخزّنة", f"{stats.get('historical_prices',0):,}")
    c2.metric("التنبيهات النشطة", f"{stats.get('alerts',0):,}")
    c3.metric("حجم DB", f"{stats.get('db_size_mb',0):.2f} MB")
    c4,c5 = st.columns(2)
    c4.metric("نتائج الباكتست", f"{stats.get('backtest_results',0):,}")
    c5.metric("تنبؤات ML", f"{stats.get('ml_predictions',0):,}")
    st.markdown("**📋 جداول DB:** `historical_prices` · `alerts` · `watchlists` · `backtest_results` · `ml_predictions` · `preferences`")


def page_about():
    st.markdown('<div class="page-header"><div class="page-title">ℹ️ عن EGX Pro Terminal v35</div></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#1a1f2e;border-radius:14px;padding:28px;line-height:2;border:1px solid #3d4a63">
    <h3 style="color:#f59e0b;margin-top:0">🚀 ما الجديد في v35</h3>
    <ul style="color:#e2e8f0">
        <li>🔴 <b>إصلاح خصم عمولة مزدوج</b> — entry_cost = sh*cp فقط (الباكتست أصبح دقيقاً)</li>
        <li>🔴 <b>إصلاح PnL</b> — يطرح التكاليف الكاملة لكلا الاتجاهين</li>
        <li>🔴 <b>Gemini AI</b> — gemini-1.5-flash بدلاً من 2.0-flash (كان 404)</li>
        <li>🔴 <b>Ultimate Oscillator</b> — إصلاح crash من list.shift() الخاطئ</li>
        <li>🟠 <b>MFI + Keltner Channels</b> — مُضافان ومعروضان في المخططات</li>
        <li>🟠 <b>LSTM + Transformer Ensemble</b> — PyTorch مع Walk-Forward</li>
        <li>🟠 <b>قاعدة بيانات SQLite</b> — 6 جداول للتخزين الدائم</li>
        <li>🟠 <b>البيانات الفصلية</b> — yfinance أو تقدير تلقائي حسب القطاع</li>
        <li>🟡 <b>Kelly من الباكتست</b> — بدلاً من قيم ثابتة</li>
        <li>🟡 <b>تحذير المحاكاة</b> — CSS animation + شارة واضحة</li>
        <li>🟡 <b>cached_backtest</b> — لا إعادة حساب غير ضرورية</li>
        <li>🟡 <b>أخبار RSS</b> — مباشر + أموال الغد + fallback محاكاة</li>
    </ul>
    <hr style="border-color:#3d4a63">
    <p style="color:#64748b;font-size:13px">
        ⚠️ للأغراض التعليمية والبحثية فقط — ليست توصية استثمارية<br>
        🔗 <a href="https://github.com/m02417710-maker/blank-app" style="color:#3b82f6">GitHub Repository</a>
    </p>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# SECTION 17 — MAIN ROUTER
# ══════════════════════════════════════════════════════════════
PAGE_FUNCS = {
    'home':        page_home,
    'analysis':    page_analysis,
    'supertrend':  page_supertrend,
    'backtest':    page_backtest,
    'ml':          page_ml,
    'portfolio':   page_portfolio,
    'watchlist':   page_watchlist,
    'screener':    page_screener,
    'alerts':      page_alerts,
    'compare':     page_compare,
    'news':        page_news,
    'quarterly':   page_quarterly,
    'sector':      page_sector,
    'fibonacci':   page_fibonacci,
    'ai_insights': page_ai_insights,
    'database':    page_database,
    'about':       page_about,
}

def main():
    init_session()
    render_sidebar()
    page_func = PAGE_FUNCS.get(st.session_state.get('page', 'home'), page_home)
    page_func()

if __name__ == "__main__":
    main()
