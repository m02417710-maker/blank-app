# 🇪🇬 EGX Pro Terminal v35

**Professional Egyptian Stock Exchange (EGX) Analysis Platform**

---

## ⚡ التشغيل السريع

```bash
# 1. نسخ المستودع
git clone https://github.com/m02417710-maker/blank-app.git
cd blank-app

# 2. تثبيت المكتبات
pip install -r requirements.txt

# 3. تشغيل التطبيق (الواجهة الموحّدة — الأسرع)
streamlit run egx_app.py

# أو الواجهة المحسّنة الكاملة
streamlit run enhanced_egx_app.py
```

---

## 🚀 أوامر التشغيل الكاملة

```bash
# الواجهة الموحّدة (15 صفحة) — موصى بها
streamlit run egx_app.py

# الواجهة المحسّنة (17 صفحة + ML Ensemble + SQLite)
streamlit run enhanced_egx_app.py

# واجهة multi-page
streamlit run app.py

# مع Gemini AI
export GEMINI_API_KEY="AIza..."
streamlit run egx_app.py

# Docker
docker build -t egx-pro-terminal .
docker run -p 8501:8501 egx-pro-terminal
docker run -p 8501:8501 -e GEMINI_API_KEY=AIza... egx-pro-terminal

# مع PyTorch (LSTM + Transformer)
pip install torch
streamlit run enhanced_egx_app.py

# الاختبارات
python -m pytest tests/ -v
```

---

## 🏗️ هيكل المشروع

```
blank-app/
├── egx_app.py                ← الواجهة الرئيسية الموحّدة (15 صفحة) ← ابدأ هنا
├── enhanced_egx_app.py       ← الواجهة المحسّنة (17 صفحة + ML Ensemble)
├── app.py                    ← نقطة دخول multi-page
├── egx_engine.py             ← محرك البيانات: 200+ شركة، 25+ مؤشر
├── egx_ml_backtest.py        ← ML Walk-Forward + 10 استراتيجيات
├── egx_ai_analyzer.py        ← Gemini AI بالعربية
├── requirements.txt          ← المكتبات
├── Dockerfile                ← Docker container
├── .streamlit/config.toml   ← إعدادات Streamlit (dark theme)
├── .gitignore               ← Git ignore
├── data/                    ← قاعدة بيانات EGX
│   ├── egx_symbols.py       ← 150+ شركة
│   ├── market_data.py       ← Yahoo Finance API
│   ├── storage.py           ← SQLite
│   └── news_dividends.py    ← الأخبار والتوزيعات
├── core/                    ← محركات التحليل
│   ├── analysis.py          ← 25+ مؤشر فني
│   ├── ai_engine.py         ← Ensemble AI + Monte Carlo
│   ├── backtest.py          ← Backtest Engine
│   ├── alerts.py            ← Alert Engine
│   ├── charts.py            ← Plotly Charts
│   └── patterns.py          ← 14 نمط شمعة
├── config/
│   └── settings.py          ← AppConfig
├── pages/                   ← Streamlit Multi-Page
│   ├── 01_Dashboard.py
│   ├── 02_Technical.py
│   ├── 03_AI_Predictions.py
│   ├── 04_Backtest.py
│   ├── 05_Alerts.py
│   ├── 06_News_Dividends.py
│   └── 07_Settings.py
├── utils/                   ← أدوات مساعدة
└── tests/                   ← اختبارات
```

---

## 🔧 الإصلاحات المُطبَّقة v35

| # | المشكلة | الإصلاح |
|---|---------|---------|
| 1 | `date/` ← `data/` (17 ملف يستورد data.*) | أُنشئ مجلد `data/` كامل |
| 2 | `Streamlit/` ← `.streamlit/` | `.streamlit/config.toml` |
| 3 | `gitignore` ← `.gitignore` | أُضيفت النقطة |
| 4 | `dockerfile` ← `Dockerfile` | capital D |
| 5 | `docker` ← `docker-compose.yml` | تمديد صحيح |
| 6 | `peges/` ← `pages/charts.py` | typo مُصحَّح |
| 7 | `validators.py:110` SyntaxError | إصلاح re.sub quotes |
| 8 | `AIEngine` غير موجود | alias لـ `AIPredictionEngine` |
| 9 | `TechnicalAnalysis` غير موجود | alias لـ `TechnicalAnalysisEngine` |
| 10 | `app_config` غير مُصدَّر | `app_config = config` في settings.py |
| 11 | `AI_PREDICTION_HORIZON` مفقودة | أُضيفت في AppConfig |
| 12 | `COMMISSION = 0.002` خاطئ | `0.00185` (EGX الرسمي 18.5 bps) |
| 13 | `data/__init__.py` فارغ | exports كاملة |
| 14 | `core/__init__.py` فارغ | aliases + exports |

---

## ⚠️ تنبيه قانوني

هذا التطبيق للأغراض التعليمية والبحثية فقط. ليست توصية استثمارية.

**EGX Pro Team | 2026**
