# 📋 تصريحات المشروع — EGX Pro Terminal v35

## 1. معلومات المشروع

| البند | القيمة |
|---|---|
| **الاسم** | EGX Pro Terminal |
| **الإصدار** | 35.0.0 |
| **الوصف** | منصة التحليل الاحترافي للبورصة المصرية |
| **الترخيص** | MIT License |
| **الفريق** | EGX Pro Team |
| **اللغة الأساسية** | Python 3.11+ |
| **Framework** | Streamlit ≥ 1.32 |
| **تاريخ الإصدار** | يونيو 2026 |

---

## 2. تصريحات الاستيراد (Import Declarations)

### المكتبات الأساسية المُصرَّح بها

```python
# Core
import streamlit as st          # ≥ 1.32.0
import pandas as pd             # ≥ 2.0.0
import numpy as np              # ≥ 1.24.0
import plotly.graph_objects as go # ≥ 5.18.0

# Finance
import yfinance as yf           # ≥ 0.2.36

# ML / Statistics
from sklearn.ensemble import GradientBoostingClassifier  # ≥ 1.4.0
from sklearn.model_selection import TimeSeriesSplit
import scipy                    # ≥ 1.10.0

# AI
import google.generativeai as genai  # ≥ 0.8.0
# Model: gemini-1.5-flash (✅ fixed from gemini-2.0-flash which returned 404)

# Optional — PyTorch (LSTM + Transformer Ensemble)
import torch                    # ≥ 2.0.0 (optional)
import torch.nn as nn

# Optional — RSS News
import feedparser               # ≥ 6.0.0

# Standard library (no install needed)
import sqlite3, json, os, sys, logging, hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple, Any
from contextlib import contextmanager
from zoneinfo import ZoneInfo
```

---

## 3. تصريحات المتغيرات العالمية (Global Variable Declarations)

```python
# EGX Commission Constants (18.5 bps — الرسمي)
EGX_COMMISSION: float = 0.00150   # عمولة الوسيط
EGX_STAMP:      float = 0.00025   # رسوم الدمغة
EGX_CUSTODY:    float = 0.00010   # رسوم الحفظ
EGX_TOTAL_COST: float = 0.00185   # الإجمالي (18.5 bps)
EGX_SLIPPAGE:   float = 0.00100   # الانزلاق السعري
MIN_TRADE_EGP:  int   = 500       # الحد الأدنى للصفقة (جنيه)

# Streamlit chart theme
BG: str = '#0f1117'

# PyTorch availability flag
TORCH_AVAILABLE: bool = False  # يُضبط تلقائياً عند import torch

# Feature columns for ML
FEATURE_COLS: List[str] = [
    'rsi', 'macd', 'macd_hist', 'bb_pct_b', 'adx',
    'stoch_k', 'cci', 'williams_r', 'vol_ratio', 'roc',
    'z_score', 'mfi'
]

# All backtest strategies
ALL_STRATEGIES: List[str] = [
    'EMA Cross', 'RSI Mean Reversion', 'MACD', 'Bollinger Bands',
    'Supertrend', 'VWAP+RSI', 'PSAR', 'Ichimoku', 'ADX Trend', 'Multi-Signal'
]
```

---

## 4. تصريحات الفئات (Class Declarations)

### Backend / Engine

```python
class EGXDatabase:
    """قاعدة بيانات 200+ شركة مصرية مع بناء المؤشرات تلقائياً."""
    STOCKS: Dict[str, Dict]  # symbol → {name, sector, yf, base, market_cap, ...}
    EGX30:  List[str]        # أكبر 30 شركة
    EGX70:  List[str]        # الشركات من 31 → 100
    EGX100: List[str]        # باقي الشركات
    SECTOR_MAP: Dict[str, List[str]]  # sector → [symbols]

class AppConfig:
    """إعدادات التطبيق — singleton عبر config = AppConfig()."""
    APP_NAME:    str   = "EGX Pro Terminal"
    APP_VERSION: str   = "35.0.0"
    AI_PREDICTION_HORIZON: int   = 5       # ✅ مُضافة (كانت مفقودة)
    COMMISSION:  float = 0.00185           # ✅ مُصحَّحة (كانت 0.002)
    MONTE_CARLO_SIMULATIONS: int = 1000
    RSI_PERIOD:  int   = 14
    MACD_FAST:   int   = 12
    MACD_SLOW:   int   = 26
    MACD_SIGNAL: int   = 9

class Trade:
    """تمثّل صفقة واحدة في الباكتست."""
    entry_date:  Any
    exit_date:   Any
    entry_price: float
    exit_price:  float
    shares:      int
    entry_cost:  float   # ✅ كان يُحسب مرتين (مُصحَّح)
    pnl:         float
    pnl_pct:     float
    trade_cost:  float   # للعرض فقط
    strategy:    str

class BacktestResult:
    """نتيجة استراتيجية باكتست واحدة."""
    strategy:           str
    initial_capital:    float
    final_capital:      float
    total_return:       float
    annualized_return:  float
    sharpe:             float
    max_drawdown:       float
    win_rate:           float
    total_trades:       int
    profit_factor:      float
    calmar:             float
    avg_win:            float
    avg_loss:           float
    equity_curve:       List[float]
    trades:             List[Trade]

class EGXMLPredictor:
    """Ensemble: GradientBoosting(25%) + LSTM(40%) + Transformer(35%)."""
    gb:        GradientBoostingClassifier
    scaler:    StandardScaler
    lstm:      LSTMModel       # إذا TORCH_AVAILABLE
    tf_model:  TransformerModel  # إذا TORCH_AVAILABLE
    trained:   bool
    SEQ_LEN:   int = 20

class PortfolioManager:
    """إدارة المحفظة: Kelly Criterion + وقف الخسارة الديناميكي."""
    capital: float

class AIAnalyzer:
    """واجهة Gemini AI — تعمل بدون مفتاح (graceful fallback)."""
    model:   GenerativeModel  # gemini-1.5-flash ✅
    _ready:  bool

class DataStorage:
    """قاعدة بيانات SQLite — 6 جداول."""
    # Tables: historical_prices, alerts, watchlists,
    #         backtest_results, ml_predictions, preferences

class NewsItem:
    """خبر واحد من RSS أو محاكاة."""
    id:           str
    title:        str
    summary:      str
    source:       str
    url:          str
    published_at: datetime
    priority:     str   # 'high' | 'medium' | 'low'
    is_real:      bool
```

### Core Engines (في core/)

```python
class TechnicalAnalysisEngine:   # core/analysis.py
    """25+ مؤشر فني: RSI, MACD, BB, VWAP, Supertrend, MFI, Keltner..."""

TechnicalAnalysis = TechnicalAnalysisEngine  # ✅ alias للتوافق مع pages/02

class AIPredictionEngine:   # core/ai_engine.py
    """نماذج AI: Ensemble + Monte Carlo + تحليل الأخبار."""

AIEngine = AIPredictionEngine  # ✅ alias للتوافق مع pages/03

class BacktestEngine:    # core/backtest.py
class AlertEngine:       # core/alerts.py
class ChartEngine:       # core/charts.py
class PatternEngine:     # core/patterns.py — 14 نمط شمعة
```

---

## 5. تصريحات الدوال الرئيسية (Function Declarations)

```python
# ── Data ──────────────────────────────────────────────────────
def load_and_compute(symbol: str, days: int = 300) -> Optional[pd.DataFrame]:
    """جلب البيانات (حقيقية أو محاكاة) وحساب جميع المؤشرات."""

def fetch_real_data(symbol: str, days: int = 300) -> Optional[pd.DataFrame]:
    """جلب البيانات الحقيقية من Yahoo Finance."""

def generate_simulated_data(symbol: str, days: int = 300) -> pd.DataFrame:
    """توليد بيانات محاكاة إحصائية بـ GARCH(1,1) اليدوي."""

def fetch_quarterly_financials(symbol: str) -> Optional[pd.DataFrame]:
    """جلب البيانات الفصلية من yfinance أو تقدير تلقائي."""

# ── Indicators ────────────────────────────────────────────────
def calc_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
def calc_macd(c, fast=12, slow=26, sig=9) -> Tuple[pd.Series, pd.Series, pd.Series]:
def calc_bollinger(c, period=20, std_dev=2.0) -> Tuple:
def calc_atr(h, l, c, period: int = 14) -> pd.Series:
def calc_mfi(h, l, c, v, n: int = 14) -> pd.Series:
    """Money Flow Index — مؤشر تدفق الأموال (0-100)."""
def calc_keltner(h, l, c, ema_period=20, atr_period=10, mult=2.0):
    """Keltner Channels — يُعيد (upper, mid, lower)."""
def calc_supertrend(df, period=10, multiplier=3.0) -> Tuple[pd.Series, pd.Series]:
    """Supertrend بـ NumPy loop — لا FutureWarning."""
def calc_vwap(df: pd.DataFrame) -> pd.Series:
    """VWAP يومي صحيح — يُعاد من الصفر كل يوم."""

# ── Signals ───────────────────────────────────────────────────
def get_composite_signal(df: pd.DataFrame) -> Tuple[str, float, str]:
    """إشارة مُركَّبة من 6 مؤشرات. يُعيد (label, strength, emoji)."""

def detect_patterns(df: pd.DataFrame) -> List[Dict]:
    """كشف 5 أنماط شموع يابانية في آخر 3 شموع."""

# ── Backtest ──────────────────────────────────────────────────
def run_all_backtests(df, capital=100_000, strategies=None) -> List[BacktestResult]:
def backtest_summary_df(results: List[BacktestResult]) -> pd.DataFrame:
def dca_simulation(df, monthly_amount: float, months: int) -> Dict:
    """محاكاة الاستثمار الدوري (DCA) مع تحقق من المدخلات."""

# ── Caching ───────────────────────────────────────────────────
@st.cache_data(ttl=900)
def cached_load(symbol: str, days: int = 300) -> Optional[pd.DataFrame]: ...

@st.cache_data(ttl=1800)
def cached_backtest(symbol: str, capital: float, strategies: tuple, days: int = 500): ...

# ── Utilities ─────────────────────────────────────────────────
def safe_last(s: pd.Series, default=0.0) -> float:
def fmt_num(num, decimals=2) -> str:
def fmt_egp(num) -> str:
def get_simulation_warning_html(symbol: str) -> str:
def get_data_source_badge(source: str) -> str:
```

---

## 6. تصريحات قاعدة البيانات (DB Schema Declarations)

```sql
-- SQLite Database: egx_terminal.db (في جذر المشروع)

CREATE TABLE historical_prices (
    id          INTEGER PRIMARY KEY,
    symbol      TEXT NOT NULL,
    date        TEXT NOT NULL,
    open        REAL, high REAL, low REAL,
    close       REAL NOT NULL,
    volume      INTEGER,
    source      TEXT DEFAULT 'simulated',
    created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, date)
);
CREATE INDEX idx_p_sym ON historical_prices(symbol);
CREATE INDEX idx_p_dt  ON historical_prices(date);

CREATE TABLE alerts (
    id          TEXT PRIMARY KEY,
    user_id     TEXT DEFAULT 'default',
    symbol      TEXT, alert_type TEXT,
    threshold   REAL, note TEXT,
    severity    TEXT DEFAULT 'MEDIUM',
    is_active   INTEGER DEFAULT 1,
    triggered   INTEGER DEFAULT 0,
    created_at  TEXT, triggered_at TEXT
);
CREATE INDEX idx_a_sym ON alerts(symbol);

CREATE TABLE watchlists (
    id          INTEGER PRIMARY KEY,
    user_id     TEXT DEFAULT 'default',
    name        TEXT, symbols TEXT,
    updated_at  TEXT,
    UNIQUE(user_id, name)
);

CREATE TABLE backtest_results (
    id           INTEGER PRIMARY KEY,
    symbol       TEXT, strategy TEXT,
    capital      REAL, total_return REAL,
    sharpe       REAL, max_drawdown REAL,
    win_rate     REAL, total_trades INTEGER,
    run_at       TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_bt_sym ON backtest_results(symbol);

CREATE TABLE ml_predictions (
    id           INTEGER PRIMARY KEY,
    symbol       TEXT, model_type TEXT,
    prediction   TEXT, confidence REAL,
    predicted_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE preferences (
    key          TEXT PRIMARY KEY,
    user_id      TEXT DEFAULT 'default',
    value        TEXT,
    updated_at   TEXT DEFAULT CURRENT_TIMESTAMP
);
```

---

## 7. تصريحات البيئة والتشغيل (Environment Declarations)

```bash
# متغيرات البيئة المطلوبة
GEMINI_API_KEY=AIza...          # اختياري — يُفعّل Gemini AI
EGX_DB_PATH=egx_terminal.db    # اختياري — مسار قاعدة البيانات

# أو في .streamlit/secrets.toml
[secrets]
GEMINI_API_KEY = "AIza..."

# Python version
python >= 3.11

# Port
STREAMLIT_SERVER_PORT = 8501
```

---

## 8. تصريحات الصفحات (Page Declarations)

| # | الصفحة | الملف | الوظيفة |
|---|--------|-------|---------|
| 1 | 🏠 الرئيسية | `egx_app.py::page_home` | KPIs + أسهم رئيسية |
| 2 | 📊 التحليل الفني | `page_analysis` | 25+ مؤشر + رسوم |
| 3 | ⚡ Supertrend | `page_supertrend` | محلل Supertrend متقدم |
| 4 | 🧪 الباكتست | `page_backtest` | 10 استراتيجيات |
| 5 | 🤖 التنبؤ الذكي | `page_ml` | GB + LSTM + Transformer |
| 6 | 💼 المحفظة | `page_portfolio` | Kelly + وقف الخسارة |
| 7 | 👁️ قائمة المراقبة | `page_watchlist` | إدارة الأسهم |
| 8 | 🔍 الفرز | `page_screener` | فلترة السوق |
| 9 | 🔔 التنبيهات | `page_alerts` | تنبيهات السعر |
| 10 | ⚖️ المقارنة | `page_compare` | مقارنة 5 أسهم |
| 11 | 📰 الأخبار | `page_news` | RSS + محاكاة |
| 12 | 📈 البيانات الفصلية | `page_quarterly` | إيرادات + أرباح |
| 13 | 🏭 القطاعات | `page_sector` | heatmap القطاعات |
| 14 | 🌀 فيبوناتشي | `page_fibonacci` | مستويات فيبو |
| 15 | 🗄️ قاعدة البيانات | `page_database` | إحصائيات SQLite |
| 16 | ✨ تحليل AI | `page_ai_insights` | Gemini بالعربية |
| 17 | ℹ️ عن v35 | `page_about` | changelog |

---

## 9. تصريحات الإصلاحات (Bug Fix Declarations)

| الكود | الخطأ | الإصلاح | الخطورة |
|---|---|---|---|
| STRUCT-1 | `date/` ← كود يستورد `data.*` | أُنشئ `data/` | 🔴 |
| STRUCT-2 | `.streamlit/` مفقودة | أُنشئت مع `config.toml` | 🔴 |
| STRUCT-3 | `gitignor` (خطأ إملائي) | `.gitignore` | 🔴 |
| STRUCT-4 | `dockerfile` (lowercase) | `Dockerfile` | 🔴 |
| STRUCT-5 | `docker` بدون امتداد | `docker-compose.yml` | 🔴 |
| STRUCT-6 | `peges/charts.py` typo | `pages/charts.py` | 🟠 |
| STRUCT-7 | `egx_app.py` مفقود | أُنشئ من `enhanced_egx_app_v35_final.py` | 🔴 |
| SYN-1 | `validators.py:110` SyntaxError | إصلاح `re.sub` quotes | 🔴 |
| IMP-1 | `AIEngine` غير موجود | `AIPredictionEngine as AIEngine` | 🔴 |
| IMP-2 | `TechnicalAnalysis` غير موجود | `TechnicalAnalysisEngine as TechnicalAnalysis` | 🔴 |
| IMP-3 | `app_config` غير مُعرَّف | `app_config = config` في settings.py | 🔴 |
| CFG-1 | `AI_PREDICTION_HORIZON` مفقودة | أُضيفت = 5 | 🟠 |
| CFG-2 | `app_config` alias مفقود | أُضيف في settings.py | 🔴 |
| CFG-3 | `COMMISSION = 0.002` (20bps خاطئ) | `0.00185` (18.5bps الرسمي) | 🟠 |
| LOG-1 | خصم عمولة مزدوج (buy) | `capital -= entry_cost` فقط | 🔴 |
| LOG-2 | `gemini-2.0-flash` → 404 | `gemini-1.5-flash` | 🔴 |
| INIT-1 | `data/__init__.py` فارغ | exports كاملة | 🟡 |
| INIT-2 | `core/__init__.py` فارغ | aliases + exports | 🟡 |
| INIT-3 | `config/__init__.py` فارغ | exports | 🟡 |
| DB-1 | `"data/egx_terminal.db"` مسار خاطئ | `"egx_terminal.db"` | 🟠 |

---

## 10. أوامر التشغيل (Run Declarations)

```bash
# ── التثبيت ────────────────────────────────────────────────────
pip install -r requirements.txt

# ── التشغيل الأساسي ───────────────────────────────────────────
streamlit run egx_app.py                         # الواجهة الموحّدة (17 صفحة)
streamlit run app.py                             # multi-page mode

# ── مع Gemini AI ──────────────────────────────────────────────
export GEMINI_API_KEY="AIza..."
streamlit run egx_app.py

# ── Docker ────────────────────────────────────────────────────
docker build -t egx-pro-terminal .
docker run -p 8501:8501 egx-pro-terminal
docker run -p 8501:8501 -e GEMINI_API_KEY=AIza... egx-pro-terminal

# ── مع PyTorch (LSTM + Transformer) ──────────────────────────
pip install torch
streamlit run egx_app.py

# ── مع أخبار RSS ──────────────────────────────────────────────
pip install feedparser
streamlit run egx_app.py

# ── الاختبارات ────────────────────────────────────────────────
python -m pytest tests/ -v
python -m pytest tests/ --cov=. --cov-report=html

# ── Production ────────────────────────────────────────────────
streamlit run egx_app.py \
  --server.port=8501 \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --browser.gatherUsageStats=false
```

---

*EGX Pro Terminal v35 — للأغراض التعليمية فقط · ليست توصية استثمارية*
