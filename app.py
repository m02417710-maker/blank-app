"""
EGX Pro Terminal v34 — نقطة الدخول الرئيسية
Egyptian Stock Exchange Professional Analysis Platform

يجمع بين:
  - egx_engine.py      → محرك البيانات والمؤشرات الفنية (200+ شركة)
  - egx_ml_backtest.py → ML Walk-Forward + Backtest (10 استراتيجيات)
  - egx_ai_analyzer.py → تحليل Gemini AI بالعربية
  - egx_app.py         → الواجهة الرئيسية الكاملة
  - core/*             → محركات التحليل الإضافية
  - data/*             → قاعدة بيانات EGX الموسّعة (150+ رمز)
  - pages/*            → صفحات Streamlit متعددة

تشغيل: streamlit run app.py
"""

import streamlit as st
import sys
import os

# ── إضافة المسار الجذر للـ Python path ────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ── ضبط الصفحة قبل أي شيء آخر ────────────────────────────────
st.set_page_config(
    page_title="🇪🇬 EGX Pro Terminal v34",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/m02417710-maker/blank-app",
        "Report a bug": "https://github.com/m02417710-maker/blank-app/issues",
        "About": "EGX Pro Terminal v34 — Professional Egyptian Stock Exchange Analysis"
    }
)

# ── استيراد آمن مع fallback ───────────────────────────────────
def _safe_import(module_name: str):
    try:
        return __import__(module_name)
    except ImportError as e:
        st.error(f"⚠️ تعذّر استيراد {module_name}: {e}")
        return None

# ── CSS عالمي ─────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp, .stMarkdown, p, div, span, h1, h2, h3, h4 {
    font-family: 'Cairo', sans-serif !important;
}

.stApp {
    direction: rtl;
    background: #0a0e1a;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0a0e1a; }
::-webkit-scrollbar-thumb { background: #2d3748; border-radius: 4px; }

/* ── Buttons ── */
.stButton > button {
    font-family: 'Cairo', sans-serif !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    padding: 10px 18px !important;
    border-radius: 8px !important;
    border: 1px solid #3d4a63 !important;
    background: linear-gradient(135deg, #1e2738, #2d3748) !important;
    color: #e2e8f0 !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    border-color: #f59e0b !important;
    color: #f59e0b !important;
    transform: translateX(-2px) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
    border-color: #3b82f6 !important;
    color: #fff !important;
}

/* ── Metrics ── */
div[data-testid="stMetric"] {
    background: #1a1f2e !important;
    border-radius: 10px !important;
    padding: 12px !important;
    border: 1px solid #2d3748 !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1117, #1a1f2e) !important;
    border-left: 1px solid #2d3748;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px; background: #0f1117; border-radius: 10px; padding: 6px;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Cairo', sans-serif !important;
    font-weight: 600 !important;
    color: #94a3b8 !important;
    border-radius: 8px !important;
}
.stTabs [aria-selected="true"] {
    background: #1d4ed8 !important;
    color: #fff !important;
}

/* ── Cards ── */
.kpi-card {
    background: linear-gradient(135deg, #1a1f2e, #2d3748);
    border: 1px solid #3d4a63;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    margin: 4px 0;
}
.kpi-val { font-size: 22px; font-weight: 800; margin: 6px 0 3px; }
.kpi-lbl { font-size: 12px; color: #64748b; }

/* ── Alert cards ── */
.alert-card {
    background: #1a1f2e;
    border-left: 4px solid #3b82f6;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 6px 0;
    font-size: 14px;
}
.alert-triggered { border-left-color: #10b981 !important; }

/* ── News ── */
.news-item {
    background: #1a1f2e;
    border-radius: 10px;
    padding: 14px;
    margin: 8px 0;
    border-right: 3px solid #3b82f6;
}
.news-item.high { border-right-color: #ef4444; }
.news-item.medium { border-right-color: #f59e0b; }

/* ── Source badges ── */
.badge-real { background:#064e3b; border:1px solid #10b981; color:#6ee7b7;
              border-radius:6px; padding:2px 8px; font-size:11px; }
.badge-sim  { background:#78350f; border:1px solid #f59e0b; color:#fcd34d;
              border-radius:6px; padding:2px 8px; font-size:11px; }
</style>
""", unsafe_allow_html=True)


# ── الشريط الجانبي الرئيسي ─────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:20px 0 12px">
            <div style="font-size:44px">📈</div>
            <div style="font-size:20px;font-weight:800;color:#f59e0b">EGX Pro Terminal</div>
            <div style="font-size:11px;color:#475569;letter-spacing:2px;margin-top:2px">v34 — PROFESSIONAL EDITION</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")

        # إحصائيات سريعة
        try:
            from data.egx_symbols import get_market_stats
            stats = get_market_stats()
            st.markdown(f"""
            <div style="font-size:12px;color:#64748b;line-height:2.2;padding:4px 0">
                🏦 <b style="color:#94a3b8">{stats['total_companies']}</b> شركة نشطة<br>
                🏭 <b style="color:#94a3b8">{stats['total_sectors']}</b> قطاع<br>
                💎 <b style="color:#94a3b8">{stats['blue_chips']}</b> شركة قيادية<br>
                📊 <b style="color:#94a3b8">{stats['indices']}</b> مؤشر رسمي
            </div>
            """, unsafe_allow_html=True)
        except Exception:
            pass

        st.markdown("---")
        st.markdown("""
        <div style="font-size:11px;color:#374151;padding:8px 0;line-height:1.8">
            🔗 <a href="https://github.com/m02417710-maker/blank-app" style="color:#3b82f6">GitHub Repository</a><br>
            ⚠️ للأغراض التعليمية فقط<br>
            📅 يونيو 2026
        </div>
        """, unsafe_allow_html=True)


# ── الصفحة الرئيسية ────────────────────────────────────────────
def render_home():
    # Header
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1e2738,#2d3748);border-radius:16px;
                padding:28px 32px;margin-bottom:24px;border:1px solid #3d4a63">
        <div style="font-size:28px;font-weight:800;color:#f59e0b">🇪🇬 EGX Pro Terminal</div>
        <div style="font-size:14px;color:#64748b;margin-top:6px">
            منصة التحليل الاحترافي للبورصة المصرية — 200+ شركة · 20+ مؤشر فني · AI بالعربية
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation cards
    st.markdown("### 🚀 الأدوات المتاحة")
    cols = st.columns(4)
    tools = [
        ("📊", "تحليل الأسهم", "egx_app.py — تحليل فني كامل مع 20+ مؤشر", "🟢"),
        ("🤖", "تحليل AI", "Gemini AI — شرح مؤشرات وتوليد استراتيجيات بالعربية", "🟢"),
        ("🧪", "الباكتست", "10 استراتيجيات · Walk-Forward · DCA", "🟢"),
        ("💼", "المحفظة", "Kelly Criterion · وقف الخسارة الديناميكي", "🟢"),
    ]
    for col, (icon, title, desc, status) in zip(cols, tools):
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div style="font-size:32px">{icon}</div>
                <div style="font-size:15px;font-weight:700;color:#e2e8f0;margin:8px 0 4px">{title}</div>
                <div style="font-size:11px;color:#64748b;line-height:1.6">{desc}</div>
                <div style="margin-top:10px;font-size:12px">{status} متاح</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Market summary
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 📈 ملخص السوق")
        try:
            from data.market_data import get_market_summary
            summary = get_market_summary()
            m_cols = st.columns(4)
            m_cols[0].metric("EGX30", f"{summary['egx30']:,.0f}", f"+{summary['egx30_change']:.2f}%")
            m_cols[1].metric("EGX70", f"{summary['egx70']:,.0f}", f"+{summary['egx70_change']:.2f}%")
            m_cols[2].metric("الصاعدة", str(summary['advancers']), "سهم")
            m_cols[3].metric("الهابطة", str(summary['decliners']), "سهم")
        except Exception as e:
            st.info(f"سيتم عرض بيانات السوق عند الاتصال بالإنترنت")

    with col2:
        st.markdown("### 📰 أحدث الأخبار")
        try:
            from data.news_dividends import news_engine
            latest = news_engine.get_all_news(3)
            for news in latest:
                priority_color = "#ef4444" if news.priority.value == "high" else "#f59e0b"
                st.markdown(f"""
                <div style="background:#1a1f2e;border-right:3px solid {priority_color};
                            border-radius:8px;padding:10px 12px;margin:6px 0">
                    <div style="font-size:12px;font-weight:600;color:#e2e8f0">{news.title_ar[:60]}...</div>
                    <div style="font-size:10px;color:#64748b;margin-top:4px">{news.source}</div>
                </div>
                """, unsafe_allow_html=True)
        except Exception:
            st.info("الأخبار جاهزة")

    st.markdown("---")

    # Architecture info
    with st.expander("🏗️ معمارية النظام — اضغط للتفاصيل"):
        st.markdown("""
        ```
        blank-app/
        ├── app.py                    ← نقطة الدخول الرئيسية (هذا الملف)
        ├── egx_engine.py             ← محرك EGX: 200+ شركة، 20+ مؤشر، GARCH
        ├── egx_ml_backtest.py        ← ML Walk-Forward + 10 استراتيجيات
        ├── egx_ai_analyzer.py        ← Gemini AI (عربي)
        ├── egx_app.py                ← الواجهة الرئيسية (15 صفحة)
        ├── .streamlit/config.toml    ← إعدادات Streamlit
        ├── requirements.txt          ← المكتبات المطلوبة
        ├── data/                     ← قاعدة بيانات EGX الموسّعة
        │   ├── egx_symbols.py        ← 150+ رمز مع بيانات كاملة
        │   ├── market_data.py        ← جلب البيانات من Yahoo Finance
        │   ├── storage.py            ← SQLite للتخزين المحلي
        │   └── news_dividends.py     ← الأخبار والتوزيعات
        ├── core/                     ← محركات التحليل
        │   ├── analysis.py           ← 25+ مؤشر فني
        │   ├── ai_engine.py          ← نماذج AI + Monte Carlo
        │   ├── backtest.py           ← محرك الباكتست المتقدم
        │   ├── alerts.py             ← نظام التنبيهات
        │   ├── charts.py             ← رسوم Plotly احترافية
        │   └── patterns.py           ← 14 نمط شمعة
        ├── config/                   ← الإعدادات
        │   ├── settings.py           ← AppConfig
        │   └── app_config.py         ← Streamlit setup
        ├── pages/                    ← صفحات multi-page
        │   ├── 01_Dashboard.py
        │   ├── 02_Technical.py
        │   ├── 03_AI_Predictions.py
        │   ├── 04_Backtest.py
        │   ├── 05_Alerts.py
        │   ├── 06_News_Dividends.py
        │   └── 07_Settings.py
        └── utils/                    ← أدوات مساعدة
            ├── formatters.py
            ├── validators.py
            └── helpers.py
        ```
        """)

    st.info("💡 **للتشغيل الكامل:** استخدم `streamlit run egx_app.py` للواجهة الموحّدة أو `streamlit run app.py` للواجهة متعددة الصفحات")


# ── التشغيل الرئيسي ─────────────────────────────────────────────
def main():
    render_sidebar()
    render_home()


if __name__ == "__main__":
    main()
