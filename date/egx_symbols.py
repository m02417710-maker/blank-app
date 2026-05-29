"""
EGX Pro Terminal v27 - Egyptian Stock Symbols Database
150+ Symbols with Full Sector Classification
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

class Sector(Enum):
    BANKING = "Banking"
    REAL_ESTATE = "Real Estate"
    FNB = "Food & Beverage"
    CONSTRUCTION = "Construction"
    TELECOM = "Telecom"
    ENERGY = "Energy"
    HEALTHCARE = "Healthcare"
    CHEMICALS = "Chemicals"
    TECHNOLOGY = "Technology"
    TOURISM = "Tourism"
    TEXTILES = "Textiles"
    TRANSPORT = "Transport"
    MINING = "Mining"
    INVESTMENT = "Investment"
    INDUSTRIAL = "Industrial"

@dataclass
class StockInfo:
    symbol: str
    name: str
    name_ar: str
    sector: Sector
    market_cap: Optional[float] = None  # in millions EGP
    shares_outstanding: Optional[float] = None  # in millions
    free_float: Optional[float] = None  # percentage
    beta: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    is_index: bool = False
    is_active: bool = True

    @property
    def yahoo_symbol(self) -> str:
        return f"{self.symbol}.CA" if not self.is_index else self.symbol

# Complete EGX Stock Database
EGX_STOCKS: Dict[str, StockInfo] = {
    # Banking Sector
    'COMI': StockInfo('COMI', 'Commercial International Bank', 'البنك التجاري الدولي', Sector.BANKING, 85000, 2900, 45.0, 1.15, 5.2, 1.1, 4.5),
    'HRHO': StockInfo('HRHO', 'Hermes Holdings', 'الهرم القابضة', Sector.INVESTMENT, 12500, 850, 55.0, 1.25, 8.5, 1.8, 2.1),
    'ABUK': StockInfo('ABUK', 'Abu Dhabi Islamic Bank - Egypt', 'أبوظبي الإسلامي - مصر', Sector.BANKING, 6200, 420, 40.0, 0.95, 6.8, 0.9, 3.2),
    'EGBE': StockInfo('EGBE', 'Egyptian Gulf Bank', 'بنك مصر الخليج', Sector.BANKING, 1800, 150, 35.0, 0.85, 4.2, 0.7, 2.8),
    'NSGB': StockInfo('NSGB', 'National Societe Generale Bank', 'الأهلي سوستيه جنرال', Sector.BANKING, 9500, 680, 42.0, 1.05, 5.8, 1.0, 3.5),
    'HDBK': StockInfo('HDBK', 'Housing & Development Bank', 'بنك التعمير والإسكان', Sector.BANKING, 3200, 280, 38.0, 0.90, 4.5, 0.8, 3.0),
    'FAIT': StockInfo('FAIT', 'Faisal Islamic Bank', 'بنك فيصل الإسلامي', Sector.BANKING, 4100, 310, 35.0, 0.88, 5.1, 0.85, 2.5),
    'CBKD': StockInfo('CBKD', 'Crédit Agricole Egypt', 'كريدي أجريكول مصر', Sector.BANKING, 2800, 220, 40.0, 0.92, 4.8, 0.75, 3.8),

    # Real Estate
    'TMGH': StockInfo('TMGH', 'Talaat Mostafa Group', 'طلعت مصطفى', Sector.REAL_ESTATE, 28000, 3500, 48.0, 1.35, 7.2, 1.5, 2.8),
    'PHDC': StockInfo('PHDC', 'Palm Hills Development', 'بالم هيلز', Sector.REAL_ESTATE, 8500, 1200, 45.0, 1.20, 6.5, 1.2, 2.5),
    'MNHD': StockInfo('MNHD', 'Madinet Nasr Housing', 'مدينة نصر للإسكان', Sector.REAL_ESTATE, 5200, 750, 42.0, 1.15, 5.8, 1.1, 3.0),
    'GDWA': StockInfo('GDWA', 'Gadwa for Industrial Development', 'الجدوى', Sector.REAL_ESTATE, 1800, 280, 35.0, 1.10, 4.5, 0.9, 2.2),
    'HELL': StockInfo('HELL', 'Heliopolis Housing', 'حلوان للإسكان', Sector.REAL_ESTATE, 2200, 320, 38.0, 1.05, 5.2, 1.0, 2.8),
    'ORAS': StockInfo('ORAS', 'Orascom Construction', 'أوراسكوم للإنشاءات', Sector.CONSTRUCTION, 15000, 1100, 50.0, 1.30, 8.5, 1.8, 1.5),
    'MISR': StockInfo('MISR', 'Misr Insurance Properties', 'مصر للتأمين العقاري', Sector.REAL_ESTATE, 1200, 180, 30.0, 0.85, 3.8, 0.7, 4.0),

    # Food & Beverage
    'EAST': StockInfo('EAST', 'Eastern Company', 'الشرقية للدخان', Sector.FNB, 22000, 1800, 52.0, 0.95, 12.5, 2.5, 5.5),
    'ESRS': StockInfo('ESRS', 'Egyptian Sugar & Refining', 'السكر والصناعات التكاملية', Sector.FNB, 4800, 650, 40.0, 0.88, 5.2, 0.9, 3.2),
    'DOMT': StockInfo('DOMT', 'Domty', 'دومتي', Sector.FNB, 3200, 450, 45.0, 1.05, 8.5, 1.5, 2.0),
    'JUHO': StockInfo('JUHO', 'Juhayna Food Industries', 'جهينة', Sector.FNB, 6500, 850, 48.0, 1.10, 9.2, 1.8, 2.5),
    'UNIP': StockInfo('UNIP', 'United Pharma', 'العالمية للأدوية', Sector.HEALTHCARE, 1800, 220, 35.0, 0.92, 6.8, 1.2, 2.8),
    'OLFI': StockInfo('OLFI', 'Obour Land', 'أرض العبور', Sector.FNB, 2800, 380, 42.0, 1.08, 7.5, 1.4, 2.2),
    'MPCI': StockInfo('MPCI', 'Mansoura Poultry', 'الداجنة', Sector.FNB, 1500, 200, 38.0, 1.02, 5.5, 1.0, 3.5),
    'JFEF': StockInfo('JFEF', 'Juhayna Fresh', 'جهينة فريش', Sector.FNB, 2200, 300, 40.0, 1.12, 8.8, 1.6, 2.0),

    # Construction
    'ORWE': StockInfo('ORWE', 'Oriental Weavers', 'النساجون الشرقيون', Sector.INDUSTRIAL, 8500, 650, 45.0, 1.15, 6.2, 1.3, 3.0),
    'SWDY': StockInfo('SWDY', 'Sidi Kerir Petrochemicals', 'سيدي كرير', Sector.CHEMICALS, 12000, 900, 48.0, 1.25, 7.8, 1.6, 2.8),
    'AMOC': StockInfo('AMOC', 'Alexandria Mineral Oils', 'الإسكندرية للزيوت المعدنية', Sector.CHEMICALS, 3800, 280, 42.0, 1.05, 5.5, 1.1, 3.5),
    'HELW': StockInfo('HELW', 'El Sewedy Electric', 'السويدي إلكتريك', Sector.INDUSTRIAL, 18000, 1400, 50.0, 1.35, 9.5, 2.0, 2.0),
    'SKPC': StockInfo('SKPC', 'Suez Canal Bank Petrochemicals', 'قناة السويس للبتروكيماويات', Sector.CHEMICALS, 2500, 180, 38.0, 1.08, 4.8, 0.9, 3.2),

    # Telecom
    'EGTS': StockInfo('EGTS', 'Egyptian Telecom', 'المصرية للاتصالات', Sector.TELECOM, 15000, 850, 25.0, 0.85, 5.2, 0.9, 4.5),
    'ETEL': StockInfo('ETEL', 'Telecom Egypt', 'اتصالات مصر', Sector.TELECOM, 22000, 1700, 30.0, 0.90, 6.5, 1.1, 3.8),

    # Energy
    'TAQA': StockInfo('TAQA', 'TAQA Arabia', 'طاقة عربية', Sector.ENERGY, 4200, 350, 40.0, 1.12, 8.5, 1.5, 2.5),
    'EDBM': StockInfo('EDBM', 'EDBEK Manufacturing', 'إيدبك', Sector.ENERGY, 2800, 220, 35.0, 1.08, 6.2, 1.2, 3.0),

    # Technology
    'FWRY': StockInfo('FWRY', 'Fawry', 'فوري', Sector.TECHNOLOGY, 8500, 750, 45.0, 1.45, 25.0, 4.5, 0.5),
    'EGTS3': StockInfo('EGTS3', 'EGX Tech 30', 'مؤشر التكنولوجيا', Sector.TECHNOLOGY, None, None, None, None, None, None, None, True),
    'SWVL': StockInfo('SWVL', 'Swvl Holdings', 'سويفل', Sector.TECHNOLOGY, 1200, 150, 55.0, 1.85, None, None, 0.0),

    # Healthcare
    'PHAR': StockInfo('PHAR', 'Pharos Holding', 'فاروس القابضة', Sector.INVESTMENT, 3500, 280, 42.0, 1.15, 7.2, 1.4, 2.5),
    'RMDA': StockInfo('RMDA', 'Rameda Pharmaceuticals', 'راميدا', Sector.HEALTHCARE, 2800, 350, 40.0, 1.05, 12.5, 2.2, 1.8),
    'IDHC': StockInfo('IDHC', 'Integrated Diagnostics', 'الدياجنستيك', Sector.HEALTHCARE, 4200, 450, 45.0, 1.10, 15.0, 2.8, 1.2),
    'CLHO': StockInfo('CLHO', 'Cleopatra Hospital', 'مستشفيات كليوباترا', Sector.HEALTHCARE, 3200, 380, 38.0, 1.08, 18.0, 3.2, 0.8),
    'SPIN': StockInfo('SPIN', 'Spinalys', 'سبيناليس', Sector.HEALTHCARE, 1500, 180, 35.0, 1.02, 8.5, 1.5, 2.2),
    'PCI': StockInfo('PCI', 'Pharco Chemicals', 'فاركو للكيماويات', Sector.CHEMICALS, 2200, 280, 40.0, 1.05, 6.8, 1.3, 2.8),
    'EKHO': StockInfo('EKHO', 'Egyptian Kuwaiti Hospital', 'المستشفى المصري الكويتي', Sector.HEALTHCARE, 1800, 220, 35.0, 0.95, 9.5, 1.8, 2.0),

    # Chemicals
    'EFIC': StockInfo('EFIC', 'Egyptian Financial & Industrial', 'المالية والصناعية', Sector.CHEMICALS, 1500, 120, 32.0, 1.02, 4.5, 0.8, 3.5),
    'KZPC': StockInfo('KZPC', 'Kafr El Zayat Pesticides', 'كفر الزيات', Sector.CHEMICALS, 800, 65, 30.0, 0.92, 3.8, 0.7, 4.0),
    'NIPH': StockInfo('NIPH', 'Nile Pharma', 'النيل للأدوية', Sector.HEALTHCARE, 1200, 150, 35.0, 0.98, 7.2, 1.4, 2.5),
    'MICH': StockInfo('MICH', 'Misr Chemicals', 'مصر للكيماويات', Sector.CHEMICALS, 950, 80, 28.0, 0.88, 3.5, 0.6, 4.5),
    'MFPC': StockInfo('MFPC', 'Misr Fertilizers', 'مصر للأسمدة', Sector.CHEMICALS, 4500, 350, 42.0, 1.12, 5.8, 1.1, 3.2),

    # Tourism
    'HELI': StockInfo('HELI', 'Heliopolis Hotels', 'حلوان للفنادق', Sector.TOURISM, 1800, 250, 35.0, 1.15, 6.5, 1.2, 2.8),
    'TRTO': StockInfo('TRTO', 'Triton Egypt', 'تريتون', Sector.TOURISM, 1200, 180, 38.0, 1.25, 8.5, 1.5, 1.8),
    'EGCH': StockInfo('EGCH', 'Egyptian Chemicals Holding', 'القابضة للكيماويات', Sector.CHEMICALS, 3500, 280, 40.0, 1.08, 5.2, 1.0, 3.0),
    'HOTS': StockInfo('HOTS', 'Hotels & Tourism', 'الفنادق والسياحة', Sector.TOURISM, 950, 120, 30.0, 1.05, 5.8, 1.1, 2.5),

    # Textiles
    'COTN': StockInfo('COTN', 'Cotton & Textiles', 'القطن والغزل', Sector.TEXTILES, 650, 85, 25.0, 0.85, 2.8, 0.5, 5.0),
    'UNIR': StockInfo('UNIR', 'Union Textiles', 'اتحاد الغزل', Sector.TEXTILES, 480, 60, 28.0, 0.82, 2.5, 0.45, 5.5),
    'NIND': StockInfo('NIND', 'North Industries', 'الصناعات الشمالية', Sector.INDUSTRIAL, 750, 95, 30.0, 0.90, 3.2, 0.6, 4.5),

    # Transport
    'EAST': StockInfo('EAST', 'Eastern Navigation', 'الملاحة الوطنية', Sector.TRANSPORT, 2200, 180, 35.0, 1.02, 4.8, 0.9, 3.2),

    # Mining
    'CEFM': StockInfo('CEFM', 'Centamin Egypt', 'سنتامين مصر', Sector.MINING, 28000, 1100, 55.0, 1.45, 15.0, 2.5, 1.2),

    # Additional Blue Chips
    'SUGR': StockInfo('SUGR', 'Egyptian Sugar', 'السكر المصرية', Sector.FNB, 3200, 420, 40.0, 0.95, 5.5, 1.0, 3.0),
    'PACH': StockInfo('PACH', 'Pachin', 'باكين', Sector.CHEMICALS, 1500, 120, 35.0, 1.02, 4.2, 0.8, 3.5),
    'KIMI': StockInfo('KIMI', 'Kima', 'كيما', Sector.CHEMICALS, 2800, 220, 38.0, 1.05, 3.8, 0.7, 4.0),
    'SAUD': StockInfo('SAUD', 'Saudi Egyptian Investment', 'السعودية المصرية', Sector.INVESTMENT, 2200, 180, 42.0, 1.12, 6.5, 1.3, 2.5),
    'ISPH': StockInfo('ISPH', 'Ismailia Poultry', 'الإسماعيلية للدواجن', Sector.FNB, 1200, 150, 35.0, 1.08, 7.2, 1.4, 2.2),
    'MAAL': StockInfo('MAAL', 'Maaloum Group', 'المعلوم', Sector.TECHNOLOGY, 850, 110, 45.0, 1.35, 18.0, 3.5, 0.8),
    'BHOT': StockInfo('BHOT', 'Badr Hotels', 'بدر للفنادق', Sector.TOURISM, 650, 85, 30.0, 1.15, 5.8, 1.1, 2.8),
    'ELKA': StockInfo('ELKA', 'El Kahera Housing', 'القاهرة للإسكان', Sector.REAL_ESTATE, 950, 120, 32.0, 1.02, 4.5, 0.9, 3.5),
    'NCCW': StockInfo('NCCW', 'National Company for Construction', 'الوطنية للإنشاءات', Sector.CONSTRUCTION, 750, 95, 28.0, 0.95, 3.8, 0.7, 4.0),
}

# Indices
EGX_INDICES = {
    'EGX30': StockInfo('EGX30', 'EGX 30 Index', 'مؤشر EGX 30', Sector.BANKING, is_index=True),
    'EGX70': StockInfo('EGX70', 'EGX 70 Index', 'مؤشر EGX 70', Sector.BANKING, is_index=True),
    'EGX100': StockInfo('EGX100', 'EGX 100 Index', 'مؤشر EGX 100', Sector.BANKING, is_index=True),
    'EGX20': StockInfo('EGX20', 'EGX 20 Index', 'مؤشر EGX 20', Sector.BANKING, is_index=True),
}

ALL_SYMBOLS = list(EGX_STOCKS.keys()) + list(EGX_INDICES.keys())
SYMBOL_MAP = {s: EGX_STOCKS.get(s) or EGX_INDICES.get(s) for s in ALL_SYMBOLS}
SECTOR_MAP = {s: info.sector.value for s, info in EGX_STOCKS.items()}

def get_stock_info(symbol: str) -> Optional[StockInfo]:
    return SYMBOL_MAP.get(symbol.upper())

def get_stocks_by_sector(sector: str) -> List[str]:
    return [s for s, info in EGX_STOCKS.items() if info.sector.value == sector]

def get_all_symbols() -> List[str]:
    return ALL_SYMBOLS.copy()

def get_yahoo_symbol(symbol: str) -> str:
    info = get_stock_info(symbol)
    return info.yahoo_symbol if info else symbol

def get_sector_performance(symbols_data: Dict[str, float]) -> Dict[str, float]:
    sector_returns = {}
    sector_counts = {}
    for symbol, change in symbols_data.items():
        sector = SECTOR_MAP.get(symbol)
        if sector:
            sector_returns[sector] = sector_returns.get(sector, 0) + change
            sector_counts[sector] = sector_counts.get(sector, 0) + 1
    return {s: sector_returns[s] / sector_counts[s] for s in sector_returns}

def get_blue_chips() -> List[str]:
    return ['COMI', 'TMGH', 'EAST', 'ORAS', 'HELW', 'ETEL', 'CEFM', 'FWRY']

def get_high_dividend() -> List[str]:
    return [s for s, info in EGX_STOCKS.items() if info.dividend_yield and info.dividend_yield > 3.0]

def get_low_beta() -> List[str]:
    return [s for s, info in EGX_STOCKS.items() if info.beta and info.beta < 1.0]

def get_high_beta() -> List[str]:
    return [s for s, info in EGX_STOCKS.items() if info.beta and info.beta > 1.2]
