"""
EGX Pro v31 — وحدة Gemini AI (اختيارية)
✅ تعمل بدون مفتاح API — تُخفي نفسها تلقائياً إذا لم يتوفر مفتاح
✅ شرح المؤشرات الفنية بالعربية
✅ توليد استراتيجيات استثمار مخصصة
"""

from typing import Optional
import os


class AIAnalyzer:
    """
    غلاف حول Gemini API. لا يفشل التطبيق إذا كانت المكتبة أو المفتاح غائبين —
    is_available() تُستخدم في الواجهة لإخفاء صفحة "التحليل الذكي" بأمان.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or self._load_key_from_secrets()
        self.model = None
        self._client_ready = False

        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash')
                self._client_ready = True
            except ImportError:
                self._client_ready = False
            except (ValueError, ConnectionError, AttributeError):
                self._client_ready = False

    def _load_key_from_secrets(self) -> Optional[str]:
        """يحاول القراءة من st.secrets أولاً، ثم متغيرات البيئة"""
        try:
            import streamlit as st
            if 'GEMINI_API_KEY' in st.secrets:
                return st.secrets['GEMINI_API_KEY']
        except (ImportError, FileNotFoundError, KeyError, AttributeError):
            pass
        return os.environ.get('GEMINI_API_KEY')

    def is_available(self) -> bool:
        return self._client_ready and self.model is not None

    def _safe_generate(self, prompt: str, fallback: str) -> str:
        if not self.is_available():
            return fallback
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"⚠️ تعذّر الاتصال بـ Gemini API: {e}\n\n{fallback}"

    # ── شرح المؤشرات الفنية ──────────────────────────────────────
    INDICATOR_FALLBACKS = {
        'RSI': """**RSI (مؤشر القوة النسبية)**

يقيس سرعة وحجم تغيرات السعر على مقياس من 0 إلى 100.
- أعلى من 70 → تشبع شراء (احتمال تصحيح هابط)
- أقل من 30 → تشبع بيع (احتمال ارتداد صاعد)
- حول 50 → منطقة محايدة

يُحسب من متوسط المكاسب مقسوماً على متوسط الخسائر خلال فترة (عادة 14 يوم).""",

        'MACD': """**MACD (تقارب وتباعد المتوسطات المتحركة)**

يقيس الفرق بين متوسطين متحركين أسيين (12 و26 يوم) مع خط إشارة (9 أيام).
- تقاطع MACD فوق خط الإشارة → إشارة شراء
- تقاطع MACD تحت خط الإشارة → إشارة بيع
- الهيستوجرام يوضح قوة الزخم الحالي""",

        'Bollinger Bands': """**نطاقات بولينجر**

ثلاثة خطوط: متوسط متحرك (20 يوم) مع نطاقين علوي وسفلي بانحراف معياري ±2.
- السعر عند النطاق العلوي → تشبع شراء نسبي
- السعر عند النطاق السفلي → تشبع بيع نسبي
- ضيق النطاقات → تقلب منخفض، احتمال انفجار سعري قادم""",

        'Supertrend': """**Supertrend**

مؤشر اتجاه يجمع بين ATR ومستويات ديناميكية لتحديد الاتجاه السائد.
- خط أخضر تحت السعر → اتجاه صاعد، يُستخدم كوقف خسارة متحرك
- خط أحمر فوق السعر → اتجاه هابط
يُعتبر من أكثر المؤشرات استخداماً لتتبع الاتجاه في الأسواق الناشئة.""",

        'VWAP': """**VWAP (السعر المتوسط الموزون بالحجم)**

يحسب السعر المتوسط مع الأخذ في الاعتبار حجم التداول، ويُعاد حسابه من جديد كل يوم تداول.
- السعر فوق VWAP → ضغط شرائي أقوى خلال اليوم
- السعر تحت VWAP → ضغط بيعي أقوى
يُستخدم بكثرة من المتداولين المؤسسيين لتقييم جودة التنفيذ.""",
    }

    def explain_indicator(self, indicator_name: str) -> str:
        fallback = self.INDICATOR_FALLBACKS.get(
            indicator_name,
            f"لا يوجد شرح مبدئي متاح لمؤشر {indicator_name} حالياً."
        )
        prompt = f"""اشرح مؤشر {indicator_name} الفني للمتداولين في البورصة المصرية باللغة العربية.
اشرح: ماذا يقيس، كيف يُحسب بشكل مبسط، وكيف يُفسَّر في إشارات الشراء والبيع.
اجعل الشرح عملياً ومناسباً لمتداول مصري متوسط الخبرة، بحد أقصى 200 كلمة."""
        return self._safe_generate(prompt, fallback)

    # ── توليد استراتيجية استثمار مخصصة ──────────────────────────
    def generate_strategy(self, risk_level: str, capital: float, goals: str) -> str:
        fallback = f"""**استراتيجية مبدئية (Gemini AI غير متاح)**

بناءً على مستوى المخاطرة "{risk_level}" ورأس مال {capital:,.0f} جنيه:

- **مخاطرة منخفضة**: التركيز على أسهم البنوك والأسمنت ذات عائد التوزيعات المرتفع (COMI, ABQQ, SKPC)
- **مخاطرة متوسطة**: توزيع بين البنوك والعقارات والصناعة، مع 70% أسهم قيادية و30% أسهم نمو
- **مخاطرة عالية**: التركيز على قطاعي التكنولوجيا والفينتك (FWRY, RAYA) مع وقف خسارة صارم عند 8-10%

نصيحة عامة: لا تتجاوز مخاطرة 2% من رأس المال في صفقة واحدة، واستخدم Supertrend كوقف خسارة متحرك.

⚠️ لتفعيل التحليل الذكي الكامل، أدخل مفتاح Gemini API في الإعدادات."""

        prompt = f"""أنت مستشار مالي متخصص في بورصة مصر (EGX). 
ولّد استراتيجية استثمار مخصصة لمستثمر بالمواصفات التالية:
- مستوى المخاطرة: {risk_level}
- رأس المال: {capital:,.0f} جنيه مصري
- الأهداف: {goals}

قدّم: توزيع مقترح للقطاعات، أمثلة أسهم مناسبة من EGX، نصائح لإدارة المخاطر، وأفق زمني مقترح.
اكتب بالعربية، بشكل عملي ومنظم، بحد أقصى 350 كلمة."""
        return self._safe_generate(prompt, fallback)

    def analyze_stock_summary(self, symbol: str, signal: str, rsi: float,
                              price: float, sector: str) -> str:
        """تحليل سردي قصير لحالة السهم — يُستخدم في صفحة التحليل"""
        fallback = (f"السهم {symbol} (قطاع {sector}) يتداول حالياً عند {price:.2f} جنيه "
                   f"مع RSI عند {rsi:.0f}، والإشارة المركّبة الحالية هي: {signal}.")
        prompt = f"""اكتب تعليقاً تحليلياً قصيراً (3-4 جمل) بالعربية عن سهم {symbol} 
من قطاع {sector} في بورصة مصر. السعر الحالي {price:.2f} جنيه، RSI عند {rsi:.0f}،
والإشارة الفنية الحالية: {signal}. لا تقدّم نصيحة استثمارية مباشرة، فقط وصف الحالة الفنية."""
        return self._safe_generate(prompt, fallback)
