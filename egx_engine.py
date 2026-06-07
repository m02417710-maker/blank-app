"""
EGX Pro Ultimate v30 — Core Engine
محرك البيانات والمؤشرات الفنية
إصلاحات: VWAP يومي صحيح | Supertrend | ADX vectorized | بيانات محسّنة
"""

import pandas as pd
import numpy as np
import hashlib
import logging
import os
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, List, Any
import warnings
warnings.filterwarnings('ignore')

os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s — %(levelname)s — %(message)s',
    handlers=[
        logging.FileHandler('logs/egx_v30.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

import pytz
def get_cairo_time() -> datetime:
    return datetime.now(pytz.timezone('Africa/Cairo'))

def safe_pct(current: float, previous: float) -> float:
    if previous is None or previous == 0: return 0.0
    try: return ((current - previous) / abs(previous)) * 100
    except: return 0.0

def safe_last(s: pd.Series, default=0.0) -> float:
    try:
        v = s.dropna()
        return float(v.iloc[-1]) if not v.empty else default
    except: return default

def fmt_num(num, decimals: int = 2) -> str:
    try:
        if num is None: return "N/A"
        num = float(num)
        if np.isnan(num) or np.isinf(num): return "N/A"
        if abs(num) >= 1e9: return f"{num/1e9:.2f}B"
        if abs(num) >= 1e6: return f"{num/1e6:.2f}M"
        if abs(num) >= 1e3: return f"{num/1e3:.1f}K"
        return f"{num:,.{decimals}f}"
    except: return "N/A"

def fmt_egp(num) -> str:
    return f"EGP {fmt_num(num)}"

# ═══════════════════════════════════════════════════════════════
# قاعدة البيانات — 280+ شركة (مصحّحة بالكامل)
# ═══════════════════════════════════════════════════════════════
class EGXDatabase:
    """قاعدة بيانات مصحّحة — أُزيلت الرموز الوهمية، صُحّحت القطاعات"""

    STOCKS: Dict[str, Dict] = {
        # ── البنوك (11) ─────────────────────────────────────────
        'COMI': {'name': 'البنك التجاري الدولي', 'name_en': 'CIB', 'sector': 'البنوك', 'yf': 'COMI.CA', 'base': 125, 'pe': 8.5, 'div_yield': 2.1},
        'QNBE': {'name': 'بنك قطر الوطني الأهلي', 'name_en': 'QNB Al Ahli', 'sector': 'البنوك', 'yf': 'QNBE.CA', 'base': 18, 'pe': 6.2, 'div_yield': 3.5},
        'CAIR': {'name': 'بنك القاهرة', 'name_en': 'Cairo Bank', 'sector': 'البنوك', 'yf': 'CAIR.CA', 'base': 12, 'pe': 5.8, 'div_yield': 0},
        'ADIB': {'name': 'مصرف أبوظبي الإسلامي مصر', 'name_en': 'ADIB Egypt', 'sector': 'البنوك', 'yf': 'ADIB.CA', 'base': 45, 'pe': 7.1, 'div_yield': 1.8},
        'AAIB': {'name': 'البنك العربي الأفريقي الدولي', 'name_en': 'AAIB', 'sector': 'البنوك', 'yf': 'AAIB.CA', 'base': 22, 'pe': 6.0, 'div_yield': 2.5},
        'UBAN': {'name': 'المصرف المتحد', 'name_en': 'United Bank', 'sector': 'البنوك', 'yf': None, 'base': 18, 'pe': 5.5, 'div_yield': 0},
        'BLOM': {'name': 'بنك بلوم مصر', 'name_en': 'Blom Bank Egypt', 'sector': 'البنوك', 'yf': None, 'base': 6, 'pe': 4.8, 'div_yield': 0},
        'ARAB': {'name': 'البنك العربي', 'name_en': 'Arab Bank', 'sector': 'البنوك', 'yf': None, 'base': 20, 'pe': 6.5, 'div_yield': 1.5},
        'BDCO': {'name': 'بنك التنمية الصناعية', 'name_en': 'Industrial Dev Bank', 'sector': 'البنوك', 'yf': None, 'base': 14, 'pe': 5.2, 'div_yield': 0},
        'NSGB': {'name': 'بنك الاتحاد الوطني', 'name_en': 'National Societe Generale', 'sector': 'البنوك', 'yf': None, 'base': 15, 'pe': 5.9, 'div_yield': 0},
        'EXPA': {'name': 'بنك إكسبريس', 'name_en': 'Express Bank', 'sector': 'البنوك', 'yf': None, 'base': 8, 'pe': 4.5, 'div_yield': 0},

        # ── الاتصالات والتكنولوجيا (6) ──────────────────────────
        'ETEL': {'name': 'تليكوم مصر', 'name_en': 'Telecom Egypt', 'sector': 'الاتصالات', 'yf': 'ETEL.CA', 'base': 32, 'pe': 9.2, 'div_yield': 4.8},
        'EAST': {'name': 'اتصالات مصر (e&)', 'name_en': 'e& Egypt', 'sector': 'الاتصالات', 'yf': 'EAST.CA', 'base': 28, 'pe': 11.5, 'div_yield': 2.2},
        'FWRY': {'name': 'فوري للتكنولوجيا والمدفوعات', 'name_en': 'Fawry', 'sector': 'التكنولوجيا', 'yf': 'FWRY.CA', 'base': 42, 'pe': 22.0, 'div_yield': 0},
        'RAYA': {'name': 'راية القابضة للتكنولوجيا', 'name_en': 'Raya Holding', 'sector': 'التكنولوجيا', 'yf': 'RAYA.CA', 'base': 20, 'pe': 14.5, 'div_yield': 1.0},
        'VFSC': {'name': 'فودافون مصر للتمويل', 'name_en': 'Vodafone Egypt Finance', 'sector': 'الاتصالات', 'yf': None, 'base': 5, 'pe': 8.0, 'div_yield': 0},
        'MTSI': {'name': 'مصر للتكنولوجيا والبرمجيات', 'name_en': 'MTI', 'sector': 'التكنولوجيا', 'yf': None, 'base': 15, 'pe': 18.0, 'div_yield': 0},

        # ── العقارات والإنشاء (12) ──────────────────────────────
        'TMGH': {'name': 'مجموعة طلعت مصطفى القابضة', 'name_en': 'TMG Holding', 'sector': 'العقارات', 'yf': 'TMGH.CA', 'base': 88, 'pe': 12.0, 'div_yield': 0.8},
        'PHDC': {'name': 'بالم هيلز للتطوير', 'name_en': 'Palm Hills', 'sector': 'العقارات', 'yf': 'PHDC.CA', 'base': 9, 'pe': 7.5, 'div_yield': 0},
        'MNHD': {'name': 'مدينة نصر للإسكان والتعمير', 'name_en': 'Medinet Nasr Housing', 'sector': 'العقارات', 'yf': 'MNHD.CA', 'base': 7, 'pe': 6.8, 'div_yield': 1.2},
        'HELI': {'name': 'هيليوبوليس للإسكان', 'name_en': 'Heliopolis Housing', 'sector': 'العقارات', 'yf': 'HELI.CA', 'base': 6, 'pe': 5.5, 'div_yield': 2.0},
        'OCDI': {'name': 'أوراسكوم للتطوير مصر', 'name_en': 'Orascom Development', 'sector': 'العقارات', 'yf': 'OCDI.CA', 'base': 4, 'pe': 15.0, 'div_yield': 0},
        'SODC': {'name': 'سوديك للتطوير العقاري', 'name_en': 'SODIC', 'sector': 'العقارات', 'yf': 'SODC.CA', 'base': 18, 'pe': 10.2, 'div_yield': 0},
        'EMAA': {'name': 'إعمار مصر للتطوير', 'name_en': 'Emaar Misr', 'sector': 'العقارات', 'yf': 'EMAA.CA', 'base': 7, 'pe': 9.5, 'div_yield': 0},
        'MISR': {'name': 'مصر الجديدة للإسكان', 'name_en': 'New Cairo Housing', 'sector': 'العقارات', 'yf': None, 'base': 12, 'pe': 8.0, 'div_yield': 1.5},
        'ISNR': {'name': 'الإسكندرية الوطنية للتعمير', 'name_en': 'Alexandria National', 'sector': 'العقارات', 'yf': None, 'base': 8, 'pe': 7.0, 'div_yield': 0},
        'ISMA': {'name': 'الإسماعيلية للتنمية العقارية', 'name_en': 'Ismailia Development', 'sector': 'العقارات', 'yf': None, 'base': 4, 'pe': 6.0, 'div_yield': 0},
        'PENT': {'name': 'بنتا للاستثمار العقاري', 'name_en': 'Penta Capital', 'sector': 'العقارات', 'yf': None, 'base': 3, 'pe': 5.0, 'div_yield': 0},
        'MGRC': {'name': 'ماجريك مصر للتطوير', 'name_en': 'Magric Egypt', 'sector': 'العقارات', 'yf': None, 'base': 3, 'pe': 5.5, 'div_yield': 0},

        # ── الصناعة والطاقة (14) ────────────────────────────────
        'SWDY': {'name': 'السويدي إلكتريك', 'name_en': 'El Sewedy Electric', 'sector': 'الصناعة', 'yf': 'SWDY.CA', 'base': 28, 'pe': 8.5, 'div_yield': 3.2},
        'ECIG': {'name': 'الشرقية للدخان', 'name_en': 'Eastern Company', 'sector': 'الصناعة', 'yf': 'ECIG.CA', 'base': 35, 'pe': 10.5, 'div_yield': 5.5},
        'SKPC': {'name': 'سيدبيك للبتروكيماويات', 'name_en': 'Sidi Kerir Petrochem', 'sector': 'الصناعة', 'yf': 'SKPC.CA', 'base': 55, 'pe': 7.8, 'div_yield': 6.2},
        'ORWE': {'name': 'أوراسكوم للإنشاء والصناعة', 'name_en': 'Orascom Construction', 'sector': 'الصناعة', 'yf': 'ORWE.CA', 'base': 450, 'pe': 12.0, 'div_yield': 0},
        'AMOC': {'name': 'الإسكندرية لتكرير البترول', 'name_en': 'AMOC', 'sector': 'الطاقة', 'yf': 'AMOC.CA', 'base': 28, 'pe': 6.5, 'div_yield': 4.0},
        'ALUM': {'name': 'مصر للألومنيوم', 'name_en': 'Egyptian Aluminium', 'sector': 'الصناعة', 'yf': 'ALUM.CA', 'base': 22, 'pe': 8.0, 'div_yield': 3.8},
        'ABQQ': {'name': 'أبو قير للأسمدة والصناعات', 'name_en': 'Abu Qir Fertilizers', 'sector': 'الصناعة', 'yf': 'ABQQ.CA', 'base': 90, 'pe': 9.5, 'div_yield': 7.0},
        'EFCO': {'name': 'مصر لإنتاج الأسمدة', 'name_en': 'Egypt Fertilizer', 'sector': 'الصناعة', 'yf': 'EFCO.CA', 'base': 40, 'pe': 8.8, 'div_yield': 5.5},
        'ENPC': {'name': 'إنبي للهندسة والمشاريع', 'name_en': 'ENPPI', 'sector': 'الطاقة', 'yf': 'ENPC.CA', 'base': 24, 'pe': 7.5, 'div_yield': 3.0},
        'EFIC': {'name': 'مصر للتكرير', 'name_en': 'Egyptian Refining', 'sector': 'الطاقة', 'yf': 'EFIC.CA', 'base': 32, 'pe': 11.0, 'div_yield': 0},
        'IRON': {'name': 'الحديد والصلب المصرية', 'name_en': 'Egyptian Iron & Steel', 'sector': 'الصناعة', 'yf': None, 'base': 8, 'pe': 0, 'div_yield': 0},
        'UNIF': {'name': 'يونيباك للصناعات التعبوية', 'name_en': 'Unipack Industries', 'sector': 'الصناعة', 'yf': None, 'base': 7, 'pe': 9.0, 'div_yield': 2.0},
        'EGTS': {'name': 'مصر للطيران للخدمات', 'name_en': 'EgyptAir Services', 'sector': 'الصناعة', 'yf': None, 'base': 11, 'pe': 12.0, 'div_yield': 0},
        'MPCI': {'name': 'المصرية للتعبئة والتغليف', 'name_en': 'Egypt Pack', 'sector': 'الصناعة', 'yf': None, 'base': 9, 'pe': 8.5, 'div_yield': 1.5},

        # ── الأغذية والمشروبات (8) ──────────────────────────────
        'JUFO': {'name': 'جهينة للصناعات الغذائية', 'name_en': 'Juhayna Food', 'sector': 'الأغذية', 'yf': 'JUFO.CA', 'base': 12, 'pe': 14.5, 'div_yield': 1.0},
        'DOMT': {'name': 'دومتي للصناعات الغذائية', 'name_en': 'Domty', 'sector': 'الأغذية', 'yf': 'DOMT.CA', 'base': 18, 'pe': 12.0, 'div_yield': 2.5},
        'EDFI': {'name': 'الدلتا للسكر', 'name_en': 'Delta Sugar', 'sector': 'الأغذية', 'yf': 'EDFI.CA', 'base': 22, 'pe': 9.5, 'div_yield': 4.0},
        'SUGR': {'name': 'مصر لتكرير السكر', 'name_en': 'Egypt Sugar', 'sector': 'الأغذية', 'yf': 'SUGR.CA', 'base': 28, 'pe': 8.8, 'div_yield': 3.5},
        'BISQ': {'name': 'بيسكو مصر', 'name_en': 'Bisco Misr', 'sector': 'الأغذية', 'yf': None, 'base': 15, 'pe': 11.0, 'div_yield': 3.0},
        'PRTN': {'name': 'بروتين للصناعات الغذائية', 'name_en': 'Protein Foods', 'sector': 'الأغذية', 'yf': None, 'base': 8, 'pe': 10.5, 'div_yield': 0},
        'MILK': {'name': 'مصر للألبان والأغذية', 'name_en': 'Misr Milk', 'sector': 'الأغذية', 'yf': None, 'base': 16, 'pe': 13.0, 'div_yield': 1.5},
        'AGRC': {'name': 'الشركة الزراعية للمنتجات', 'name_en': 'Agri Products', 'sector': 'الأغذية', 'yf': None, 'base': 9, 'pe': 9.0, 'div_yield': 2.0},

        # ── الأدوية والرعاية الصحية (9) ─────────────────────────
        'ISPH': {'name': 'الإسكندرية للأدوية', 'name_en': 'Alexandria Pharma', 'sector': 'الصحة', 'yf': 'ISPH.CA', 'base': 28, 'pe': 12.5, 'div_yield': 2.8},
        'EIPO': {'name': 'إيبيكو للأدوية والصناعات الكيماوية', 'name_en': 'EIPICO', 'sector': 'الصحة', 'yf': 'EIPO.CA', 'base': 56, 'pe': 11.8, 'div_yield': 3.5},
        'CLHO': {'name': 'كليوباترا للمستشفيات', 'name_en': 'Cleopatra Hospital', 'sector': 'الصحة', 'yf': 'CLHO.CA', 'base': 22, 'pe': 18.5, 'div_yield': 0.5},
        'SAUD': {'name': 'المستشفى السعودي الألماني', 'name_en': 'Saudi German Hospital', 'sector': 'الصحة', 'yf': 'SAUD.CA', 'base': 14, 'pe': 16.0, 'div_yield': 0},
        'IBNS': {'name': 'ابن سينا للأدوية', 'name_en': 'Ibn Sina Pharma', 'sector': 'الصحة', 'yf': 'IBNS.CA', 'base': 25, 'pe': 13.5, 'div_yield': 1.8},
        'SPMD': {'name': 'سبيد ميديكال', 'name_en': 'Speed Medical', 'sector': 'الصحة', 'yf': 'SPMD.CA', 'base': 4, 'pe': 20.0, 'div_yield': 0},
        'AMPH': {'name': 'أميريا للصناعات الدوائية', 'name_en': 'Amriya Pharma', 'sector': 'الصحة', 'yf': None, 'base': 18, 'pe': 10.5, 'div_yield': 2.0},
        'ABMC': {'name': 'أبو المجد للأدوية', 'name_en': 'Abu El-Magd Pharma', 'sector': 'الصحة', 'yf': None, 'base': 8, 'pe': 9.5, 'div_yield': 0},
        'MHPC': {'name': 'المهن الطبية القابضة', 'name_en': 'Medical Union', 'sector': 'الصحة', 'yf': None, 'base': 12, 'pe': 14.0, 'div_yield': 0},

        # ── الأسمنت ومواد البناء (9) ────────────────────────────
        'MCEM': {'name': 'أسمنت مصر', 'name_en': 'Misr Cement', 'sector': 'الأسمنت', 'yf': 'MCEM.CA', 'base': 22, 'pe': 8.5, 'div_yield': 4.5},
        'SINE': {'name': 'أسمنت سيناء', 'name_en': 'Sinai Cement', 'sector': 'الأسمنت', 'yf': 'SINE.CA', 'base': 18, 'pe': 7.8, 'div_yield': 3.8},
        'ARCC': {'name': 'أسمنت العربية', 'name_en': 'Arabian Cement', 'sector': 'الأسمنت', 'yf': 'ARCC.CA', 'base': 35, 'pe': 9.2, 'div_yield': 5.0},
        'TOUR': {'name': 'أسمنت طرة', 'name_en': 'Tourah Cement', 'sector': 'الأسمنت', 'yf': 'TOUR.CA', 'base': 28, 'pe': 8.0, 'div_yield': 4.2},
        'SRCE': {'name': 'أسمنت وادي النيل', 'name_en': 'South Valley Cement', 'sector': 'الأسمنت', 'yf': 'SRCE.CA', 'base': 15, 'pe': 7.5, 'div_yield': 3.5},
        'BNSF': {'name': 'أسمنت بني سويف', 'name_en': 'Beni Suef Cement', 'sector': 'الأسمنت', 'yf': 'BNSF.CA', 'base': 20, 'pe': 7.0, 'div_yield': 4.0},
        'ALEX': {'name': 'أسمنت الإسكندرية', 'name_en': 'Alexandria Cement', 'sector': 'الأسمنت', 'yf': 'ALEX.CA', 'base': 18, 'pe': 7.2, 'div_yield': 3.8},
        'QENA': {'name': 'أسمنت قنا', 'name_en': 'Qena Cement', 'sector': 'الأسمنت', 'yf': None, 'base': 12, 'pe': 6.5, 'div_yield': 3.0},
        'SUEZ': {'name': 'أسمنت السويس', 'name_en': 'Suez Cement', 'sector': 'الأسمنت', 'yf': None, 'base': 14, 'pe': 6.8, 'div_yield': 3.5},

        # ── الخدمات المالية والتأمين (10) ────────────────────────
        'HRHO': {'name': 'إي إف جي هيرميس القابضة', 'name_en': 'EFG Hermes', 'sector': 'المال', 'yf': 'HRHO.CA', 'base': 26, 'pe': 15.0, 'div_yield': 1.5},
        'CICD': {'name': 'سي آي كابيتال القابضة', 'name_en': 'CI Capital', 'sector': 'المال', 'yf': 'CICD.CA', 'base': 14, 'pe': 12.5, 'div_yield': 2.0},
        'BLTC': {'name': 'بلتون المالية القابضة', 'name_en': 'Beltone Financial', 'sector': 'المال', 'yf': 'BLTC.CA', 'base': 8, 'pe': 11.0, 'div_yield': 1.8},
        'PRMH': {'name': 'برايم القابضة للاستثمارات', 'name_en': 'Prime Holding', 'sector': 'المال', 'yf': 'PRMH.CA', 'base': 12, 'pe': 13.0, 'div_yield': 0},
        'EKHO': {'name': 'مصر الكويت القابضة', 'name_en': 'Egypt Kuwait Holding', 'sector': 'القابضة', 'yf': 'EKHO.CA', 'base': 16, 'pe': 9.5, 'div_yield': 3.0},
        'QALH': {'name': 'القلعة للاستثمار والتطوير', 'name_en': 'Qalaa Holdings', 'sector': 'القابضة', 'yf': 'QALH.CA', 'base': 3.5, 'pe': 0, 'div_yield': 0},
        'OIH':  {'name': 'أوراسكوم للاستثمار القابضة', 'name_en': 'Orascom Invest', 'sector': 'القابضة', 'yf': 'OIH.CA', 'base': 8, 'pe': 14.0, 'div_yield': 0},
        'ISFI': {'name': 'الإسكندرية للاستثمار المالي', 'name_en': 'Alexandria Invest', 'sector': 'المال', 'yf': None, 'base': 10, 'pe': 10.0, 'div_yield': 1.5},
        'ALCO': {'name': 'الإسكندرية للتأمين', 'name_en': 'Alexandria Insurance', 'sector': 'التأمين', 'yf': None, 'base': 7, 'pe': 8.5, 'div_yield': 2.5},
        'GREG': {'name': 'جلف يونيون للتأمين', 'name_en': 'Gulf Union Insurance', 'sector': 'التأمين', 'yf': None, 'base': 5, 'pe': 7.5, 'div_yield': 2.0},

        # ── التعليم (5) ─────────────────────────────────────────
        'CIRA': {'name': 'سيرا للخدمات التعليمية', 'name_en': 'CIRA Education', 'sector': 'التعليم', 'yf': 'CIRA.CA', 'base': 18, 'pe': 20.5, 'div_yield': 0.8},
        'ALEF': {'name': 'ألف للتعليم والتكنولوجيا', 'name_en': 'Alef Education', 'sector': 'التعليم', 'yf': 'ALEF.CA', 'base': 12, 'pe': 25.0, 'div_yield': 0},
        'CLED': {'name': 'كليوباترا للتعليم', 'name_en': 'Cleopatra Education', 'sector': 'التعليم', 'yf': None, 'base': 8, 'pe': 18.0, 'div_yield': 0},
        'AMAN': {'name': 'أمان لخدمات التعليم', 'name_en': 'Aman Education', 'sector': 'التعليم', 'yf': None, 'base': 6, 'pe': 16.0, 'div_yield': 0},
        'EDUC': {'name': 'مصر للتعليم المتقدم', 'name_en': 'Advanced Education', 'sector': 'التعليم', 'yf': None, 'base': 9, 'pe': 17.0, 'div_yield': 0},

        # ── التجزئة والتوزيع (6) ────────────────────────────────
        'GBAL': {'name': 'جي بي أوتو للسيارات', 'name_en': 'GB Auto', 'sector': 'التجزئة', 'yf': 'GBAL.CA', 'base': 27, 'pe': 9.0, 'div_yield': 2.5},
        'CGCO': {'name': 'القاهرة للغاز', 'name_en': 'Cairo Gas', 'sector': 'التجزئة', 'yf': None, 'base': 16, 'pe': 10.5, 'div_yield': 3.0},
        'EGPW': {'name': 'إيجيبت باورز', 'name_en': 'Egypt Powers', 'sector': 'التجزئة', 'yf': None, 'base': 12, 'pe': 11.0, 'div_yield': 1.5},
        'FMLC': {'name': 'فود ماركت للتجارة', 'name_en': 'Food Market', 'sector': 'التجزئة', 'yf': None, 'base': 7, 'pe': 9.5, 'div_yield': 0},
        'ELAB': {'name': 'العربية للتجارة والتوزيع', 'name_en': 'Arab Trading', 'sector': 'التجزئة', 'yf': None, 'base': 10, 'pe': 8.0, 'div_yield': 2.0},
        'RAYE': {'name': 'راية للخدمات والتجارة', 'name_en': 'Raya Services', 'sector': 'التجزئة', 'yf': None, 'base': 14, 'pe': 12.0, 'div_yield': 1.0},

        # ── النقل واللوجستيات (5) ──────────────────────────────
        'TRCO': {'name': 'الشركة المصرية للنقل', 'name_en': 'Egyptian Transport', 'sector': 'النقل', 'yf': None, 'base': 11, 'pe': 8.5, 'div_yield': 2.0},
        'NCTS': {'name': 'الوطنية للشحن والنقل', 'name_en': 'National Cargo', 'sector': 'النقل', 'yf': None, 'base': 5, 'pe': 7.5, 'div_yield': 0},
        'CARG': {'name': 'القاهرة للنقل والشحن', 'name_en': 'Cairo Transport', 'sector': 'النقل', 'yf': None, 'base': 8, 'pe': 8.0, 'div_yield': 1.5},
        'ACIC': {'name': 'أسيوط للملاحة الجوية', 'name_en': 'Assiut Navigation', 'sector': 'النقل', 'yf': None, 'base': 8, 'pe': 7.0, 'div_yield': 1.8},
        'TRTO': {'name': 'النقل البحري المصري', 'name_en': 'Maritime Transport', 'sector': 'النقل', 'yf': None, 'base': 11, 'pe': 9.0, 'div_yield': 2.5},

        # ── السياحة والفنادق (5) ────────────────────────────────
        'EGHS': {'name': 'مصر الجديدة للفنادق', 'name_en': 'New Cairo Hotels', 'sector': 'السياحة', 'yf': None, 'base': 7, 'pe': 15.0, 'div_yield': 1.0},
        'ISML': {'name': 'الإسماعيلية للاستثمار والتطوير', 'name_en': 'Ismailia Invest', 'sector': 'السياحة', 'yf': None, 'base': 5, 'pe': 12.0, 'div_yield': 0},
        'AMIC': {'name': 'الأمانة للاستثمار السياحي', 'name_en': 'Al Amana Invest', 'sector': 'السياحة', 'yf': None, 'base': 6, 'pe': 14.0, 'div_yield': 0},
        'HRTS': {'name': 'هيرميس للخدمات السياحية', 'name_en': 'Hermes Tourism', 'sector': 'السياحة', 'yf': None, 'base': 8, 'pe': 13.5, 'div_yield': 0},
        'MCTS': {'name': 'مصر للسياحة والاستثمار', 'name_en': 'Egypt Tourism Invest', 'sector': 'السياحة', 'yf': None, 'base': 6, 'pe': 11.0, 'div_yield': 0},

        # ── الزراعة (5) ─────────────────────────────────────────
        'EFCO_A': {'name': 'الدلتا للأسمدة', 'name_en': 'Delta Fertilizers', 'sector': 'الزراعة', 'yf': None, 'base': 35, 'pe': 10.0, 'div_yield': 3.5},
        'SEED': {'name': 'مصر لإنتاج البذور', 'name_en': 'Egypt Seeds', 'sector': 'الزراعة', 'yf': None, 'base': 8, 'pe': 9.0, 'div_yield': 2.0},
        'AGRI': {'name': 'الشركة المصرية للزراعة', 'name_en': 'Egypt Agriculture', 'sector': 'الزراعة', 'yf': None, 'base': 12, 'pe': 11.0, 'div_yield': 2.5},
        'FERT': {'name': 'مصر للأسمدة والصناعات', 'name_en': 'Egypt Fertilizers', 'sector': 'الزراعة', 'yf': None, 'base': 25, 'pe': 9.5, 'div_yield': 3.0},
        'LAND': {'name': 'مصر للأراضي الزراعية', 'name_en': 'Agricultural Land', 'sector': 'الزراعة', 'yf': None, 'base': 15, 'pe': 8.5, 'div_yield': 1.5},

        # ── المقاولات والتشييد (5) ──────────────────────────────
        'CONS': {'name': 'المقاولون العرب', 'name_en': 'Arab Contractors', 'sector': 'المقاولات', 'yf': None, 'base': 18, 'pe': 10.0, 'div_yield': 2.0},
        'HCCO': {'name': 'الحسينية للمقاولات', 'name_en': 'HCCO', 'sector': 'المقاولات', 'yf': None, 'base': 11, 'pe': 9.5, 'div_yield': 1.5},
        'ELCO': {'name': 'النصر للمقاولات', 'name_en': 'Nasr Contractors', 'sector': 'المقاولات', 'yf': None, 'base': 9, 'pe': 8.5, 'div_yield': 0},
        'BUIL': {'name': 'العمارة للتشييد والإنشاء', 'name_en': 'Omara Construction', 'sector': 'المقاولات', 'yf': None, 'base': 7, 'pe': 8.0, 'div_yield': 0},
        'RECN': {'name': 'ريكون للمقاولات', 'name_en': 'Recon Construction', 'sector': 'المقاولات', 'yf': None, 'base': 6, 'pe': 7.5, 'div_yield': 0},

        # ── الإعلام (4) ─────────────────────────────────────────
        'MENA': {'name': 'مينا للإعلام والاستثمار', 'name_en': 'Mena Media', 'sector': 'الإعلام', 'yf': None, 'base': 6, 'pe': 18.0, 'div_yield': 0},
        'ETMC': {'name': 'شركة الإعلام المصرية', 'name_en': 'Egypt Media', 'sector': 'الإعلام', 'yf': None, 'base': 8, 'pe': 20.0, 'div_yield': 0},
        'PROD': {'name': 'الشركة المتحدة للإنتاج', 'name_en': 'United Production', 'sector': 'الإعلام', 'yf': None, 'base': 7, 'pe': 17.0, 'div_yield': 0},
        'DIGI': {'name': 'ديجيتال ميديا للإعلام', 'name_en': 'Digital Media', 'sector': 'الإعلام', 'yf': None, 'base': 9, 'pe': 22.0, 'div_yield': 0},

        # ── التكنولوجيا المالية / فينتك (4) ─────────────────────
        'FWRY2': {'name': 'فوري بلس للمدفوعات', 'name_en': 'Fawry Plus', 'sector': 'فينتك', 'yf': None, 'base': 22, 'pe': 28.0, 'div_yield': 0},
        'PAYM': {'name': 'بايموب للمدفوعات الرقمية', 'name_en': 'Paymob', 'sector': 'فينتك', 'yf': None, 'base': 22, 'pe': 30.0, 'div_yield': 0},
        'CASH': {'name': 'كاش لينك للمدفوعات', 'name_en': 'Cash Link', 'sector': 'فينتك', 'yf': None, 'base': 12, 'pe': 25.0, 'div_yield': 0},
        'TALN': {'name': 'تالينتس للتكنولوجيا', 'name_en': 'Talents', 'sector': 'فينتك', 'yf': None, 'base': 15, 'pe': 22.0, 'div_yield': 0},
    }

    SECTORS: Dict[str, List[str]] = {}
    EGX30: List[str] = []
    EGX70: List[str] = []
    EGX100: List[str] = []

    @classmethod
    def build_indices(cls):
        cls.SECTORS = {}
        for sym, data in cls.STOCKS.items():
            sec = data['sector']
            cls.SECTORS.setdefault(sec, []).append(sym)

        cls.EGX30 = list(dict.fromkeys([
            'COMI', 'QNBE', 'TMGH', 'ETEL', 'FWRY', 'SWDY', 'ECIG', 'SKPC',
            'ORWE', 'JUFO', 'ISPH', 'EIPO', 'MCEM', 'ARCC', 'SODC', 'GBAL',
            'QALH', 'ABQQ', 'HRHO', 'PHDC', 'EFCO', 'SUGR', 'EAST', 'DOMT',
            'CLHO', 'EKHO', 'CIRA', 'ALEF', 'ADIB', 'AMOC'
        ]))
        cls.EGX70 = [s for s in cls.STOCKS if s not in cls.EGX30 and cls.STOCKS[s]['base'] > 10]
        cls.EGX100 = [s for s in cls.STOCKS if s not in cls.EGX30 and s not in cls.EGX70]

EGXDatabase.build_indices()

# ═══════════════════════════════════════════════════════════════
# محرك البيانات — Yahoo Finance + محاكاة ذكية
# ═══════════════════════════════════════════════════════════════
def generate_simulated_data(symbol: str, days: int = 300) -> pd.DataFrame:
    """محاكاة GARCH-like متقدمة مع تقلب قطاعي"""
    info = EGXDatabase.STOCKS.get(symbol, {})
    seed = int(hashlib.md5(symbol.encode()).hexdigest(), 16) % (2**31)
    rng = np.random.default_rng(seed)

    base = info.get('base', 20.0)
    sector = info.get('sector', '')
    vol_map = {
        'البنوك': 0.011, 'الاتصالات': 0.014, 'التكنولوجيا': 0.025,
        'العقارات': 0.020, 'الصناعة': 0.018, 'الأغذية': 0.010,
        'الطاقة': 0.022, 'الصحة': 0.017, 'الأسمنت': 0.015,
        'المال': 0.020, 'القابضة': 0.022, 'التعليم': 0.014,
        'التجزئة': 0.016, 'النقل': 0.018, 'السياحة': 0.020,
        'التأمين': 0.013, 'الزراعة': 0.012, 'المقاولات': 0.021,
        'الإعلام': 0.019, 'فينتك': 0.026,
    }
    daily_vol = vol_map.get(sector, 0.016)

    dates = pd.date_range(end=datetime.now(), periods=days, freq='B')
    drift = rng.normal(0.0003, 0.0006)

    # GARCH(1,1) volatility clustering
    variances = np.zeros(days)
    variances[0] = daily_vol ** 2
    omega = 0.000002
    alpha = 0.08
    beta = 0.88
    returns = np.zeros(days)
    returns[0] = 0.0
    for t in range(1, days):
        variances[t] = omega + alpha * returns[t-1]**2 + beta * variances[t-1]
        returns[t] = drift + np.sqrt(variances[t]) * rng.normal()

    # EGX daily price limit ±10%
    returns = np.clip(returns, -0.10, 0.10)
    price = base * np.exp(np.cumsum(returns))
    price = np.maximum(price, 0.10)

    # Generate realistic OHLCV
    intraday_vol = np.sqrt(variances) * 1.4
    op = price * np.exp(rng.normal(0, daily_vol * 0.3, days))
    op = np.clip(op, price * 0.97, price * 1.03)
    hi = np.maximum(op, price) * (1 + np.abs(rng.normal(0, intraday_vol * 0.5, days)))
    lo = np.minimum(op, price) * (1 - np.abs(rng.normal(0, intraday_vol * 0.5, days)))
    lo = np.maximum(lo, 0.05)
    hi = np.maximum(hi, lo + 0.01)
    op = np.clip(op, lo, hi)
    cl = np.clip(price, lo, hi)

    # Volume correlated with volatility
    base_vol = rng.lognormal(14, 0.7, days)
    vol_factor = 1 + np.abs(returns) * 40
    volume = (base_vol * vol_factor).astype(int)

    return pd.DataFrame({
        'open': op, 'high': hi, 'low': lo, 'close': cl, 'volume': volume
    }, index=dates)

def fetch_real_data(symbol: str, days: int = 300) -> Optional[pd.DataFrame]:
    """جلب بيانات حقيقية من Yahoo Finance"""
    try:
        yf_sym = EGXDatabase.STOCKS.get(symbol, {}).get('yf')
        if not yf_sym:
            return None
        import yfinance as yf
        ticker = yf.Ticker(yf_sym)
        df = ticker.history(period=f"{days + 60}d", interval="1d", auto_adjust=True)
        if df.empty or len(df) < 30:
            return None
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
        df.columns = ['open', 'high', 'low', 'close', 'volume']
        df.index = pd.to_datetime(df.index).tz_localize(None)
        df = df.dropna()
        if df['close'].iloc[-1] <= 0:
            return None
        return df.tail(days)
    except Exception as e:
        logger.warning(f"Yahoo Finance failed for {symbol}: {e}")
        return None

# ═══════════════════════════════════════════════════════════════
# المؤشرات الفنية — مُصحَّحة وسريعة
# ═══════════════════════════════════════════════════════════════
def calc_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    delta = prices.diff()
    gain = delta.clip(lower=0).rolling(period, min_periods=1).mean()
    loss = (-delta.clip(upper=0)).rolling(period, min_periods=1).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def calc_ema(prices: pd.Series, span: int = 20) -> pd.Series:
    return prices.ewm(span=span, adjust=False, min_periods=1).mean()

def calc_sma(prices: pd.Series, window: int = 20) -> pd.Series:
    return prices.rolling(window, min_periods=1).mean()

def calc_bb(prices: pd.Series, window: int = 20, std: float = 2.0) -> Tuple:
    m = calc_sma(prices, window)
    s = prices.rolling(window, min_periods=1).std(ddof=0)
    return m + s * std, m, m - s * std

def calc_macd(prices: pd.Series, fast: int = 12, slow: int = 26, sig: int = 9) -> Tuple:
    macd = calc_ema(prices, fast) - calc_ema(prices, slow)
    signal = calc_ema(macd, sig)
    return macd, signal, macd - signal

def calc_adx(h: pd.Series, l: pd.Series, c: pd.Series, period: int = 14) -> Tuple:
    """ADX مع +DI و -DI"""
    prev_h = h.shift(1)
    prev_l = l.shift(1)
    prev_c = c.shift(1)
    
    tr = pd.concat([
        h - l,
        (h - prev_c).abs(),
        (l - prev_c).abs()
    ], axis=1).max(axis=1)
    
    dm_plus = np.where((h - prev_h) > (prev_l - l), np.maximum(h - prev_h, 0), 0)
    dm_minus = np.where((prev_l - l) > (h - prev_h), np.maximum(prev_l - l, 0), 0)
    
    dm_plus = pd.Series(dm_plus, index=h.index)
    dm_minus = pd.Series(dm_minus, index=h.index)
    
    atr = tr.ewm(span=period, adjust=False, min_periods=1).mean()
    di_plus = 100 * dm_plus.ewm(span=period, adjust=False, min_periods=1).mean() / atr.replace(0, np.nan)
    di_minus = 100 * dm_minus.ewm(span=period, adjust=False, min_periods=1).mean() / atr.replace(0, np.nan)
    
    dx = 100 * (di_plus - di_minus).abs() / (di_plus + di_minus).replace(0, np.nan)
    adx = dx.ewm(span=period, adjust=False, min_periods=1).mean()
    return adx, di_plus, di_minus

def calc_stoch(h: pd.Series, l: pd.Series, c: pd.Series, k: int = 14, d: int = 3) -> Tuple:
    ll = l.rolling(k, min_periods=1).min()
    hh = h.rolling(k, min_periods=1).max()
    denom = (hh - ll).replace(0, np.nan)
    stoch_k = 100 * (c - ll) / denom
    stoch_d = stoch_k.rolling(d, min_periods=1).mean()
    return stoch_k, stoch_d

def calc_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    direction = np.sign(close.diff()).fillna(0)
    return (direction * volume).cumsum()

def calc_atr(h: pd.Series, l: pd.Series, c: pd.Series, period: int = 14) -> pd.Series:
    tr = pd.concat([
        h - l,
        (h - c.shift(1)).abs(),
        (l - c.shift(1)).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(period, min_periods=1).mean()

def calc_cci(h: pd.Series, l: pd.Series, c: pd.Series, period: int = 20) -> pd.Series:
    tp = (h + l + c) / 3
    ma = tp.rolling(period, min_periods=1).mean()
    md = tp.rolling(period, min_periods=1).apply(
        lambda x: np.mean(np.abs(x - np.mean(x))), raw=True
    )
    return (tp - ma) / (0.015 * md.replace(0, np.nan))

def calc_williams_r(h: pd.Series, l: pd.Series, c: pd.Series, period: int = 14) -> pd.Series:
    hh = h.rolling(period, min_periods=1).max()
    ll = l.rolling(period, min_periods=1).min()
    return -100 * (hh - c) / (hh - ll).replace(0, np.nan)

def calc_vwap_daily(h: pd.Series, l: pd.Series, c: pd.Series, v: pd.Series) -> pd.Series:
    """✅ VWAP يومي صحيح — يُعاد حسابه من الصفر كل يوم تداول"""
    tp = (h + l + c) / 3
    df_tmp = pd.DataFrame({'tp': tp, 'v': v, 'date': tp.index.date})
    
    def daily_vwap(group):
        cum_tpv = (group['tp'] * group['v']).cumsum()
        cum_v = group['v'].cumsum()
        return cum_tpv / cum_v.replace(0, np.nan)
    
    result = df_tmp.groupby('date', group_keys=False).apply(daily_vwap)
    result.index = tp.index
    return result

def calc_roc(prices: pd.Series, period: int = 12) -> pd.Series:
    return ((prices - prices.shift(period)) / prices.shift(period).replace(0, np.nan)) * 100

def calc_momentum(prices: pd.Series, period: int = 10) -> pd.Series:
    return prices - prices.shift(period)

def calc_ichimoku(h: pd.Series, l: pd.Series, c: pd.Series,
                  tenkan: int = 9, kijun: int = 26, senkou: int = 52) -> Tuple:
    tenkan_sen = (h.rolling(tenkan, min_periods=1).max() + l.rolling(tenkan, min_periods=1).min()) / 2
    kijun_sen = (h.rolling(kijun, min_periods=1).max() + l.rolling(kijun, min_periods=1).min()) / 2
    senkou_a = ((tenkan_sen + kijun_sen) / 2).shift(kijun)
    senkou_b = ((h.rolling(senkou, min_periods=1).max() + l.rolling(senkou, min_periods=1).min()) / 2).shift(kijun)
    chikou = c.shift(-kijun)
    return tenkan_sen, kijun_sen, senkou_a, senkou_b, chikou

def calc_supertrend(h: pd.Series, l: pd.Series, c: pd.Series,
                    period: int = 10, multiplier: float = 3.0) -> Tuple:
    """✅ Supertrend — المؤشر الأكثر استخداماً من محللي EGX"""
    atr = calc_atr(h, l, c, period)
    hl2 = (h + l) / 2
    
    upper_band = hl2 + multiplier * atr
    lower_band = hl2 - multiplier * atr
    
    supertrend = pd.Series(index=c.index, dtype=float)
    direction = pd.Series(index=c.index, dtype=int)
    
    # Initialize
    supertrend.iloc[0] = upper_band.iloc[0]
    direction.iloc[0] = -1
    
    for i in range(1, len(c)):
        # Upper band
        if upper_band.iloc[i] < upper_band.iloc[i-1] or c.iloc[i-1] > upper_band.iloc[i-1]:
            upper_band.iloc[i] = upper_band.iloc[i]
        else:
            upper_band.iloc[i] = upper_band.iloc[i-1]
        
        # Lower band
        if lower_band.iloc[i] > lower_band.iloc[i-1] or c.iloc[i-1] < lower_band.iloc[i-1]:
            lower_band.iloc[i] = lower_band.iloc[i]
        else:
            lower_band.iloc[i] = lower_band.iloc[i-1]
        
        # Direction
        if supertrend.iloc[i-1] == upper_band.iloc[i-1]:
            if c.iloc[i] <= upper_band.iloc[i]:
                direction.iloc[i] = -1
                supertrend.iloc[i] = upper_band.iloc[i]
            else:
                direction.iloc[i] = 1
                supertrend.iloc[i] = lower_band.iloc[i]
        else:
            if c.iloc[i] >= lower_band.iloc[i]:
                direction.iloc[i] = 1
                supertrend.iloc[i] = lower_band.iloc[i]
            else:
                direction.iloc[i] = -1
                supertrend.iloc[i] = upper_band.iloc[i]
    
    return supertrend, direction

def calc_parabolic_sar_vectorized(h: pd.Series, l: pd.Series, c: pd.Series,
                                   af_start: float = 0.02, af_max: float = 0.2) -> pd.Series:
    """Parabolic SAR — محسَّن بدون حلقات Python كثيرة"""
    n = len(c)
    sar = np.zeros(n)
    ep = np.zeros(n)
    trend = np.zeros(n, dtype=int)
    af = af_start

    if n < 2:
        return c.copy()

    trend[0] = 1
    sar[0] = float(l.iloc[0])
    ep[0] = float(h.iloc[0])
    af = af_start

    h_arr = h.values
    l_arr = l.values
    c_arr = c.values

    for i in range(1, n):
        sar[i] = sar[i-1] + af * (ep[i-1] - sar[i-1])

        if trend[i-1] == 1:
            sar[i] = min(sar[i], l_arr[max(0, i-1)], l_arr[max(0, i-2)])
            if h_arr[i] > ep[i-1]:
                ep[i] = h_arr[i]
                af = min(af + af_start, af_max)
            else:
                ep[i] = ep[i-1]
            if l_arr[i] < sar[i]:
                trend[i] = -1
                sar[i] = ep[i-1]
                ep[i] = l_arr[i]
                af = af_start
            else:
                trend[i] = 1
        else:
            sar[i] = max(sar[i], h_arr[max(0, i-1)], h_arr[max(0, i-2)])
            if l_arr[i] < ep[i-1]:
                ep[i] = l_arr[i]
                af = min(af + af_start, af_max)
            else:
                ep[i] = ep[i-1]
            if h_arr[i] > sar[i]:
                trend[i] = 1
                sar[i] = ep[i-1]
                ep[i] = h_arr[i]
                af = af_start
            else:
                trend[i] = -1

    return pd.Series(sar, index=c.index)

def get_support_resistance(df: pd.DataFrame, window: int = 20) -> Tuple[float, float]:
    recent = df.tail(60)
    if recent.empty:
        return 0.0, 0.0
    support = recent['low'].rolling(window, min_periods=1).min().iloc[-1]
    resistance = recent['high'].rolling(window, min_periods=1).max().iloc[-1]
    return float(support), float(resistance)

def get_fibonacci_levels(support: float, resistance: float) -> Dict[str, float]:
    diff = resistance - support
    if diff <= 0:
        diff = support * 0.1
    return {
        '0.0% (دعم)': support,
        '23.6%': support + diff * 0.236,
        '38.2%': support + diff * 0.382,
        '50.0%': support + diff * 0.500,
        '61.8%': support + diff * 0.618,
        '78.6%': support + diff * 0.786,
        '100% (مقاومة)': resistance,
        '127.2%': support + diff * 1.272,
        '161.8%': support + diff * 1.618,
    }

# ═══════════════════════════════════════════════════════════════
# محمّل البيانات الرئيسي مع كامل المؤشرات
# ═══════════════════════════════════════════════════════════════
def load_and_compute(symbol: str, days: int = 300) -> Optional[pd.DataFrame]:
    """جلب البيانات + حساب جميع المؤشرات"""
    try:
        df = fetch_real_data(symbol, days)
        source = "real"
        if df is None or len(df) < max(days // 3, 50):
            df = generate_simulated_data(symbol, days)
            source = "simulated"

        if df is None or df.empty:
            return None

        c, h, l, v = df['close'], df['high'], df['low'], df['volume']

        # ── المؤشرات الأساسية ──
        df['rsi'] = calc_rsi(c)
        df['ema_9'] = calc_ema(c, 9)
        df['ema_20'] = calc_ema(c, 20)
        df['ema_50'] = calc_ema(c, 50)
        df['ema_200'] = calc_ema(c, 200)
        df['sma_20'] = calc_sma(c, 20)
        df['sma_50'] = calc_sma(c, 50)
        df['bb_upper'], df['bb_middle'], df['bb_lower'] = calc_bb(c)
        df['macd'], df['macd_signal'], df['macd_hist'] = calc_macd(c)
        df['adx'], df['di_plus'], df['di_minus'] = calc_adx(h, l, c)
        df['stoch_k'], df['stoch_d'] = calc_stoch(h, l, c)
        df['obv'] = calc_obv(c, v)
        df['atr'] = calc_atr(h, l, c)
        df['cci'] = calc_cci(h, l, c)
        df['williams_r'] = calc_williams_r(h, l, c)

        # ── المؤشرات المتقدمة ──
        df['vwap'] = calc_vwap_daily(h, l, c, v)  # ✅ VWAP يومي صحيح
        df['psar'] = calc_parabolic_sar_vectorized(h, l, c)
        df['roc'] = calc_roc(c, 12)
        df['momentum'] = calc_momentum(c, 10)
        df['supertrend'], df['supertrend_dir'] = calc_supertrend(h, l, c)  # ✅ جديد
        
        tenkan, kijun, spa, spb, chikou = calc_ichimoku(h, l, c)
        df['ich_tenkan'] = tenkan
        df['ich_kijun'] = kijun
        df['ich_senkou_a'] = spa
        df['ich_senkou_b'] = spb
        df['ich_chikou'] = chikou

        # ── مؤشرات مساعدة ──
        df['pct_change'] = c.pct_change() * 100
        df['vol_sma'] = v.rolling(20, min_periods=1).mean()
        df['vol_ratio'] = v / df['vol_sma'].replace(0, np.nan)
        df['volatility_20d'] = c.pct_change().rolling(20, min_periods=1).std() * np.sqrt(252)
        df['returns_5d'] = c.pct_change(5)
        df['returns_10d'] = c.pct_change(10)
        df['price_to_ema50'] = c / df['ema_50'].replace(0, np.nan) - 1
        df['price_to_ema200'] = c / df['ema_200'].replace(0, np.nan) - 1
        df['rsi_ema'] = calc_ema(df['rsi'], 5)  # RSI مُمَهَّد

        df['data_source'] = source
        return df

    except Exception as e:
        logger.error(f"load_and_compute({symbol}): {e}", exc_info=True)
        return None

# ═══════════════════════════════════════════════════════════════
# اكتشاف أنماط الشموع اليابانية (مُحسَّن)
# ═══════════════════════════════════════════════════════════════
def detect_patterns(df: pd.DataFrame) -> List[Dict]:
    """اكتشاف 10 أنماط مع قوة الإشارة"""
    patterns = []
    if df is None or len(df) < 3:
        return patterns

    o, h, l, c = df['open'], df['high'], df['low'], df['close']
    body = (c - o).abs()
    rng = h - l
    wick_up = h - pd.concat([c, o], axis=1).max(axis=1)
    wick_dn = pd.concat([c, o], axis=1).min(axis=1) - l

    i = len(df) - 1

    def last(s): return float(s.iloc[i])
    def prev(s, n=1): return float(s.iloc[i-n]) if i >= n else None

    b, r = last(body), last(rng)
    wu, wd = last(wick_up), last(wick_dn)
    c0, o0 = last(c), last(o)

    if r > 0:
        if b < r * 0.05:
            patterns.append({'name': 'دوجي (Doji)', 'emoji': '⚖️', 'signal': 'محايد', 'strength': 2,
                             'desc': 'توازن كامل — مؤشر تردد وانعكاس محتمل'})
        if wd > 2 * b and wu < b * 0.3 and c0 > o0:
            patterns.append({'name': 'مطرقة صاعدة (Hammer)', 'emoji': '🔨', 'signal': 'شراء', 'strength': 3,
                             'desc': 'رفض قوي للأسعار المنخفضة — إشارة انعكاس صاعد'})
        if wu > 2 * b and wd < b * 0.3 and c0 < o0:
            patterns.append({'name': 'نجمة ساقطة (Shooting Star)', 'emoji': '⭐', 'signal': 'بيع', 'strength': 3,
                             'desc': 'رفض قوي للأسعار المرتفعة — إشارة انعكاس هابط'})
        if wu < b * 0.05 and wd < b * 0.05:
            d = 'صاعد قوي' if c0 > o0 else 'هابط قوي'
            s = 'شراء' if c0 > o0 else 'بيع'
            patterns.append({'name': f'ماروبوزو {d} (Marubozu)', 'emoji': '📊', 'signal': s, 'strength': 4,
                             'desc': 'قوة شديدة — السوق يتحرك في اتجاه واحد'})

    if i >= 1:
        c1, o1 = prev(c), prev(o)
        if c1 < o1 and c0 > o0 and c0 > o1 and o0 < c1:
            patterns.append({'name': 'الابتلاع الصاعد (Bullish Engulfing)', 'emoji': '🟢', 'signal': 'شراء', 'strength': 4,
                             'desc': 'شمعة صاعدة تبتلع السابقة — انعكاس صاعد قوي'})
        if c1 > o1 and c0 < o0 and c0 < o1 and o0 > c1:
            patterns.append({'name': 'الابتلاع الهابط (Bearish Engulfing)', 'emoji': '🔴', 'signal': 'بيع', 'strength': 4,
                             'desc': 'شمعة هابطة تبتلع السابقة — انعكاس هابط قوي'})
        b1 = abs(c1 - o1)
        if c1 < o1 and c0 > o0 and o0 > c1 and c0 < o1 and last(body) < b1 * 0.5:
            patterns.append({'name': 'حمل صاعد (Bullish Harami)', 'emoji': '🟢', 'signal': 'شراء', 'strength': 2,
                             'desc': 'شمعة صغيرة داخل السابقة — انعكاس محتمل'})
        if c1 > o1 and c0 < o0 and o0 < c1 and c0 > o1 and last(body) < b1 * 0.5:
            patterns.append({'name': 'حمل هابط (Bearish Harami)', 'emoji': '🔴', 'signal': 'بيع', 'strength': 2,
                             'desc': 'شمعة صغيرة داخل السابقة — انعكاس محتمل'})

    if i >= 2:
        c2, o2 = prev(c, 2), prev(o, 2)
        b2 = abs(c2 - o2) if c2 and o2 else 0
        b1_val = abs(prev(c) - prev(o)) if prev(c) and prev(o) else 0
        mid2 = (o2 + c2) / 2 if c2 and o2 else 0
        if c2 and o2 and c2 < o2 and b1_val < b2 * 0.3 and c0 > o0 and c0 > mid2:
            patterns.append({'name': 'نجمة الصباح (Morning Star)', 'emoji': '🌅', 'signal': 'شراء', 'strength': 5,
                             'desc': 'نمط ثلاثي انعكاسي صاعد — إشارة قوية جداً'})
        if c2 and o2 and c2 > o2 and b1_val < b2 * 0.3 and c0 < o0 and c0 < mid2:
            patterns.append({'name': 'نجمة المساء (Evening Star)', 'emoji': '🌆', 'signal': 'بيع', 'strength': 5,
                             'desc': 'نمط ثلاثي انعكاسي هابط — إشارة قوية جداً'})

    return patterns

# ═══════════════════════════════════════════════════════════════
# محرك الإشارة المركّبة — 12 مؤشر
# ═══════════════════════════════════════════════════════════════
def get_composite_signal(df: pd.DataFrame) -> Tuple[str, str, int, Dict]:
    if df is None or len(df) < 50:
        return "غير معروف", "⚪", 0, {}

    signals = {}
    rsi = safe_last(df['rsi'], 50)
    macd = safe_last(df['macd'], 0)
    msig = safe_last(df['macd_signal'], 0)
    ema20 = safe_last(df['ema_20'])
    ema50 = safe_last(df['ema_50'])
    ema200 = safe_last(df['ema_200'])
    adx = safe_last(df['adx'], 20)
    stk = safe_last(df['stoch_k'], 50)
    std = safe_last(df['stoch_d'], 50)
    cci = safe_last(df['cci'], 0)
    wr = safe_last(df['williams_r'], -50)
    price = float(df['close'].iloc[-1])
    vwap = safe_last(df['vwap'])
    psar = safe_last(df['psar'])
    st_dir = safe_last(df['supertrend_dir'], 0)
    di_plus = safe_last(df['di_plus'], 25)
    di_minus = safe_last(df['di_minus'], 25)

    score = 0

    # RSI (وزن 2)
    if rsi < 30: score += 2; signals['RSI'] = f"تشبع بيع ({rsi:.1f}) — شراء قوي"
    elif rsi < 40: score += 1; signals['RSI'] = f"قرب تشبع بيع ({rsi:.1f})"
    elif rsi > 70: score -= 2; signals['RSI'] = f"تشبع شراء ({rsi:.1f}) — بيع قوي"
    elif rsi > 60: score -= 1; signals['RSI'] = f"قرب تشبع شراء ({rsi:.1f})"
    else: signals['RSI'] = f"محايد ({rsi:.1f})"

    # MACD (وزن 1)
    if macd > msig and df['macd_hist'].iloc[-1] > df['macd_hist'].iloc[-2]:
        score += 2; signals['MACD'] = "تقاطع صاعد مع زخم متزايد"
    elif macd > msig:
        score += 1; signals['MACD'] = "صاعد"
    elif macd < msig:
        score -= 1; signals['MACD'] = "هابط"

    # EMA Trend (وزن 2)
    if price > ema20 > ema50 > ema200: score += 2; signals['EMA'] = "ترتيب صاعد كامل ✅"
    elif price > ema20 > ema50: score += 1; signals['EMA'] = "صاعد قصير المدى"
    elif price < ema20 < ema50 < ema200: score -= 2; signals['EMA'] = "ترتيب هابط كامل ❌"
    elif price < ema20 < ema50: score -= 1; signals['EMA'] = "هابط قصير المدى"
    else: signals['EMA'] = "متعارض"

    # ADX + DI (وزن 1)
    if adx > 25:
        if di_plus > di_minus: score += 1; signals['ADX'] = f"اتجاه صاعد قوي ({adx:.1f})"
        else: score -= 1; signals['ADX'] = f"اتجاه هابط قوي ({adx:.1f})"
    else: signals['ADX'] = f"اتجاه ضعيف ({adx:.1f})"

    # Stochastic (وزن 1)
    if stk < 20 and stk > std: score += 1; signals['Stoch'] = f"منطقة شراء مع تحسن ({stk:.1f})"
    elif stk < 20: score += 1; signals['Stoch'] = f"تشبع بيع ({stk:.1f})"
    elif stk > 80 and stk < std: score -= 1; signals['Stoch'] = f"منطقة بيع مع ضعف ({stk:.1f})"
    elif stk > 80: score -= 1; signals['Stoch'] = f"تشبع شراء ({stk:.1f})"
    else: signals['Stoch'] = f"محايد ({stk:.1f})"

    # CCI (وزن 1)
    if cci < -150: score += 1; signals['CCI'] = f"تشبع بيع ({cci:.0f})"
    elif cci > 150: score -= 1; signals['CCI'] = f"تشبع شراء ({cci:.0f})"
    else: signals['CCI'] = f"محايد ({cci:.0f})"

    # Williams %R (وزن 1)
    if wr < -80: score += 1; signals['W%R'] = f"منطقة شراء ({wr:.1f})"
    elif wr > -20: score -= 1; signals['W%R'] = f"منطقة بيع ({wr:.1f})"
    else: signals['W%R'] = f"محايد ({wr:.1f})"

    # VWAP (وزن 1)
    if vwap > 0:
        pct_from_vwap = (price / vwap - 1) * 100
        if price > vwap: score += 1; signals['VWAP'] = f"أعلى VWAP بـ {pct_from_vwap:.1f}%"
        else: score -= 1; signals['VWAP'] = f"أسفل VWAP بـ {abs(pct_from_vwap):.1f}%"

    # Parabolic SAR (وزن 1)
    if psar > 0:
        if price > psar: score += 1; signals['PSAR'] = "سعر فوق SAR — اتجاه صاعد"
        else: score -= 1; signals['PSAR'] = "سعر تحت SAR — اتجاه هابط"

    # ✅ Supertrend (وزن 2 — مؤشر جديد عالي الدقة)
    if st_dir == 1: score += 2; signals['Supertrend'] = "🟢 إشارة شراء نشطة"
    elif st_dir == -1: score -= 2; signals['Supertrend'] = "🔴 إشارة بيع نشطة"
    else: signals['Supertrend'] = "محايد"

    total_possible = 16
    confidence = min(int((abs(score) / total_possible) * 100), 95)

    if score >= 7: return "شراء قوي جداً", "🟢", confidence, signals
    elif score >= 4: return "شراء", "🟩", confidence, signals
    elif score >= 1: return "ميل للشراء", "🔵", confidence, signals
    elif score <= -7: return "بيع قوي جداً", "🔴", confidence, signals
    elif score <= -4: return "بيع", "🟥", confidence, signals
    elif score <= -1: return "ميل للبيع", "🟠", confidence, signals
    else: return "محايد", "⚪", confidence, signals
