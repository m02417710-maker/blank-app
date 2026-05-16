# 📚 توثيق API - EGX Pro Terminal

> **الإصدار:** v26.0.0  
> **آخر تحديث:** مايو 2026

---

## نظرة عامة

EGX Pro Terminal يوفر واجهة برمجية (API) داخلية لتحليل الأسهم المصرية. هذه الوثيقة توضح كيفية استخدام المحركات الأساسية.

---

## EGXAnalyzer

### الوصف

المحرك الرئيسي للتحليل الفني. يجلب البيانات من Yahoo Finance ويحسب المؤشرات الفنية.

### الاستخدام:

```python
from core.analysis import EGXAnalyzer

# إنشاء محلل
analyzer = EGXAnalyzer("COMI", period="1y", interval="1d")

# جلب البيانات
data = analyzer.fetch_data()

# حساب المؤشرات
indicators = analyzer.calculate_all_indicators()

# الحصول على ملخص
summary = analyzer.get_summary()
```

### المعلمات:

| المعامل | النوع | الافتراضي | الوصف |
|---------|-------|-----------|-------|
| `symbol` | str | - | رمز السهم المصري (مثال: COMI) |
| `period` | str | "1y" | الفترة الزمنية: 1mo, 3mo, 6mo, 1y, 2y, 5y |
| `interval` | str | "1d" | الفاصل: 1d, 1wk, 1mo |

### الدوال:

#### `fetch_data()` → pd.DataFrame

يجلب البيانات التاريخية من Yahoo Finance.

**العائد:** DataFrame يحتوي على Open, High, Low, Close, Volume.

**الاستثناءات:**
- `ConnectionError`: فشل الاتصال بـ Yahoo Finance.
- `ValueError`: لا توجد بيانات للرمز المحدد.

#### `calculate_all_indicators()` → dict

يحسب جميع المؤشرات الفنية المتاحة.

**المؤشرات المحسوبة:**

| المؤشر | المفتاح | الوصف |
|--------|---------|-------|
| EMA 9 | `EMA_9` | المتوسط المتحرك الأسي 9 أيام |
| EMA 20 | `EMA_20` | المتوسط المتحرك الأسي 20 يوماً |
| EMA 50 | `EMA_50` | المتوسط المتحرك الأسي 50 يوماً |
| EMA 200 | `EMA_200` | المتوسط المتحرك الأسي 200 يوماً |
| RSI | `RSI` | مؤشر القوة النسبية |
| MACD | `MACD` | خط MACD |
| MACD Signal | `MACD_Signal` | خط إشارة MACD |
| Bollinger Upper | `BB_Upper` | الحد العلوي لبولينجر |
| Bollinger Lower | `BB_Lower` | الحد السفلي لبولينجر |
| ATR | `ATR` | متوسط المدى الحقيقي |
| ADX | `ADX` | مؤشر الحركة الاتجاهية |

#### `get_trend_analysis()` → dict

يحلل الاتجاه العام للسهم.

**العائد:**

```python
{
    "direction": "Bullish|Bearish|Strong Bullish|Strong Bearish|Neutral",
    "strength": "Strong|Moderate|Weak",
    "score": int,  # -3 to +3
    "signals": ["..."]  # قائمة الإشارات
}
```

#### `get_support_resistance(lookback=20)` → dict

يحسب مستويات الدعم والمقاومة الديناميكية.

**العائد:**

```python
{
    "support": float,
    "resistance": float,
    "pivot": float,
    "range_pct": float  # نسبة النطاق %
}
```

#### `get_summary()` → dict

ملخص شامل لآخر تحليل.

---

## AlertEngine

### الوصف

محرك التنبيهات الذكي. يراقب الأسهم ويُنشئ إشارات تداول آلية.

### الاستخدام:

```python
from core.alerts import AlertEngine

engine = AlertEngine()
engine.add_to_watchlist("COMI")
engine.add_to_watchlist("TMGH")

# مسح سهم واحد
alerts = engine.scan_stock("COMI")

# مسح قائمة المراقبة
all_alerts = engine.scan_watchlist()

# التنبيهات الأخيرة
recent = engine.get_recent_alerts(hours=24)
```

### أنواع الإشارات:

| النوع | الوصف |
|-------|-------|
| `STRONG_BUY` | إشارة شراء قوية |
| `BUY` | إشارة شراء |
| `HOLD` | انتظار |
| `SELL` | إشارة بيع |
| `STRONG_SELL` | إشارة بيع قوية |

### أنواع الأولويات:

| الأولوية | الوصف |
|----------|-------|
| `HIGH` | تنبيه عالي (RSI متطرف، تقاطع MACD) |
| `MEDIUM` | تنبيه متوسط (تقاطع EMA، حجم استثنائي) |
| `LOW` | تنبيه منخفض (اختراق Bollinger) |

---

## EGX Symbols Database

### الوصف

قاعدة بيانات رموز الأسهم المصرية.

### الاستخدام:

```python
from data.egx_symbols import *

# جميع الرموز
symbols = get_all_symbols()

# معلومات سهم
info = get_stock_info("COMI")
# {'name_ar': 'البنك التجاري الدولي', 'name_en': 'Commercial International Bank', 'sector': 'Banking'}

# بحث
results = search_stocks("بنك")
# [("COMI", {...}), ("QNB", {...}), ...]

# فلترة بالقطاع
banks = get_stocks_by_sector("Banking")
```

---

## أمثلة متقدمة

### مثال 1: مسح جميع الأسهم للتنبيهات

```python
from core.alerts import AlertEngine
from data.egx_symbols import get_all_symbols

engine = AlertEngine()
all_symbols = get_all_symbols()

for symbol in all_symbols[:10]:  # أول 10 أسهم
    alerts = engine.scan_stock(symbol)
    for alert in alerts:
        print(f"{alert.symbol}: {alert.signal.value} - {alert.message}")
```

### مثال 2: تحليل اتجاه محفظة

```python
from core.analysis import EGXAnalyzer

portfolio = ["COMI", "TMGH", "ETEL", "ESRS"]
results = []

for symbol in portfolio:
    analyzer = EGXAnalyzer(symbol, period="6mo")
    analyzer.fetch_data()
    trend = analyzer.get_trend_analysis()
    results.append({
        "symbol": symbol,
        "direction": trend["direction"],
        "score": trend["score"]
    })

# ترتيب حسب القوة
results.sort(key=lambda x: x["score"], reverse=True)
```

---

## ⚠️ تحذير

> **جميع البيانات والتحليلات هي للأغراض التعليمية فقط.**  
> **لا تعتبر نصيحة استثمارية.**
