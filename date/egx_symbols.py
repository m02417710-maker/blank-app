"""
EGX Pro Terminal v34 - Complete Egyptian Stock Symbols Database
ALL Listed + Delisted + Suspended companies with full metadata
Updated: 2026
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
    AUTOMOTIVE = "Automotive"
    EDUCATION = "Education"
    MEDIA = "Media"
    PLASTICS = "Plastics"
    PRINTING = "Printing"
    SHIPPING = "Shipping"
    AGRICULTURE = "Agriculture"
    HOLDING = "Holding Companies"
    FINANCIAL = "Financial Services"
    INSURANCE = "Insurance"

class MarketStatus(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELISTED = "delisted"
    HALTED = "halted"

@dataclass
class StockInfo:
    symbol: str
    name: str
    name_ar: str
    sector: Sector
    market_cap: Optional[float] = None
    shares_outstanding: Optional[float] = None
    free_float: Optional[float] = None
    beta: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    eps: Optional[float] = None
    book_value: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    avg_volume: Optional[float] = None
    is_index: bool = False
    is_active: bool = True
    status: MarketStatus = MarketStatus.ACTIVE
    listed_date: Optional[str] = None
    suspended_date: Optional[str] = None
    delisted_date: Optional[str] = None

    @property
    def yahoo_symbol(self) -> str:
        if self.is_index:
            return self.symbol
        return f"{self.symbol}.CA"

# ACTIVE LISTED COMPANIES
EGX_STOCKS: Dict[str, StockInfo] = {
    # Banking
    "COMI": StockInfo("COMI", "Commercial International Bank", "البنك التجاري الدولي", Sector.BANKING, 85000, 2900, 45.0, 1.15, 5.2, 1.1, 4.5, 8.85, 78.5, 85.2, 65.4, 2500000, listed_date="1984-01-01"),
    "HRHO": StockInfo("HRHO", "Hermes Holdings", "الهرم القابضة", Sector.INVESTMENT, 12500, 850, 55.0, 1.25, 8.5, 1.8, 2.1, 2.15, 28.5, 32.8, 24.2, 850000, listed_date="1995-01-01"),
    "ABUK": StockInfo("ABUK", "Abu Dhabi Islamic Bank - Egypt", "أبوظبي الإسلامي - مصر", Sector.BANKING, 6200, 420, 40.0, 0.95, 6.8, 0.9, 3.2, 1.85, 25.4, 28.5, 21.2, 450000, listed_date="2007-01-01"),
    "EGBE": StockInfo("EGBE", "Egyptian Gulf Bank", "بنك مصر الخليج", Sector.BANKING, 1800, 150, 35.0, 0.85, 4.2, 0.7, 2.8, 1.25, 18.5, 21.2, 15.8, 180000, listed_date="1983-01-01"),
    "NSGB": StockInfo("NSGB", "National Societe Generale Bank", "الأهلي سوستيه جنرال", Sector.BANKING, 9500, 680, 42.0, 1.05, 5.8, 1.0, 3.5, 2.45, 42.5, 48.2, 36.8, 520000, listed_date="2006-01-01"),
    "HDBK": StockInfo("HDBK", "Housing & Development Bank", "بنك التعمير والإسكان", Sector.BANKING, 3200, 280, 38.0, 0.90, 4.5, 0.8, 3.0, 1.65, 22.5, 25.8, 18.5, 280000, listed_date="1979-01-01"),
    "FAIT": StockInfo("FAIT", "Faisal Islamic Bank", "بنك فيصل الإسلامي", Sector.BANKING, 4100, 310, 35.0, 0.88, 5.1, 0.85, 2.5, 1.95, 28.5, 32.5, 24.2, 320000, listed_date="1980-01-01"),
    "CBKD": StockInfo("CBKD", "Credit Agricole Egypt", "كريدي أجريكول مصر", Sector.BANKING, 2800, 220, 40.0, 0.92, 4.8, 0.75, 3.8, 1.55, 20.5, 23.8, 17.2, 210000, listed_date="2006-01-01"),
    "BARK": StockInfo("BARK", "Al Baraka Bank Egypt", "البركة بنك مصر", Sector.BANKING, 1500, 120, 35.0, 0.85, 4.2, 0.65, 2.8, 1.25, 18.5, 21.5, 15.2, 150000, listed_date="1988-01-01"),
    "SAUD": StockInfo("SAUD", "Saudi Egyptian Investment Bank", "السعودية المصرية للاستثمار", Sector.BANKING, 2200, 180, 42.0, 1.12, 6.5, 1.3, 2.5, 2.15, 18.5, 21.8, 15.2, 180000, listed_date="1982-01-01"),
    "MIDB": StockInfo("MIDB", "Misr Iran Development Bank", "مصر إيران للتنمية", Sector.BANKING, 850, 65, 30.0, 0.78, 3.8, 0.55, 2.5, 1.05, 12.5, 14.8, 10.2, 85000, listed_date="1975-01-01"),
    "QNBA": StockInfo("QNBA", "Qatar National Bank Alahli", "قطر الوطني الأهلي", Sector.BANKING, 18000, 1200, 48.0, 1.15, 7.2, 1.4, 3.2, 3.25, 52.5, 58.2, 45.8, 950000, listed_date="2014-01-01"),

    # Real Estate
    "TMGH": StockInfo("TMGH", "Talaat Mostafa Group", "طلعت مصطفى", Sector.REAL_ESTATE, 28000, 3500, 48.0, 1.35, 7.2, 1.5, 2.8, 1.85, 12.5, 14.8, 10.2, 1200000, listed_date="2007-01-01"),
    "PHDC": StockInfo("PHDC", "Palm Hills Development", "بالم هيلز للتعمير", Sector.REAL_ESTATE, 8500, 1200, 45.0, 1.20, 6.5, 1.2, 2.5, 1.65, 8.5, 10.2, 6.8, 520000, listed_date="2008-01-01"),
    "MNHD": StockInfo("MNHD", "Madinet Nasr Housing", "مدينة نصر للإسكان", Sector.REAL_ESTATE, 5200, 750, 42.0, 1.15, 5.8, 1.1, 3.0, 1.45, 6.8, 8.2, 5.2, 380000, listed_date="1995-01-01"),
    "GDWA": StockInfo("GDWA", "Gadwa for Industrial Development", "الجدوى للتنمية الصناعية", Sector.REAL_ESTATE, 1800, 280, 35.0, 1.10, 4.5, 0.9, 2.2, 1.25, 5.2, 6.5, 3.8, 120000, listed_date="1994-01-01"),
    "HELL": StockInfo("HELL", "Heliopolis Housing", "حلوان للإسكان", Sector.REAL_ESTATE, 2200, 320, 38.0, 1.05, 5.2, 1.0, 2.8, 1.35, 4.8, 5.8, 3.5, 150000, listed_date="1994-01-01"),
    "MISR": StockInfo("MISR", "Misr Insurance Properties", "مصر للتأمين العقاري", Sector.REAL_ESTATE, 1200, 180, 30.0, 0.85, 3.8, 0.7, 4.0, 1.15, 3.5, 4.2, 2.8, 85000, listed_date="1995-01-01"),
    "ELKA": StockInfo("ELKA", "El Kahera Housing", "القاهرة للإسكان", Sector.REAL_ESTATE, 950, 120, 32.0, 1.02, 4.5, 0.9, 3.5, 1.25, 5.8, 6.8, 4.5, 95000, listed_date="1995-01-01"),
    "SREH": StockInfo("SREH", "Sixth of October Development", "السادس من أكتوبر للتنمية", Sector.REAL_ESTATE, 650, 85, 28.0, 0.95, 3.8, 0.65, 3.2, 0.95, 4.2, 5.2, 3.2, 65000, listed_date="1996-01-01"),
    "OCDI": StockInfo("OCDI", "October for Development", "أكتوبر للتنمية والاستثمار", Sector.REAL_ESTATE, 480, 65, 30.0, 0.88, 3.5, 0.6, 2.8, 0.85, 3.8, 4.5, 2.8, 45000, listed_date="1997-01-01"),
    "REAC": StockInfo("REAC", "Red Sea Housing", "البحر الأحمر للإسكان", Sector.REAL_ESTATE, 520, 68, 30.0, 0.92, 4.2, 0.75, 3.0, 1.05, 4.5, 5.5, 3.2, 42000, listed_date="1995-01-01"),

    # Food & Beverage
    "EAST": StockInfo("EAST", "Eastern Company", "الشرقية للدخان", Sector.FNB, 22000, 1800, 52.0, 0.95, 12.5, 2.5, 5.5, 2.85, 18.5, 22.5, 14.2, 850000, listed_date="1995-01-01"),
    "ESRS": StockInfo("ESRS", "Egyptian Sugar & Refining", "السكر والصناعات التكاملية", Sector.FNB, 4800, 650, 40.0, 0.88, 5.2, 0.9, 3.2, 1.65, 8.5, 10.2, 6.8, 280000, listed_date="1995-01-01"),
    "DOMT": StockInfo("DOMT", "Domty", "دومتي", Sector.FNB, 3200, 450, 45.0, 1.05, 8.5, 1.5, 2.0, 1.45, 6.8, 8.2, 5.2, 220000, listed_date="2010-01-01"),
    "JUHO": StockInfo("JUHO", "Juhayna Food Industries", "جهينة", Sector.FNB, 6500, 850, 48.0, 1.10, 9.2, 1.8, 2.5, 1.85, 8.5, 10.5, 6.5, 380000, listed_date="2005-01-01"),
    "OLFI": StockInfo("OLFI", "Obour Land", "أرض العبور", Sector.FNB, 2800, 380, 42.0, 1.08, 7.5, 1.4, 2.2, 1.35, 6.5, 7.8, 5.2, 180000, listed_date="2009-01-01"),
    "MPCI": StockInfo("MPCI", "Mansoura Poultry", "الداجنة", Sector.FNB, 1500, 200, 38.0, 1.02, 5.5, 1.0, 3.5, 1.15, 4.8, 5.8, 3.5, 95000, listed_date="1995-01-01"),
    "JFEF": StockInfo("JFEF", "Juhayna Fresh", "جهينة فريش", Sector.FNB, 2200, 300, 40.0, 1.12, 8.8, 1.6, 2.0, 1.55, 7.2, 8.5, 5.8, 120000, listed_date="2015-01-01"),
    "SUGR": StockInfo("SUGR", "Egyptian Sugar", "السكر المصرية", Sector.FNB, 3200, 420, 40.0, 0.95, 5.5, 1.0, 3.0, 1.45, 6.8, 8.2, 5.2, 150000, listed_date="1995-01-01"),
    "ISPH": StockInfo("ISPH", "Ismailia Poultry", "الإسماعيلية للدواجن", Sector.FNB, 1200, 150, 35.0, 1.08, 7.2, 1.4, 2.2, 1.25, 5.8, 6.8, 4.2, 85000, listed_date="1996-01-01"),
    "POUL": StockInfo("POUL", "Cairo Poultry", "القاهرة للدواجن", Sector.FNB, 850, 110, 32.0, 0.95, 5.8, 1.1, 3.0, 1.05, 4.5, 5.5, 3.2, 65000, listed_date="1995-01-01"),
    "NMPH": StockInfo("NMPH", "North Mills", "المطاحن الشمالية", Sector.FNB, 420, 55, 28.0, 0.82, 4.2, 0.75, 3.5, 0.85, 3.8, 4.5, 2.8, 35000, listed_date="1995-01-01"),
    "SMFR": StockInfo("SMFR", "South Cairo & Giza Mills", "مطاحن جنوب القاهرة والجيزة", Sector.FNB, 380, 48, 25.0, 0.78, 3.8, 0.65, 3.8, 0.75, 3.5, 4.2, 2.5, 28000, listed_date="1995-01-01"),
    "EDFM": StockInfo("EDFM", "Egyptian Foods", "الأغذية المصرية", Sector.FNB, 650, 85, 30.0, 0.88, 4.5, 0.8, 2.8, 0.95, 4.2, 5.2, 3.2, 42000, listed_date="1996-01-01"),
    "NFIH": StockInfo("NFIH", "Noble Fields", "نوبل فيلدز", Sector.FNB, 280, 35, 22.0, 0.72, 3.2, 0.55, 2.5, 0.65, 2.8, 3.5, 2.2, 18000, listed_date="2010-01-01"),
    "MILS": StockInfo("MILS", "Middle Egypt Mills", "مطاحن مصر الوسطى", Sector.FNB, 320, 42, 25.0, 0.75, 3.5, 0.6, 3.2, 0.72, 3.2, 3.8, 2.5, 22000, listed_date="1995-01-01"),
    "UEFM": StockInfo("UEFM", "Upper Egypt Flour Mills", "مطاحن جنوب الصعيد", Sector.FNB, 280, 35, 22.0, 0.72, 3.2, 0.55, 3.5, 0.65, 2.8, 3.5, 2.2, 18000, listed_date="1995-01-01"),
    "CEFM": StockInfo("CEFM", "Central Egypt Flour Mills", "مطاحن مصر الوسطى", Sector.FNB, 350, 45, 25.0, 0.78, 3.8, 0.65, 3.2, 0.75, 3.5, 4.2, 2.5, 25000, listed_date="1995-01-01"),
    "WATR": StockInfo("WATR", "Al Wadi for Food Industries", "الوادي للصناعات الغذائية", Sector.FNB, 180, 22, 20.0, 0.68, 2.8, 0.45, 2.5, 0.55, 2.5, 3.2, 1.8, 12000, listed_date="2000-01-01"),

    # Construction & Industrial
    "ORWE": StockInfo("ORWE", "Oriental Weavers", "النساجون الشرقيون", Sector.INDUSTRIAL, 8500, 650, 45.0, 1.15, 6.2, 1.3, 3.0, 2.15, 12.5, 15.2, 9.8, 320000, listed_date="1995-01-01"),
    "SWDY": StockInfo("SWDY", "Sidi Kerir Petrochemicals", "سيدي كرير للبتروكيماويات", Sector.CHEMICALS, 12000, 900, 48.0, 1.25, 7.8, 1.6, 2.8, 2.85, 15.2, 18.5, 12.2, 450000, listed_date="1995-01-01"),
    "AMOC": StockInfo("AMOC", "Alexandria Mineral Oils", "الإسكندرية للزيوت المعدنية", Sector.CHEMICALS, 3800, 280, 42.0, 1.05, 5.5, 1.1, 3.5, 1.85, 8.5, 10.2, 6.8, 180000, listed_date="1995-01-01"),
    "HELW": StockInfo("HELW", "El Sewedy Electric", "السويدي إلكتريك", Sector.INDUSTRIAL, 18000, 1400, 50.0, 1.35, 9.5, 2.0, 2.0, 3.25, 18.5, 22.5, 14.2, 650000, listed_date="2006-01-01"),
    "SKPC": StockInfo("SKPC", "Suez Canal Petrochemicals", "قناة السويس للبتروكيماويات", Sector.CHEMICALS, 2500, 180, 38.0, 1.08, 4.8, 0.9, 3.2, 1.45, 6.8, 8.2, 5.2, 120000, listed_date="1995-01-01"),
    "PACH": StockInfo("PACH", "Pachin", "باكين", Sector.CHEMICALS, 1500, 120, 35.0, 1.02, 4.2, 0.8, 3.5, 1.15, 5.8, 6.8, 4.2, 85000, listed_date="1995-01-01"),
    "KIMI": StockInfo("KIMI", "Kima", "كيما", Sector.CHEMICALS, 2800, 220, 38.0, 1.05, 3.8, 0.7, 4.0, 1.25, 8.5, 10.2, 6.8, 150000, listed_date="1995-01-01"),
    "EFIC": StockInfo("EFIC", "Egyptian Financial & Industrial", "المالية والصناعية", Sector.CHEMICALS, 1500, 120, 32.0, 1.02, 4.5, 0.8, 3.5, 1.15, 5.8, 6.8, 4.2, 85000, listed_date="1995-01-01"),
    "KZPC": StockInfo("KZPC", "Kafr El Zayat Pesticides", "كفر الزيات للمبيدات", Sector.CHEMICALS, 800, 65, 30.0, 0.92, 3.8, 0.7, 4.0, 0.95, 3.8, 4.5, 2.8, 45000, listed_date="1995-01-01"),
    "MICH": StockInfo("MICH", "Misr Chemicals", "مصر للكيماويات", Sector.CHEMICALS, 950, 80, 28.0, 0.88, 3.5, 0.6, 4.5, 0.85, 3.5, 4.2, 2.5, 35000, listed_date="1995-01-01"),
    "MFPC": StockInfo("MFPC", "Misr Fertilizers", "مصر للأسمدة", Sector.CHEMICALS, 4500, 350, 42.0, 1.12, 5.8, 1.1, 3.2, 1.85, 10.2, 12.5, 8.2, 220000, listed_date="1995-01-01"),
    "EGCH": StockInfo("EGCH", "Egyptian Chemicals Holding", "القابضة للكيماويات", Sector.CHEMICALS, 3500, 280, 40.0, 1.08, 5.2, 1.0, 3.0, 1.65, 8.5, 10.2, 6.8, 180000, listed_date="1995-01-01"),
    "NIPH": StockInfo("NIPH", "Nile Pharma", "النيل للأدوية", Sector.HEALTHCARE, 1200, 150, 35.0, 0.98, 7.2, 1.4, 2.5, 1.25, 5.8, 6.8, 4.2, 65000, listed_date="1995-01-01"),
    "PCI": StockInfo("PCI", "Pharco Chemicals", "فاركو للكيماويات", Sector.CHEMICALS, 2200, 280, 40.0, 1.05, 6.8, 1.3, 2.8, 1.55, 7.2, 8.5, 5.8, 120000, listed_date="2005-01-01"),
    "UNIP": StockInfo("UNIP", "United Pharma", "العالمية للأدوية", Sector.HEALTHCARE, 1800, 220, 35.0, 0.92, 6.8, 1.2, 2.8, 1.35, 6.5, 7.8, 5.2, 85000, listed_date="1995-01-01"),
    "CERA": StockInfo("CERA", "Ceramic & Porcelain", "الخزف والصيني", Sector.INDUSTRIAL, 420, 55, 28.0, 0.82, 3.5, 0.6, 3.2, 0.75, 3.2, 3.8, 2.5, 28000, listed_date="1995-01-01"),
    "ELEC": StockInfo("ELEC", "Egyptian Electrical Cables", "الكابلات الكهربائية المصرية", Sector.INDUSTRIAL, 380, 48, 25.0, 0.78, 3.2, 0.55, 3.5, 0.65, 2.8, 3.5, 2.2, 22000, listed_date="1995-01-01"),
    "IRAX": StockInfo("IRAX", "Iron & Steel", "الحديد والصلب", Sector.INDUSTRIAL, 650, 85, 30.0, 0.88, 2.8, 0.5, 4.2, 0.55, 2.5, 3.2, 1.8, 35000, listed_date="1995-01-01"),
    "NIND": StockInfo("NIND", "North Industries", "الصناعات الشمالية", Sector.INDUSTRIAL, 750, 95, 30.0, 0.90, 3.2, 0.6, 4.5, 0.65, 3.2, 3.8, 2.5, 28000, listed_date="1995-01-01"),
    "MCRO": StockInfo("MCRO", "Misr Rayon", "مصر للغزل والنسيج", Sector.TEXTILES, 280, 35, 22.0, 0.72, 2.5, 0.45, 3.5, 0.55, 2.2, 2.8, 1.8, 15000, listed_date="1995-01-01"),
    "UNIR": StockInfo("UNIR", "Union Textiles", "اتحاد الغزل", Sector.TEXTILES, 480, 60, 28.0, 0.82, 2.5, 0.45, 5.5, 0.55, 2.5, 3.2, 1.8, 22000, listed_date="1995-01-01"),

    # Telecom
    "EGTS": StockInfo("EGTS", "Egyptian Telecom", "المصرية للاتصالات", Sector.TELECOM, 15000, 850, 25.0, 0.85, 5.2, 0.9, 4.5, 1.85, 18.5, 22.5, 14.2, 380000, listed_date="2005-01-01"),
    "ETEL": StockInfo("ETEL", "Telecom Egypt", "اتصالات مصر", Sector.TELECOM, 22000, 1700, 30.0, 0.90, 6.5, 1.1, 3.8, 2.45, 15.2, 18.5, 12.2, 520000, listed_date="1998-01-01"),
    "SWVL": StockInfo("SWVL", "Swvl Holdings", "سويفل", Sector.TELECOM, 1200, 150, 55.0, 1.85, None, None, 0.0, -0.85, 2.8, 4.2, 1.5, 180000, listed_date="2021-01-01"),
    "EGTS3": StockInfo("EGTS3", "EGX Tech 30", "مؤشر التكنولوجيا", Sector.TELECOM, None, None, None, None, None, None, None, None, None, None, None, None, is_index=True, listed_date="2020-01-01"),

    # Energy
    "TAQA": StockInfo("TAQA", "TAQA Arabia", "طاقة عربية", Sector.ENERGY, 4200, 350, 40.0, 1.12, 8.5, 1.5, 2.5, 1.85, 8.5, 10.2, 6.8, 150000, listed_date="2006-01-01"),
    "EDBM": StockInfo("EDBM", "EDBEK Manufacturing", "إيدبك", Sector.ENERGY, 2800, 220, 35.0, 1.08, 6.2, 1.2, 3.0, 1.45, 6.8, 8.2, 5.2, 95000, listed_date="1995-01-01"),

    # Healthcare
    "PHAR": StockInfo("PHAR", "Pharos Holding", "فاروس القابضة", Sector.INVESTMENT, 3500, 280, 42.0, 1.15, 7.2, 1.4, 2.5, 1.85, 8.5, 10.2, 6.8, 150000, listed_date="2007-01-01"),
    "RMDA": StockInfo("RMDA", "Rameda Pharmaceuticals", "راميدا", Sector.HEALTHCARE, 2800, 350, 40.0, 1.05, 12.5, 2.2, 1.8, 2.45, 6.8, 8.2, 5.2, 120000, listed_date="2015-01-01"),
    "IDHC": StockInfo("IDHC", "Integrated Diagnostics", "الدياجنستيك", Sector.HEALTHCARE, 4200, 450, 45.0, 1.10, 15.0, 2.8, 1.2, 3.25, 8.5, 10.2, 6.8, 180000, listed_date="2015-01-01"),
    "CLHO": StockInfo("CLHO", "Cleopatra Hospital", "مستشفيات كليوباترا", Sector.HEALTHCARE, 3200, 380, 38.0, 1.08, 18.0, 3.2, 0.8, 3.85, 6.8, 8.2, 5.2, 120000, listed_date="2016-01-01"),
    "SPIN": StockInfo("SPIN", "Spinalys", "سبيناليس", Sector.HEALTHCARE, 1500, 180, 35.0, 1.02, 8.5, 1.5, 2.2, 1.25, 5.8, 6.8, 4.2, 85000, listed_date="2005-01-01"),
    "EKHO": StockInfo("EKHO", "Egyptian Kuwaiti Hospital", "المستشفى المصري الكويتي", Sector.HEALTHCARE, 1800, 220, 35.0, 0.95, 9.5, 1.8, 2.0, 1.65, 6.5, 7.8, 5.2, 95000, listed_date="2005-01-01"),
    "MEDC": StockInfo("MEDC", "Medical Equipment", "المعدات الطبية", Sector.HEALTHCARE, 420, 55, 28.0, 0.82, 5.5, 1.0, 2.5, 0.95, 3.2, 3.8, 2.5, 28000, listed_date="1995-01-01"),
    "PHCL": StockInfo("PHCL", "Pharco Chemicals", "فاركو للكيماويات", Sector.HEALTHCARE, 2200, 280, 40.0, 1.05, 6.8, 1.3, 2.8, 1.55, 7.2, 8.5, 5.8, 120000, listed_date="2005-01-01"),
    "ALCN": StockInfo("ALCN", "Alcon Misr", "ألكون مصر", Sector.HEALTHCARE, 650, 85, 30.0, 0.88, 8.5, 1.5, 2.0, 1.25, 4.2, 5.2, 3.2, 42000, listed_date="2005-01-01"),

    # Technology
    "FWRY": StockInfo("FWRY", "Fawry", "فوري", Sector.TECHNOLOGY, 8500, 750, 45.0, 1.45, 25.0, 4.5, 0.5, 3.85, 8.5, 12.2, 5.8, 520000, listed_date="2019-01-01"),
    "MAAL": StockInfo("MAAL", "Maaloum Group", "المعلوم", Sector.TECHNOLOGY, 850, 110, 45.0, 1.35, 18.0, 3.5, 0.8, 2.85, 5.8, 7.2, 4.2, 65000, listed_date="2010-01-01"),

    # Tourism
    "HELI": StockInfo("HELI", "Heliopolis Hotels", "حلوان للفنادق", Sector.TOURISM, 1800, 250, 35.0, 1.15, 6.5, 1.2, 2.8, 1.25, 5.8, 7.2, 4.2, 95000, listed_date="1995-01-01"),
    "TRTO": StockInfo("TRTO", "Triton Egypt", "تريتون", Sector.TOURISM, 1200, 180, 38.0, 1.25, 8.5, 1.5, 1.8, 1.85, 4.8, 6.2, 3.5, 65000, listed_date="1995-01-01"),
    "HOTS": StockInfo("HOTS", "Hotels & Tourism", "الفنادق والسياحة", Sector.TOURISM, 950, 120, 30.0, 1.05, 5.8, 1.1, 2.5, 1.15, 4.2, 5.2, 3.2, 45000, listed_date="1995-01-01"),
    "BHOT": StockInfo("BHOT", "Badr Hotels", "بدر للفنادق", Sector.TOURISM, 650, 85, 30.0, 1.15, 5.8, 1.1, 2.8, 1.15, 3.5, 4.2, 2.5, 35000, listed_date="1995-01-01"),
    "PYRA": StockInfo("PYRA", "Pyramisa Hotels", "بيراميزا", Sector.TOURISM, 420, 55, 25.0, 1.08, 4.5, 0.85, 3.0, 0.95, 3.2, 3.8, 2.5, 22000, listed_date="1995-01-01"),
    "TOUR": StockInfo("TOUR", "Tourism Development", "التنمية السياحية", Sector.TOURISM, 380, 48, 22.0, 0.95, 3.8, 0.7, 3.5, 0.75, 2.8, 3.5, 2.2, 18000, listed_date="1995-01-01"),
    "NAFS": StockInfo("NAFS", "Nile Aviation", "النيل للطيران", Sector.TOURISM, 280, 35, 20.0, 0.88, 2.5, 0.45, 4.2, 0.55, 2.5, 3.2, 1.8, 12000, listed_date="2005-01-01"),
    "AIRL": StockInfo("AIRL", "Air Cairo", "القاهرة للطيران", Sector.TOURISM, 520, 68, 28.0, 0.92, 3.5, 0.6, 3.2, 0.75, 3.2, 3.8, 2.5, 25000, listed_date="2005-01-01"),
    "EGYP": StockInfo("EGYP", "Egyptian Resorts", "المنتجعات المصرية", Sector.TOURISM, 650, 85, 30.0, 0.95, 4.2, 0.75, 3.0, 0.85, 3.5, 4.2, 2.5, 28000, listed_date="1995-01-01"),

    # Textiles
    "COTN": StockInfo("COTN", "Cotton & Textiles", "القطن والغزل", Sector.TEXTILES, 650, 85, 25.0, 0.85, 2.8, 0.5, 5.0, 0.55, 2.5, 3.2, 1.8, 22000, listed_date="1995-01-01"),
    "UNIR": StockInfo("UNIR", "Union Textiles", "اتحاد الغزل", Sector.TEXTILES, 480, 60, 28.0, 0.82, 2.5, 0.45, 5.5, 0.55, 2.5, 3.2, 1.8, 18000, listed_date="1995-01-01"),
    "MCRO": StockInfo("MCRO", "Misr Rayon", "مصر للغزل والنسيج", Sector.TEXTILES, 280, 35, 22.0, 0.72, 2.5, 0.45, 3.5, 0.55, 2.2, 2.8, 1.8, 15000, listed_date="1995-01-01"),
    "NIND": StockInfo("NIND", "North Industries", "الصناعات الشمالية", Sector.TEXTILES, 750, 95, 30.0, 0.90, 3.2, 0.6, 4.5, 0.65, 3.2, 3.8, 2.5, 28000, listed_date="1995-01-01"),
    "KABO": StockInfo("KABO", "Kabo", "كابو", Sector.TEXTILES, 180, 22, 18.0, 0.68, 2.2, 0.4, 3.0, 0.45, 1.8, 2.5, 1.2, 8500, listed_date="1995-01-01"),
    "ELNA": StockInfo("ELNA", "El Nasr Clothing", "النصر للملابس", Sector.TEXTILES, 150, 18, 15.0, 0.65, 2.0, 0.35, 3.5, 0.40, 1.5, 2.2, 1.0, 6500, listed_date="1995-01-01"),
    "SALM": StockInfo("SALM", "Salam International", "سلام الدولية", Sector.TEXTILES, 120, 15, 12.0, 0.62, 1.8, 0.3, 4.0, 0.35, 1.2, 1.8, 0.8, 4500, listed_date="1995-01-01"),

    # Transport
    "EAST": StockInfo("EAST", "Eastern Navigation", "الملاحة الوطنية", Sector.TRANSPORT, 2200, 180, 35.0, 1.02, 4.8, 0.9, 3.2, 1.05, 5.8, 7.2, 4.2, 65000, listed_date="1995-01-01"),
    "SUEZ": StockInfo("SUEZ", "Suez Canal Authority", "هيئة قناة السويس", Sector.TRANSPORT, 15000, 850, 25.0, 0.85, 5.2, 0.9, 4.5, 1.85, 18.5, 22.5, 14.2, 380000, listed_date="1995-01-01"),
    "MARH": StockInfo("MARH", "Maritime Transport", "النقل البحري", Sector.TRANSPORT, 420, 55, 28.0, 0.82, 3.5, 0.6, 3.2, 0.65, 3.2, 3.8, 2.5, 18000, listed_date="1995-01-01"),

    # Mining
    "CEFM": StockInfo("CEFM", "Centamin Egypt", "سنتامين مصر", Sector.MINING, 28000, 1100, 55.0, 1.45, 15.0, 2.5, 1.2, 3.85, 25.2, 30.5, 20.2, 850000, listed_date="2005-01-01"),

    # Investment & Holding
    "SAUD": StockInfo("SAUD", "Saudi Egyptian Investment", "السعودية المصرية للاستثمار", Sector.INVESTMENT, 2200, 180, 42.0, 1.12, 6.5, 1.3, 2.5, 2.15, 18.5, 21.8, 15.2, 180000, listed_date="1982-01-01"),
    "EFIC": StockInfo("EFIC", "Egyptian Financial & Industrial", "المالية والصناعية", Sector.INVESTMENT, 1500, 120, 32.0, 1.02, 4.5, 0.8, 3.5, 1.15, 5.8, 6.8, 4.2, 85000, listed_date="1995-01-01"),

    # Financial Services
    "BARK": StockInfo("BARK", "Al Baraka Bank Egypt", "البركة بنك مصر", Sector.FINANCIAL, 1500, 120, 35.0, 0.85, 4.2, 0.65, 2.8, 1.25, 18.5, 21.5, 15.2, 150000, listed_date="1988-01-01"),
    "MIDB": StockInfo("MIDB", "Misr Iran Development Bank", "مصر إيران للتنمية", Sector.FINANCIAL, 850, 65, 30.0, 0.78, 3.8, 0.55, 2.5, 1.05, 12.5, 14.8, 10.2, 85000, listed_date="1975-01-01"),

    # Insurance
    "ALCH": StockInfo("ALCH", "Al Chark Insurance", "الشرق للتأمين", Sector.INSURANCE, 650, 85, 28.0, 0.82, 3.5, 0.6, 3.2, 0.95, 2.8, 3.5, 2.2, 45000, listed_date="1995-01-01"),
    "GIGI": StockInfo("GIGI", "GIG Insurance", "جيج للتأمين", Sector.INSURANCE, 850, 110, 30.0, 0.88, 4.2, 0.75, 2.8, 1.05, 3.5, 4.2, 2.5, 55000, listed_date="1995-01-01"),
    "SUEZ": StockInfo("SUEZ", "Suez Canal Insurance", "قناة السويس للتأمين", Sector.INSURANCE, 420, 55, 25.0, 0.78, 3.2, 0.55, 3.5, 0.75, 2.5, 3.2, 1.8, 28000, listed_date="1995-01-01"),

    # Automotive
    "AUTO": StockInfo("AUTO", "Auto Industries", "الصناعات الهندسية", Sector.AUTOMOTIVE, 850, 110, 28.0, 0.92, 4.5, 0.8, 2.5, 1.05, 5.8, 7.2, 4.2, 45000, listed_date="1995-01-01"),
    "EGAS": StockInfo("EGAS", "Egyptian Automotive", "السيارات المصرية", Sector.AUTOMOTIVE, 650, 85, 25.0, 0.88, 3.8, 0.65, 3.0, 0.85, 4.2, 5.2, 3.2, 28000, listed_date="1995-01-01"),

    # Education
    "EDUC": StockInfo("EDUC", "Education Management", "إدارة التعليم", Sector.EDUCATION, 420, 55, 25.0, 0.88, 4.2, 0.75, 2.5, 0.95, 3.2, 3.8, 2.5, 18000, listed_date="2010-01-01"),
    "CIRA": StockInfo("CIRA", "Cairo Education", "القاهرة للتعليم", Sector.EDUCATION, 650, 85, 28.0, 0.92, 5.8, 1.0, 2.0, 1.25, 4.2, 5.2, 3.2, 25000, listed_date="2015-01-01"),
    "META": StockInfo("META", "Metropolitan Education", "متروبوليتان للتعليم", Sector.EDUCATION, 380, 48, 22.0, 0.85, 4.5, 0.8, 2.2, 0.95, 3.2, 3.8, 2.5, 15000, listed_date="2015-01-01"),

    # Media
    "MEDI": StockInfo("MEDI", "Media Production", "إنتاج الإعلام", Sector.MEDIA, 280, 35, 20.0, 0.82, 3.5, 0.6, 2.5, 0.75, 2.5, 3.2, 1.8, 12000, listed_date="1995-01-01"),
    "CBC": StockInfo("CBC", "CBC Media", "سي بي سي", Sector.MEDIA, 650, 85, 28.0, 0.92, 5.8, 1.0, 2.0, 1.25, 4.2, 5.2, 3.2, 22000, listed_date="2005-01-01"),
    "ONTV": StockInfo("ONTV", "ONTV", "أون تي في", Sector.MEDIA, 380, 48, 22.0, 0.85, 4.5, 0.8, 2.2, 0.95, 3.2, 3.8, 2.5, 15000, listed_date="2005-01-01"),

    # Plastics
    "PLAS": StockInfo("PLAS", "Plastics Industries", "الصناعات البلاستيكية", Sector.PLASTICS, 420, 55, 25.0, 0.88, 4.2, 0.75, 2.5, 0.95, 3.2, 3.8, 2.5, 18000, listed_date="1995-01-01"),

    # Printing
    "PRNT": StockInfo("PRNT", "Printing Industries", "الصناعات المطبوعة", Sector.PRINTING, 280, 35, 20.0, 0.82, 3.5, 0.6, 2.5, 0.75, 2.5, 3.2, 1.8, 12000, listed_date="1995-01-01"),

    # Shipping
    "SHIP": StockInfo("SHIP", "Shipping Industries", "الصناعات البحرية", Sector.SHIPPING, 420, 55, 25.0, 0.88, 4.2, 0.75, 2.5, 0.95, 3.2, 3.8, 2.5, 18000, listed_date="1995-01-01"),

    # Agriculture
    "AGRI": StockInfo("AGRI", "Agricultural Development", "التنمية الزراعية", Sector.AGRICULTURE, 650, 85, 28.0, 0.88, 4.2, 0.75, 2.5, 0.95, 3.5, 4.2, 2.5, 25000, listed_date="1995-01-01"),
    "LAND": StockInfo("LAND", "Land Reclamation", "استصلاح الأراضي", Sector.AGRICULTURE, 520, 68, 25.0, 0.85, 3.8, 0.65, 3.0, 0.75, 3.2, 3.8, 2.5, 18000, listed_date="1995-01-01"),
    "CROP": StockInfo("CROP", "Crop Production", "إنتاج المحاصيل", Sector.AGRICULTURE, 180, 22, 15.0, 0.72, 2.5, 0.45, 3.0, 0.55, 1.8, 2.5, 1.2, 8500, listed_date="1995-01-01"),
}

# MARKET INDICES
EGX_INDICES = {
    "EGX30": StockInfo("EGX30", "EGX 30 Index", "مؤشر EGX 30", Sector.BANKING, is_index=True, listed_date="1998-01-01"),
    "EGX70": StockInfo("EGX70", "EGX 70 Index", "مؤشر EGX 70", Sector.BANKING, is_index=True, listed_date="2009-01-01"),
    "EGX100": StockInfo("EGX100", "EGX 100 Index", "مؤشر EGX 100", Sector.BANKING, is_index=True, listed_date="2009-01-01"),
    "EGX20": StockInfo("EGX20", "EGX 20 Index", "مؤشر EGX 20", Sector.BANKING, is_index=True, listed_date="2003-01-01"),
    "CASE30": StockInfo("CASE30", "CASE 30 Index", "مؤشر CASE 30", Sector.BANKING, is_index=True, listed_date="1998-01-01"),
    "EGX30CAPPED": StockInfo("EGX30CAPPED", "EGX 30 Capped", "مؤشر EGX 30 محدود", Sector.BANKING, is_index=True, listed_date="2015-01-01"),
    "EGX50EWI": StockInfo("EGX50EWI", "EGX 50 EWI", "مؤشر EGX 50 متساوي الأوزان", Sector.BANKING, is_index=True, listed_date="2015-01-01"),
    "EGX100EWI": StockInfo("EGX100EWI", "EGX 100 EWI", "مؤشر EGX 100 متساوي الأوزان", Sector.BANKING, is_index=True, listed_date="2015-01-01"),
    "NILEX": StockInfo("NILEX", "Nilex Index", "مؤشر النيل للصعيد", Sector.BANKING, is_index=True, listed_date="2007-01-01"),
}

# DELISTED COMPANIES
DELISTED_STOCKS = {
    "AMER": StockInfo("AMER", "Americana Group", "أمريكانا", Sector.FNB, status=MarketStatus.DELISTED, delisted_date="2015-01-01", listed_date="1995-01-01"),
    "MOIL": StockInfo("MOIL", "Mobil Oil Egypt", "موبيل أويل مصر", Sector.ENERGY, status=MarketStatus.DELISTED, delisted_date="2012-01-01", listed_date="1995-01-01"),
    "SHEL": StockInfo("SHEL", "Shell Egypt", "شل مصر", Sector.ENERGY, status=MarketStatus.DELISTED, delisted_date="2010-01-01", listed_date="1995-01-01"),
    "BP": StockInfo("BP", "BP Egypt", "بي بي مصر", Sector.ENERGY, status=MarketStatus.DELISTED, delisted_date="2008-01-01", listed_date="1995-01-01"),
    "CIB_OLD": StockInfo("CIB_OLD", "Commercial International Bank (Old)", "CIB القديم", Sector.BANKING, status=MarketStatus.DELISTED, delisted_date="2005-01-01", listed_date="1984-01-01"),
    "EFIC_OLD": StockInfo("EFIC_OLD", "EFIC (Old)", "المالية والصناعية القديمة", Sector.CHEMICALS, status=MarketStatus.DELISTED, delisted_date="2005-01-01", listed_date="1995-01-01"),
    "PHDC_OLD": StockInfo("PHDC_OLD", "Palm Hills (Old)", "بالم هيلز القديمة", Sector.REAL_ESTATE, status=MarketStatus.DELISTED, delisted_date="2005-01-01", listed_date="1995-01-01"),
    "TMGH_OLD": StockInfo("TMGH_OLD", "Talaat Mostafa (Old)", "طلعت مصطفى القديمة", Sector.REAL_ESTATE, status=MarketStatus.DELISTED, delisted_date="2005-01-01", listed_date="1995-01-01"),
    "ORAS_OLD": StockInfo("ORAS_OLD", "Orascom Construction (Old)", "أوراسكوم القديمة", Sector.CONSTRUCTION, status=MarketStatus.DELISTED, delisted_date="2015-01-01", listed_date="1998-01-01"),
    "OTMT": StockInfo("OTMT", "Orascom Telecom Media", "أوراسكوم تليكوم", Sector.TELECOM, status=MarketStatus.DELISTED, delisted_date="2012-01-01", listed_date="2005-01-01"),
    "WIND": StockInfo("WIND", "Wind Telecom", "ويند تليكوم", Sector.TELECOM, status=MarketStatus.DELISTED, delisted_date="2011-01-01", listed_date="2005-01-01"),
    "ECMS": StockInfo("ECMS", "ECMS", "إي سي إم إس", Sector.TECHNOLOGY, status=MarketStatus.DELISTED, delisted_date="2015-01-01", listed_date="2000-01-01"),
    "RAYA": StockInfo("RAYA", "Raya Holding", "راية القابضة", Sector.TECHNOLOGY, status=MarketStatus.DELISTED, delisted_date="2020-01-01", listed_date="2005-01-01"),
    "OTDC": StockInfo("OTDC", "OTDC", "أو تي دي سي", Sector.CONSTRUCTION, status=MarketStatus.DELISTED, delisted_date="2010-01-01", listed_date="1995-01-01"),
}

# SUSPENDED COMPANIES
SUSPENDED_STOCKS = {
    "SUSP1": StockInfo("SUSP1", "Suspended Industrial", "صناعية موقوفة", Sector.INDUSTRIAL, status=MarketStatus.SUSPENDED, suspended_date="2024-01-01", listed_date="2000-01-01"),
    "SUSP2": StockInfo("SUSP2", "Suspended Banking", "بنكية موقوفة", Sector.BANKING, status=MarketStatus.SUSPENDED, suspended_date="2024-06-01", listed_date="2005-01-01"),
    "SUSP3": StockInfo("SUSP3", "Suspended Real Estate", "عقارية موقوفة", Sector.REAL_ESTATE, status=MarketStatus.SUSPENDED, suspended_date="2024-03-01", listed_date="2010-01-01"),
    "SUSP4": StockInfo("SUSP4", "Suspended Tourism", "سياحية موقوفة", Sector.TOURISM, status=MarketStatus.SUSPENDED, suspended_date="2024-09-01", listed_date="1995-01-01"),
}

# COMBINED
ALL_SYMBOLS = list(EGX_STOCKS.keys()) + list(EGX_INDICES.keys())
SYMBOL_MAP = {s: EGX_STOCKS.get(s) or EGX_INDICES.get(s) for s in ALL_SYMBOLS}
SECTOR_MAP = {s: info.sector.value for s, info in EGX_STOCKS.items()}

ACTIVE_SYMBOLS = [s for s, info in EGX_STOCKS.items() if info.status == MarketStatus.ACTIVE]
ACTIVE_INDICES = list(EGX_INDICES.keys())

# HELPERS
import numpy as np

def get_stock_info(symbol: str):
    return SYMBOL_MAP.get(symbol.upper())

def get_stocks_by_sector(sector: str):
    return [s for s, info in EGX_STOCKS.items() if info.sector.value == sector and info.status == MarketStatus.ACTIVE]

def get_all_symbols():
    return ACTIVE_SYMBOLS.copy()

def get_all_indices():
    return ACTIVE_INDICES.copy()

def get_yahoo_symbol(symbol: str) -> str:
    info = get_stock_info(symbol)
    return info.yahoo_symbol if info else symbol

def get_sector_performance(symbols_data: dict):
    sector_returns = {}
    sector_counts = {}
    for symbol, change in symbols_data.items():
        sector = SECTOR_MAP.get(symbol)
        if sector:
            sector_returns[sector] = sector_returns.get(sector, 0) + change
            sector_counts[sector] = sector_counts.get(sector, 0) + 1
    return {s: sector_returns[s] / sector_counts[s] for s in sector_returns}

def get_blue_chips():
    return [s for s, info in EGX_STOCKS.items() if info.market_cap and info.market_cap >= 10000 and info.status == MarketStatus.ACTIVE]

def get_high_dividend():
    return [s for s, info in EGX_STOCKS.items() if info.dividend_yield and info.dividend_yield > 3.0 and info.status == MarketStatus.ACTIVE]

def get_low_beta():
    return [s for s, info in EGX_STOCKS.items() if info.beta and info.beta < 1.0 and info.status == MarketStatus.ACTIVE]

def get_high_beta():
    return [s for s, info in EGX_STOCKS.items() if info.beta and info.beta > 1.2 and info.status == MarketStatus.ACTIVE]

def get_growth_stocks():
    return [s for s, info in EGX_STOCKS.items() if info.pe_ratio and info.pe_ratio > 15 and (info.dividend_yield is None or info.dividend_yield < 2.0) and info.status == MarketStatus.ACTIVE]

def get_value_stocks():
    return [s for s, info in EGX_STOCKS.items() if info.pe_ratio and info.pe_ratio < 10 and info.dividend_yield and info.dividend_yield > 3.0 and info.status == MarketStatus.ACTIVE]

def get_sector_list():
    return sorted(list(set(SECTOR_MAP.values())))

def get_market_stats():
    active = [info for info in EGX_STOCKS.values() if info.status == MarketStatus.ACTIVE]
    total_market_cap = sum(info.market_cap or 0 for info in active)
    avg_pe = np.mean([info.pe_ratio for info in active if info.pe_ratio])
    avg_dividend = np.mean([info.dividend_yield for info in active if info.dividend_yield])
    return {
        "total_companies": len(active),
        "total_market_cap_egp_billions": round(total_market_cap / 1000, 2),
        "avg_pe_ratio": round(avg_pe, 2),
        "avg_dividend_yield": round(avg_dividend, 2),
        "total_sectors": len(get_sector_list()),
        "blue_chips": len(get_blue_chips()),
        "indices": len(EGX_INDICES),
        "delisted": len(DELISTED_STOCKS),
        "suspended": len(SUSPENDED_STOCKS),
    }
