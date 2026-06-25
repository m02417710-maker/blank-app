"""
EGX Pro Terminal v35 — نقطة الدخول الرئيسية
تشغيل: streamlit run egx_app.py  (واجهة موحّدة)
        streamlit run app.py       (multi-page)
"""
import sys, os
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import streamlit as st

st.set_page_config(
    page_title="🇪🇬 EGX Pro Terminal v35",
    page_icon="📈", layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Cairo', sans-serif !important; }
.stApp { direction: rtl; background: #0a0e1a; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-thumb { background: #2d3748; border-radius: 4px; }
</style>""", unsafe_allow_html=True)

def main():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:16px 0">
            <div style="font-size:40px">📈</div>
            <div style="font-size:18px;font-weight:800;color:#f59e0b">EGX Pro Terminal</div>
            <div style="font-size:11px;color:#475569;letter-spacing:2px">v35 — PROFESSIONAL</div>
        </div>""", unsafe_allow_html=True)
        st.info("💡 استخدم **egx_app.py** للواجهة الموحّدة الكاملة\n\n`streamlit run egx_app.py`")
        st.markdown("---")
        st.markdown("""<div style="font-size:11px;color:#374151">
            🔗 <a href="https://github.com/m02417710-maker/blank-app" style="color:#3b82f6">GitHub</a><br>
            ⚠️ للأغراض التعليمية فقط</div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="background:linear-gradient(135deg,#1e2738,#2d3748);border-radius:16px;
                padding:28px;margin-bottom:24px;border:1px solid #3d4a63">
        <div style="font-size:26px;font-weight:800;color:#f59e0b">🇪🇬 EGX Pro Terminal v35</div>
        <div style="font-size:14px;color:#64748b;margin-top:6px">
            منصة التحليل الاحترافي للبورصة المصرية — 200+ شركة · 25+ مؤشر فني · AI بالعربية
        </div>
    </div>""", unsafe_allow_html=True)

    cols = st.columns(4)
    tools = [
        ("📊","التحليل الفني","25+ مؤشر · شموع · إشارات مركّبة"),
        ("🤖","Gemini AI","تحليل وشرح مؤشرات بالعربية"),
        ("🧪","الباكتست","10 استراتيجيات · Walk-Forward · DCA"),
        ("💼","المحفظة","Kelly Criterion · وقف الخسارة الديناميكي"),
    ]
    for col, (icon, title, desc) in zip(cols, tools):
        with col:
            st.markdown(f"""
            <div style="background:#1a1f2e;border:1px solid #3d4a63;border-radius:12px;
                        padding:16px;text-align:center">
                <div style="font-size:28px">{icon}</div>
                <div style="font-size:14px;font-weight:700;color:#e2e8f0;margin:6px 0">{title}</div>
                <div style="font-size:11px;color:#64748b">{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🚀 الأوامر السريعة")
    st.code("""# الواجهة الموحّدة (الكاملة — موصى بها)
streamlit run egx_app.py

# واجهة multi-page
streamlit run app.py

# تثبيت المكتبات
pip install -r requirements.txt

# Docker
docker build -t egx-pro .
docker run -p 8501:8501 egx-pro

# مع Gemini AI
export GEMINI_API_KEY="AIza..."
streamlit run egx_app.py""", language="bash")

if __name__ == "__main__":
    main()
