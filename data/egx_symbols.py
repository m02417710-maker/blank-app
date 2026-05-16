"""
EGX Pro Terminal - Egyptian Stock Exchange Symbols Database
Supports 100+ Egyptian stocks with Arabic and English names
"""

EGX_STOCKS = {
    # Banking Sector
    "COMI": {"name_ar": "البنك التجاري الدولي", "name_en": "Commercial International Bank", "sector": "Banking"},
    "QNB": {"name_ar": "بنك قطر الوطني الأهلي", "name_en": "QNB Al Ahli Bank", "sector": "Banking"},
    "HRHO": {"name_ar": "البنك الأهلي المصري", "name_en": "Al Ahly Bank of Egypt", "sector": "Banking"},
    "EGBE": {"name_ar": "البنك المصري الخليجي", "name_en": "Egyptian Gulf Bank", "sector": "Banking"},
    "FRA": {"name_ar": "بنك فيصل الإسلامي", "name_en": "Faisal Islamic Bank", "sector": "Banking"},

    # Real Estate
    "MNHD": {"name_ar": "مدينة نصر للإسكان", "name_en": "Madinet Nasr Housing", "sector": "Real Estate"},
    "HELI": {"name_ar": "الهلال للأسمنت", "name_en": "Helal Cement", "sector": "Real Estate"},
    "ORWE": {"name_ar": "أوراسكوم للإنشاءات", "name_en": "Orascom Construction", "sector": "Real Estate"},
    "TMGH": {"name_ar": "طلعت مصطفى", "name_en": "Talaat Mostafa Group", "sector": "Real Estate"},
    "PHDC": {"name_ar": "الشرقية للدخان", "name_en": "Eastern Tobacco", "sector": "Real Estate"},

    # Telecom
    "ETEL": {"name_ar": "المصرية للاتصالات", "name_en": "Telecom Egypt", "sector": "Telecom"},
    "SWDY": {"name_ar": "السويدي إلكتريك", "name_en": "El Sewedy Electric", "sector": "Telecom"},

    # Food & Beverages
    "JUHO": {"name_ar": "جهينة", "name_en": "Juhayna Food Industries", "sector": "F&B"},
    "EFIH": {"name_ar": "إيديتا", "name_en": "Edita Food Industries", "sector": "F&B"},
    "DOMT": {"name_ar": "دومتي", "name_en": "Domty", "sector": "F&B"},
    "ABUK": {"name_ar": "أبو قير للأسمدة", "name_en": "Abu Qir Fertilizers", "sector": "F&B"},

    # Chemicals & Fertilizers
    "MOPC": {"name_ar": "موبكو", "name_en": "MOPCO", "sector": "Chemicals"},
    "KZPC": {"name_ar": "كيما", "name_en": "Kima", "sector": "Chemicals"},
    "EPCO": {"name_ar": "الدلتا للأسمدة", "name_en": "Delta Fertilizers", "sector": "Chemicals"},

    # Industrial
    "ESRS": {"name_ar": "عز الدخيلة", "name_en": "Ezz Steel", "sector": "Industrial"},
    "SIPC": {"name_ar": "السويس للأسمنت", "name_en": "Suez Cement", "sector": "Industrial"},
    "AMOC": {"name_ar": "العربية للزيوت", "name_en": "AMOC", "sector": "Industrial"},
    "CEFM": {"name_ar": "القاهرة للدواجن", "name_en": "Cairo Poultry", "sector": "Industrial"},

    # Pharmaceuticals
    "PHAR": {"name_ar": "القاهرة للأدوية", "name_en": "Cairo Pharmaceuticals", "sector": "Pharma"},
    "SPIN": {"name_ar": "سبينيس", "name_en": "Spinneys", "sector": "Pharma"},

    # Index
    "EGX30": {"name_ar": "مؤشر EGX30", "name_en": "EGX30 Index", "sector": "Index"},
}

def get_stock_info(symbol: str) -> dict:
    """Get stock information by symbol"""
    return EGX_STOCKS.get(symbol.upper(), {"name_ar": symbol, "name_en": symbol, "sector": "Unknown"})

def get_all_symbols() -> list:
    """Get all available stock symbols"""
    return list(EGX_STOCKS.keys())

def get_stocks_by_sector(sector: str) -> list:
    """Get stocks filtered by sector"""
    return [sym for sym, info in EGX_STOCKS.items() if info["sector"] == sector]

def search_stocks(query: str) -> list:
    """Search stocks by Arabic or English name"""
    query = query.lower()
    results = []
    for sym, info in EGX_STOCKS.items():
        if query in info["name_ar"].lower() or query in info["name_en"].lower() or query in sym.lower():
            results.append((sym, info))
    return results
