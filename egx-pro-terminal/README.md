<div align="center">

# 📈 EGX Pro Terminal v26

**منصة تحليل احترافية للبورصة المصرية (EGX)**  
*Professional Technical Analysis Platform for Egyptian Stock Exchange*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-ff4b4b)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![EGX](https://img.shields.io/badge/EGX-100%2B%20Stocks-gold)](https://www.egx.com.eg)

[🇬🇧 English](#english) | [🇪🇬 العربية](#arabic)

</div>

---

<a name="arabic"></a>
## 🇪🇬 نظرة عامة

**EGX Pro Terminal** هي منصة تحليل فني متكاملة للبورصة المصرية، تدعم أكثر من **100 سهم مصري** مع مؤشرات فنية متقدمة، تنبيهات آلية، وتحليل ذكي بالذكاء الاصطناعي.

### ✨ المميزات الرئيسية

| الميزة | الوصف |
|--------|-------|
| 📊 **تحليل فني متقدم** | RSI, MACD, Bollinger Bands, EMA, SMA, ATR, ADX |
| 🔔 **تنبيهات آلية** | إشارات شراء/بيع فورية عند تقاطعات المؤشرات |
| 📈 **رسم بياني تفاعلي** | شموع يابانية + حجم التداول + مؤشرات تراكبية |
| 🤖 **تحليل ذكي** | تقييم آلي للاتجاه باستخدام نماذج مدمجة |
| 📋 **قائمة مراقبة** | متابعة محفظة مخصصة من الأسهم المفضلة |
| 📱 **واجهة عربية** | دعم كامل للعربية مع أرقام عربية/هندية |

### 🚀 التشغيل السريع

```bash
# 1. استنساخ المستودع
git clone https://github.com/m02417710-maker/egx-pro-terminal.git
cd egx-pro-terminal

# 2. تثبيت المتطلبات
pip install -r requirements.txt

# 3. تشغيل المنصة
streamlit run app.py
```

### 📁 هيكل المشروع

```
egx-pro-terminal/
├── 📄 app.py                 # التطبيق الرئيسي (Streamlit)
├── 📁 core/
│   ├── 📄 analysis.py        # محرك التحليل الفني
│   ├── 📄 alerts.py          # نظام التنبيهات الذكي
│   └── 📄 patterns.py        # التعرف على أنماط الشموع
├── 📁 data/
│   ├── 📄 egx_symbols.py     # قائمة أسهم EGX (100+ سهم)
│   └── 📄 market_data.py     # جلب البيانات من Yahoo Finance
├── 📁 config/
│   └── 📄 settings.py        # الإعدادات والثوابت
├── 📁 tests/
│   └── 📄 test_analysis.py   # اختبارات الوحدة
├── 📁 docs/
│   ├── 📄 API.md             # توثيق API
│   └── 📄 STRATEGIES.md      # استراتيجيات التداول المدعومة
├── 📄 README.md              # هذا الملف
├── 📄 requirements.txt       # المكتبات المطلوبة
├── 📄 LICENSE                # ترخيص MIT
├── 📄 CODE_OF_CONDUCT.md   # مدونة السلوك
└── 📄 CONTRIBUTING.md        # دليل المساهمة
```

### ⚙️ المتطلبات

- Python 3.10+
- pandas, numpy, yfinance
- streamlit, plotly
- ta (Technical Analysis Library)

### 📝 الترخيص

هذا المشروع مرخص بموجب [MIT License](LICENSE).  
**البيانات للأغراض التعليمية فقط — ليست نصيحة استثمارية.**

---

<a name="english"></a>
## 🇬🇧 Overview

**EGX Pro Terminal** is a comprehensive technical analysis platform for the Egyptian Stock Exchange (EGX), supporting **100+ Egyptian stocks** with advanced technical indicators, automated alerts, and AI-powered analysis.

### ✨ Key Features

| Feature | Description |
|---------|-------------|
| 📊 **Advanced Technical Analysis** | RSI, MACD, Bollinger Bands, EMA, SMA, ATR, ADX |
| 🔔 **Automated Alerts** | Instant buy/sell signals at indicator crossovers |
| 📈 **Interactive Charts** | Japanese candlesticks + volume + overlay indicators |
| 🤖 **Smart Analysis** | Automated trend assessment using built-in models |
| 📋 **Watchlist** | Track a custom portfolio of favorite stocks |
| 📱 **Arabic UI** | Full Arabic support with Arabic/Indian numerals |

### 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/m02417710-maker/egx-pro-terminal.git
cd egx-pro-terminal

# 2. Install requirements
pip install -r requirements.txt

# 3. Run the platform
streamlit run app.py
```

### 📝 License

This project is licensed under the [MIT License](LICENSE).  
**Data is for educational purposes only — not investment advice.**

---

<div align="center">

**صُنع بـ ❤️ في مصر** 🇪🇬  
*Made with ❤️ in Egypt*

</div>
