"""
EGX Pro Terminal v34 - News & Dividends Module
Market news, company announcements, and dividend distributions
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum
import random

class NewsCategory(Enum):
    EARNINGS = "earnings"
    DIVIDEND = "dividend"
    MERGER = "merger"
    ACQUISITION = "acquisition"
    IPO = "ipo"
    SUSPENSION = "suspension"
    REINSTATEMENT = "reinstatement"
    CAPITAL_INCREASE = "capital_increase"
    BONUS = "bonus"
    RIGHTS_ISSUE = "rights_issue"
    BOARD_CHANGE = "board_change"
    REGULATORY = "regulatory"
    MARKET_UPDATE = "market_update"
    ECONOMIC = "economic"
    SECTOR_NEWS = "sector_news"

class NewsPriority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class MarketNews:
    id: str
    title: str
    title_ar: str
    content: str
    content_ar: str
    category: NewsCategory
    priority: NewsPriority
    symbol: Optional[str]
    source: str
    published_at: datetime
    related_symbols: List[str]
    tags: List[str]

@dataclass
class DividendDistribution:
    id: str
    symbol: str
    company_name: str
    dividend_type: str  # cash, stock, bonus
    amount_per_share: float
    total_amount: float
    record_date: datetime
    distribution_date: datetime
    ex_dividend_date: datetime
    currency: str
    status: str  # announced, approved, distributed

class NewsEngine:
    def __init__(self):
        self.news_cache: List[MarketNews] = []
        self.dividends_cache: List[DividendDistribution] = []
        self._generate_sample_data()

    def _generate_sample_data(self):
        """Generate sample news and dividends for demonstration."""
        now = datetime.now()

        # Sample news
        sample_news = [
            MarketNews(
                id="NEWS001", 
                title="COMI Reports Record Q3 2026 Profits",
                title_ar="البنك التجاري الدولي يحقق أرباح قياسية في الربع الثالث 2026",
                content="Commercial International Bank (COMI) reported net profits of EGP 8.5 billion for Q3 2026, up 22% YoY. The bank's NIM improved to 5.8% and asset quality remained stable with NPL ratio at 2.1%.",
                content_ar="أعلن البنك التجاري الدولي عن أرباح صافية بلغت 8.5 مليار جنيه للربع الثالث 2026، بزيادة 22% على أساس سنوي. تحسنت هوامش الفائدة الصافية إلى 5.8% وظلت جودة الأصول مستقرة.",
                category=NewsCategory.EARNINGS,
                priority=NewsPriority.HIGH,
                symbol="COMI",
                source="EGX Disclosure",
                published_at=now - timedelta(hours=2),
                related_symbols=["HRHO", "ABUK"],
                tags=["earnings", "banking", "profits"]
            ),
            MarketNews(
                id="NEWS002",
                title="EGX30 Reaches New All-Time High",
                title_ar="مؤشر EGX30 يسجل مستوى قياسي جديد",
                content="The EGX30 index surged 2.8% to close at 28,450 points, driven by strong buying in banking and real estate sectors. Foreign investors were net buyers for the 5th consecutive session.",
                content_ar="قفز مؤشر EGX30 بنسبة 2.8% ليغلق عند 28450 نقطة، مدفوعاً بقوة الشراء في قطاعي البنوك والعقارات. كان المستثمرون الأجانب مشترين صافيين للجلسة الخامسة على التوالي.",
                category=NewsCategory.MARKET_UPDATE,
                priority=NewsPriority.HIGH,
                symbol=None,
                source="EGX Official",
                published_at=now - timedelta(hours=4),
                related_symbols=["COMI", "TMGH", "PHDC"],
                tags=["index", "market", "foreign_investors"]
            ),
            MarketNews(
                id="NEWS003",
                title="TMGH Announces New Capital Increase",
                title_ar="طلعت مصطفى تعلن زيادة رأس مال جديدة",
                content="Talaat Mostafa Group announced a capital increase of EGP 2 billion through rights issue at EGP 12.5 per share. The funds will be used for new project development in New Cairo.",
                content_ar="أعلنت مجموعة طلعت مصطفى عن زيادة رأسمال بقيمة 2 مليار جنيه من خلال إصدار حقوق بسعر 12.5 جنيه للسهم. سيتم استخدام الأموال لتطوير مشاريع جديدة في القاهرة الجديدة.",
                category=NewsCategory.CAPITAL_INCREASE,
                priority=NewsPriority.HIGH,
                symbol="TMGH",
                source="Company Disclosure",
                published_at=now - timedelta(hours=6),
                related_symbols=["PHDC", "MNHD"],
                tags=["capital_increase", "real_estate", "rights_issue"]
            ),
            MarketNews(
                id="NEWS004",
                title="Eastern Company Approves EGP 2.5 Dividend",
                title_ar="الشرقية للدخان توافق على توزيع 2.5 جنيه للسهم",
                content="Eastern Company (EAST) board approved cash dividend of EGP 2.5 per share for FY2026, representing a yield of 13.5%. Record date set for October 15, 2026.",
                content_ar="وافق مجلس إدارة الشرقية للدخان على توزيع نقدي بقيمة 2.5 جنيه للسهم للعام المالي 2026، بعائد 13.5%. تم تحديد 15 أكتوبر 2026 كتاريخ استحقاق.",
                category=NewsCategory.DIVIDEND,
                priority=NewsPriority.MEDIUM,
                symbol="EAST",
                source="EGX Disclosure",
                published_at=now - timedelta(hours=8),
                related_symbols=["COMI", "JUHO"],
                tags=["dividend", "distribution", "high_yield"]
            ),
            MarketNews(
                id="NEWS005",
                title="Fawry Partners with Central Bank for Digital Payments",
                title_ar="فوري تتعاون مع البنك المركزي للمدفوعات الرقمية",
                content="Fawry (FWRY) signed a strategic partnership with the Central Bank of Egypt to expand digital payment infrastructure across 5000 new locations nationwide.",
                content_ar="وقعت فوري شراكة استراتيجية مع البنك المركزي المصري لتوسيع البنية التحتية للمدفوعات الرقمية عبر 5000 موقع جديد على مستوى الجمهورية.",
                category=NewsCategory.SECTOR_NEWS,
                priority=NewsPriority.MEDIUM,
                symbol="FWRY",
                source="Company Press Release",
                published_at=now - timedelta(hours=12),
                related_symbols=["EGTS", "ETEL"],
                tags=["fintech", "digital_payments", "partnership"]
            ),
            MarketNews(
                id="NEWS006",
                title="Egypt Inflation Drops to 18.5% in June 2026",
                title_ar="التضخم في مصر ينخفض إلى 18.5% في يونيو 2026",
                content="Egypt's annual urban consumer price inflation fell to 18.5% in June 2026 from 21.2% in May, according to CAPMAS. This marks the 4th consecutive monthly decline.",
                content_ar="انخفض التضخم السنوي للمستهلكين في المدن المصرية إلى 18.5% في يونيو 2026 من 21.2% في مايو، وفقاً للجهاز المركزي للتعبئة العامة والإحصاء. يمثل هذا الانخفاض الرابع على التوالي.",
                category=NewsCategory.ECONOMIC,
                priority=NewsPriority.HIGH,
                symbol=None,
                source="CAPMAS",
                published_at=now - timedelta(hours=24),
                related_symbols=["COMI", "TMGH", "EAST"],
                tags=["inflation", "macro", "economy"]
            ),
            MarketNews(
                id="NEWS007",
                title="Centamin Egypt Reports Strong Gold Production",
                title_ar="سنتامين مصر تبلغ عن إنتاج قوي من الذهب",
                content="Centamin Egypt (CEFM) reported Q2 2026 gold production of 125,000 ounces, exceeding guidance. Full year production target raised to 480,000 ounces.",
                content_ar="أبلغت سنتامين مصر عن إنتاج ذهب قدره 125000 أوقية في الربع الثاني 2026، متجاوزة التوقعات. تم رفع هدف الإنتاج السنوي إلى 480000 أوقية.",
                category=NewsCategory.EARNINGS,
                priority=NewsPriority.MEDIUM,
                symbol="CEFM",
                source="Company Disclosure",
                published_at=now - timedelta(hours=36),
                related_symbols=["SWDY", "AMOC"],
                tags=["gold", "mining", "production"]
            ),
            MarketNews(
                id="NEWS008",
                title="New IPO: Metroplex for Education Lists on EGX",
                title_ar="طرح جديد: متروبلكس للتعليم تدرج في البورصة",
                content="Metroplex for Education (METX) will list on EGX next week with an IPO price of EGP 8.5 per share. The company operates 15 schools across Egypt with 25,000 students.",
                content_ar="ستدرج متروبلكس للتعليم في البورصة الأسبوع المقبل بسعر طرح 8.5 جنيه للسهم. تدير الشركة 15 مدرسة في مصر بـ 25000 طالب.",
                category=NewsCategory.IPO,
                priority=NewsPriority.HIGH,
                symbol="METX",
                source="EGX Official",
                published_at=now - timedelta(hours=48),
                related_symbols=["EDUC", "CIRA"],
                tags=["ipo", "education", "new_listing"]
            ),
            MarketNews(
                id="NEWS009",
                title="Telecom Egypt 5G Rollout Accelerates",
                title_ar="اتصالات مصر تسرع طرح خدمات الجيل الخامس",
                content="Telecom Egypt (ETEL) announced acceleration of 5G network rollout, targeting coverage in Cairo and Alexandria by Q4 2026. CAPEX budget increased by EGP 3 billion.",
                content_ar="أعلنت اتصالات مصر عن تسريع طرح شبكة الجيل الخامس، مستهدفة التغطية في القاهرة والإسكندرية بحلول الربع الرابع 2026. زيادة ميزانية الاستثمارات بـ 3 مليار جنيه.",
                category=NewsCategory.SECTOR_NEWS,
                priority=NewsPriority.MEDIUM,
                symbol="ETEL",
                source="Company Press Release",
                published_at=now - timedelta(hours=72),
                related_symbols=["EGTS", "FWRY"],
                tags=["5g", "telecom", "technology"]
            ),
            MarketNews(
                id="NEWS010",
                title="CBE Maintains Interest Rates at 27.25%",
                title_ar="البنك المركزي يبقي على أسعار الفائدة عند 27.25%",
                content="The Central Bank of Egypt kept overnight deposit rate at 27.25% and lending rate at 28.25%, citing the need to anchor inflation expectations amid global uncertainty.",
                content_ar="أبقى البنك المركزي المصري على سعر الإيداع لليلة واحدة عند 27.25% وسعر الإقراض عند 28.25%، مشيراً إلى ضرورة تثبيت توقعات التضخم وسط عدم اليقين العالمي.",
                category=NewsCategory.ECONOMIC,
                priority=NewsPriority.HIGH,
                symbol=None,
                source="CBE",
                published_at=now - timedelta(days=5),
                related_symbols=["COMI", "HRHO", "ABUK"],
                tags=["interest_rates", "cbe", "monetary_policy"]
            ),
        ]

        # Sample dividends
        sample_dividends = [
            DividendDistribution(
                id="DIV001", symbol="EAST", company_name="Eastern Company",
                dividend_type="cash", amount_per_share=2.5, total_amount=4500.0,
                record_date=datetime(2026, 10, 15),
                distribution_date=datetime(2026, 11, 1),
                ex_dividend_date=datetime(2026, 10, 13),
                currency="EGP", status="approved"
            ),
            DividendDistribution(
                id="DIV002", symbol="COMI", company_name="Commercial International Bank",
                dividend_type="cash", amount_per_share=1.85, total_amount=5365.0,
                record_date=datetime(2026, 9, 20),
                distribution_date=datetime(2026, 10, 5),
                ex_dividend_date=datetime(2026, 9, 18),
                currency="EGP", status="distributed"
            ),
            DividendDistribution(
                id="DIV003", symbol="JUHO", company_name="Juhayna Food Industries",
                dividend_type="cash", amount_per_share=0.75, total_amount=637.5,
                record_date=datetime(2026, 8, 25),
                distribution_date=datetime(2026, 9, 10),
                ex_dividend_date=datetime(2026, 8, 23),
                currency="EGP", status="distributed"
            ),
            DividendDistribution(
                id="DIV004", symbol="TMGH", company_name="Talaat Mostafa Group",
                dividend_type="stock", amount_per_share=0.0, total_amount=0.0,
                record_date=datetime(2026, 11, 1),
                distribution_date=datetime(2026, 11, 15),
                ex_dividend_date=datetime(2026, 10, 30),
                currency="EGP", status="announced"
            ),
            DividendDistribution(
                id="DIV005", symbol="SWDY", company_name="Sidi Kerir Petrochemicals",
                dividend_type="cash", amount_per_share=3.2, total_amount=2880.0,
                record_date=datetime(2026, 7, 15),
                distribution_date=datetime(2026, 8, 1),
                ex_dividend_date=datetime(2026, 7, 13),
                currency="EGP", status="distributed"
            ),
            DividendDistribution(
                id="DIV006", symbol="ETEL", company_name="Telecom Egypt",
                dividend_type="cash", amount_per_share=1.2, total_amount=2040.0,
                record_date=datetime(2026, 6, 20),
                distribution_date=datetime(2026, 7, 5),
                ex_dividend_date=datetime(2026, 6, 18),
                currency="EGP", status="distributed"
            ),
            DividendDistribution(
                id="DIV007", symbol="FWRY", company_name="Fawry",
                dividend_type="cash", amount_per_share=0.35, total_amount=262.5,
                record_date=datetime(2026, 5, 15),
                distribution_date=datetime(2026, 6, 1),
                ex_dividend_date=datetime(2026, 5, 13),
                currency="EGP", status="distributed"
            ),
            DividendDistribution(
                id="DIV008", symbol="CEFM", company_name="Centamin Egypt",
                dividend_type="cash", amount_per_share=0.15, total_amount=165.0,
                record_date=datetime(2026, 4, 10),
                distribution_date=datetime(2026, 4, 25),
                ex_dividend_date=datetime(2026, 4, 8),
                currency="USD", status="distributed"
            ),
        ]

        self.news_cache = sample_news
        self.dividends_cache = sample_dividends

    def get_all_news(self, limit: int = 50) -> List[MarketNews]:
        return sorted(self.news_cache, key=lambda x: x.published_at, reverse=True)[:limit]

    def get_news_by_symbol(self, symbol: str) -> List[MarketNews]:
        return [n for n in self.news_cache if n.symbol == symbol or symbol in n.related_symbols]

    def get_news_by_category(self, category: NewsCategory) -> List[MarketNews]:
        return [n for n in self.news_cache if n.category == category]

    def get_high_priority_news(self) -> List[MarketNews]:
        return [n for n in self.news_cache if n.priority == NewsPriority.HIGH]

    def get_dividends(self, symbol: Optional[str] = None) -> List[DividendDistribution]:
        if symbol:
            return [d for d in self.dividends_cache if d.symbol == symbol]
        return sorted(self.dividends_cache, key=lambda x: x.distribution_date, reverse=True)

    def get_upcoming_dividends(self) -> List[DividendDistribution]:
        now = datetime.now()
        return [d for d in self.dividends_cache if d.distribution_date > now]

    def get_dividend_calendar(self) -> Dict:
        """Get dividend calendar by month."""
        calendar = {}
        for div in self.dividends_cache:
            month_key = div.distribution_date.strftime("%Y-%m")
            if month_key not in calendar:
                calendar[month_key] = []
            calendar[month_key].append(div)
        return calendar

    def get_sector_news(self, sector: str) -> List[MarketNews]:
        sector_tags = {
            "banking": ["COMI", "HRHO", "ABUK", "EGBE", "NSGB"],
            "real_estate": ["TMGH", "PHDC", "MNHD"],
            "technology": ["FWRY", "EGTS", "ETEL"],
            "energy": ["TAQA", "EDBM", "AMOC"],
            "healthcare": ["RMDA", "IDHC", "CLHO"],
            "food": ["EAST", "JUHO", "DOMT"],
        }
        symbols = sector_tags.get(sector.lower(), [])
        return [n for n in self.news_cache if any(s in n.related_symbols or n.symbol == s for s in symbols)]

    def get_market_summary(self) -> Dict:
        """Get daily market news summary."""
        high_priority = self.get_high_priority_news()
        earnings = self.get_news_by_category(NewsCategory.EARNINGS)
        dividends = self.get_news_by_category(NewsCategory.DIVIDEND)

        return {
            "total_news": len(self.news_cache),
            "high_priority": len(high_priority),
            "earnings_reports": len(earnings),
            "dividend_announcements": len(dividends),
            "upcoming_dividends": len(self.get_upcoming_dividends()),
            "latest_news": self.get_all_news(5),
        }

news_engine = NewsEngine()
