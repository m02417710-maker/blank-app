"""
EGX Pro Ultimate v31 — واجهة احترافية كاملة
✅ أزرار واضحة القراءة  ✅ تنسيق محسّن  ✅ أخبار وتوزيعات وتوقعات
✅ 200+ شركة  ✅ جميع الأخطاء مصحّحة
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from egx_engine import (
    EGXDatabase, load_and_compute, detect_patterns,
    get_composite_signal, get_support_resistance, get_fibonacci_levels,
    safe_last, fmt_num, fmt_egp, calc_supertrend, calc_atr,
    get_stock_news, get_dividends_history, get_price_targets
)
from egx_ml_backtest import (
    EGXMLPredictor, PortfolioManager,
    run_all_backtests, backtest_summary_df, ALL_STRATEGIES,
    dca_simulation
)
from egx_ai_analyzer import AIAnalyzer

st.set_page_config(page_title="EGX Pro v31", page_icon="📈", layout="wide",
                   initial_sidebar_state="expanded")

# ═══════════════════════════════════════════════════════════════
# CSS — تنسيق احترافي مع أزرار واضحة
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], .stApp, .stMarkdown, p, div, span, h1, h2, h3, h4 {
    font-family: 'Cairo', sans-serif !important;
}
.stApp { direction: rtl; background: #0a0e1a; }

/* ── أزرار واضحة ── */
.stButton > button {
    font-family: 'Cairo', sans-serif !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    border-radius: 8px !important;
    border: 1.5px solid #3d4a63 !important;
    background: linear-gradient(135deg, #1e2738, #2d3748) !important;
    color: #e2e8f0 !important;
    transition: all 0.2s !important;
    width: 100% !important;
    text-align: center !important;
    white-space: normal !important;
    line-height: 1.4 !important;
    min-height: 44px !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2d3748, #374151) !important;
    border-color: #f59e0b !important;
    color: #f59e0b !important;
    transform: translateX(-2px) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
    border-color: #3b82f6 !important;
    color: #ffffff !important;
    font-size: 16px !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
    box-shadow: 0 4px 15px rgba(59,130,246,0.4) !important;
}

/* ── بطاقات السوق ── */
.mcard {
    background: linear-gradient(135deg, #1a1f2e, #2d3748);
    border: 1px solid #3d4a63; border-radius: 14px;
    padding: 18px 16px; text-align: center; margin: 6px 0;
    transition: transform 0.2s, box-shadow 0.2s;
}
.mcard:hover { transform: translateY(-3px); box-shadow: 0 10px 30px rgba(0,0,0,0.4); }
.mcard-price { font-size: 24px; font-weight: 800; margin: 6px 0 3px; }
.mcard-name { font-size: 13px; color: #94a3b8; margin-bottom: 4px; }
.mcard-change { font-size: 15px; font-weight: 600; }
.mcard-vol { font-size: 11px; color: #64748b; margin-top: 4px; }

/* ── بطاقات الإشارة ── */
.sig-buy  { background: linear-gradient(135deg,#052e16,#064e3b); border:2px solid #10b981;
            border-radius:14px; padding:18px; text-align:center; }
.sig-sell { background: linear-gradient(135deg,#4c0519,#7f1d1d); border:2px solid #ef4444;
            border-radius:14px; padding:18px; text-align:center; }
.sig-neu  { background: linear-gradient(135deg,#0f172a,#1e293b); border:2px solid #475569;
            border-radius:14px; padding:18px; text-align:center; }
.sig-text { font-size: 22px; font-weight: 700; }
.sig-conf { font-size: 13px; color: #94a3b8; margin-top: 6px; }

/* ── قسم المؤشرات ── */
.ind-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 10px 14px; border-radius: 8px; margin: 4px 0;
    background: #1a1f2e; border: 1px solid #2d3748;
    font-size: 14px;
}
.ind-buy  { border-right: 4px solid #10b981; }
.ind-sell { border-right: 4px solid #ef4444; }
.ind-neu  { border-right: 4px solid #64748b; }
.ind-name { font-weight: 600; color: #e2e8f0; }
.ind-val  { color: #94a3b8; font-size: 13px; }

/* ── بطاقات المقاييس ── */
div[data-testid="stMetric"] {
    background: #1a1f2e !important; border-radius: 12px !important;
    padding: 14px !important; border: 1px solid #3d4a63 !important;
}
div[data-testid="stMetricLabel"] { font-size: 13px !important; font-weight: 600 !important; }
div[data-testid="stMetricValue"] { font-size: 22px !important; font-weight: 700 !important; }

/* ── تبويبات ── */
.stTabs [data-baseweb="tab-list"] { gap: 4px; background: #0f1117; border-radius: 10px; padding: 6px; }
.stTabs [data-baseweb="tab"] {
    font-family: 'Cairo', sans-serif !important; font-weight: 600 !important;
    font-size: 14px !important; color: #94a3b8 !important;
    padding: 8px 16px !important; border-radius: 8px !important;
}
.stTabs [aria-selected="true"] {
    background: #1d4ed8 !important; color: #ffffff !important;
}

/* ── شريط جانبي ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1117, #1a1f2e) !important;
    border-left: 1px solid #2d3748;
}
[data-testid="stSidebar"] .stButton > button {
    text-align: right !important; padding-right: 14px !important;
    font-size: 14px !important; margin-bottom: 2px !important;
}

/* ── أخبار ── */
.news-card {
    background: #1a1f2e; border: 1px solid #2d3748; border-radius: 10px;
    padding: 14px; margin: 8px 0; border-right: 4px solid #3b82f6;
}
.news-title { font-size: 14px; font-weight: 600; color: #e2e8f0; margin-bottom: 6px; }
.news-meta { font-size: 12px; color: #64748b; }
.news-body { font-size: 13px; color: #94a3b8; margin-top: 6px; line-height: 1.7; }

/* ── بطاقة التوزيعات ── */
.div-card {
    background: linear-gradient(135deg,#052e16,#064e3b); border:1px solid #10b981;
    border-radius:12px; padding:16px; text-align:center;
}
.div-val { font-size:28px; font-weight:800; color:#10b981; }
.div-lbl { font-size:13px; color:#6ee7b7; }

/* ── تقدم RSI ── */
.progress-bar { height: 8px; border-radius: 4px; background: #2d3748; overflow: hidden; margin: 6px 0; }
.progress-fill { height: 100%; border-radius: 4px; }

/* ── شريط عنوان ── */
.page-header {
    background: linear-gradient(135deg,#1e2738,#2d3748);
    border-radius:14px; padding:20px 24px; margin-bottom:20px;
    border:1px solid #3d4a63;
}
.page-title { font-size:22px; font-weight:700; color:#f59e0b; }
.page-sub   { font-size:13px; color:#64748b; margin-top:4px; }

/* ── شارات المصدر ── */
.badge-real { background:#064e3b; border:1px solid #10b981; color:#6ee7b7;
              border-radius:6px; padding:2px 10px; font-size:11px; }
.badge-sim  { background:#78350f; border:1px solid #f59e0b; color:#fcd34d;
              border-radius:6px; padding:2px 10px; font-size:11px; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# دوال مساعدة
# ═══════════════════════════════════════════════════════════════
def safe_plotly_chart(fig, **kwargs):
    """✅ FIX #10: تغليف st.plotly_chart بـ try-except لمنع تعطل التطبيق عند بيانات فارغة"""
    try:
        st.plotly_chart(fig, **kwargs)
    except Exception as e:
        st.error(f"⚠️ فشل رسم البيانات: {e}")

@st.cache_data(ttl=900, show_spinner="جاري تحميل بيانات السهم...")
def cached_load(symbol: str, days: int = 300):
    # ✅ FIX #7: show_spinner مفعّل — جلب Yahoo Finance متزامن (synchronous) وقد يستغرق
    # ثانية أو أكثر؛ السبينر يمنع شعور المستخدم بتجمّد الواجهة. التخزين المؤقت (TTL=15 دقيقة)
    # يضمن أن هذا التأخير يحدث مرة واحدة فقط لكل سهم خلال هذه النافذة الزمنية.
    return load_and_compute(symbol, days)

def init_state():
    for k,v in {'watchlist':['COMI','TMGH','ETEL','FWRY','SWDY','ECIG','SKPC'],
                'alerts':[],'capital':100_000.0,'page':'home'}.items():
        if k not in st.session_state: st.session_state[k]=v
init_state()

@st.cache_resource(show_spinner=False)
def get_ai_analyzer():
    return AIAnalyzer()

AI = get_ai_analyzer()

BG = '#0f1117'
CHART_LAYOUT = dict(paper_bgcolor=BG, plot_bgcolor=BG,
    font=dict(color='#e2e8f0',family='Cairo'),
    xaxis=dict(gridcolor='#1e2738',showgrid=True,zeroline=False),
    yaxis=dict(gridcolor='#1e2738',showgrid=True,zeroline=False),
    margin=dict(l=50,r=20,t=50,b=40), showlegend=True,
    legend=dict(bgcolor='#1a1f2e',bordercolor='#3d4a63',font=dict(size=12)))

def clr_sign(v): return "#10b981" if v>=0 else "#ef4444"

# ✅ دالة تلوين جدول الباكتست — مستوى الوحدة (بدون تعارض)
def _color_backtest(df_style):
    def _cell_color(val):
        if isinstance(val, str) and '%' in val:
            try:
                v = float(val.replace('%',''))
                if v > 10: return 'color:#10b981;font-weight:700'
                elif v > 0: return 'color:#84cc16'
                elif v < 0: return 'color:#ef4444;font-weight:700'
            except: pass
        return ''
    return df_style.map(_cell_color)  # ✅ map بدلاً من applymap

# ═══════════════════════════════════════════════════════════════
# الرسم البياني الرئيسي
# ═══════════════════════════════════════════════════════════════
def plot_main(df, symbol, indicators):
    extra = sum(x in indicators for x in ['RSI','MACD','Volume'])
    rows = 1 + extra
    rh = [0.55] + [0.15]*extra
    specs = [[{"secondary_y":True}]] + [[{}]]*extra
    subtitles = [f"سعر {symbol}"] + [x for x in ['RSI','MACD','Volume'] if x in indicators]
    fig = make_subplots(rows=rows,cols=1,shared_xaxes=True,
                        row_heights=rh,specs=specs,
                        subplot_titles=subtitles,vertical_spacing=0.03)

    fig.add_trace(go.Candlestick(x=df.index,open=df['open'],high=df['high'],
        low=df['low'],close=df['close'],name='السعر',
        increasing_line_color='#10b981',decreasing_line_color='#ef4444',
        increasing_fillcolor='#10b981',decreasing_fillcolor='#ef4444'), row=1,col=1)

    if 'EMA' in indicators:
        for col,clr,lbl in [('ema_9','#f59e0b','EMA 9'),('ema_20','#3b82f6','EMA 20'),
                             ('ema_50','#8b5cf6','EMA 50'),('ema_200','#ec4899','EMA 200')]:
            if col in df.columns:
                fig.add_trace(go.Scatter(x=df.index,y=df[col],name=lbl,
                    line=dict(color=clr,width=1.5),opacity=0.9),row=1,col=1)

    if 'Bollinger' in indicators and 'bb_upper' in df.columns:
        fig.add_trace(go.Scatter(x=df.index,y=df['bb_upper'],name='BB Upper',
            line=dict(color='#64748b',dash='dash',width=1),opacity=0.7),row=1,col=1)
        fig.add_trace(go.Scatter(x=df.index,y=df['bb_lower'],name='BB Lower',
            line=dict(color='#64748b',dash='dash',width=1),opacity=0.7,
            fill='tonexty',fillcolor='rgba(100,116,139,0.07)'),row=1,col=1)

    if 'VWAP' in indicators and 'vwap' in df.columns:
        fig.add_trace(go.Scatter(x=df.index,y=df['vwap'],name='VWAP يومي',
            line=dict(color='#fbbf24',width=2,dash='dot')),row=1,col=1)

    if 'Supertrend' in indicators and 'supertrend' in df.columns:
        up=df['supertrend'].where(df['supertrend_dir']==1)
        dn=df['supertrend'].where(df['supertrend_dir']==-1)
        fig.add_trace(go.Scatter(x=df.index,y=up,name='ST شراء',
            line=dict(color='#10b981',width=2.5)),row=1,col=1)
        fig.add_trace(go.Scatter(x=df.index,y=dn,name='ST بيع',
            line=dict(color='#ef4444',width=2.5)),row=1,col=1)

    if 'Ichimoku' in indicators:
        for col,clr,lbl in [('ich_tenkan','#f59e0b','Tenkan'),('ich_kijun','#3b82f6','Kijun')]:
            if col in df.columns:
                fig.add_trace(go.Scatter(x=df.index,y=df[col],name=lbl,
                    line=dict(color=clr,width=1.5)),row=1,col=1)
        if 'ich_senkou_a' in df.columns and 'ich_senkou_b' in df.columns:
            fig.add_trace(go.Scatter(x=df.index,y=df['ich_senkou_a'],name='Senkou A',
                line=dict(color='#10b981',width=1),opacity=0.5),row=1,col=1)
            fig.add_trace(go.Scatter(x=df.index,y=df['ich_senkou_b'],name='Senkou B',
                line=dict(color='#ef4444',width=1),opacity=0.5,fill='tonexty',
                fillcolor='rgba(16,185,129,0.08)'),row=1,col=1)

    if 'PSAR' in indicators and 'psar' in df.columns:
        fig.add_trace(go.Scatter(x=df.index,y=df['psar'],name='Parabolic SAR',
            mode='markers',marker=dict(size=3,color='#a78bfa')),row=1,col=1)

    cr=2
    if 'RSI' in indicators and 'rsi' in df.columns:
        fig.add_trace(go.Scatter(x=df.index,y=df['rsi'],name='RSI',
            line=dict(color='#f59e0b',width=1.5)),row=cr,col=1)
        for lvl,c_ in [(70,'#ef4444'),(30,'#10b981'),(50,'#64748b')]:
            fig.add_hline(y=lvl,line_dash='dash',line_color=c_,opacity=0.5,row=cr,col=1)
        fig.update_yaxes(range=[0,100],row=cr,col=1); cr+=1

    if 'MACD' in indicators and 'macd' in df.columns:
        fig.add_trace(go.Scatter(x=df.index,y=df['macd'],name='MACD',
            line=dict(color='#3b82f6',width=1.5)),row=cr,col=1)
        fig.add_trace(go.Scatter(x=df.index,y=df['macd_signal'],name='Signal',
            line=dict(color='#f59e0b',width=1.5)),row=cr,col=1)
        clrs_hist=['#10b981' if v>=0 else '#ef4444' for v in df['macd_hist'].fillna(0)]
        fig.add_trace(go.Bar(x=df.index,y=df['macd_hist'],name='Hist',
            marker_color=clrs_hist,opacity=0.7),row=cr,col=1); cr+=1

    if 'Volume' in indicators and 'volume' in df.columns:
        vclrs=['#10b981' if c_>=o_ else '#ef4444' for c_,o_ in zip(df['close'],df['open'])]
        fig.add_trace(go.Bar(x=df.index,y=df['volume'],name='الحجم',
            marker_color=vclrs,opacity=0.8),row=cr,col=1)
        if 'vol_sma' in df.columns:
            fig.add_trace(go.Scatter(x=df.index,y=df['vol_sma'],name='متوسط الحجم',
                line=dict(color='#f59e0b',width=1.5,dash='dot')),row=cr,col=1)

    fig.update_layout(**CHART_LAYOUT, height=600+150*extra, xaxis_rangeslider_visible=False)
    for i in range(1,rows+1):
        fig.update_xaxes(gridcolor='#1e2738',row=i,col=1)
        fig.update_yaxes(gridcolor='#1e2738',row=i,col=1)
    return fig

# ═══════════════════════════════════════════════════════════════
# الصفحات
# ═══════════════════════════════════════════════════════════════
def _navigate_to(page_key: str):
    """✅ FIX (DOM removeChild): تغيير الصفحة عبر callback واحد بدل rerun() متفرق
    يضمن تحديث session_state قبل بدء إعادة الرسم، فلا يحدث تعارض في DOM."""
    st.session_state['page'] = page_key

def page_home():
    st.markdown('<div class="page-header"><div class="page-title">📊 لوحة السوق الرئيسية</div><div class="page-sub">بورصة الأوراق المالية المصرية — تحديث فوري</div></div>', unsafe_allow_html=True)

    # ── أزرار التنقل السريع ──
    cols_nav = st.columns(5)
    nav_items = [("🔍 تحليل سهم","analysis"),("⚡ Supertrend","supertrend"),
                 ("🧪 باكتست","backtest"),("🤖 ذكاء اصطناعي","ml"),("💼 محفظة","portfolio")]
    for col,(lbl,pg) in zip(cols_nav,nav_items):
        with col:
            st.button(lbl, key=f"nav_quick_{pg}", on_click=_navigate_to, args=(pg,))

    st.markdown("---")

    # ── EGX30 لوحة ──
    st.markdown("### 🏆 أبرز أسهم EGX30")
    display_syms = EGXDatabase.EGX30[:10]
    for row_start in range(0, len(display_syms), 5):
        cols = st.columns(5)
        for col, sym in zip(cols, display_syms[row_start:row_start+5]):
            df = cached_load(sym)
            info = EGXDatabase.STOCKS.get(sym,{})
            if df is not None and len(df)>1:
                price=float(df['close'].iloc[-1]); chg=float(df['pct_change'].iloc[-1])
                vol=int(df['volume'].iloc[-1]); src=df.get('data_source',pd.Series(['?'])).iloc[-1]
                clr=clr_sign(chg); arr="▲" if chg>=0 else "▼"
                with col:
                    st.markdown(f"""
                    <div class="mcard">
                        <div class="mcard-name">{info.get('name','')[:18]}</div>
                        <div class="mcard-name" style="color:#64748b;font-size:11px">{sym}</div>
                        <div class="mcard-price" style="color:{clr}">{price:.2f}</div>
                        <div class="mcard-change" style="color:{clr}">{arr} {abs(chg):.2f}%</div>
                        <div class="mcard-vol">حجم: {fmt_num(vol)}</div>
                        <span class="{'badge-real' if src=='real' else 'badge-sim'}">{'🟢 حقيقي' if src=='real' else '🟡 محاكاة'}</span>
                    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    # ── قائمة المراقبة أداء ──
    st.markdown("### 👁️ أداء قائمة المراقبة")
    wl = st.session_state['watchlist'][:8]
    if wl:
        perf=[]
        with st.spinner("جاري تحليل القائمة..."):
            for sym in wl:
                df=cached_load(sym)
                if df is not None and len(df)>5:
                    chg1=float(df['pct_change'].iloc[-1])
                    chg5=float(df['close'].pct_change(5).iloc[-1]*100)
                    sig,em,conf,_=get_composite_signal(df)
                    perf.append({'رمز':sym,'الشركة':EGXDatabase.STOCKS.get(sym,{}).get('name','')[:20],
                                 'اليوم':chg1,'5 أيام':chg5,'إشارة':f"{em} {sig}",'ثقة':f"{conf}%"})
        if perf:
            df_p=pd.DataFrame(perf).sort_values('5 أيام',ascending=False)
            c1,c2=st.columns(2)
            with c1:
                st.markdown("#### 🟢 أفضل أداء")
                for _,r in df_p.head(3).iterrows():
                    st.success(f"**{r['رمز']}** {r['الشركة']} | اليوم: {r['اليوم']:+.2f}% | 5 أيام: {r['5 أيام']:+.2f}%")
            with c2:
                st.markdown("#### 🔴 أضعف أداء")
                for _,r in df_p.tail(3).iloc[::-1].iterrows():
                    st.error(f"**{r['رمز']}** {r['الشركة']} | اليوم: {r['اليوم']:+.2f}% | 5 أيام: {r['5 أيام']:+.2f}%")

def page_analysis():
    st.markdown('<div class="page-header"><div class="page-title">🔍 تحليل السهم</div><div class="page-sub">تحليل فني شامل مع جميع المؤشرات</div></div>', unsafe_allow_html=True)
    all_syms=sorted(EGXDatabase.STOCKS.keys())
    c1,c2,c3=st.columns([3,1,1])
    with c1: sym=st.selectbox("اختر السهم",all_syms,index=all_syms.index('COMI') if 'COMI' in all_syms else 0)
    with c2: days=st.slider("عدد الأيام",60,500,300,30)
    with c3:
        st.markdown("<br>",unsafe_allow_html=True)
        if st.button("➕ أضف للمراقبة"):
            if sym not in st.session_state['watchlist']:
                st.session_state['watchlist'].append(sym); st.success(f"✅ تمت إضافة {sym}")

    with st.spinner(f"جاري تحليل {sym}..."):
        df=cached_load(sym,days)
    if df is None or df.empty: st.error("⚠️ لا بيانات كافية"); return

    info=EGXDatabase.STOCKS.get(sym,{})
    src=df['data_source'].iloc[-1] if 'data_source' in df.columns else '?'
    price=float(df['close'].iloc[-1]); chg=float(df['pct_change'].iloc[-1])
    clr=clr_sign(chg)

    # ── Header السهم ──
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#1a1f2e,#2d3748);border-radius:14px;
                padding:20px 24px;margin-bottom:20px;border:1px solid #3d4a63;
                display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap">
        <div>
            <div style="font-size:20px;font-weight:800;color:#f1f5f9">{info.get('name',sym)}</div>
            <div style="color:#64748b;font-size:13px;margin-top:4px">
                {sym} &nbsp;·&nbsp; {info.get('sector','')} &nbsp;·&nbsp;
                <span class="{'badge-real' if src=='real' else 'badge-sim'}">
                    {'🟢 بيانات حقيقية' if src=='real' else '🟡 محاكاة GARCH'}</span>
            </div>
        </div>
        <div style="text-align:left">
            <div style="font-size:32px;font-weight:800;color:{clr}">{price:.2f} EGP</div>
            <div style="color:{clr};font-size:16px;font-weight:600">
                {"▲" if chg>=0 else "▼"} {abs(chg):.2f}%
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    # ── مقاييس سريعة ──
    h52=float(df['high'].tail(252).max()); l52=float(df['low'].tail(252).min())
    avg_vol=int(df['volume'].tail(20).mean()); rsi_v=safe_last(df['rsi'],50)
    atr_v=safe_last(df['atr']); vol20=safe_last(df['volatility_20d'],0)*100
    pe=info.get('pe',0); div_y=info.get('div_yield',0)

    m=st.columns(7)
    m[0].metric("أعلى 52 أسبوع",f"{h52:.2f}")
    m[1].metric("أدنى 52 أسبوع",f"{l52:.2f}")
    m[2].metric("متوسط الحجم 20ي",fmt_num(avg_vol))
    m[3].metric("RSI",f"{rsi_v:.1f}")
    m[4].metric("ATR",f"{atr_v:.2f}")
    m[5].metric("تذبذب سنوي",f"{vol20:.1f}%")
    m[6].metric("عائد التوزيعات",f"{div_y:.1f}%")

    # ── تبويبات التحليل ──
    tabs=st.tabs(["📈 الرسم البياني","🎯 الإشارات","🕯️ الشموع","📐 دعم ومقاومة","📰 الأخبار","💰 التوزيعات","🎯 التوقعات"])

    with tabs[0]:
        ind_opts=['EMA','Bollinger','VWAP','Supertrend','Ichimoku','PSAR','RSI','MACD','Volume']
        show_ind=st.multiselect("المؤشرات المعروضة",ind_opts,
                                default=['EMA','Supertrend','RSI','MACD','Volume'],
                                key=f"ind_{sym}")
        fig=plot_main(df,sym,show_ind)
        safe_plotly_chart(fig,use_container_width=True)

    with tabs[1]:
        sig,emoji,conf,sigs=get_composite_signal(df)
        sig_cls="sig-buy" if "شراء" in sig else "sig-sell" if "بيع" in sig else "sig-neu"
        st.markdown(f"""
        <div class="{sig_cls}">
            <div style="font-size:40px">{emoji}</div>
            <div class="sig-text">{sig}</div>
            <div class="sig-conf">مبني على 12 مؤشر · ثقة {conf}%</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("")
        st.markdown("#### تفاصيل المؤشرات")
        for name,desc in sigs.items():
            is_buy="شراء" in desc or "صاعد" in desc or "✅" in desc or "فوق" in desc
            is_sell="بيع" in desc or "هابط" in desc or "❌" in desc or "تحت" in desc
            cls="ind-buy" if is_buy else "ind-sell" if is_sell else "ind-neu"
            icon="🟢" if is_buy else "🔴" if is_sell else "⚪"
            st.markdown(f"""
            <div class="ind-row {cls}">
                <span class="ind-name">{icon} {name}</span>
                <span class="ind-val">{desc}</span>
            </div>""", unsafe_allow_html=True)

    with tabs[2]:
        patterns=detect_patterns(df)
        if patterns:
            for p in patterns:
                s_clr="#10b981" if p['signal']=="شراء" else "#ef4444" if p['signal']=="بيع" else "#94a3b8"
                stars="⭐"*p['strength']
                st.markdown(f"""
                <div style="background:#1a1f2e;border:1px solid #2d3748;border-right:4px solid {s_clr};
                            border-radius:10px;padding:14px;margin:8px 0">
                    <div style="font-size:15px;font-weight:700;color:#e2e8f0">{p['emoji']} {p['name']}</div>
                    <div style="font-size:12px;color:#64748b;margin:4px 0">{stars} · إشارة: <b style="color:{s_clr}">{p['signal']}</b></div>
                    <div style="font-size:13px;color:#94a3b8">{p['desc']}</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("لا توجد أنماط شموع واضحة في آخر 3 شموع")

    with tabs[3]:
        sup,res=get_support_resistance(df)
        fib=get_fibonacci_levels(sup,res)
        pos_pct=((price-sup)/(res-sup)*100) if res>sup else 50
        c1,c2=st.columns(2)
        with c1:
            st.markdown("#### مستويات الدعم والمقاومة")
            st.markdown(f"**🔴 مقاومة:** `{res:.2f} EGP`")
            st.progress(min(max(int(pos_pct),0),100))
            st.caption(f"السعر الحالي عند {pos_pct:.1f}% من النطاق")
            st.markdown(f"**🟢 دعم:** `{sup:.2f} EGP`")
        with c2:
            st.markdown("#### مستويات فيبوناتشي")
            for lvl,val in fib.items():
                near=abs(price-val)/price<0.02
                st.markdown(f"{'⭐ ' if near else ''}`{lvl}:` **{val:.2f}**{'  ← أقرب مستوى' if near else ''}")

    with tabs[4]:
        st.markdown("#### 📰 آخر الأخبار")
        news=get_stock_news(sym)
        if news:
            for n in news:
                ts=datetime.fromtimestamp(n['time']).strftime('%Y-%m-%d') if n.get('time') else 'N/A'
                sim_badge='<span class="badge-sim">محاكاة</span>' if n.get('simulated') else ''
                st.markdown(f"""
                <div class="news-card">
                    <div class="news-title">{n['title']} {sim_badge}</div>
                    <div class="news-meta">📅 {ts} · 📰 {n.get('source','')}</div>
                    <div class="news-body">{n.get('summary','')}</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("لا توجد أخبار متاحة حالياً")

    with tabs[5]:
        st.markdown("#### 💰 التوزيعات النقدية")
        div=info.get('dividend',0); div_y=info.get('div_yield',0); div_dt=info.get('div_date','N/A')
        c1,c2,c3=st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="div-card">
                <div class="div-val">{div:.3f}</div>
                <div class="div-lbl">آخر توزيع (EGP للسهم)</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.metric("عائد التوزيعات",f"{div_y:.1f}%")
        with c3:
            st.metric("موعد التوزيع المتوقع",div_dt or "لا يوزّع")
        st.markdown("")
        hist=get_dividends_history(sym)
        if not hist.empty:
            st.markdown("#### سجل التوزيعات")
            st.dataframe(hist,use_container_width=True)
        else:
            st.info("هذه الشركة لا توزّع أرباحاً حالياً")

    with tabs[6]:
        st.markdown("#### 🎯 توقعات الأسعار وتقييم السهم")
        targets=get_price_targets(sym,df)
        if targets:
            rec=targets['recommendation']; rec_clr=targets['rec_color']
            st.markdown(f"""
            <div style="background:#1a1f2e;border:2px solid {rec_clr};border-radius:14px;padding:20px;text-align:center;margin-bottom:20px">
                <div style="font-size:28px;font-weight:800;color:{rec_clr}">{rec}</div>
                <div style="font-size:13px;color:#64748b;margin-top:6px">التوصية الإجمالية</div>
            </div>""", unsafe_allow_html=True)
            c1,c2,c3,c4=st.columns(4)
            c1.metric("🟢 هدف صاعد",f"{targets['bull_target']:.2f}",
                      f"+{targets['upside_pct']:.1f}%")
            c2.metric("📊 هدف أساسي",f"{targets['base_target']:.2f}")
            c3.metric("🔴 هدف هابط",f"{targets['bear_target']:.2f}",
                      f"{targets['downside_pct']:.1f}%")
            c4.metric("💡 القيمة العادلة",f"{targets['fair_value_pe']:.2f}")

            st.markdown("")
            c1,c2,c3=st.columns(3)
            c1.metric("P/E الحالي",f"{targets['pe']:.1f}x")
            c2.metric("P/E القطاعي",f"{targets['fair_pe']:.1f}x")
            c3.metric("EPS",f"{targets['eps']:.2f} EGP")

            # رسم مستويات الأهداف
            fig2=go.Figure()
            recent=df.tail(60)
            fig2.add_trace(go.Candlestick(x=recent.index,open=recent['open'],high=recent['high'],
                low=recent['low'],close=recent['close'],name='السعر',
                increasing_line_color='#10b981',decreasing_line_color='#ef4444'))
            for val,clr2,lbl2 in [
                (targets['bull_target'],'#10b981',f"هدف صاعد {targets['bull_target']:.2f}"),
                (targets['base_target'],'#f59e0b',f"هدف أساسي {targets['base_target']:.2f}"),
                (targets['bear_target'],'#ef4444',f"هدف هابط {targets['bear_target']:.2f}"),
                (price,'#3b82f6',f"السعر الحالي {price:.2f}"),
            ]:
                fig2.add_hline(y=val,line_color=clr2,line_dash='dash',line_width=2,
                               annotation_text=lbl2,annotation_position="right")
            fig2.update_layout(**CHART_LAYOUT,height=400,xaxis_rangeslider_visible=False)
            safe_plotly_chart(fig2,use_container_width=True)

def page_supertrend():
    st.markdown('<div class="page-header"><div class="page-title">⚡ محلل Supertrend</div><div class="page-sub">أقوى مؤشر اتجاه في السوق المصري</div></div>', unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    with c1: sym=st.selectbox("السهم",sorted(EGXDatabase.STOCKS.keys()),key='st_sym')
    with c2: period=st.slider("الفترة",5,20,10)
    with c3: mult=st.slider("المضاعف",1.0,5.0,3.0,0.5)

    df=cached_load(sym,300)
    if df is None: st.error("لا بيانات"); return

    st_vals,st_dir=calc_supertrend(df['high'],df['low'],df['close'],period,mult)
    df=df.copy(); df['st_c']=st_vals; df['st_d']=st_dir

    cur_price=float(df['close'].iloc[-1]); cur_st=float(df['st_c'].iloc[-1])
    cur_dir=int(df['st_d'].iloc[-1]); pct_st=(cur_price-cur_st)/cur_st*100

    c1,c2,c3,c4=st.columns(4)
    c1.metric("السعر الحالي",f"{cur_price:.2f}")
    c2.metric("مستوى Supertrend",f"{cur_st:.2f}")
    c3.metric("الإشارة الحالية","🟢 شراء" if cur_dir==1 else "🔴 بيع")
    c4.metric("% من ST",f"{pct_st:+.2f}%")

    fig=go.Figure()
    fig.add_trace(go.Candlestick(x=df.index,open=df['open'],high=df['high'],
        low=df['low'],close=df['close'],name='السعر',
        increasing_line_color='#10b981',decreasing_line_color='#ef4444'))
    up=df['st_c'].where(df['st_d']==1); dn=df['st_c'].where(df['st_d']==-1)
    fig.add_trace(go.Scatter(x=df.index,y=up,name='ST صاعد',line=dict(color='#10b981',width=2.5)))
    fig.add_trace(go.Scatter(x=df.index,y=dn,name='ST هابط',line=dict(color='#ef4444',width=2.5)))
    cu=((df['st_d']==1)&(df['st_d'].shift(1)==-1)); cd=((df['st_d']==-1)&(df['st_d'].shift(1)==1))
    if cu.any():
        fig.add_trace(go.Scatter(x=df.index[cu],y=df['close'][cu],mode='markers+text',
            name=f"شراء ({cu.sum()})",text=['▲']*cu.sum(),textposition='bottom center',
            marker=dict(size=14,color='#10b981',symbol='triangle-up')))
    if cd.any():
        fig.add_trace(go.Scatter(x=df.index[cd],y=df['close'][cd],mode='markers+text',
            name=f"بيع ({cd.sum()})",text=['▼']*cd.sum(),textposition='top center',
            marker=dict(size=14,color='#ef4444',symbol='triangle-down')))
    fig.update_layout(**CHART_LAYOUT,height=550,xaxis_rangeslider_visible=False,
                      title=f"Supertrend — {sym} (Period={period}, Mult={mult})")
    safe_plotly_chart(fig,use_container_width=True)
    st.info(f"📊 إجمالي إشارات الفترة: 🟢 {int(cu.sum())} شراء | 🔴 {int(cd.sum())} بيع")

def page_backtest():
    st.markdown('<div class="page-header"><div class="page-title">🧪 الباكتست التاريخي</div><div class="page-sub">اختبر 10 استراتيجيات على بيانات حقيقية مع محاكاة عمولات EGX</div></div>', unsafe_allow_html=True)

    bt_tabs = st.tabs(["📊 اختبار الاستراتيجيات", "💰 محاكاة DCA"])

    with bt_tabs[0]:
        c1,c2,c3=st.columns(3)
        with c1: sym=st.selectbox("السهم",sorted(EGXDatabase.STOCKS.keys()),key='bt_sym')
        with c2: capital=st.number_input("رأس المال (EGP)",10_000,10_000_000,100_000,10_000)
        with c3: strat_sel=st.multiselect("الاستراتيجيات",ALL_STRATEGIES,default=ALL_STRATEGIES[:5])

        if st.button("🚀 تشغيل الباكتست الآن", type="primary"):
            with st.spinner("جاري تشغيل الاختبار التاريخي..."):
                df=cached_load(sym,500)
                if df is None: st.error("لا بيانات"); return
                results=run_all_backtests(df,capital,strat_sel)
                summary=backtest_summary_df(results)
            st.success(f"✅ اكتمل على {len(df)} يوم | {len(results)} استراتيجية")
            st.markdown("### 📊 مقارنة الاستراتيجيات")
            styled=_color_backtest(summary.style)
            st.dataframe(styled,use_container_width=True,height=350)
            best=max(results,key=lambda r:r.sharpe_ratio)
            st.info(f"🏆 أفضل استراتيجية: **{best.strategy}** | عائد {best.total_return*100:.1f}% | Sharpe {best.sharpe_ratio:.2f} | Win Rate {best.win_rate*100:.1f}%")

            st.markdown("### 📈 منحنيات رأس المال")
            fig=go.Figure()
            clrs_list=['#3b82f6','#10b981','#f59e0b','#8b5cf6','#ef4444','#06b6d4','#ec4899','#84cc16','#f97316','#6366f1']
            for r,cl in zip(results,clrs_list):
                if not r.equity_curve.empty:
                    norm=r.equity_curve/r.equity_curve.iloc[0]*100
                    fig.add_trace(go.Scatter(x=norm.index,y=norm,name=f"{r.strategy} ({r.total_return*100:+.1f}%)",
                        line=dict(color=cl,width=2)))
            fig.update_layout(**CHART_LAYOUT,height=450,yaxis_title="رأس المال (100=البداية)")
            safe_plotly_chart(fig,use_container_width=True)

            sel_s=st.selectbox("تفاصيل الصفقات",[ r.strategy for r in results if r.total_trades>0])
            sel_r=next((r for r in results if r.strategy==sel_s),None)
            if sel_r and sel_r.trades:
                trades_df=pd.DataFrame([{'دخول':str(t.entry_date)[:10],'خروج':str(t.exit_date)[:10],
                    'سعر الدخول':f"{t.entry_price:.2f}",'سعر الخروج':f"{t.exit_price:.2f}",
                    'أسهم':t.shares,'ربح/خسارة EGP':f"{t.pnl:+.0f}",'العائد':f"{t.pnl_pct*100:+.2f}%"}
                    for t in sel_r.trades])
                st.dataframe(trades_df,use_container_width=True,height=300)

    with bt_tabs[1]:
        st.markdown("#### 💰 محاكاة الاستثمار بالمبالغ الدورية (DCA)")
        st.caption("استراتيجية شراء مبلغ ثابت كل شهر — تقلل أثر تقلبات السوق على المدى الطويل")
        c1,c2,c3=st.columns(3)
        with c1: dca_sym=st.selectbox("السهم",sorted(EGXDatabase.STOCKS.keys()),key='dca_sym')
        with c2: monthly=st.number_input("المبلغ الشهري (EGP)",500,1_000_000,5_000,500)
        with c3: months=st.slider("عدد الشهور",3,36,12)

        if st.button("🚀 ابدأ محاكاة DCA", type="primary"):
            with st.spinner("جاري محاكاة DCA..."):
                df_dca=cached_load(dca_sym,max(months*22,300))
                if df_dca is None: st.error("لا بيانات"); return
                result=dca_simulation(df_dca,monthly,months)
            if 'error' in result:
                st.error(result['error'])
            else:
                c1,c2,c3,c4=st.columns(4)
                c1.metric("إجمالي المستثمر",fmt_egp(result['total_invested']))
                c2.metric("القيمة النهائية",fmt_egp(result['final_value']))
                c3.metric("الربح/الخسارة",fmt_egp(result['total_pnl']),
                          f"{result['total_pnl_pct']:+.2f}%")
                c4.metric("متوسط التكلفة",f"{result['average_cost']:.2f} EGP")

                st.markdown("")
                comp_clr = "#10b981" if result['dca_vs_lump_sum']>=0 else "#ef4444"
                comp_txt = "أفضل" if result['dca_vs_lump_sum']>=0 else "أضعف"
                st.markdown(f"""
                <div style="background:#1a1f2e;border:1px solid {comp_clr};border-radius:12px;padding:14px 18px">
                    <b style="color:{comp_clr}">DCA كانت {comp_txt} بـ {abs(result['dca_vs_lump_sum']):.1f} نقطة مقارنة بالشراء دفعة واحدة</b><br>
                    <span style="color:#94a3b8;font-size:13px">عائد DCA: {result['total_pnl_pct']:+.1f}% · عائد الدفعة الواحدة: {result['lump_sum_pnl_pct']:+.1f}%</span>
                </div>""", unsafe_allow_html=True)

                df_m=pd.DataFrame(result['monthly_data'])
                fig=go.Figure()
                fig.add_trace(go.Scatter(x=df_m['month'],y=df_m['total_invested'],
                    name='إجمالي المستثمر',line=dict(color='#64748b',width=2,dash='dash')))
                fig.add_trace(go.Scatter(x=df_m['month'],y=df_m['current_value'],
                    name='القيمة الحالية',line=dict(color='#10b981',width=2.5),fill='tonexty',
                    fillcolor='rgba(16,185,129,0.08)'))
                fig.update_layout(**CHART_LAYOUT,height=400,xaxis_title="الشهر",yaxis_title="EGP")
                safe_plotly_chart(fig,use_container_width=True)
                st.dataframe(df_m,use_container_width=True,height=250)

@st.cache_resource(show_spinner=False)
def _train_ml_cached(symbol: str, days: int, n_splits: int):
    """✅ FIX #6: تخزين مؤقت للنموذج المُدرَّب — يمنع إعادة التدريب في كل نقرة"""
    df = load_and_compute(symbol, days)
    if df is None:
        return None, {'error': 'لا بيانات كافية'}
    pred = EGXMLPredictor()
    metrics = pred.train_walk_forward(df, n_splits)
    return pred, metrics

def page_ml():
    st.markdown('<div class="page-header"><div class="page-title">🤖 تحليل الذكاء الاصطناعي</div><div class="page-sub">Walk-Forward Validation — تدريب على الماضي، اختبار على المستقبل</div></div>', unsafe_allow_html=True)
    st.success("✅ الخوارزمية تستخدم Walk-Forward Validation الصحيح — بدون Data Leakage")
    sym=st.selectbox("السهم",sorted(EGXDatabase.STOCKS.keys()),key='ml_sym')
    c1,c2=st.columns(2)
    with c1: n_splits=st.slider("عدد الـ Folds",3,8,5)
    with c2: days=st.slider("الفترة (يوم)",100,500,300,50,key='ml_days')

    c_train, c_clear = st.columns([3,1])
    with c_train:
        train_clicked = st.button("🧠 تدريب النموذج الآن", type="primary")
    with c_clear:
        if st.button("🗑️ مسح ذاكرة النماذج"):
            _train_ml_cached.clear()
            st.success("✅ تم مسح النماذج المخزّنة")

    if train_clicked:
        with st.spinner("جاري التدريب بـ Walk-Forward Validation (أو الجلب من الذاكرة المؤقتة)..."):
            df=cached_load(sym,days)
            if df is None: st.error("لا بيانات"); return
            pred, metrics = _train_ml_cached(sym, days, n_splits)
        if pred is None or 'error' in metrics: st.error(f"خطأ: {metrics.get('error','فشل غير معروف')}"); return
        st.success("✅ النموذج جاهز (مخزَّن مؤقتاً لنفس السهم/الفترة/عدد الـ Folds)")
        c1,c2,c3,c4=st.columns(4)
        c1.metric("متوسط الدقة",f"{metrics['avg_accuracy']*100:.1f}%")
        c2.metric("متوسط AUC",f"{metrics['avg_auc']:.3f}")
        c3.metric("متوسط Precision",f"{metrics['avg_precision']*100:.1f}%")
        c4.metric("عدد الـ Folds",str(metrics['n_folds']))

        st.markdown("#### نتائج الـ Folds")
        st.dataframe(pd.DataFrame(metrics['folds']),use_container_width=True)

        label,prob,clr=pred.predict(df)
        st.markdown(f"""
        <div style="background:#1a1f2e;border-radius:14px;padding:24px;text-align:center;border:2px solid #3d4a63;margin:16px 0">
            <div style="font-size:14px;color:#64748b;margin-bottom:8px">تنبؤ النموذج — 5 أيام القادمة</div>
            <div style="font-size:36px">{clr}</div>
            <div style="font-size:24px;font-weight:800;margin:8px 0;color:#e2e8f0">{label}</div>
            <div style="font-size:16px;color:#94a3b8">احتمالية الارتفاع: {prob*100:.1f}%</div>
        </div>""", unsafe_allow_html=True)

        fi=pred.get_feature_importance()
        if not fi.empty:
            st.markdown("#### أهم المتغيرات")
            fig=px.bar(fi,x='الأهمية',y='المتغير',orientation='h',
                       color='الأهمية',color_continuous_scale='Blues')
            fig.update_layout(**CHART_LAYOUT,height=400)
            safe_plotly_chart(fig,use_container_width=True)

def page_portfolio():
    st.markdown('<div class="page-header"><div class="page-title">💼 إدارة المحفظة</div><div class="page-sub">Kelly Criterion + وقف الخسارة الديناميكي — مبني على نتائج باكتست فعلية</div></div>', unsafe_allow_html=True)
    st.session_state['capital']=st.number_input("رأس المال الكلي (EGP)",10_000.0,10_000_000.0,
                                                  st.session_state['capital'],10_000.0)
    max_risk=st.slider("نسبة المخاطرة لكل صفقة %",0.5,5.0,2.0,0.5)/100
    sym=st.selectbox("اختر سهم للتحليل",sorted(EGXDatabase.STOCKS.keys()),key='pm_sym')
    strategy_for_sizing = st.selectbox("استراتيجية حساب حجم المركز", ALL_STRATEGIES,
                                       index=ALL_STRATEGIES.index('Multi-Signal'),
                                       help="يُستخدم أداء هذه الاستراتيجية التاريخي لحساب Kelly% بدقة")
    df=cached_load(sym)
    if df is None: st.error("لا بيانات"); return
    price=float(df['close'].iloc[-1]); atr_v=safe_last(df['atr'])
    info=EGXDatabase.STOCKS.get(sym,{})

    # ✅ FIX #5: حساب win_rate/avg_win/avg_loss من باكتست فعلي بدلاً من قيم ثابتة
    bt_results = run_all_backtests(df, st.session_state['capital'], [strategy_for_sizing])
    bt_result = bt_results[0] if bt_results else None
    if bt_result and bt_result.total_trades >= 5:
        wr, aw, al = bt_result.win_rate, bt_result.avg_win, bt_result.avg_loss
        data_quality_note = f"✅ مبني على {bt_result.total_trades} صفقة فعلية من استراتيجية {strategy_for_sizing}"
    else:
        # احتياطي معقول عند عدم وجود صفقات كافية، موضّح بصريًا أنه تقديري
        wr, aw, al = 0.50, 0.03, 0.02
        data_quality_note = "⚠️ صفقات تاريخية غير كافية (<5) — استُخدمت قيم افتراضية تقديرية"

    pm=PortfolioManager(st.session_state['capital'])
    pos=pm.calc_position_size(price,wr,aw,al,max_risk)
    sl=pm.calc_stop_loss(price,atr_v)

    st.markdown(f"### 📊 {info.get('name',sym)} — {price:.2f} EGP")
    st.caption(data_quality_note)
    c1,c2,c3,c4=st.columns(4)
    c1.metric("عدد الأسهم (Kelly)",str(pos['shares']))
    c2.metric("رأس المال المطلوب",fmt_egp(pos['capital']))
    c3.metric("% من المحفظة",f"{pos['position_pct']:.1f}%")
    c4.metric("نسبة Kelly",f"{pos['kelly']*100:.1f}%")
    st.markdown("---")
    c5,c6,c7,c8=st.columns(4)
    c5.metric("🛑 وقف الخسارة",fmt_egp(sl['stop_loss']))
    c6.metric("🎯 هدف الربح",fmt_egp(sl['take_profit']))
    c7.metric("% مخاطرة",f"{sl['risk_pct']:.1f}%")
    c8.metric("نسبة R:R",f"{sl['rr_ratio']:.1f}:1")

    fig=go.Figure()
    recent=df.tail(60)
    fig.add_trace(go.Candlestick(x=recent.index,open=recent['open'],high=recent['high'],
        low=recent['low'],close=recent['close'],name='السعر',
        increasing_line_color='#10b981',decreasing_line_color='#ef4444'))
    fig.add_hline(y=price,line_color='#3b82f6',line_dash='dash',line_width=2,annotation_text=f"دخول {price:.2f}")
    fig.add_hline(y=sl['stop_loss'],line_color='#ef4444',line_dash='dot',line_width=2,annotation_text=f"وقف {sl['stop_loss']:.2f}")
    fig.add_hline(y=sl['take_profit'],line_color='#10b981',line_dash='dot',line_width=2,annotation_text=f"هدف {sl['take_profit']:.2f}")
    fig.add_hrect(y0=sl['stop_loss'],y1=price,fillcolor='rgba(239,68,68,0.07)',line_width=0)
    fig.add_hrect(y0=price,y1=sl['take_profit'],fillcolor='rgba(16,185,129,0.07)',line_width=0)
    fig.update_layout(**CHART_LAYOUT,height=450,xaxis_rangeslider_visible=False)
    safe_plotly_chart(fig,use_container_width=True)

def page_watchlist():
    st.markdown('<div class="page-header"><div class="page-title">👁️ قائمة المراقبة</div><div class="page-sub">تابع أسهمك المفضلة في مكان واحد</div></div>', unsafe_allow_html=True)
    new_wl=st.multiselect("اختر الأسهم",sorted(EGXDatabase.STOCKS.keys()),
                          default=st.session_state['watchlist'])
    if new_wl!=st.session_state['watchlist']: st.session_state['watchlist']=new_wl
    if not new_wl: st.warning("أضف أسهماً للقائمة"); return
    with st.spinner("جاري التحليل..."):
        rows=[]
        for sym in new_wl:
            df=cached_load(sym)
            if df is None: continue
            sig,em,conf,_=get_composite_signal(df)
            price=float(df['close'].iloc[-1]); chg=float(df['pct_change'].iloc[-1])
            rsi=safe_last(df['rsi'],50); vol=int(df['volume'].iloc[-1])
            src=df['data_source'].iloc[-1] if 'data_source' in df.columns else '?'
            std=safe_last(df['supertrend_dir'],0) if 'supertrend_dir' in df.columns else 0
            rows.append({'رمز':sym,'الشركة':EGXDatabase.STOCKS.get(sym,{}).get('name','')[:22],
                'القطاع':EGXDatabase.STOCKS.get(sym,{}).get('sector',''),
                'السعر':f"{price:.2f}",'تغيير%':f"{chg:+.2f}%",'RSI':f"{rsi:.0f}",
                'Supertrend':'🟢 صاعد' if std==1 else '🔴 هابط',
                'إشارة':f"{em} {sig}",'ثقة':f"{conf}%",'حجم':fmt_num(vol),
                'بيانات':'🟢 حقيقية' if src=='real' else '🟡 محاكاة'})
    if rows:
        df_wl=pd.DataFrame(rows)
        st.dataframe(df_wl,use_container_width=True,height=500)
        buy_c=sum(1 for r in rows if 'شراء' in r['إشارة'])
        sell_c=sum(1 for r in rows if 'بيع' in r['إشارة'])
        c1,c2,c3=st.columns(3)
        c1.metric("🟢 إشارات شراء",str(buy_c))
        c2.metric("🔴 إشارات بيع",str(sell_c))
        c3.metric("⚪ محايد",str(len(rows)-buy_c-sell_c))

def page_screener():
    st.markdown('<div class="page-header"><div class="page-title">🔎 فلترة الأسهم</div><div class="page-sub">ابحث عن أفضل الفرص بمعايير متعددة</div></div>', unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    with c1: sector=st.selectbox("القطاع",['الكل']+sorted(EGXDatabase.SECTORS.keys()))
    with c2: signal_filter=st.selectbox("الإشارة",['الكل','شراء','بيع','محايد'])
    with c3: rsi_range=st.slider("نطاق RSI",0,100,(20,80))
    min_div=st.slider("الحد الأدنى لعائد التوزيعات %",0.0,10.0,0.0,0.5)
    supertrend_only=st.checkbox("Supertrend شراء فقط",False)

    if st.button("🔍 تشغيل الفلترة الآن", type="primary"):
        syms=list(EGXDatabase.STOCKS.keys() if sector=='الكل' else EGXDatabase.SECTORS.get(sector,[]))
        results_sc=[]
        prog=st.progress(0, text="بدء الفلترة...")
        n=len(syms)
        # ✅ FIX #9: استدعاء واحد لـ progress.progress() لكل تكرار مع نص حالة مباشر،
        # بدلاً من استدعاءات متكررة في كل فرع شرطي
        for idx,sym in enumerate(syms):
            passed = True
            df=cached_load(sym)
            if df is None:
                passed = False
            else:
                rsi=safe_last(df['rsi'],50)
                info=EGXDatabase.STOCKS.get(sym,{})
                std=safe_last(df['supertrend_dir'],0) if 'supertrend_dir' in df.columns else 0
                if not (rsi_range[0]<=rsi<=rsi_range[1]): passed = False
                elif info.get('div_yield',0)<min_div: passed = False
                elif supertrend_only and std!=1: passed = False
                else:
                    sig,em,conf,_=get_composite_signal(df)
                    if signal_filter!='الكل' and signal_filter not in sig:
                        passed = False
                    else:
                        price=float(df['close'].iloc[-1]); chg=float(df['pct_change'].iloc[-1])
                        results_sc.append({'رمز':sym,'الشركة':info.get('name','')[:22],'القطاع':info.get('sector',''),
                            'السعر':f"{price:.2f}",'تغيير%':f"{chg:+.2f}%",'RSI':f"{rsi:.0f}",
                            'عائد التوزيعات':f"{info.get('div_yield',0):.1f}%",
                            'Supertrend':'🟢' if std==1 else '🔴',
                            'إشارة':f"{em} {sig}",'ثقة':f"{conf}%"})
            prog.progress((idx+1)/n, text=f"فحص {sym} ({idx+1}/{n}) — {len(results_sc)} مطابق حتى الآن")
        prog.empty()
        if results_sc:
            st.success(f"✅ {len(results_sc)} سهم مطابق")
            st.dataframe(pd.DataFrame(results_sc),use_container_width=True,height=500)
        else: st.warning("لا توجد أسهم مطابقة")

def page_sector():
    st.markdown('<div class="page-header"><div class="page-title">🏭 تحليل القطاعات</div><div class="page-sub">مقارنة أداء القطاعات ورسم خريطة السوق</div></div>', unsafe_allow_html=True)
    sel=st.multiselect("اختر القطاعات",sorted(EGXDatabase.SECTORS.keys()),
                       default=sorted(EGXDatabase.SECTORS.keys())[:6])
    if not sel: return
    data=[]
    with st.spinner("جاري تحليل القطاعات..."):
        for sec in sel:
            syms=EGXDatabase.SECTORS.get(sec,[])[:5]
            chgs,rsis,sigs=[],[],[]
            for sym in syms:
                df=cached_load(sym)
                if df is None: continue
                chgs.append(float(df['pct_change'].iloc[-1]))
                rsis.append(safe_last(df['rsi'],50))
                s,_,_,_=get_composite_signal(df); sigs.append(s)
            if chgs:
                buy_p=sum(1 for s in sigs if 'شراء' in s)/len(sigs)*100
                data.append({'القطاع':sec,'أسهم':len(syms),'متوسط التغيير%':np.mean(chgs),
                             'متوسط RSI':np.mean(rsis),'إشارات شراء%':buy_p})
    if not data: return
    df_s=pd.DataFrame(data).sort_values('متوسط التغيير%',ascending=False)
    c1,c2=st.columns(2)
    with c1:
        fig=px.bar(df_s,x='القطاع',y='متوسط التغيير%',color='متوسط التغيير%',
                   color_continuous_scale='RdYlGn',title='التغيير اليومي لكل قطاع')
        fig.update_layout(**CHART_LAYOUT,height=400); safe_plotly_chart(fig,use_container_width=True)
    with c2:
        fig2=px.scatter(df_s,x='متوسط RSI',y='إشارات شراء%',size='أسهم',
                        color='متوسط التغيير%',text='القطاع',color_continuous_scale='RdYlGn',
                        title='خريطة القطاعات: RSI vs إشارات الشراء')
        fig2.update_layout(**CHART_LAYOUT,height=400); safe_plotly_chart(fig2,use_container_width=True)
    st.dataframe(df_s,use_container_width=True)

def page_alerts():
    st.markdown('<div class="page-header"><div class="page-title">🔔 نظام التنبيهات</div><div class="page-sub">راقب شروطك تلقائياً في كل تحديث</div></div>', unsafe_allow_html=True)
    sym=st.selectbox("السهم",sorted(EGXDatabase.STOCKS.keys()),key='alert_sym')
    df=cached_load(sym)
    if df is None: st.error("لا بيانات"); return
    price=float(df['close'].iloc[-1]); st.caption(f"السعر الحالي: **{price:.2f} EGP**")
    with st.form("add_alert_form"):
        st.markdown("#### ➕ إضافة تنبيه جديد")
        c1,c2,c3=st.columns(3)
        with c1: atype=st.selectbox("النوع",['سعر أعلى من','سعر أقل من','RSI تشبع شراء (>70)',
                                              'RSI تشبع بيع (<30)','Supertrend شراء','Supertrend بيع'])
        with c2: thresh=st.number_input("القيمة",value=price*1.05,format="%.2f")
        with c3: note=st.text_input("ملاحظة","")
        if st.form_submit_button("➕ إضافة التنبيه", type="primary"):
            st.session_state['alerts'].append({'sym':sym,'type':atype,'threshold':thresh,
                'note':note,'created':str(datetime.now())[:16]})
            st.success("✅ تمت إضافة التنبيه")

    if st.session_state['alerts']:
        st.markdown("#### 📋 التنبيهات الحالية")
        for al in st.session_state['alerts']:
            a_df=cached_load(al['sym'])
            if a_df is None: continue
            ap=float(a_df['close'].iloc[-1]); ar=safe_last(a_df['rsi'],50)
            asd=safe_last(a_df['supertrend_dir'],0) if 'supertrend_dir' in a_df.columns else 0
            trig=((al['type']=='سعر أعلى من' and ap>al['threshold']) or
                  (al['type']=='سعر أقل من' and ap<al['threshold']) or
                  ('تشبع شراء' in al['type'] and ar>70) or
                  ('تشبع بيع' in al['type'] and ar<30) or
                  ('Supertrend شراء' in al['type'] and asd==1) or
                  ('Supertrend بيع' in al['type'] and asd==-1))
            icon='🔔' if trig else '🔕'; stat='✅ محقق!' if trig else '⏳ منتظر'
            bg='background:#052e16;border-color:#10b981;color:#6ee7b7' if trig else 'background:#1a1f2e;border-color:#3d4a63;color:#94a3b8'
            st.markdown(f"""
            <div style="border-radius:10px;padding:14px 18px;margin:6px 0;border-right:4px solid;
                        border:1px solid;{bg};font-size:14px">
                {icon} <b>{al['sym']}</b> — {al['type']} {al.get('threshold',''):g}
                | الحالي: <b>{ap:.2f}</b> | <b>{stat}</b>
                {f" | {al['note']}" if al.get('note') else ''}
            </div>""", unsafe_allow_html=True)
        def _clear_alerts():
            st.session_state['alerts'] = []
        st.button("🗑️ مسح جميع التنبيهات", on_click=_clear_alerts)

def page_compare():
    st.markdown('<div class="page-header"><div class="page-title">⚖️ مقارنة الأسهم</div><div class="page-sub">قارن أداء حتى 5 أسهم معاً</div></div>', unsafe_allow_html=True)
    selected=st.multiselect("اختر حتى 5 أسهم",sorted(EGXDatabase.STOCKS.keys()),
                            default=['COMI','TMGH','ETEL'])[:5]
    if len(selected)<2: st.warning("اختر سهمين على الأقل"); return
    period=st.radio("الفترة",['60 يوم','90 يوم','120 يوم','300 يوم'],horizontal=True)
    n={'60 يوم':60,'90 يوم':90,'120 يوم':120,'300 يوم':300}[period]
    fig=go.Figure(); rows=[]; clrs_list=['#3b82f6','#10b981','#f59e0b','#ef4444','#8b5cf6']
    for sym,cl in zip(selected,clrs_list):
        df=cached_load(sym,n)
        if df is None: continue
        norm=df['close']/df['close'].iloc[0]*100
        chg=(df['close'].iloc[-1]/df['close'].iloc[0]-1)*100
        rsi=safe_last(df['rsi'],50); vol=safe_last(df['volatility_20d'],0)*100
        sig,_,conf,_=get_composite_signal(df)
        fig.add_trace(go.Scatter(x=df.index,y=norm,name=f"{sym} ({chg:+.1f}%)",
            line=dict(color=cl,width=2.5)))
        rows.append({'رمز':sym,'الشركة':EGXDatabase.STOCKS.get(sym,{}).get('name','')[:20],
                     'العائد%':f"{chg:+.1f}%",'RSI':f"{rsi:.0f}",'تذبذب%':f"{vol:.1f}%",
                     'إشارة':sig,'ثقة':f"{conf}%"})
    fig.add_hline(y=100,line_color='#64748b',line_dash='dash',opacity=0.5,annotation_text="نقطة البداية")
    fig.update_layout(**CHART_LAYOUT,height=500,yaxis_title="الأداء (100=البداية)")
    safe_plotly_chart(fig,use_container_width=True)
    if rows: st.dataframe(pd.DataFrame(rows),use_container_width=True)

def page_fibonacci():
    st.markdown('<div class="page-header"><div class="page-title">🌀 تحليل فيبوناتشي</div><div class="page-sub">مستويات الدعم والمقاومة الفنية</div></div>', unsafe_allow_html=True)
    sym=st.selectbox("السهم",sorted(EGXDatabase.STOCKS.keys()),key='fib_sym')
    df=cached_load(sym)
    if df is None: st.error("لا بيانات"); return
    c1,c2=st.columns(2)
    with c1: fp=st.slider("فترة الحساب (يوم)",20,252,60)
    with c2: ext=st.checkbox("مستويات التمديد",True)
    recent=df.tail(fp); sup=float(recent['low'].min()); res=float(recent['high'].max())
    fib=get_fibonacci_levels(sup,res)
    if ext: d=res-sup; fib.update({'161.8%':sup+d*1.618,'200%':sup+d*2.0,'261.8%':sup+d*2.618})
    price=float(df['close'].iloc[-1])
    fig=go.Figure()
    fig.add_trace(go.Candlestick(x=recent.index,open=recent['open'],high=recent['high'],
        low=recent['low'],close=recent['close'],name='السعر',
        increasing_line_color='#10b981',decreasing_line_color='#ef4444'))
    fib_clrs={'0% (دعم)':'#10b981','23.6%':'#84cc16','38.2%':'#f59e0b','50%':'#f97316',
              '61.8%':'#ef4444','78.6%':'#dc2626','100% (مقاومة)':'#991b1b',
              '127.2%':'#8b5cf6','161.8%':'#6366f1','200%':'#3b82f6','261.8%':'#06b6d4'}
    for lvl,val in fib.items():
        near=abs(price-val)/price<0.015
        fig.add_hline(y=val,line_color=fib_clrs.get(lvl,'#64748b'),
                      line_dash='solid' if near else 'dash',line_width=2 if near else 1,opacity=0.9 if near else 0.6,
                      annotation_text=f"{lvl}: {val:.2f}{'  ⭐' if near else ''}",annotation_position="right")
    fig.add_hline(y=price,line_color='#ffffff',line_width=2,line_dash='dot',
                  annotation_text=f"الحالي {price:.2f}")
    fig.update_layout(**CHART_LAYOUT,height=550,xaxis_rangeslider_visible=False)
    safe_plotly_chart(fig,use_container_width=True)
    near_lvl=min(fib.items(),key=lambda x:abs(price-x[1]))
    st.info(f"📍 أقرب مستوى: **{near_lvl[0]}** عند **{near_lvl[1]:.2f} EGP** (بُعد {abs(price-near_lvl[1])/price*100:.2f}%)")

def page_ai_insights():
    st.markdown('<div class="page-header"><div class="page-title">🧠 التحليل الذكي (Gemini AI)</div><div class="page-sub">شرح المؤشرات وتوليد استراتيجيات استثمار مخصصة بالعربية</div></div>', unsafe_allow_html=True)

    if not AI.is_available():
        st.warning("⚠️ Gemini API غير مُفعّل حالياً — تُعرض إجابات مبدئية بديلة. لتفعيل التحليل الكامل، أضف `GEMINI_API_KEY` في `.streamlit/secrets.toml` أو متغيرات البيئة.")

    ai_tabs = st.tabs(["📚 شرح المؤشرات", "🎯 توليد استراتيجية", "💬 ملخص سهم"])

    with ai_tabs[0]:
        st.markdown("#### اختر مؤشراً لشرحه")
        indicator = st.selectbox("المؤشر", ["RSI", "MACD", "Bollinger Bands", "Supertrend", "VWAP"])
        if st.button("📖 اشرح المؤشر", type="primary"):
            with st.spinner("جاري التحليل..."):
                explanation = AI.explain_indicator(indicator)
            st.markdown(f"""<div style="background:#1a1f2e;border:1px solid #3d4a63;border-radius:12px;
                        padding:20px;line-height:1.9;color:#e2e8f0">{explanation}</div>""",
                        unsafe_allow_html=True)

    with ai_tabs[1]:
        st.markdown("#### توليد استراتيجية استثمار مخصصة")
        c1, c2 = st.columns(2)
        with c1:
            risk = st.select_slider("مستوى المخاطرة",
                options=["منخفض جداً", "منخفض", "متوسط", "عالي", "عالي جداً"], value="متوسط")
            capital_ai = st.number_input("رأس المال (جنيه)", 10_000, 10_000_000, 100_000, 10_000, key='ai_capital')
        with c2:
            goals = st.text_area("أهدافك الاستثمارية",
                "بناء محفظة متوازنة على المدى المتوسط مع توزيع مخاطر معقول")
        if st.button("🎯 ولّد الاستراتيجية الآن", type="primary"):
            with st.spinner("جاري توليد الاستراتيجية..."):
                strategy_text = AI.generate_strategy(risk, capital_ai, goals)
            st.markdown(f"""<div style="background:#1a1f2e;border:1px solid #3d4a63;border-radius:12px;
                        padding:20px;line-height:1.9;color:#e2e8f0">{strategy_text}</div>""",
                        unsafe_allow_html=True)

    with ai_tabs[2]:
        st.markdown("#### ملخص تحليلي سردي لسهم")
        sym_ai = st.selectbox("السهم", sorted(EGXDatabase.STOCKS.keys()), key='ai_sym')
        if st.button("💬 ولّد الملخص", type="primary"):
            df_ai = cached_load(sym_ai)
            if df_ai is None:
                st.error("لا بيانات")
            else:
                sig, _, _, _ = get_composite_signal(df_ai)
                rsi_ai = safe_last(df_ai['rsi'], 50)
                price_ai = float(df_ai['close'].iloc[-1])
                sector_ai = EGXDatabase.STOCKS.get(sym_ai, {}).get('sector', '')
                with st.spinner("جاري التحليل..."):
                    summary = AI.analyze_stock_summary(sym_ai, sig, rsi_ai, price_ai, sector_ai)
                st.markdown(f"""<div style="background:#1a1f2e;border:1px solid #3d4a63;border-radius:12px;
                            padding:20px;line-height:1.9;color:#e2e8f0">{summary}</div>""",
                            unsafe_allow_html=True)

def page_database():
    st.markdown('<div class="page-header"><div class="page-title">📚 قاعدة بيانات EGX</div><div class="page-sub">عرض وفلترة تفصيلية لجميع الشركات المدعومة</div></div>', unsafe_allow_html=True)

    db_df = pd.DataFrame([
        {'الرمز': k, 'الاسم': v['name'], 'الاسم بالإنجليزية': v.get('name_en',''),
         'القطاع': v['sector'], 'P/E': v.get('pe', 0), 'EPS': v.get('eps', 0),
         'عائد التوزيعات%': v.get('div_yield', 0), 'القيمة السوقية (مليون)': v.get('market_cap', 0),
         'بيانات حقيقية': '🟢' if v.get('yf') else '🟡'}
        for k, v in EGXDatabase.STOCKS.items()
    ])

    c1, c2, c3 = st.columns(3)
    with c1:
        sector_f = st.selectbox("فلترة بالقطاع", ['الكل'] + sorted(EGXDatabase.SECTORS.keys()), key='db_sector')
    with c2:
        only_real = st.checkbox("بيانات حقيقية فقط (Yahoo Finance)", False)
    with c3:
        min_div = st.slider("الحد الأدنى لعائد التوزيعات%", 0.0, 8.0, 0.0, 0.5, key='db_div')

    filtered = db_df.copy()
    if sector_f != 'الكل':
        filtered = filtered[filtered['القطاع'] == sector_f]
    if only_real:
        filtered = filtered[filtered['بيانات حقيقية'] == '🟢']
    filtered = filtered[filtered['عائد التوزيعات%'] >= min_div]

    st.markdown(f"#### عرض {len(filtered)} من {len(db_df)} شركة")
    st.dataframe(filtered.sort_values('الرمز'), use_container_width=True, height=500, hide_index=True)

    st.markdown("---")
    st.markdown("#### 📊 توزيع الشركات حسب القطاع")
    sector_counts = db_df['القطاع'].value_counts().reset_index()
    sector_counts.columns = ['القطاع', 'عدد الشركات']
    fig = px.bar(sector_counts, x='القطاع', y='عدد الشركات', color='عدد الشركات',
                color_continuous_scale='Blues')
    fig.update_layout(**CHART_LAYOUT, height=380)
    safe_plotly_chart(fig, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي الشركات", str(len(db_df)))
    c2.metric("شركات ببيانات حقيقية", str((db_df['بيانات حقيقية']=='🟢').sum()))
    c3.metric("عدد القطاعات", str(len(EGXDatabase.SECTORS)))

def page_about():
    st.markdown('<div class="page-header"><div class="page-title">ℹ️ عن EGX Pro v31</div><div class="page-sub">منصة التحليل الفني الاحترافية لبورصة الأوراق المالية المصرية</div></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#1a1f2e;border-radius:14px;padding:28px;line-height:2;border:1px solid #3d4a63">
    <h3 style="color:#f59e0b;margin-top:0">🚀 ما الجديد في v31</h3>
    <ul style="color:#e2e8f0">
      <li>✅ <b>VWAP يومي صحيح</b> — يُعاد من الصفر كل يوم (v29 كان خاطئاً)</li>
      <li>✅ <b>Supertrend بـ NumPy</b> — سريع بدون FutureWarning</li>
      <li>✅ <b>ML Walk-Forward</b> بدون Data Leakage + إصلاح class imbalance</li>
      <li>✅ <b>.map() بدلاً من .applymap()</b> — توافق مع pandas 2.1+</li>
      <li>✅ <b>أزرار واضحة القراءة</b> — CSS محسّن بخط Cairo وأحجام مناسبة</li>
      <li>✅ <b>أخبار السهم</b> — حقيقية من Yahoo Finance أو محاكاة ذكية</li>
      <li>✅ <b>التوزيعات النقدية</b> — سجل كامل + عائد التوزيعات</li>
      <li>✅ <b>توقعات الأسعار</b> — 3 سيناريوهات + قيمة عادلة + توصية</li>
      <li>✅ <b>200+ شركة</b> بقيانات: EPS, P/E, توزيعات, مارکت کاب</li>
    </ul>
    <hr style="border-color:#3d4a63">
    <p style="color:#64748b;font-size:13px">
      ⚠️ للأغراض التعليمية والبحثية فقط — ليست توصية استثمارية
    </p>
    </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# الشريط الجانبي والتنقل
# ═══════════════════════════════════════════════════════════════
PAGES = {
    'home':      ("🏠 الرئيسية",      page_home),
    'analysis':  ("🔍 تحليل السهم",   page_analysis),
    'supertrend':("⚡ Supertrend",     page_supertrend),
    'backtest':  ("🧪 الباكتست",      page_backtest),
    'ml':        ("🤖 الذكاء الاصطناعي", page_ml),
    'ai_insights':("🧠 التحليل الذكي AI", page_ai_insights),
    'portfolio': ("💼 إدارة المحفظة", page_portfolio),
    'watchlist': ("👁️ قائمة المراقبة", page_watchlist),
    'screener':  ("🔎 فلترة الأسهم",  page_screener),
    'sector':    ("🏭 تحليل القطاعات",page_sector),
    'database':  ("📚 قاعدة البيانات",page_database),
    'alerts':    ("🔔 التنبيهات",     page_alerts),
    'fibonacci': ("🌀 فيبوناتشي",     page_fibonacci),
    'compare':   ("⚖️ مقارنة الأسهم", page_compare),
    'about':     ("ℹ️ عن التطبيق",    page_about),
}

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:20px 0 16px">
            <div style="font-size:42px">📈</div>
            <div style="font-size:20px;font-weight:800;color:#f59e0b;margin:4px 0">EGX Pro</div>
            <div style="font-size:12px;color:#475569;letter-spacing:2px">ULTIMATE v31</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("---")
        cur=st.session_state.get('page','home')
        for key,(label,_) in PAGES.items():
            is_active=key==cur
            st.button(label, key=f"sb_{key}", help=label,
                     type="primary" if is_active else "secondary",
                     on_click=_navigate_to, args=(key,))
        st.markdown("---")
        n_real=len(EGXDatabase.EGX30); n_total=len(EGXDatabase.STOCKS)
        wl_n=len(st.session_state['watchlist']); alerts_n=len(st.session_state['alerts'])
        st.markdown(f"""
        <div style="font-size:12px;color:#475569;padding:8px 0;line-height:2">
            🏦 {n_total} شركة · {len(EGXDatabase.SECTORS)} قطاع<br>
            🏆 EGX30: {n_real} سهم<br>
            👁️ المراقبة: {wl_n} سهم<br>
            🔔 التنبيهات: {alerts_n}<br>
            📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}
        </div>""", unsafe_allow_html=True)

def main():
    render_sidebar()
    page_key=st.session_state.get('page','home')
    _,func=PAGES.get(page_key,PAGES['home'])
    func()

if __name__=="__main__":
    main()
