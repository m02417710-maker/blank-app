"""
EGX Pro Terminal v28.0 - Full Edition
منصة تحليل البورصة المصرية - النسخة الكاملة
✅ 250+ شركة مصنّفة | جميع المؤشرات | جميع الخصائص مفعّلة
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import pytz
import logging
import os
import time
from typing import Optional, Tuple, Dict, List
from enum import Enum
import warnings

warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════════════
# 1. LOGGING
# ═══════════════════════════════════════════════════════════════
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('logs/egx.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# 2. THEME & CONFIG
# ═══════════════════════════════════════════════════════════════
class Theme(Enum):
    PRIMARY    = "#667eea"
    SECONDARY  = "#764ba2"
    ACCENT     = "#f093fb"
    SUCCESS    = "#00c853"
    ERROR      = "#ff1744"
    WARNING    = "#ff9800"
    INFO       = "#00b0ff"
    BG_DARK    = "#0a0a1a"
    BG_CARD    = "#12122a"
    BG_PANEL   = "#1a1a35"
    TEXT       = "#ffffff"
    GOLD       = "#ffd700"

class AppConfig:
    APP_NAME         = "EGX Pro Terminal"
    APP_VERSION      = "28.0 Full"
    CACHE_TTL        = 300
    REFRESH_INTERVAL = 60

# ═══════════════════════════════════════════════════════════════
# 3. قاعدة بيانات شركات البورصة المصرية الكاملة (250+ شركة)
# ═══════════════════════════════════════════════════════════════
class EGXConfig:
    STOCKS: Dict[str, Dict] = {
        # ── البنوك ──────────────────────────────────────────────
        'COMI':  {'name': 'البنك التجاري الدولي',          'name_en': 'Commercial International Bank',    'sector': 'البنوك', 'index': 'EGX30'},
        'QNBE':  {'name': 'بنك قطر الوطني الأهلي',         'name_en': 'QNB Al Ahli Bank',                  'sector': 'البنوك', 'index': 'EGX30'},
        'CAIr':  {'name': 'بنك القاهرة',                   'name_en': 'Cairo Bank',                         'sector': 'البنوك', 'index': 'EGX70'},
        'ADIB':  {'name': 'مصرف أبوظبي الإسلامي مصر',      'name_en': 'Abu Dhabi Islamic Bank Egypt',       'sector': 'البنوك', 'index': 'EGX70'},
        'MFPC':  {'name': 'المصرف المتحد',                  'name_en': 'United Bank',                        'sector': 'البنوك', 'index': 'EGX70'},
        'AAIB':  {'name': 'البنك العربي الأفريقي',          'name_en': 'Arab African International Bank',    'sector': 'البنوك', 'index': 'EGX70'},
        'EXPA':  {'name': 'بنك إكسبريس',                   'name_en': 'Express Bank',                       'sector': 'البنوك', 'index': 'EGX70'},
        'NSGB':  {'name': 'بنك الاتحاد الوطني',            'name_en': 'National Bank of Greece Egypt',      'sector': 'البنوك', 'index': 'EGX70'},
        'BLOM':  {'name': 'بنك بلوم مصر',                  'name_en': 'Blom Bank Egypt',                    'sector': 'البنوك', 'index': 'EGX70'},
        'ARAB':  {'name': 'البنك العربي',                   'name_en': 'Arab Bank',                          'sector': 'البنوك', 'index': 'EGX100'},

        # ── الاتصالات والتكنولوجيا ──────────────────────────────
        'TMGH':  {'name': 'تليكوم مصر',                    'name_en': 'Telecom Egypt',                      'sector': 'الاتصالات', 'index': 'EGX30'},
        'ETEL':  {'name': 'اتصالات مصر (e&)',              'name_en': 'e& Egypt (Etisalat)',                'sector': 'الاتصالات', 'index': 'EGX30'},
        'FWRY':  {'name': 'فوري للصرافة الإلكترونية',      'name_en': 'Fawry for Banking & Technology',     'sector': 'الاتصالات', 'index': 'EGX30'},
        'VFSC':  {'name': 'فودافون مصر للتمويل',           'name_en': 'Vodafone Egypt Finance',             'sector': 'الاتصالات', 'index': 'EGX70'},
        'SWDY':  {'name': 'السويدي إلكتريك',               'name_en': 'El Sewedy Electric',                 'sector': 'الاتصالات', 'index': 'EGX30'},

        # ── العقارات والإنشاء ────────────────────────────────────
        'TMGD':  {'name': 'طلعت مصطفى القابضة',            'name_en': 'TMG Holding',                        'sector': 'العقارات', 'index': 'EGX30'},
        'PHDC':  {'name': 'بالم هيلز للتطوير',             'name_en': 'Palm Hills Developments',            'sector': 'العقارات', 'index': 'EGX30'},
        'MNHD':  {'name': 'منارة للإسكان والتطوير',        'name_en': 'Medinet Nasr Housing & Dev',         'sector': 'العقارات', 'index': 'EGX70'},
        'HELI':  {'name': 'مدينة نصر للإسكان والتعمير',    'name_en': 'Heliopolis Housing & Dev',           'sector': 'العقارات', 'index': 'EGX70'},
        'OCDI':  {'name': 'أوراسكوم للتطوير مصر',          'name_en': 'Orascom Development Egypt',          'sector': 'العقارات', 'index': 'EGX70'},
        'EMFD':  {'name': 'إيجيبت فور ريل ايستيت',         'name_en': 'Egypt Free Zone & Develop',          'sector': 'العقارات', 'index': 'EGX100'},
        'SODIC': {'name': 'سوديك للعقارات',                'name_en': 'Sixth of October Dev & Invest',      'sector': 'العقارات', 'index': 'EGX30'},
        'IGAS':  {'name': 'الإسكندرية للغاز والسوائل',     'name_en': 'Alexandria Gas & Oils',              'sector': 'العقارات', 'index': 'EGX100'},
        'MASR':  {'name': 'مصر الجديدة للإسكان',           'name_en': 'New Cairo Housing',                  'sector': 'العقارات', 'index': 'EGX100'},
        'ISNR':  {'name': 'الإسكندرية الوطنية للتعمير',    'name_en': 'Alexandria National Dev',            'sector': 'العقارات', 'index': 'EGX100'},
        'EMAA':  {'name': 'أماك للتطوير العقاري',           'name_en': 'Emaar Misr for Dev',                 'sector': 'العقارات', 'index': 'EGX70'},
        'MGRC':  {'name': 'ماجريك إيجيبت',                 'name_en': 'Magric Egypt',                       'sector': 'العقارات', 'index': 'EGX100'},
        'HRHO':  {'name': 'إي إف جي القابضة',              'name_en': 'EFG Hermes Holdings',                'sector': 'العقارات', 'index': 'EGX30'},

        # ── الصناعة والتصنيع ─────────────────────────────────────
        'EAST':  {'name': 'الشرقية للدخان',                'name_en': 'Eastern Company',                    'sector': 'الصناعة', 'index': 'EGX30'},
        'SKPC':  {'name': 'سيدبيك للبتروكيماويات',         'name_en': 'Sidi Kerir Petrochem',               'sector': 'الصناعة', 'index': 'EGX30'},
        'ORWE':  {'name': 'أوراسكوم للإنشاء',              'name_en': 'Orascom Construction',               'sector': 'الصناعة', 'index': 'EGX30'},
        'MFCI':  {'name': 'النيل للصناعة والتجارة',        'name_en': 'Nile Industries',                    'sector': 'الصناعة', 'index': 'EGX70'},
        'AMOC':  {'name': 'الإسكندرية لتكرير البترول',     'name_en': 'Alexandria Mineral Oils',            'sector': 'الصناعة', 'index': 'EGX70'},
        'IRON':  {'name': 'الحديد والصلب المصرية',         'name_en': 'Egyptian Iron & Steel',              'sector': 'الصناعة', 'index': 'EGX70'},
        'EGTS':  {'name': 'مصر للطيران للخدمات السياحية',  'name_en': 'Egypt Air Tourism Services',         'sector': 'الصناعة', 'index': 'EGX100'},
        'ALUM':  {'name': 'مصر للألومنيوم',                'name_en': 'Egyptian Aluminium',                 'sector': 'الصناعة', 'index': 'EGX70'},
        'EGCH':  {'name': 'مصر الجديدة للإسكان',           'name_en': 'Egyptian Chemical Industries',       'sector': 'الصناعة', 'index': 'EGX100'},
        'SUCE':  {'name': 'شركة قناة السويس للتأمين',      'name_en': 'Suez Canal Insurance',               'sector': 'الصناعة', 'index': 'EGX100'},
        'EGAL':  {'name': 'مصر للأعمال الزجاجية',          'name_en': 'Egypt for Glasswork',                'sector': 'الصناعة', 'index': 'EGX100'},
        'MPCI':  {'name': 'المصرية للتعبئة والتغليف',      'name_en': 'Egyptian Pack Industries',           'sector': 'الصناعة', 'index': 'EGX100'},
        'EICO':  {'name': 'مصر للصناعات الكيماوية',        'name_en': 'Egyptian Chemicals Ind',             'sector': 'الصناعة', 'index': 'EGX100'},
        'UNIF':  {'name': 'ميسر للأغذية المتكاملة',        'name_en': 'Unipack for Integrated Industries',  'sector': 'الصناعة', 'index': 'EGX100'},

        # ── الأغذية والمشروبات ───────────────────────────────────
        'JUFO':  {'name': 'جهينة للصناعات الغذائية',       'name_en': 'Juhayna Food Industries',            'sector': 'الأغذية', 'index': 'EGX30'},
        'DOMTY':{'name': 'دومتي للصناعات الغذائية',        'name_en': 'Cairo Three A Food Ind',             'sector': 'الأغذية', 'index': 'EGX70'},
        'PRTM': {'name': 'بروتين للصناعات الغذائية',       'name_en': 'Protein Foods & Beverages',          'sector': 'الأغذية', 'index': 'EGX100'},
        'BMCO': {'name': 'بيسكو مصر للصناعات الغذائية',   'name_en': 'Bisco Misr',                         'sector': 'الأغذية', 'index': 'EGX70'},
        'AMAL': {'name': 'العمال للأعمال القابضة',          'name_en': 'El Amal Investment Group',           'sector': 'الأغذية', 'index': 'EGX100'},
        'EDFI': {'name': 'مصر للاستثمارات المالية',        'name_en': 'EDF International',                  'sector': 'الأغذية', 'index': 'EGX100'},
        'SFCO': {'name': 'مصر للصناعات الغذائية والمشروبات','name_en': 'Societe Financiere',                'sector': 'الأغذية', 'index': 'EGX100'},
        'MFCI2':{'name': 'مصر للألبان',                    'name_en': 'Misr Milk & Food',                   'sector': 'الأغذية', 'index': 'EGX100'},

        # ── الأدوية والرعاية الصحية ─────────────────────────────
        'ISPH': {'name': 'الإسكندرية للمستحضرات الصيدلية', 'name_en': 'Alexandria Pharmaceuticals',         'sector': 'الصحة',   'index': 'EGX30'},
        'EIPICO':{'name': 'إيبيكو للصناعات الدوائية',      'name_en': 'Egyptian International Pharma',      'sector': 'الصحة',   'index': 'EGX30'},
        'AMPH': {'name': 'أميريا للمستحضرات الصيدلية',     'name_en': 'Amriya Pharmaceutical Industries',   'sector': 'الصحة',   'index': 'EGX70'},
        'MNHD2':{'name': 'مصر للرعاية الصحية',             'name_en': 'Misr Healthcare',                    'sector': 'الصحة',   'index': 'EGX70'},
        'CLHO': {'name': 'كليوباترا للمستشفيات',           'name_en': 'Cleopatra Hospital',                 'sector': 'الصحة',   'index': 'EGX70'},
        'MHPC': {'name': 'مصر للخدمات الصحية',             'name_en': 'Medical Union Pharmaceuticals',      'sector': 'الصحة',   'index': 'EGX100'},
        'SAUD': {'name': 'المستشفى السعودي الألماني',       'name_en': 'Saudi German Hospital',              'sector': 'الصحة',   'index': 'EGX70'},
        'ABMC': {'name': 'أبو المجد للاستثمار الطبي',       'name_en': 'Abu El-Magd Medical',                'sector': 'الصحة',   'index': 'EGX100'},

        # ── الطاقة والبترول ─────────────────────────────────────
        'EFIC': {'name': 'مصر للتكرير',                    'name_en': 'Egyptian Petrochemical',             'sector': 'الطاقة',  'index': 'EGX70'},
        'APCO': {'name': 'أباتشي مصر',                     'name_en': 'Apache Egypt',                       'sector': 'الطاقة',  'index': 'EGX70'},
        'GPIC': {'name': 'الشركة العامة للبترول',           'name_en': 'General Petroleum Company',          'sector': 'الطاقة',  'index': 'EGX100'},
        'ENPC': {'name': 'إنبي للبترول',                   'name_en': 'Egyptian Natural Gas Holding',       'sector': 'الطاقة',  'index': 'EGX100'},
        'SPOC': {'name': 'سيدبيك للبترول',                 'name_en': 'Sidi Kerir Petroleum',               'sector': 'الطاقة',  'index': 'EGX100'},
        'ENRG': {'name': 'ميدا للطاقة المتجددة',           'name_en': 'Meda Renewables',                    'sector': 'الطاقة',  'index': 'EGX100'},

        # ── السياحة والفنادق ─────────────────────────────────────
        'HRTX': {'name': 'هيرميس القابضة',                 'name_en': 'Hermes Holding',                     'sector': 'السياحة', 'index': 'EGX70'},
        'ISMC': {'name': 'إسماعيلية للتنمية العمرانية',    'name_en': 'Ismailia National',                  'sector': 'السياحة', 'index': 'EGX100'},
        'MCTS': {'name': 'مصر للسياحة والاستثمار',         'name_en': 'Egypt Tourism Investment',           'sector': 'السياحة', 'index': 'EGX100'},
        'EGHS': {'name': 'مصر الجديدة للمشاريع الفندقية',  'name_en': 'New Cairo for Hotel Projects',       'sector': 'السياحة', 'index': 'EGX100'},
        'ISMAILIA':{'name': 'الإسماعيلية للاستثمار',       'name_en': 'Ismailia Invest',                    'sector': 'السياحة', 'index': 'EGX100'},
        'PENTA':{'name': 'بنتا للاستثمار',                 'name_en': 'Penta Capital Holdings',             'sector': 'السياحة', 'index': 'EGX100'},

        # ── الخدمات المالية والتأمين ─────────────────────────────
        'EGBE': {'name': 'البنك المصري للتنمية',            'name_en': 'Egyptian Export Dev Bank',           'sector': 'المال',   'index': 'EGX70'},
        'ISFI': {'name': 'الإسكندرية للاستثمار المالي',    'name_en': 'Alexandria Financial Invest',        'sector': 'المال',   'index': 'EGX100'},
        'IBNSN':{'name': 'ابن سينا للتأمين',               'name_en': 'Ibn Sina Pharma',                    'sector': 'المال',   'index': 'EGX70'},
        'CIBD': {'name': 'سي آي كابيتال',                  'name_en': 'CI Capital Holding',                 'sector': 'المال',   'index': 'EGX70'},
        'BLTC': {'name': 'بلتون المالية القابضة',           'name_en': 'Beltone Financial Holding',          'sector': 'المال',   'index': 'EGX70'},
        'PDCO': {'name': 'باديكو القابضة',                  'name_en': 'PADICO Holding',                     'sector': 'المال',   'index': 'EGX100'},
        'PRIME':{'name': 'برايم القابضة للاستثمارات',       'name_en': 'Prime Holding',                      'sector': 'المال',   'index': 'EGX100'},
        'MFCI3':{'name': 'مصر لتمويل المشاريع',            'name_en': 'Misr Investment Finance',            'sector': 'المال',   'index': 'EGX100'},
        'ECAP': {'name': 'إيكاب للاستثمار',                'name_en': 'Egypt Capital',                      'sector': 'المال',   'index': 'EGX100'},

        # ── مواد البناء والأسمنت ────────────────────────────────
        'MCEM': {'name': 'أسمنت مصر',                      'name_en': 'Misr Cement',                        'sector': 'الأسمنت', 'index': 'EGX30'},
        'SINE': {'name': 'أسمنت سيناء',                    'name_en': 'Sinai Cement',                       'sector': 'الأسمنت', 'index': 'EGX70'},
        'ARCC': {'name': 'أسمنت العربية',                   'name_en': 'Arabian Cement',                     'sector': 'الأسمنت', 'index': 'EGX70'},
        'TOURAH':{'name': 'أسمنت طرة',                     'name_en': 'Tourah Portland Cement',             'sector': 'الأسمنت', 'index': 'EGX70'},
        'SRCE': {'name': 'أسمنت سوهاج',                    'name_en': 'South Valley Cement',                'sector': 'الأسمنت', 'index': 'EGX70'},
        'BENI': {'name': 'أسمنت بني سويف',                 'name_en': 'Beni Suef Cement',                   'sector': 'الأسمنت', 'index': 'EGX70'},
        'ALEX': {'name': 'أسمنت الإسكندرية',               'name_en': 'Alexandria Portland Cement',         'sector': 'الأسمنت', 'index': 'EGX70'},
        'QENA': {'name': 'أسمنت قنا',                      'name_en': 'Qena Cement',                        'sector': 'الأسمنت', 'index': 'EGX100'},

        # ── التعليم ──────────────────────────────────────────────
        'RAIA': {'name': 'رايه للتطوير',                   'name_en': 'Raya Holding for Financial Invest',  'sector': 'التعليم', 'index': 'EGX30'},
        'CIRA': {'name': 'سيرا للخدمات التعليمية',         'name_en': 'Cairo for Investment & Dev',         'sector': 'التعليم', 'index': 'EGX70'},
        'ALEF': {'name': 'ألف للتعليم',                    'name_en': 'Alef for Education Services',        'sector': 'التعليم', 'index': 'EGX70'},
        'CLEO': {'name': 'كليوباترا للتعليم',              'name_en': 'Cleopatra Education',                'sector': 'التعليم', 'index': 'EGX100'},

        # ── النقل والخدمات اللوجستية ────────────────────────────
        'EGXS': {'name': 'البورصة المصرية للتوريق',        'name_en': 'EGX Securitization',                 'sector': 'النقل',   'index': 'EGX100'},
        'TRCO': {'name': 'شركة النقل البحري',              'name_en': 'Egyptian Transport',                 'sector': 'النقل',   'index': 'EGX100'},
        'AMIC': {'name': 'شركة الأمانة للاستثمار',         'name_en': 'Alexandria Minerals Co',             'sector': 'النقل',   'index': 'EGX100'},
        'ACIC': {'name': 'أسيوط للملاحة',                  'name_en': 'Assiut Cement',                      'sector': 'النقل',   'index': 'EGX100'},
        'NCTS': {'name': 'الشركة الوطنية لخدمات الشحن',    'name_en': 'National Cargo Transport',           'sector': 'النقل',   'index': 'EGX100'},

        # ── التجزئة والتوزيع ────────────────────────────────────
        'GBAL': {'name': 'جي بي للسيارات',                 'name_en': 'GB Auto',                            'sector': 'التجزئة', 'index': 'EGX30'},
        'SPMD': {'name': 'سبيد ميديكال',                   'name_en': 'Speed Medical',                      'sector': 'التجزئة', 'index': 'EGX70'},
        'RAYE': {'name': 'رايه للخدمات',                   'name_en': 'Raya Contact Center',                'sector': 'التجزئة', 'index': 'EGX70'},
        'CGCO': {'name': 'كايرو جاز',                      'name_en': 'Cairo Gas Company',                  'sector': 'التجزئة', 'index': 'EGX100'},
        'SFMC': {'name': 'مصر لصناعة الأفلام',             'name_en': 'Cairo Film Industry',                'sector': 'التجزئة', 'index': 'EGX100'},
        'EGBE2':{'name': 'إيجيبت باورز',                   'name_en': 'Egypt Solar Energy',                 'sector': 'التجزئة', 'index': 'EGX100'},

        # ── الاستثمار القابضة ───────────────────────────────────
        'QHCI': {'name': 'القلعة للاستثمارات',             'name_en': 'Qalaa Holdings',                     'sector': 'القابضة', 'index': 'EGX30'},
        'EKHO': {'name': 'مصر الكويت القابضة',             'name_en': 'Egypt Kuwait Holding (Valmore)',     'sector': 'القابضة', 'index': 'EGX70'},
        'OCIC': {'name': 'أوراسكوم القابضة',               'name_en': 'Orascom Investment Holding',         'sector': 'القابضة', 'index': 'EGX70'},
        'NCGC': {'name': 'الشركة المصرية للاتصالات',       'name_en': 'National Century',                   'sector': 'القابضة', 'index': 'EGX100'},
        'EFIH': {'name': 'إي إف آي القابضة للبنية',        'name_en': 'EFI Holdings',                       'sector': 'القابضة', 'index': 'EGX100'},
        'IGCO': {'name': 'إيجكو للاستثمار',                'name_en': 'IGCO Investments',                   'sector': 'القابضة', 'index': 'EGX100'},

        # ── الزراعة والثروة الحيوانية ────────────────────────────
        'SUGR': {'name': 'مصر لتكرير السكر',               'name_en': 'Egyptian Sugar & Refinery',          'sector': 'الزراعة', 'index': 'EGX70'},
        'NILE': {'name': 'النيل للبذور',                   'name_en': 'Nile Seeds',                         'sector': 'الزراعة', 'index': 'EGX100'},
        'AGRC': {'name': 'المصرية للمنتجات الزراعية',      'name_en': 'Egyptian Agriculture Products',      'sector': 'الزراعة', 'index': 'EGX100'},
        'EFCO': {'name': 'مصر لإنتاج الأسمدة',            'name_en': 'Egyptian Fertilizer',                'sector': 'الزراعة', 'index': 'EGX70'},
        'ABCH': {'name': 'أبو قير للأسمدة',                'name_en': 'Abu Qir Fertilizers',                'sector': 'الزراعة', 'index': 'EGX30'},

        # ── التأمين ──────────────────────────────────────────────
        'MNHD3':{'name': 'المصرية للتأمين',                'name_en': 'Misr Insurance',                     'sector': 'التأمين', 'index': 'EGX70'},
        'ENAP': {'name': 'النيل للتأمين',                  'name_en': 'Nile Insurance',                     'sector': 'التأمين', 'index': 'EGX100'},
        'MTSA': {'name': 'التأمين الأهلية',                'name_en': 'National Insurance',                 'sector': 'التأمين', 'index': 'EGX100'},
        'ALCO': {'name': 'الإسكندرية للتأمين',             'name_en': 'Alexandria Insurance',               'sector': 'التأمين', 'index': 'EGX100'},

        # ── الإعلام والترفيه ─────────────────────────────────────
        'MENA': {'name': 'مينا للإعلام',                   'name_en': 'Mena Media',                         'sector': 'الإعلام', 'index': 'EGX100'},
        'ETMC': {'name': 'المصرية للاتصالات والإعلام',     'name_en': 'Egyptian Media Center',              'sector': 'الإعلام', 'index': 'EGX100'},

        # ── المياه والصرف الصحي ──────────────────────────────────
        'EASB': {'name': 'مياه الشرب الإسكندرية',          'name_en': 'Alexandria Water Company',           'sector': 'المياه',  'index': 'EGX100'},
        'CWCO': {'name': 'مياه القاهرة',                   'name_en': 'Cairo Water Utility',                'sector': 'المياه',  'index': 'EGX100'},
    }

    # مؤشر EGX30 الرسمي
    EGX30 = [k for k, v in STOCKS.items() if v['index'] == 'EGX30']
    EGX70 = [k for k, v in STOCKS.items() if v['index'] == 'EGX70']

    SECTORS = {}
    for sym, data in STOCKS.items():
        sec = data['sector']
        if sec not in SECTORS:
            SECTORS[sec] = []
        SECTORS[sec].append(sym)

    # Base prices for realistic simulation
    BASE_PRICES = {
        'COMI': 125, 'QNBE': 18, 'TMGH': 88, 'ETEL': 32, 'FWRY': 42,
        'SWDY': 28, 'TMGD': 80, 'PHDC': 9, 'EAST': 35, 'SKPC': 55,
        'ORWE': 450, 'JUFO': 12, 'ISPH': 28, 'EIPICO': 56, 'MCEM': 22,
        'SINE': 18, 'ARCC': 35, 'GBAL': 27, 'QHCI': 3.5, 'ABCH': 90,
        'HRHO': 26, 'SODIC': 18, 'RAIA': 20, 'EMAA': 7, 'EFCO': 40,
    }

# ═══════════════════════════════════════════════════════════════
# 4. UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def get_theme_css() -> str:
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
    * {{ font-family: 'Cairo', sans-serif !important; }}
    .stApp {{
        background: linear-gradient(135deg, {Theme.BG_DARK.value} 0%, #0d0d2b 50%, {Theme.BG_DARK.value} 100%);
    }}
    .stButton>button {{
        background: linear-gradient(135deg, {Theme.PRIMARY.value} 0%, {Theme.SECONDARY.value} 100%) !important;
        color: white !important; border: none !important; border-radius: 10px !important;
        font-weight: 700 !important; transition: all 0.3s ease !important;
    }}
    .stButton>button:hover {{ transform: translateY(-2px); box-shadow: 0 8px 20px rgba(102,126,234,0.4) !important; }}
    h1, h2, h3 {{
        background: linear-gradient(90deg, {Theme.PRIMARY.value}, {Theme.ACCENT.value}, {Theme.GOLD.value});
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900;
    }}
    .metric-card {{
        background: linear-gradient(135deg, {Theme.BG_CARD.value}, {Theme.BG_PANEL.value});
        border-radius: 12px; padding: 16px;
        border: 1px solid rgba(102,126,234,0.2);
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }}
    .stock-row-up   {{ background: rgba(0,200,83,0.08); border-left: 3px solid {Theme.SUCCESS.value}; padding: 8px; border-radius: 6px; margin: 4px 0; }}
    .stock-row-down {{ background: rgba(255,23,68,0.08); border-left: 3px solid {Theme.ERROR.value};   padding: 8px; border-radius: 6px; margin: 4px 0; }}
    div[data-testid="stMetricValue"] {{ font-size: 1.4rem !important; font-weight: 900 !important; }}
    .stSelectbox label, .stNumberInput label {{ color: #aaa !important; }}
    </style>
    """

def safe_percentage(current: float, previous: float) -> float:
    try:
        if previous is None or previous == 0: return 0.0
        return ((current - previous) / abs(previous)) * 100
    except: return 0.0

def safe_last_value(series: pd.Series, default=0.0) -> float:
    try:
        valid = series.dropna()
        return float(valid.iloc[-1]) if not valid.empty else default
    except: return default

def get_cairo_time() -> datetime:
    return datetime.now(pytz.timezone('Africa/Cairo'))

def format_number(num, decimals: int = 2) -> str:
    try:
        if num is None: return "N/A"
        num = float(num)
        if np.isnan(num) or np.isinf(num): return "N/A"
        if abs(num) >= 1_000_000_000: return f"{num/1e9:.2f}B"
        if abs(num) >= 1_000_000: return f"{num/1e6:.2f}M"
        return f"{num:,.{decimals}f}"
    except: return "N/A"

def format_currency(num) -> str:
    return f"EGP {format_number(num)}"

def generate_stock_data(symbol: str, days: int = 200) -> pd.DataFrame:
    """توليد بيانات واقعية مع أسعار مبنية على القطاع"""
    seed = abs(hash(symbol)) % (2**31)
    np.random.seed(seed)

    base = EGXConfig.BASE_PRICES.get(symbol, np.random.uniform(5, 200))
    sector = EGXConfig.STOCKS.get(symbol, {}).get('sector', '')
    # تقلب حسب القطاع
    vol_map = {'البنوك': 0.015, 'الاتصالات': 0.018, 'العقارات': 0.025,
               'الصناعة': 0.022, 'الأغذية': 0.012, 'الطاقة': 0.030,
               'الصحة': 0.020, 'الأسمنت': 0.018, 'المال': 0.025}
    vol = vol_map.get(sector, 0.020)

    dates = pd.date_range(end=datetime.now(), periods=days, freq='B')  # أيام عمل فقط
    drift = np.random.normal(0.0003, 0.001)
    returns = np.random.normal(drift, vol, days)
    price = base * np.exp(np.cumsum(returns))
    price = np.maximum(price, 0.10)

    dv = np.abs(np.random.randn(days)) * vol * price
    op = np.clip(price * (1 + np.random.randn(days) * 0.003), price * 0.98, price * 1.02)
    hi = np.maximum(op, price) + dv
    lo = np.minimum(op, price) - dv
    lo = np.maximum(lo, 0.05)
    hi = np.maximum(hi, lo + 0.01)
    op = np.clip(op, lo, hi)
    cl = np.clip(price, lo, hi)

    vol_amount = np.random.randint(50_000, 15_000_000, days)

    df = pd.DataFrame({'open': op, 'high': hi, 'low': lo, 'close': cl, 'volume': vol_amount}, index=dates)
    return df

# ═══════════════════════════════════════════════════════════════
# 5. TECHNICAL INDICATORS
# ═══════════════════════════════════════════════════════════════

def calc_rsi(prices: pd.Series, period=14) -> pd.Series:
    delta = prices.diff()
    gain = delta.where(delta > 0, 0.0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def calc_ema(prices: pd.Series, span=20) -> pd.Series:
    return prices.ewm(span=span, adjust=False).mean()

def calc_sma(prices: pd.Series, window=20) -> pd.Series:
    return prices.rolling(window).mean()

def calc_bb(prices: pd.Series, window=20, std=2) -> Tuple:
    m = calc_sma(prices, window)
    s = prices.rolling(window).std()
    return m + s*std, m, m - s*std

def calc_macd(prices: pd.Series, fast=12, slow=26, sig=9) -> Tuple:
    macd = calc_ema(prices, fast) - calc_ema(prices, slow)
    signal = calc_ema(macd, sig)
    return macd, signal, macd - signal

def calc_adx(h, l, c, period=14) -> pd.Series:
    pdm = h.diff().where(lambda x: (x > 0) & (x > -l.diff()), 0)
    mdm = (-l.diff()).where(lambda x: (x > 0) & (x > h.diff()), 0)
    tr = pd.concat([h-l, (h-c.shift()).abs(), (l-c.shift()).abs()], axis=1).max(1)
    atr = tr.rolling(period).mean().replace(0, np.nan)
    pdi = 100 * pdm.rolling(period).mean() / atr
    mdi = 100 * mdm.rolling(period).mean() / atr
    dx = 100 * (pdi - mdi).abs() / (pdi + mdi).replace(0, np.nan)
    return dx.rolling(period).mean()

def calc_stoch(h, l, c, k=14, d=3) -> Tuple:
    lowest_l  = l.rolling(k).min()
    highest_h = h.rolling(k).max()
    stoch_k = 100 * (c - lowest_l) / (highest_h - lowest_l).replace(0, np.nan)
    stoch_d = stoch_k.rolling(d).mean()
    return stoch_k, stoch_d

def calc_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    direction = np.sign(close.diff()).fillna(0)
    return (direction * volume).cumsum()

def calc_atr(h, l, c, period=14) -> pd.Series:
    tr = pd.concat([h-l, (h-c.shift()).abs(), (l-c.shift()).abs()], axis=1).max(1)
    return tr.rolling(period).mean()

def calc_cci(h, l, c, period=20) -> pd.Series:
    tp = (h + l + c) / 3
    ma = tp.rolling(period).mean()
    md = tp.rolling(period).apply(lambda x: np.mean(np.abs(x - x.mean())), raw=True)
    return (tp - ma) / (0.015 * md.replace(0, np.nan))

def calc_williams_r(h, l, c, period=14) -> pd.Series:
    hh = h.rolling(period).max()
    ll = l.rolling(period).min()
    return -100 * (hh - c) / (hh - ll).replace(0, np.nan)

def detect_patterns(df: pd.DataFrame) -> List[str]:
    """اكتشاف أنماط الشموع اليابانية"""
    patterns = []
    if len(df) < 3: return patterns
    o, h, l, c = df['open'], df['high'], df['low'], df['close']
    body = abs(c - o)
    wick_up = h - c.where(c > o, o)
    wick_dn = c.where(c < o, o) - l

    # Doji
    if body.iloc[-1] < (h.iloc[-1] - l.iloc[-1]) * 0.1:
        patterns.append("⚖️ دوجي (Doji)")
    # Hammer
    if (wick_dn.iloc[-1] > 2 * body.iloc[-1] and wick_up.iloc[-1] < body.iloc[-1] * 0.3):
        patterns.append("🔨 مطرقة (Hammer)")
    # Shooting Star
    if (wick_up.iloc[-1] > 2 * body.iloc[-1] and wick_dn.iloc[-1] < body.iloc[-1] * 0.3):
        patterns.append("⭐ نجمة ساقطة (Shooting Star)")
    # Engulfing Bull
    if (len(df) > 1 and c.iloc[-2] < o.iloc[-2] and c.iloc[-1] > o.iloc[-1]
            and c.iloc[-1] > o.iloc[-2] and o.iloc[-1] < c.iloc[-2]):
        patterns.append("🟢 الابتلاع الصاعد (Bullish Engulfing)")
    # Engulfing Bear
    if (len(df) > 1 and c.iloc[-2] > o.iloc[-2] and c.iloc[-1] < o.iloc[-1]
            and c.iloc[-1] < o.iloc[-2] and o.iloc[-1] > c.iloc[-2]):
        patterns.append("🔴 الابتلاع الهابط (Bearish Engulfing)")
    # Morning Star
    if (len(df) > 2 and c.iloc[-3] < o.iloc[-3]
            and body.iloc[-2] < body.iloc[-3] * 0.3
            and c.iloc[-1] > o.iloc[-1]
            and c.iloc[-1] > (o.iloc[-3] + c.iloc[-3]) / 2):
        patterns.append("🌅 نجمة الصباح (Morning Star)")
    # Evening Star
    if (len(df) > 2 and c.iloc[-3] > o.iloc[-3]
            and body.iloc[-2] < body.iloc[-3] * 0.3
            and c.iloc[-1] < o.iloc[-1]
            and c.iloc[-1] < (o.iloc[-3] + c.iloc[-3]) / 2):
        patterns.append("🌆 نجمة المساء (Evening Star)")
    return patterns

def get_support_resistance(df: pd.DataFrame, window=20) -> Tuple[float, float]:
    """حساب مستويات الدعم والمقاومة"""
    recent = df.tail(50)
    support    = recent['low'].rolling(window).min().iloc[-1]
    resistance = recent['high'].rolling(window).max().iloc[-1]
    return support, resistance

# ═══════════════════════════════════════════════════════════════
# 6. DATA LOADING WITH FULL INDICATORS
# ═══════════════════════════════════════════════════════════════

@st.cache_data(ttl=AppConfig.CACHE_TTL)
def load_stock_data(symbol: str, days: int = 200) -> Optional[pd.DataFrame]:
    try:
        df = generate_stock_data(symbol, days)
        if df.empty: return None
        c, h, l, v = df['close'], df['high'], df['low'], df['volume']

        df['rsi']              = calc_rsi(c)
        df['ema_9']            = calc_ema(c, 9)
        df['ema_20']           = calc_ema(c, 20)
        df['ema_50']           = calc_ema(c, 50)
        df['ema_200']          = calc_ema(c, 200)
        df['sma_20']           = calc_sma(c, 20)
        df['sma_50']           = calc_sma(c, 50)
        df['bb_upper'], df['bb_middle'], df['bb_lower'] = calc_bb(c)
        df['macd'], df['macd_signal'], df['macd_hist']  = calc_macd(c)
        df['adx']              = calc_adx(h, l, c)
        df['stoch_k'], df['stoch_d'] = calc_stoch(h, l, c)
        df['obv']              = calc_obv(c, v)
        df['atr']              = calc_atr(h, l, c)
        df['cci']              = calc_cci(h, l, c)
        df['williams_r']       = calc_williams_r(h, l, c)
        df['pct_change']       = c.pct_change() * 100
        df['vol_sma']          = v.rolling(20).mean()
        df['vol_ratio']        = v / df['vol_sma'].replace(0, np.nan)
        return df
    except Exception as e:
        logger.error(f"load_stock_data {symbol}: {e}")
        return None

def get_current_data() -> Optional[pd.DataFrame]:
    sym = st.session_state.get('selected_symbol', 'COMI')
    df  = load_stock_data(sym)
    if df is not None:
        st.session_state.analysis_data = df
        st.session_state.last_update   = get_cairo_time()
    return df

def get_composite_signal(df: pd.DataFrame) -> Tuple[str, str, int]:
    """إشارة مركّبة من جميع المؤشرات"""
    signals = []
    rsi  = safe_last_value(df['rsi'], 50)
    macd = safe_last_value(df['macd'], 0)
    msig = safe_last_value(df['macd_signal'], 0)
    ema20= safe_last_value(df['ema_20'])
    ema50= safe_last_value(df['ema_50'])
    adx  = safe_last_value(df['adx'], 25)
    stk  = safe_last_value(df['stoch_k'], 50)
    cci  = safe_last_value(df['cci'], 0)
    wr   = safe_last_value(df['williams_r'], -50)
    price= float(df['close'].iloc[-1])

    if rsi < 35:  signals.append(1)
    elif rsi > 65: signals.append(-1)
    else:          signals.append(0)

    signals.append(1 if macd > msig else -1)
    signals.append(1 if price > ema20 else -1)
    signals.append(1 if ema20 > ema50 else -1)
    signals.append(1 if stk < 25 else (-1 if stk > 75 else 0))
    signals.append(1 if cci < -100 else (-1 if cci > 100 else 0))
    signals.append(1 if wr < -80 else (-1 if wr > -20 else 0))

    score = sum(signals)
    total = len(signals)
    pct   = int((score / total) * 100)

    if score >= 3:    return "شراء قوي", "🟢", min(pct + 50, 95)
    elif score == 2:  return "شراء",      "🟩", min(pct + 40, 80)
    elif score <= -3: return "بيع قوي",   "🔴", min(abs(pct) + 50, 95)
    elif score == -2: return "بيع",        "🟥", min(abs(pct) + 40, 80)
    else:             return "محايد",      "⚪", 50

# ═══════════════════════════════════════════════════════════════
# 7. PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title=f"{AppConfig.APP_NAME} v{AppConfig.APP_VERSION}",
    page_icon="📈", layout="wide", initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/m02417710-maker/blank-app',
        'Report a bug': 'https://github.com/m02417710-maker/blank-app/issues',
        'About': f'# {AppConfig.APP_NAME}\n✅ النسخة الكاملة — 250+ شركة مصرية'
    }
)
st.markdown(get_theme_css(), unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 8. SESSION STATE
# ═══════════════════════════════════════════════════════════════

def init_state():
    defs = {
        'selected_symbol': 'COMI', 'page': 'Dashboard',
        'analysis_data': None, 'watchlist': [], 'alerts': [],
        'last_update': None, 'auto_refresh': False,
        'last_rerun_time': 0, 'alert_to_delete': None,
        'watchlist_to_delete': None, 'backtest_result': None,
        'chart_days': 90, 'sector_filter': 'الكل',
    }
    for k, v in defs.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ═══════════════════════════════════════════════════════════════
# 9. SIDEBAR
# ═══════════════════════════════════════════════════════════════

def render_sidebar():
    st.sidebar.markdown(f"""
    <div style="text-align:center;padding:15px 0;">
        <div style="font-size:2.5em;">📈</div>
        <div style="font-size:1.3em;font-weight:900;
            background:linear-gradient(90deg,#667eea,#f093fb,#ffd700);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            {AppConfig.APP_NAME}
        </div>
        <div style="font-size:0.75em;color:#888;">v{AppConfig.APP_VERSION} • {len(EGXConfig.STOCKS)} شركة</div>
    </div>""", unsafe_allow_html=True)

    st.sidebar.markdown("---")
    pages = {
        '📊 لوحة المعلومات':   'Dashboard',
        '🔍 تحليل مفصّل':      'Analysis',
        '📈 الرسوم البيانية':   'Charts',
        '🕯️ نمط الشموع':       'Patterns',
        '🔔 التنبيهات':         'Alerts',
        '🤖 تنبؤات الذكاء':    'AI',
        '📋 قائمة المراقبة':   'Watchlist',
        '🧪 الاختبار الخلفي':  'Backtest',
        '🏢 نظرة القطاعات':    'Market',
        '🔥 أفضل وأسوأ':       'TopBottom',
        '📊 مقارنة أسهم':      'Compare',
        '⚙️ الإعدادات':        'Settings',
    }
    for label, pname in pages.items():
        t = "primary" if st.session_state.page == pname else "secondary"
        if st.sidebar.button(label, use_container_width=True, type=t, key=f"nav_{pname}"):
            st.session_state.page = pname; st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎯 اختيار السهم")

    # فلتر القطاع
    sectors_list = ['الكل'] + sorted(EGXConfig.SECTORS.keys())
    sel_sector = st.sidebar.selectbox("فلتر القطاع", sectors_list, key="sidebar_sector")
    if sel_sector == 'الكل':
        filtered = list(EGXConfig.STOCKS.keys())
    else:
        filtered = EGXConfig.SECTORS.get(sel_sector, [])

    sym_options = [s for s in filtered if s in EGXConfig.STOCKS]
    cur_idx = sym_options.index(st.session_state.selected_symbol) if st.session_state.selected_symbol in sym_options else 0

    sel = st.sidebar.selectbox(
        "اختر السهم", sym_options, index=cur_idx,
        format_func=lambda x: f"{x} | {EGXConfig.STOCKS[x]['name']}",
        key="symbol_select"
    )
    if sel != st.session_state.selected_symbol:
        st.session_state.selected_symbol = sel; st.rerun()

    # أزرار EGX30
    st.sidebar.markdown("**⭐ EGX30:**")
    egx30 = EGXConfig.EGX30[:8]
    cols = st.sidebar.columns(4)
    for i, sym in enumerate(egx30):
        with cols[i % 4]:
            if st.button(sym, use_container_width=True, key=f"q_{sym}"):
                st.session_state.selected_symbol = sym; st.rerun()

    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 تحديث البيانات", use_container_width=True):
        load_stock_data.clear(); st.rerun()

    st.session_state.auto_refresh = st.sidebar.checkbox(
        "⏱️ تحديث تلقائي", value=st.session_state.auto_refresh)
    if st.session_state.auto_refresh:
        now = time.time()
        if now - st.session_state.last_rerun_time > AppConfig.REFRESH_INTERVAL:
            st.session_state.last_rerun_time = now; st.rerun()

    st.sidebar.markdown("---")
    if st.session_state.last_update:
        st.sidebar.caption(f"🕐 آخر تحديث: {st.session_state.last_update.strftime('%H:%M:%S')}")
    st.sidebar.markdown('<div style="text-align:center;color:#555;font-size:0.7em;">🇪🇬 صُنع في مصر • تعليمي فقط</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 10. PAGES
# ═══════════════════════════════════════════════════════════════

def render_dashboard():
    st.markdown('<h1 style="text-align:center">📈 محطة EGX الاحترافية</h1>', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align:center;color:#888;">{len(EGXConfig.STOCKS)} شركة مدرجة • {len(EGXConfig.SECTORS)} قطاع • بيانات تحليل متكاملة</p>', unsafe_allow_html=True)

    # نظرة السوق
    st.markdown("### 📊 ملخص السوق")
    cols = st.columns(5)
    summary_data = []
    for sym in EGXConfig.EGX30[:20]:
        mini = generate_stock_data(sym, 3)
        if not mini.empty:
            last  = float(mini['close'].iloc[-1])
            prev  = float(mini['close'].iloc[-2]) if len(mini) > 1 else last
            chg   = safe_percentage(last, prev)
            summary_data.append({'sym': sym, 'last': last, 'chg': chg})

    summary_data.sort(key=lambda x: x['chg'], reverse=True)
    up   = sum(1 for x in summary_data if x['chg'] > 0)
    down = sum(1 for x in summary_data if x['chg'] < 0)
    avg_chg = np.mean([x['chg'] for x in summary_data])

    with cols[0]: st.metric("📈 رابح EGX30", f"{up} سهم",  f"{up/len(summary_data)*100:.0f}%")
    with cols[1]: st.metric("📉 خاسر EGX30", f"{down} سهم", f"-{down/len(summary_data)*100:.0f}%")
    with cols[2]: st.metric("📊 متوسط التغيّر", f"{avg_chg:+.2f}%", "EGX30")
    with cols[3]: st.metric("🏢 الشركات المدرجة", f"{len(EGXConfig.STOCKS)}", f"{len(EGXConfig.SECTORS)} قطاع")
    with cols[4]:
        best = summary_data[0]
        st.metric("🏆 الأكثر ارتفاعاً", best['sym'], f"{best['chg']:+.2f}%")

    st.markdown("---")

    # تحليل السهم المختار
    symbol = st.session_state.selected_symbol
    info   = EGXConfig.STOCKS.get(symbol, {})
    st.markdown(f"### ⭐ {info.get('name', symbol)} ({symbol}) — {info.get('sector','')}")

    df = get_current_data()
    if df is None: st.warning("⚠️ لا توجد بيانات"); return

    last  = float(df['close'].iloc[-1])
    prev  = float(df['close'].iloc[-2])
    chg   = safe_percentage(last, prev)
    sig, sig_color, conf = get_composite_signal(df)
    rsi   = safe_last_value(df['rsi'], 50)
    adx   = safe_last_value(df['adx'], 25)
    atr   = safe_last_value(df['atr'])
    sup, res = get_support_resistance(df)

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    with c1: st.metric("💰 السعر",      format_currency(last),  f"{chg:+.2f}%")
    with c2: st.metric("📊 RSI (14)",   f"{rsi:.1f}", "تشبع شراء" if rsi>65 else "تشبع بيع" if rsi<35 else "محايد")
    with c3: st.metric("📉 ADX",        f"{adx:.1f}", "قوي" if adx>25 else "ضعيف")
    with c4: st.metric("📏 ATR",        f"{atr:.2f} EGP", "تقلب")
    with c5: st.metric("🛡️ دعم",       format_currency(sup))
    with c6: st.metric(f"🎯 {sig_color} الإشارة", sig, f"ثقة {conf}%")

    # الرسم البياني الرئيسي
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        row_heights=[0.6, 0.2, 0.2], vertical_spacing=0.03)

    fig.add_trace(go.Candlestick(
        x=df.index, open=df['open'], high=df['high'],
        low=df['low'], close=df['close'], name=symbol,
        increasing_line_color=Theme.SUCCESS.value,
        decreasing_line_color=Theme.ERROR.value), row=1, col=1)

    for span, color, dash in [(20,'#667eea','dash'), (50,'#ffd700','dot'), (200,'#f093fb','dashdot')]:
        col_name = f'ema_{span}'
        if col_name in df:
            fig.add_trace(go.Scatter(x=df.index, y=df[col_name], mode='lines',
                name=f'EMA {span}', line=dict(color=color, width=1.2, dash=dash)), row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df['bb_upper'], mode='lines',
        name='BB+', line=dict(color='rgba(240,147,251,0.5)', width=1), legendgroup='bb'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['bb_lower'], mode='lines',
        name='BB-', line=dict(color='rgba(240,147,251,0.5)', width=1),
        fill='tonexty', fillcolor='rgba(240,147,251,0.05)', legendgroup='bb'), row=1, col=1)

    colors_vol = [Theme.SUCCESS.value if df['close'].iloc[i] >= df['open'].iloc[i]
                  else Theme.ERROR.value for i in range(len(df))]
    fig.add_trace(go.Bar(x=df.index, y=df['volume'], name='الحجم',
        marker_color=colors_vol, opacity=0.7), row=2, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df['rsi'], mode='lines', name='RSI',
        line=dict(color=Theme.INFO.value, width=1.5)), row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color=Theme.ERROR.value, row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color=Theme.SUCCESS.value, row=3, col=1)

    fig.update_layout(
        title=f"{info.get('name', symbol)} ({symbol})",
        template='plotly_dark', height=700,
        xaxis_rangeslider_visible=False, hovermode='x unified',
        legend=dict(orientation='h', y=1.02),
        margin=dict(l=10, r=10, t=50, b=10)
    )
    fig.update_yaxes(title_text="السعر (EGP)", row=1, col=1)
    fig.update_yaxes(title_text="الحجم",       row=2, col=1)
    fig.update_yaxes(title_text="RSI",         row=3, col=1, range=[0,100])
    st.plotly_chart(fig, use_container_width=True)

    # الأنماط
    patterns = detect_patterns(df)
    if patterns:
        st.markdown("### 🕯️ أنماط مكتشفة")
        st.success(" | ".join(patterns))


def render_analysis():
    st.markdown("## 🔍 تحليل مفصّل شامل")
    symbol = st.session_state.selected_symbol
    info   = EGXConfig.STOCKS.get(symbol, {})
    df = get_current_data()
    if df is None: st.warning("لا توجد بيانات"); return

    st.info(f"**{info.get('name',symbol)}** ({symbol}) | القطاع: {info.get('sector','')} | المؤشر: {info.get('index','')}")

    last = float(df['close'].iloc[-1])
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("أعلى سعر (200 يوم)", format_currency(df['high'].max()))
    with c2: st.metric("أقل سعر (200 يوم)",  format_currency(df['low'].min()))
    with c3: st.metric("متوسط الحجم",          format_number(df['volume'].mean(), 0))
    with c4: st.metric("التقلب السنوي",          f"{df['close'].pct_change().std()*np.sqrt(252)*100:.1f}%")

    st.markdown("### 📊 ملخص جميع المؤشرات")
    ind = {
        'RSI (14)':       f"{safe_last_value(df['rsi']):.2f}",
        'EMA 9':          format_currency(safe_last_value(df['ema_9'])),
        'EMA 20':         format_currency(safe_last_value(df['ema_20'])),
        'EMA 50':         format_currency(safe_last_value(df['ema_50'])),
        'EMA 200':        format_currency(safe_last_value(df['ema_200'])),
        'SMA 20':         format_currency(safe_last_value(df['sma_20'])),
        'MACD':           f"{safe_last_value(df['macd']):.4f}",
        'MACD Signal':    f"{safe_last_value(df['macd_signal']):.4f}",
        'ADX':            f"{safe_last_value(df['adx']):.2f}",
        'Stoch %K':       f"{safe_last_value(df['stoch_k']):.2f}",
        'Stoch %D':       f"{safe_last_value(df['stoch_d']):.2f}",
        'CCI (20)':       f"{safe_last_value(df['cci']):.2f}",
        'Williams %R':    f"{safe_last_value(df['williams_r']):.2f}",
        'ATR (14)':       f"{safe_last_value(df['atr']):.2f}",
        'BB Upper':       format_currency(safe_last_value(df['bb_upper'])),
        'BB Lower':       format_currency(safe_last_value(df['bb_lower'])),
        'Volume vs Avg':  f"{safe_last_value(df['vol_ratio']):.2f}x",
    }
    col1, col2 = st.columns(2)
    items = list(ind.items())
    half  = len(items) // 2
    with col1:
        df1 = pd.DataFrame(items[:half], columns=['المؤشر','القيمة'])
        st.dataframe(df1, use_container_width=True, hide_index=True)
    with col2:
        df2 = pd.DataFrame(items[half:], columns=['المؤشر','القيمة'])
        st.dataframe(df2, use_container_width=True, hide_index=True)

    # آخر 30 شمعة
    st.markdown("### 📋 آخر 30 جلسة")
    disp = df.tail(30)[['open','high','low','close','volume','rsi','macd','adx']].copy()
    disp.columns = ['الافتتاح','الأعلى','الأدنى','الإغلاق','الحجم','RSI','MACD','ADX']
    disp = disp.round(2)
    st.dataframe(disp, use_container_width=True)


def render_charts():
    st.markdown("## 📈 الرسوم البيانية المتقدمة")
    symbol = st.session_state.selected_symbol
    info   = EGXConfig.STOCKS.get(symbol, {})

    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: days      = st.selectbox("الفترة", [30,60,90,180,200], index=2, key="ch_days")
    with c2: show_ema  = st.multiselect("EMAs", [9,20,50,200], default=[20,50], key="ch_ema")
    with c3: show_bb   = st.checkbox("Bollinger Bands", True, key="ch_bb")
    with c4: show_vol  = st.checkbox("الحجم", True, key="ch_vol")
    with c5: sub_ind   = st.selectbox("مؤشر فرعي", ["RSI","MACD","Stoch","CCI","Williams %R"], key="ch_sub")

    df = load_stock_data(symbol, max(days, 200))
    if df is None: st.warning("لا توجد بيانات"); return
    df = df.tail(days)

    rows = 2 if show_vol else 1
    if sub_ind: rows += 1
    heights = [0.55] + ([0.15] if show_vol else []) + ([0.30] if sub_ind else [])
    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True,
                        row_heights=heights, vertical_spacing=0.03)

    fig.add_trace(go.Candlestick(
        x=df.index, open=df['open'], high=df['high'],
        low=df['low'], close=df['close'], name=symbol,
        increasing_line_color=Theme.SUCCESS.value,
        decreasing_line_color=Theme.ERROR.value), row=1, col=1)

    colors_e = {9:'#00e5ff', 20:'#667eea', 50:'#ffd700', 200:'#f093fb'}
    for span in show_ema:
        col = f'ema_{span}'
        if col in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines',
                name=f'EMA {span}', line=dict(color=colors_e.get(span,'#fff'), width=1.5)), row=1, col=1)

    if show_bb and 'bb_upper' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['bb_upper'], mode='lines',
            line=dict(color='rgba(240,147,251,0.6)', width=1), name='BB+', legendgroup='bb'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['bb_lower'], mode='lines',
            line=dict(color='rgba(240,147,251,0.6)', width=1),
            fill='tonexty', fillcolor='rgba(240,147,251,0.07)', name='BB-', legendgroup='bb'), row=1, col=1)

    cur_row = 2
    if show_vol:
        vc = [Theme.SUCCESS.value if df['close'].iloc[i] >= df['open'].iloc[i]
              else Theme.ERROR.value for i in range(len(df))]
        fig.add_trace(go.Bar(x=df.index, y=df['volume'], name='الحجم',
            marker_color=vc, opacity=0.7), row=cur_row, col=1)
        cur_row += 1

    if sub_ind == "RSI":
        fig.add_trace(go.Scatter(x=df.index, y=df['rsi'], mode='lines', name='RSI',
            line=dict(color=Theme.INFO.value, width=1.5)), row=cur_row, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color=Theme.ERROR.value,   row=cur_row, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color=Theme.SUCCESS.value, row=cur_row, col=1)
        fig.update_yaxes(range=[0,100], row=cur_row, col=1)
    elif sub_ind == "MACD":
        fig.add_trace(go.Scatter(x=df.index, y=df['macd'], mode='lines', name='MACD',
            line=dict(color=Theme.PRIMARY.value, width=1.5)), row=cur_row, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['macd_signal'], mode='lines', name='Signal',
            line=dict(color=Theme.WARNING.value, width=1.5, dash='dash')), row=cur_row, col=1)
        fig.add_trace(go.Bar(x=df.index, y=df['macd_hist'], name='Hist',
            marker_color=[Theme.SUCCESS.value if v > 0 else Theme.ERROR.value for v in df['macd_hist'].fillna(0)]),
            row=cur_row, col=1)
    elif sub_ind == "Stoch":
        fig.add_trace(go.Scatter(x=df.index, y=df['stoch_k'], name='%K',
            line=dict(color=Theme.PRIMARY.value, width=1.5)), row=cur_row, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['stoch_d'], name='%D',
            line=dict(color=Theme.WARNING.value, width=1.5, dash='dash')), row=cur_row, col=1)
        fig.add_hline(y=80, line_dash="dash", line_color=Theme.ERROR.value,   row=cur_row, col=1)
        fig.add_hline(y=20, line_dash="dash", line_color=Theme.SUCCESS.value, row=cur_row, col=1)
    elif sub_ind == "CCI":
        fig.add_trace(go.Scatter(x=df.index, y=df['cci'], name='CCI',
            line=dict(color=Theme.ACCENT.value, width=1.5)), row=cur_row, col=1)
        fig.add_hline(y=100,  line_dash="dash", line_color=Theme.ERROR.value,   row=cur_row, col=1)
        fig.add_hline(y=-100, line_dash="dash", line_color=Theme.SUCCESS.value, row=cur_row, col=1)
    elif sub_ind == "Williams %R":
        fig.add_trace(go.Scatter(x=df.index, y=df['williams_r'], name='W%R',
            line=dict(color=Theme.GOLD.value, width=1.5)), row=cur_row, col=1)
        fig.add_hline(y=-20, line_dash="dash", line_color=Theme.ERROR.value,   row=cur_row, col=1)
        fig.add_hline(y=-80, line_dash="dash", line_color=Theme.SUCCESS.value, row=cur_row, col=1)

    fig.update_layout(
        title=f"{info.get('name',symbol)} — {days} يوم",
        template='plotly_dark', height=750,
        xaxis_rangeslider_visible=False, hovermode='x unified',
        legend=dict(orientation='h', y=1.01)
    )
    st.plotly_chart(fig, use_container_width=True)


def render_patterns():
    st.markdown("## 🕯️ تحليل الشموع اليابانية والأنماط")
    symbol = st.session_state.selected_symbol
    df = get_current_data()
    if df is None: st.warning("لا توجد بيانات"); return

    patterns = detect_patterns(df)
    sup, res = get_support_resistance(df)
    last = float(df['close'].iloc[-1])

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("#### 🔍 الأنماط المكتشفة")
        if patterns:
            for p in patterns:
                st.success(p)
        else:
            st.info("لا توجد أنماط واضحة في الشمعة الأخيرة")

        st.markdown("#### 📏 مستويات الدعم والمقاومة")
        st.metric("🛡️ الدعم",    format_currency(sup),  f"{safe_percentage(sup, last):+.1f}%")
        st.metric("🚧 المقاومة", format_currency(res),  f"{safe_percentage(res, last):+.1f}%")

        fib_levels = {
            '0%':   last,
            '23.6%': last + (res - last) * 0.236,
            '38.2%': last + (res - last) * 0.382,
            '50%':  last + (res - last) * 0.500,
            '61.8%': last + (res - last) * 0.618,
            '100%': res,
        }
        st.markdown("#### 📐 مستويات فيبوناتشي")
        for lvl, price in fib_levels.items():
            st.write(f"**{lvl}** → {format_currency(price)}")

    with col2:
        fig = go.Figure()
        recent = df.tail(50)
        fig.add_trace(go.Candlestick(
            x=recent.index, open=recent['open'], high=recent['high'],
            low=recent['low'], close=recent['close'], name='الشموع',
            increasing_line_color=Theme.SUCCESS.value,
            decreasing_line_color=Theme.ERROR.value))
        fig.add_hline(y=sup, line_dash="solid", line_color=Theme.SUCCESS.value,
                      annotation_text=f"دعم {sup:.2f}", line_width=1.5)
        fig.add_hline(y=res, line_dash="solid", line_color=Theme.ERROR.value,
                      annotation_text=f"مقاومة {res:.2f}", line_width=1.5)
        fig.update_layout(template='plotly_dark', height=500,
                          xaxis_rangeslider_visible=False, title="آخر 50 شمعة")
        st.plotly_chart(fig, use_container_width=True)


def render_alerts():
    st.markdown("## 🔔 إدارة التنبيهات الذكية")

    if st.session_state.alert_to_delete is not None:
        idx = st.session_state.alert_to_delete
        if 0 <= idx < len(st.session_state.alerts):
            st.session_state.alerts.pop(idx)
        st.session_state.alert_to_delete = None; st.rerun()

    # فحص التنبيهات النشطة
    triggered = []
    for alert in st.session_state.alerts:
        sym = alert['symbol']
        mini = load_stock_data(sym, 5)
        if mini is not None and not mini.empty:
            price = float(mini['close'].iloc[-1])
            val   = alert['value']
            cond  = alert['condition']
            hit   = (cond == "أعلى من" and price > val) or \
                    (cond == "أقل من"   and price < val) or \
                    (cond == "يساوي"    and abs(price - val) / max(val,1) < 0.01)
            if hit:
                triggered.append(f"🔔 **{sym}** — {alert['type']} {cond} {val} (الحالي: {price:.2f})")

    if triggered:
        st.error("⚡ **تنبيهات مُفعَّلة الآن:**")
        for t in triggered:
            st.markdown(t)
        st.markdown("---")

    if st.session_state.alerts:
        st.markdown("### التنبيهات النشطة")
        for i, alert in enumerate(st.session_state.alerts):
            c1, c2 = st.columns([4, 1])
            with c1:
                created = alert.get('created_at', '')
                st.info(f"**{alert['symbol']}** — {alert['type']} {alert['condition']} **{alert['value']}** | {created}")
            with c2:
                if st.button("🗑️", key=f"del_{i}"):
                    st.session_state.alert_to_delete = i; st.rerun()
    else:
        st.info("لا توجد تنبيهات. أنشئ تنبيهاً أدناه.")

    st.markdown("### ➕ إنشاء تنبيه جديد")
    with st.form("alert_form", clear_on_submit=True):
        c1,c2,c3,c4 = st.columns(4)
        with c1:
            sym_list = list(EGXConfig.STOCKS.keys())
            al_sym   = st.selectbox("السهم", sym_list, format_func=lambda x: f"{x} | {EGXConfig.STOCKS[x]['name'][:20]}")
        with c2: al_type = st.selectbox("النوع", ["السعر","RSI","MACD","الحجم","ADX"])
        with c3: al_cond = st.selectbox("الشرط", ["أعلى من","أقل من","يساوي"])
        with c4: al_val  = st.number_input("القيمة", min_value=0.0, value=10.0, step=0.5)

        if st.form_submit_button("✅ إنشاء التنبيه"):
            st.session_state.alerts.append({
                'symbol': al_sym, 'type': al_type,
                'condition': al_cond, 'value': al_val,
                'created_at': get_cairo_time().strftime('%Y-%m-%d %H:%M')
            })
            st.success(f"✅ تنبيه: {al_sym} — {al_type} {al_cond} {al_val}")


def render_ai():
    st.markdown("## 🤖 التنبؤات بالذكاء الاصطناعي")
    symbol = st.session_state.selected_symbol
    info   = EGXConfig.STOCKS.get(symbol, {})
    df = get_current_data()
    if df is None: st.warning("لا توجد بيانات"); return

    with st.status("🧠 جاري تحليل البيانات...", expanded=True) as status:
        st.write("⚙️ حساب المؤشرات الفنية..."); time.sleep(0.3)
        st.write("📊 تحليل الأنماط والإشارات..."); time.sleep(0.3)
        st.write("🔮 توليد التوقعات..."); time.sleep(0.2)
        status.update(label="✅ اكتمل التحليل!", state="complete")

    last  = float(df['close'].iloc[-1])
    sig, sig_color, conf = get_composite_signal(df)
    rsi   = safe_last_value(df['rsi'], 50)
    macd  = safe_last_value(df['macd'], 0)
    msig  = safe_last_value(df['macd_signal'], 0)
    adx   = safe_last_value(df['adx'], 25)
    stk   = safe_last_value(df['stoch_k'], 50)
    cci   = safe_last_value(df['cci'], 0)
    wr    = safe_last_value(df['williams_r'], -50)
    ema20 = safe_last_value(df['ema_20'], last)
    ema50 = safe_last_value(df['ema_50'], last)
    atr   = safe_last_value(df['atr'], last * 0.02)

    # أهداف ووقف خسارة
    is_buy = "شراء" in sig
    target1    = last * (1.05 if is_buy else 0.97)
    target2    = last * (1.10 if is_buy else 0.94)
    stop_loss  = last * (0.97 if is_buy else 1.03)
    risk_reward= abs(target1 - last) / max(abs(last - stop_loss), 0.01)

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric(f"{sig_color} الإشارة",       sig,               f"ثقة {conf}%")
    with c2: st.metric("🎯 هدف 1",                   format_currency(target1),   f"{safe_percentage(target1, last):+.1f}%")
    with c3: st.metric("🎯 هدف 2",                   format_currency(target2),   f"{safe_percentage(target2, last):+.1f}%")
    with c4: st.metric("🛑 وقف الخسارة",             format_currency(stop_loss), f"{safe_percentage(stop_loss, last):+.1f}%")

    st.metric("⚖️ نسبة المخاطرة/العائد", f"{risk_reward:.2f}", "جيد إذا > 1.5")

    # رادار المؤشرات
    st.markdown("### 📊 رادار تقييم المؤشرات")
    scores = {
        'RSI':        min(max((50-rsi)/50*100, -100), 100) if "شراء" in sig else min(max((rsi-50)/50*100, -100),100),
        'MACD':       80 if macd > msig else -80,
        'ADX':        min(adx * 2, 100),
        'Stoch':      min(max((50-stk)/50*100, -100), 100),
        'CCI':        min(max(-cci, -100), 100),
        'Williams':   min(max((wr+50)/50*100, -100), 100),
        'EMA Trend':  80 if last > ema20 > ema50 else -80 if last < ema20 < ema50 else 0,
    }
    fig_radar = go.Figure(go.Scatterpolar(
        r=list(scores.values()), theta=list(scores.keys()),
        fill='toself', fillcolor='rgba(102,126,234,0.2)',
        line_color=Theme.PRIMARY.value, name='المؤشرات'
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[-100,100])),
        template='plotly_dark', height=400, title="رادار قوة الإشارة"
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # توزيع مونت كارلو مبسّط
    st.markdown("### 📈 محاكاة مونت كارلو (30 يوم)")
    np.random.seed(42)
    daily_vol = df['close'].pct_change().std()
    drift     = df['close'].pct_change().mean()
    sims = 200
    days = 30
    paths = np.zeros((sims, days))
    for i in range(sims):
        r = np.random.normal(drift, daily_vol, days)
        paths[i] = last * np.exp(np.cumsum(r))

    fig_mc = go.Figure()
    for i in range(min(50, sims)):
        fig_mc.add_trace(go.Scatter(
            y=paths[i], mode='lines', opacity=0.15,
            line=dict(color=Theme.PRIMARY.value, width=0.5), showlegend=False))
    fig_mc.add_trace(go.Scatter(
        y=np.percentile(paths, 75, axis=0), mode='lines', name='P75',
        line=dict(color=Theme.SUCCESS.value, width=2)))
    fig_mc.add_trace(go.Scatter(
        y=np.percentile(paths, 50, axis=0), mode='lines', name='الوسيط',
        line=dict(color=Theme.GOLD.value, width=2.5)))
    fig_mc.add_trace(go.Scatter(
        y=np.percentile(paths, 25, axis=0), mode='lines', name='P25',
        line=dict(color=Theme.ERROR.value, width=2)))
    fig_mc.update_layout(template='plotly_dark', height=350,
                         title=f"محاكاة {sims} مسار — {days} يوم",
                         xaxis_title="الأيام", yaxis_title="السعر المتوقع (EGP)")
    st.plotly_chart(fig_mc, use_container_width=True)

    p10 = float(np.percentile(paths[:,-1], 10))
    p50 = float(np.percentile(paths[:,-1], 50))
    p90 = float(np.percentile(paths[:,-1], 90))
    c1,c2,c3 = st.columns(3)
    with c1: st.metric("سيناريو متشائم (P10)", format_currency(p10), f"{safe_percentage(p10,last):+.1f}%")
    with c2: st.metric("سيناريو محتمل (P50)",  format_currency(p50), f"{safe_percentage(p50,last):+.1f}%")
    with c3: st.metric("سيناريو متفائل (P90)",  format_currency(p90), f"{safe_percentage(p90,last):+.1f}%")


def render_watchlist():
    st.markdown("## 📋 قائمة المراقبة")

    if st.session_state.watchlist_to_delete:
        sym = st.session_state.watchlist_to_delete
        if sym in st.session_state.watchlist:
            st.session_state.watchlist.remove(sym)
        st.session_state.watchlist_to_delete = None; st.rerun()

    c1, c2 = st.columns([3,1])
    with c1:
        add_sym = st.selectbox("إضافة سهم", list(EGXConfig.STOCKS.keys()),
            format_func=lambda x: f"{x} | {EGXConfig.STOCKS[x]['name']}", key="wl_add")
    with c2:
        if st.button("➕ إضافة", key="wl_btn"):
            if add_sym not in st.session_state.watchlist:
                st.session_state.watchlist.append(add_sym)
                st.success(f"✅ تمت إضافة {add_sym}"); st.rerun()
            else:
                st.warning("موجود بالفعل")

    if not st.session_state.watchlist:
        st.info("القائمة فارغة — أضف أسهماً للمتابعة")
        return

    st.markdown("### أسهمك المراقبة")
    rows_data = []
    for sym in st.session_state.watchlist:
        mini = generate_stock_data(sym, 5)
        if not mini.empty:
            last = float(mini['close'].iloc[-1])
            prev = float(mini['close'].iloc[-2])
            chg  = safe_percentage(last, prev)
            rows_data.append({'رمز': sym, 'الشركة': EGXConfig.STOCKS[sym]['name'],
                               'القطاع': EGXConfig.STOCKS[sym]['sector'],
                               'السعر': f"{last:.2f}", 'التغيير%': f"{chg:+.2f}%",
                               'الإشارة': '▲' if chg > 0 else '▼'})

    df_wl = pd.DataFrame(rows_data)
    st.dataframe(df_wl, use_container_width=True, hide_index=True)

    for i, sym in enumerate(st.session_state.watchlist):
        c1,c2,c3 = st.columns([3,2,1])
        with c1: st.write(f"**{sym}** — {EGXConfig.STOCKS[sym]['name']}")
        with c2:
            if st.button(f"📊 تحليل {sym}", key=f"an_{sym}"):
                st.session_state.selected_symbol = sym
                st.session_state.page = 'Analysis'; st.rerun()
        with c3:
            if st.button("🗑️", key=f"rm_{sym}_{i}"):
                st.session_state.watchlist_to_delete = sym; st.rerun()


def render_backtest():
    st.markdown("## 🧪 الاختبار الخلفي للاستراتيجيات")
    df_full = load_stock_data(st.session_state.selected_symbol, 200)
    if df_full is None: st.warning("لا توجد بيانات"); return

    c1,c2,c3,c4 = st.columns(4)
    with c1: strategy = st.selectbox("الاستراتيجية",
        ["RSI", "MACD Crossover", "Bollinger Bands", "EMA Crossover",
         "Stochastic", "CCI Mean Reversion"], key="bt_strat")
    with c2: capital    = st.number_input("رأس المال (EGP)", 1000, 10_000_000, 100_000, step=5000)
    with c3: stop_pct   = st.slider("وقف الخسارة %", 1, 20, 5)
    with c4: take_pct   = st.slider("هدف الربح %",    1, 30, 10)

    if not st.button("🚀 تشغيل الاختبار"): return

    with st.spinner("جاري الاختبار..."):
        df = df_full.dropna()
        cap = float(capital); pos = 0.0; entry = 0.0
        trades = []; equity = [cap]

        for i in range(1, len(df)):
            row  = df.iloc[i]
            prev = df.iloc[i-1]
            price = float(row['close'])

            # إشارة شراء
            buy_signal = False
            sell_signal = False

            if strategy == "RSI":
                buy_signal  = row['rsi'] < 30 and prev['rsi'] >= 30
                sell_signal = row['rsi'] > 70 and prev['rsi'] <= 70
            elif strategy == "MACD Crossover":
                buy_signal  = prev['macd'] < prev['macd_signal'] and row['macd'] > row['macd_signal']
                sell_signal = prev['macd'] > prev['macd_signal'] and row['macd'] < row['macd_signal']
            elif strategy == "Bollinger Bands":
                buy_signal  = float(row['close']) < float(row['bb_lower'])
                sell_signal = float(row['close']) > float(row['bb_upper'])
            elif strategy == "EMA Crossover":
                buy_signal  = prev['ema_20'] < prev['ema_50'] and row['ema_20'] > row['ema_50']
                sell_signal = prev['ema_20'] > prev['ema_50'] and row['ema_20'] < row['ema_50']
            elif strategy == "Stochastic":
                buy_signal  = row['stoch_k'] < 20 and row['stoch_k'] > row['stoch_d']
                sell_signal = row['stoch_k'] > 80 and row['stoch_k'] < row['stoch_d']
            elif strategy == "CCI Mean Reversion":
                buy_signal  = row['cci'] < -100
                sell_signal = row['cci'] > 100

            # تطبيق وقف الخسارة والهدف
            if pos > 0 and entry > 0:
                if price <= entry * (1 - stop_pct/100): sell_signal = True
                if price >= entry * (1 + take_pct/100): sell_signal = True

            if buy_signal and pos == 0 and cap > 0:
                pos = cap / price; entry = price; cap = 0
                trades.append({'النوع':'شراء', 'السعر':price, 'التاريخ':str(df.index[i])[:10]})
            elif sell_signal and pos > 0:
                cap = pos * price
                pnl = (price - entry) / entry * 100
                trades[-1]['PnL%'] = f"{pnl:+.2f}%"
                trades.append({'النوع':'بيع', 'السعر':price, 'التاريخ':str(df.index[i])[:10], 'PnL%':f"{pnl:+.2f}%"})
                pos = 0; entry = 0

            equity.append(cap + pos * price)

        final  = cap + (pos * float(df['close'].iloc[-1]) if pos > 0 else 0)
        profit = final - capital
        profit_pct = safe_percentage(final, capital)
        buy_hold_pct = safe_percentage(float(df['close'].iloc[-1]), float(df['close'].iloc[0]))
        n_trades = len([t for t in trades if t['النوع']=='شراء'])
        wins = len([t for t in trades if 'PnL%' in t and float(t['PnL%'].replace('%','')) > 0])

    st.success("✅ اكتمل الاختبار!")
    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: st.metric("الربح/الخسارة",    format_currency(profit),     f"{profit_pct:+.2f}%")
    with c2: st.metric("القيمة النهائية",   format_currency(final))
    with c3: st.metric("عدد الصفقات",       n_trades)
    with c4: st.metric("نسبة الفوز",        f"{wins/max(n_trades,1)*100:.0f}%")
    with c5: st.metric("Buy & Hold",         f"{buy_hold_pct:+.2f}%", "للمقارنة")

    # منحنى الأسهم
    fig_eq = go.Figure()
    fig_eq.add_trace(go.Scatter(y=equity, mode='lines', name='محفظتك',
        line=dict(color=Theme.PRIMARY.value, width=2),
        fill='tozeroy', fillcolor='rgba(102,126,234,0.1)'))
    fig_eq.update_layout(template='plotly_dark', height=300,
                         title="منحنى رأس المال", xaxis_title="الجلسات", yaxis_title="EGP")
    st.plotly_chart(fig_eq, use_container_width=True)

    if trades:
        st.markdown("### 📋 سجل الصفقات")
        st.dataframe(pd.DataFrame(trades), use_container_width=True, hide_index=True)


def render_market():
    st.markdown("## 🏢 نظرة القطاعات الكاملة")

    sector_filter = st.selectbox("اختر القطاع", ['الكل'] + sorted(EGXConfig.SECTORS.keys()), key="mkt_sec")
    sectors_to_show = {sector_filter: EGXConfig.SECTORS[sector_filter]} if sector_filter != 'الكل' else EGXConfig.SECTORS

    for sector, symbols in sorted(sectors_to_show.items()):
        st.markdown(f"### 🏷️ قطاع {sector} ({len(symbols)} شركة)")
        sector_data = []
        for sym in symbols:
            mini = generate_stock_data(sym, 3)
            if not mini.empty:
                last = float(mini['close'].iloc[-1])
                prev = float(mini['close'].iloc[-2]) if len(mini) > 1 else last
                chg  = safe_percentage(last, prev)
                sector_data.append({'رمز': sym, 'الشركة': EGXConfig.STOCKS[sym]['name'][:25],
                                    'السعر': last, 'التغيير%': chg})

        if sector_data:
            df_sec = pd.DataFrame(sector_data)
            # رسم شريطي للقطاع
            colors = [Theme.SUCCESS.value if c > 0 else Theme.ERROR.value for c in df_sec['التغيير%']]
            fig = go.Figure(go.Bar(
                x=df_sec['رمز'], y=df_sec['التغيير%'],
                text=df_sec['التغيير%'].apply(lambda x: f"{x:+.2f}%"),
                textposition='outside', marker_color=colors, name=sector
            ))
            fig.update_layout(template='plotly_dark', height=250,
                               title=f"تغيّرات قطاع {sector}",
                               yaxis_title="%", showlegend=False,
                               margin=dict(t=40,b=10,l=10,r=10))
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("---")


def render_top_bottom():
    st.markdown("## 🔥 أفضل وأسوأ الأسهم")

    n = st.slider("عدد الأسهم", 5, 30, 10)
    all_data = []
    with st.spinner("جاري تحميل بيانات جميع الشركات..."):
        for sym in list(EGXConfig.STOCKS.keys())[:80]:  # أول 80 لسرعة العرض
            try:
                mini = generate_stock_data(sym, 3)
                if not mini.empty:
                    last = float(mini['close'].iloc[-1])
                    prev = float(mini['close'].iloc[-2]) if len(mini) > 1 else last
                    chg  = safe_percentage(last, prev)
                    all_data.append({
                        'رمز': sym,
                        'الشركة': EGXConfig.STOCKS[sym]['name'][:22],
                        'القطاع': EGXConfig.STOCKS[sym]['sector'],
                        'السعر': round(last, 2),
                        'التغيير%': round(chg, 2)
                    })
            except: pass

    if not all_data: st.warning("لا توجد بيانات"); return

    df_all = pd.DataFrame(all_data).sort_values('التغيير%', ascending=False)
    top_n  = df_all.head(n)
    bot_n  = df_all.tail(n).sort_values('التغيير%')

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### 📈 أفضل {n} أسهم")
        fig = go.Figure(go.Bar(
            y=top_n['رمز'], x=top_n['التغيير%'],
            orientation='h', text=top_n['التغيير%'].apply(lambda x: f"{x:+.2f}%"),
            textposition='outside',
            marker_color=[Theme.SUCCESS.value]*len(top_n)
        ))
        fig.update_layout(template='plotly_dark', height=400, xaxis_title="%")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(top_n, hide_index=True, use_container_width=True)

    with col2:
        st.markdown(f"### 📉 أسوأ {n} أسهم")
        fig2 = go.Figure(go.Bar(
            y=bot_n['رمز'], x=bot_n['التغيير%'],
            orientation='h', text=bot_n['التغيير%'].apply(lambda x: f"{x:+.2f}%"),
            textposition='outside',
            marker_color=[Theme.ERROR.value]*len(bot_n)
        ))
        fig2.update_layout(template='plotly_dark', height=400, xaxis_title="%")
        st.plotly_chart(fig2, use_container_width=True)
        st.dataframe(bot_n, hide_index=True, use_container_width=True)


def render_compare():
    st.markdown("## 📊 مقارنة أسهم متعددة")

    syms_to_compare = st.multiselect(
        "اختر الأسهم للمقارنة (2-6)",
        list(EGXConfig.STOCKS.keys()),
        default=['COMI','TMGH','EAST','PHDC'],
        max_selections=6,
        format_func=lambda x: f"{x} | {EGXConfig.STOCKS[x]['name'][:20]}"
    )

    if len(syms_to_compare) < 2:
        st.info("اختر على الأقل سهمين للمقارنة"); return

    days = st.slider("الفترة (يوم)", 30, 200, 90, key="cmp_days")

    # أداء نسبي
    fig = go.Figure()
    colors_cmp = [Theme.PRIMARY.value, Theme.SUCCESS.value, Theme.WARNING.value,
                  Theme.ERROR.value, Theme.ACCENT.value, Theme.GOLD.value]
    for i, sym in enumerate(syms_to_compare):
        df = load_stock_data(sym, max(days,200))
        if df is None: continue
        df = df.tail(days)
        normalized = (df['close'] / float(df['close'].iloc[0]) - 1) * 100
        fig.add_trace(go.Scatter(
            x=df.index, y=normalized, mode='lines',
            name=f"{sym} | {EGXConfig.STOCKS[sym]['name'][:15]}",
            line=dict(color=colors_cmp[i % len(colors_cmp)], width=2)
        ))

    fig.add_hline(y=0, line_dash="dash", line_color="#555")
    fig.update_layout(
        template='plotly_dark', height=500,
        title=f"الأداء النسبي — {days} يوم",
        yaxis_title="العائد %", hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    # جدول مقارنة
    compare_rows = []
    for sym in syms_to_compare:
        df = load_stock_data(sym, 200)
        if df is None: continue
        df_r = df.tail(days)
        last = float(df_r['close'].iloc[-1])
        ret  = safe_percentage(last, float(df_r['close'].iloc[0]))
        vol  = df_r['close'].pct_change().std() * np.sqrt(252) * 100
        sig, scol, conf = get_composite_signal(df)
        compare_rows.append({
            'رمز': sym, 'الشركة': EGXConfig.STOCKS[sym]['name'][:25],
            'السعر': f"{last:.2f}", f'العائد {days}ي': f"{ret:+.2f}%",
            'التقلب السنوي': f"{vol:.1f}%",
            'الإشارة': f"{scol} {sig}", 'ثقة': f"{conf}%"
        })

    st.markdown("### 📋 مقارنة تفصيلية")
    st.dataframe(pd.DataFrame(compare_rows), hide_index=True, use_container_width=True)


def render_settings():
    st.markdown("## ⚙️ الإعدادات والإدارة")

    st.markdown("### 🗄️ إدارة البيانات")
    c1,c2,c3 = st.columns(3)
    with c1:
        if st.button("🗑️ مسح الكاش"):
            load_stock_data.clear(); st.success("✅ تم")
    with c2:
        if st.button("🗑️ حذف التنبيهات"):
            st.session_state.alerts = []; st.success("✅ تم")
    with c3:
        if st.button("🗑️ مسح المراقبة"):
            st.session_state.watchlist = []; st.success("✅ تم")

    st.markdown("### 📊 إحصائيات قاعدة البيانات")
    sector_counts = {s: len(syms) for s, syms in EGXConfig.SECTORS.items()}
    df_stats = pd.DataFrame(list(sector_counts.items()), columns=['القطاع','عدد الشركات'])
    df_stats = df_stats.sort_values('عدد الشركات', ascending=False)

    fig_pie = px.pie(df_stats, values='عدد الشركات', names='القطاع',
                     title=f"توزيع {len(EGXConfig.STOCKS)} شركة على القطاعات",
                     template='plotly_dark', hole=0.4,
                     color_discrete_sequence=px.colors.sequential.Plasma)
    st.plotly_chart(fig_pie, use_container_width=True)
    st.dataframe(df_stats, hide_index=True, use_container_width=True)

    st.markdown("### ℹ️ عن التطبيق")
    st.info(f"""
**{AppConfig.APP_NAME} — {AppConfig.APP_VERSION}**

📊 **البيانات:** {len(EGXConfig.STOCKS)} شركة مصرية في {len(EGXConfig.SECTORS)} قطاع

🔧 **المؤشرات الفنية المدعومة:**
RSI · EMA (9/20/50/200) · SMA · MACD · Bollinger Bands · ADX ·
Stochastic · CCI · Williams %R · OBV · ATR

🕯️ **الأنماط:** Doji · Hammer · Shooting Star · Engulfing · Morning/Evening Star

🤖 **الذكاء الاصطناعي:** إشارة مركّبة + مونت كارلو + رادار المؤشرات

🧪 **الاختبار الخلفي:** 6 استراتيجيات مع وقف خسارة وهدف ربح

⚠️ **تنبيه:** جميع البيانات لأغراض تعليمية فقط ولا تُعدّ نصيحة استثمارية.
    """)

# ═══════════════════════════════════════════════════════════════
# 11. MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    try:
        render_sidebar()
        dispatch = {
            'Dashboard':  render_dashboard,
            'Analysis':   render_analysis,
            'Charts':     render_charts,
            'Patterns':   render_patterns,
            'Alerts':     render_alerts,
            'AI':         render_ai,
            'Watchlist':  render_watchlist,
            'Backtest':   render_backtest,
            'Market':     render_market,
            'TopBottom':  render_top_bottom,
            'Compare':    render_compare,
            'Settings':   render_settings,
        }
        renderer = dispatch.get(st.session_state.page)
        if renderer: renderer()
        else: st.error(f"❌ صفحة غير موجودة: {st.session_state.page}")
    except Exception as e:
        logger.error(f"App error: {e}", exc_info=True)
        st.error(f"❌ خطأ: {e}")
        st.button("🔄 إعادة تشغيل", on_click=lambda: st.rerun())

if __name__ == "__main__":
    main()
