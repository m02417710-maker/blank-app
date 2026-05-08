# data/screener_criteria.py

SCREENER_CRITERIA = {
    "price": {
        "name": "السعر الحالي",
        "type": "range",
        "min": 0,
        "max": 1000,
        "unit": "EGP",
        "description": "سعر السهم الحالي"
    },
    "change_percent": {
        "name": "نسبة التغير",
        "type": "range",
        "min": -20,
        "max": 20,
        "unit": "%",
        "description": "نسبة التغير خلال اليوم"
    },
    "volume": {
        "name": "حجم التداول",
        "type": "range",
        "min": 0,
        "max": 10000000,
        "unit": "سهم",
        "description": "عدد الأسهم المتداولة"
    },
    "pe_ratio": {
        "name": "مكرر الربحية",
        "type": "range",
        "min": 0,
        "max": 50,
        "unit": "x",
        "description": "السعر / ربحية السهم"
    },
    "eps": {
        "name": "ربحية السهم",
        "type": "range",
        "min": -10,
        "max": 50,
        "unit": "EGP",
        "description": "صافي الربح / عدد الأسهم"
    },
    "revenue_growth": {
        "name": "نمو الإيرادات",
        "type": "range",
        "min": -50,
        "max": 100,
        "unit": "%",
        "description": "نمو الإيرادات السنوي"
    },
    "market_cap": {
        "name": "القيمة السوقية",
        "type": "categories",
        "categories": ["صغيرة (<1B)", "متوسطة (1B-10B)", "كبيرة (10B-50B)", "قيادية (>50B)"],
        "description": "تصنيف حجم الشركة"
    },
    "beta": {
        "name": "معامل بيتا",
        "type": "range",
        "min": 0,
        "max": 3,
        "unit": "x",
        "description": "مقياس التذبذب والمخاطرة"
    },
    "dividend_yield": {
        "name": "عائد توزيعات الأرباح",
        "type": "range",
        "min": 0,
        "max": 20,
        "unit": "%",
        "description": "نسبة العائد من التوزيعات"
    },
    "rsi": {
        "name": "مؤشر القوة النسبية",
        "type": "range",
        "min": 0,
        "max": 100,
        "unit": "",
        "description": "مؤشر فني لقياس الزخم"
    }
}
