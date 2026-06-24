# 🇪🇬 EGX Pro Terminal v34

**Professional Egyptian Stock Exchange (EGX) Analysis Platform**

منصة تحليل احترافية متكاملة لبورصة الأوراق المالية المصرية.

---

## ⚡ التشغيل السريع (3 خطوات)

```bash
# 1. نسخ المستودع
git clone https://github.com/m02417710-maker/blank-app.git
cd blank-app

# 2. تثبيت المكتبات
pip install -r requirements.txt

# 3. تشغيل التطبيق
streamlit run egx_app.py
```

---

## 🚀 أوامر التشغيل الكاملة

### التشغيل الأساسي
```bash
# الواجهة الموحّدة (15 صفحة) — الأسرع والأكثر اكتمالاً
streamlit run egx_app.py

# الواجهة متعددة الصفحات (multi-page)
streamlit run app.py
```

### تشغيل على بورت محدد
```bash
streamlit run egx_app.py --server.port 8501
streamlit run egx_app.py --server.port 8502 --server.address 0.0.0.0
```

### وضع Production (Streamlit Cloud / Server)
```bash
streamlit run egx_app.py \
  --server.headless true \
  --server.enableCORS false \
  --server.enableXsrfProtection true \
  --browser.gatherUsageStats false
```

### تشغيل Docker
```bash
# بناء الصورة
docker build -t egx-pro-terminal .

# تشغيل
docker run -p 8501:8501 egx-pro-terminal

# مع متغيرات البيئة (Gemini API)
docker run -p 8501:8501 -e GEMINI_API_KEY=your_key egx-pro-terminal
```

### تشغيل مع Gemini AI (اختياري)
```bash
# إضافة مفتاح Gemini في .streamlit/secrets.toml:
# [secrets]
# GEMINI_API_KEY = "AIza..."

# أو عبر متغير البيئة:
export GEMINI_API_KEY="AIza..."
streamlit run egx_app.py
```

### تشغيل الاختبارات
```bash
# جميع الاختبارات
python -m pytest tests/ -v

# اختبار محدد
python -m pytest tests/test_analysis.py -v
python -m pytest tests/test_data_loading.py -v

# مع تقرير التغطية
pip install pytest-cov
python -m pytest tests/ --cov=. --cov-report=html
```

---

## 📦 التثبيت التفصيلي

### بيئة افتراضية (مُوصى به)
```bash
# إنشاء البيئة الافتراضية
python -m venv venv

# تفعيل (Linux/Mac)
source venv/bin/activate

# تفعيل (Windows)
venv\Scripts\activate

# تثبيت المكتبات
pip install -r requirements.txt

# تشغيل
streamlit run egx_app.py
```

### conda
```bash
conda create -n egx python=3.11 -y
conda activate egx
pip install -r requirements.txt
streamlit run egx_app.py
```

---

## 🏗️ معمارية المشروع

```
blank-app/
├── app.py                    ← نقطة الدخول (multi-page entry)
├── egx_app.py                ← الواجهة الموحّدة الرئيسية (15 صفحة)
├── egx_engine.py             ← محرك البيانات: 200+ شركة، 20+ مؤشر
├── egx_ml_backtest.py        ← ML Walk-Forward + 10 استراتيجيات
├── egx_ai_analyzer.py        ← Gemini AI (تحليل عربي)
├── requirements.txt          ← المكتبات
├── .streamlit/
│   └── config.toml           ← إعدادات Streamlit (dark theme)
├── data/                     ← قاعدة بيانات EGX الموسّعة
│   ├── __init__.py
│   ├── egx_symbols.py        ← 150+ رمز مع بيانات كاملة
│   ├── market_data.py        ← Yahoo Finance API
│   ├── storage.py            ← SQLite (alerts, watchlists)
│   └── news_dividends.py     ← الأخبار والتوزيعات
├── core/                     ← محركات التحليل
│   ├── __init__.py
│   ├── analysis.py           ← 25+ مؤشر فني
│   ├── ai_engine.py          ← Ensemble AI + Monte Carlo
│   ├── backtest.py           ← Backtest Engine (8 strategies)
│   ├── alerts.py             ← Alert Engine
│   ├── charts.py             ← Plotly Charts
│   └── patterns.py           ← 14 Candlestick Patterns
├── config/
│   ├── __init__.py
│   ├── settings.py           ← AppConfig
│   └── app_config.py         ← Streamlit config helper
├── pages/                    ← Streamlit Multi-Page
│   ├── __init__.py
│   ├── 01_Dashboard.py
│   ├── 02_Technical.py
│   ├── 03_AI_Predictions.py
│   ├── 04_Backtest.py
│   ├── 05_Alerts.py
│   ├── 06_News_Dividends.py
│   └── 07_Settings.py
├── utils/
│   ├── __init__.py
│   ├── formatters.py
│   ├── validators.py
│   └── helpers.py
└── tests/
    ├── __init__.py
    ├── test_analysis.py
    ├── test_data_loading.py
    └── test_validation.py
```

---

## 🔧 الإصلاحات المُطبَّقة في v34

| # | المشكلة | الإصلاح |
|---|---------|---------|
| 1 | `date/` ← `data/` (اسم مجلد خاطئ) | تم نسخ المحتوى لمجلد `data/` |
| 2 | `Streamlit/config.toml` ← `.streamlit/config.toml` | تم نسخ للمسار الصحيح |
| 3 | `gitignore` ← `.gitignore` (بدون نقطة) | تم إنشاء `.gitignore` |
| 4 | `app.py` مفقود (README يشير إليه) | تم إنشاؤه |
| 5 | `utils/validators.py` — SyntaxError في `re.sub` | تم إصلاح الاقتباسات |
| 6 | `from config.settings import app_config` (خاطئ) | `import config as app_config` |
| 7 | `peges/` (typo) → `pages/` | تم نسخ `charts.py` للمجلد الصحيح |
| 8 | `data/storage.py` — مسار DB خاطئ | إصلاح `db_path` |
| 9 | خصم عمولة مزدوج في `egx_ml_backtest.py` | إصلاح حساب `entry_cost` |
| 10 | `gemini-2.0-flash` غير موجود | تغيير لـ `gemini-1.5-flash` |
| 11 | MFI و Keltner غير محسوبين | إضافة `calc_mfi()` و`calc_keltner()` |
| 12 | Bare except في كل مكان | `except Exception as e` |

---

## 📊 الميزات

### التحليل الفني (20+ مؤشر)
- RSI, MACD, Bollinger Bands, VWAP (يومي صحيح)
- Supertrend (NumPy — بدون FutureWarning)
- Ichimoku Cloud, Parabolic SAR, ADX
- Stochastic, CCI, Williams %R, OBV, ATR
- **MFI** (Money Flow Index) ← مُضاف في v32
- **Keltner Channels** ← مُضاف في v32

### ML والذكاء الاصطناعي
- Walk-Forward Validation (بدون Data Leakage)
- GradientBoosting مع class balancing
- Monte Carlo (1000 مسار)
- Gemini AI بالعربية (اختياري)

### الباكتست
- 10 استراتيجيات: EMA Cross, RSI, MACD, Bollinger, Supertrend, VWAP+RSI, PSAR, Ichimoku, ADX, Multi-Signal
- عمولات EGX الرسمية: 18.5 bps
- Kelly Criterion + Sharpe + Calmar + Drawdown
- محاكاة DCA

---

## 🌐 النشر على Streamlit Cloud

1. Fork المستودع على GitHub
2. اذهب إلى [share.streamlit.io](https://share.streamlit.io)
3. اختر المستودع وحدد `egx_app.py` كملف رئيسي
4. في Secrets أضف `GEMINI_API_KEY` (اختياري)

---

## ⚠️ تنبيه قانوني

هذا التطبيق للأغراض التعليمية والبحثية فقط. ليست توصية استثمارية. استشر مستشاراً مالياً مرخصاً قبل اتخاذ أي قرار استثماري.

---

**EGX Pro Team | 2026**
