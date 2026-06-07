"""
EGX Pro Ultimate v30 — واجهة Streamlit الكاملة
✅ 14 صفحة تحليلية
✅ Supertrend + VWAP يومي + ML Walk-Forward
✅ محفظة ذكية + تنبيهات + مقارنة قطاعية
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json, os, hashlib, warnings
warnings.filterwarnings('ignore')

from egx_engine import (
    EGXDatabase, load_and_compute, detect_patterns,
    get_composite_signal, get_support_resistance,
    get_fibonacci_levels, safe_last, fmt_num, fmt_egp
)
from egx_ml_backtest import (
    EGXMLPredictor, PortfolioManager,
    run_all_backtests, backtest_summary_df, ALL_STRATEGIES
)

# ═══════════════════════════════════════════════════════════════
# إعدادات الصفحة
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="EGX Pro Ultimate v30",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS احترافي ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700&display=swap');
* { font-family: 'Cairo', sans-serif !important; }
body, .stApp { direction: rtl; }
.metric-card {
    background: linear-gradient(135deg, #1a1f2e 0%, #2d3748 100%);
    border: 1px solid #3d4a63; border-radius: 12px;
    padding: 16px; text-align: center; margin: 4px;
    transition: transform 0.2s, box-shadow 0.2s;
}
.metric-card:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0,0,0,0.3); }
.metric-val { font-size: 22px; font-weight: 700; margin: 6px 0 2px; }
.metric-lbl { font-size: 12px; color: #a0aec0; }
.metric-sub { font-size: 11px; color: #718096; }
.signal-buy  { background: linear-gradient(135deg,#065f46,#047857); border:1px solid #059669; border-radius:10px; padding:12px; }
.signal-sell { background: linear-gradient(135deg,#7f1d1d,#991b1b); border:1px solid #dc2626; border-radius:10px; padding:12px; }
.signal-neu  { background: linear-gradient(135deg,#1e293b,#334155); border:1px solid #475569; border-radius:10px; padding:12px; }
.stTabs [data-baseweb="tab"] { font-family:'Cairo',sans-serif !important; font-weight:500; }
.alert-box { border-radius:10px; padding:12px 16px; margin:6px 0;
             border-right:4px solid; font-size:13px; }
.alert-buy  { background:#064e3b22; border-color:#10b981; color:#6ee7b7; }
.alert-sell { background:#7f1d1d22; border-color:#ef4444; color:#fca5a5; }
.source-sim  { background:#78350f22; border:1px solid #f59e0b;
               color:#fcd34d; border-radius:6px; padding:3px 10px;
               font-size:11px; display:inline-block; margin:2px; }
.source-real { background:#064e3b22; border:1px solid #10b981;
               color:#6ee7b7; border-radius:6px; padding:3px 10px;
               font-size:11px; display:inline-block; margin:2px; }
div[data-testid="stMetric"] { background:#1a1f2e; border-radius:10px; padding:12px; border:1px solid #3d4a63; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# Cache & State
# ═══════════════════════════════════════════════════════════════
@st.cache_data(ttl=900, show_spinner=False)
def cached_load(symbol: str, days: int = 300):
    return load_and_compute(symbol, days)

@st.cache_data(ttl=1800, show_spinner=False)
def cached_signal(symbol: str):
    df = cached_load(symbol)
    if df is None: return None, None, 0, {}
    return get_composite_signal(df)

def init_state():
    defaults = {
        'theme': 'dark', 'watchlist': ['COMI','TMGH','ETEL','FWRY','SWDY'],
        'alerts': [], 'portfolio': {}, 'ml_cache': {},
        'capital': 100_000.0, 'page': 'الرئيسية'
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
init_state()

# ═══════════════════════════════════════════════════════════════
# مكوّنات الرسم البياني
# ═══════════════════════════════════════════════════════════════
DARK_TEMPLATE = dict(
    paper_bgcolor='#0f1117', plot_bgcolor='#0f1117',
    font=dict(color='#e2e8f0', family='Cairo'),
    gridcolor='#1e2738', zerolinecolor='#2d3748'
)

def make_base_layout(title=""):
    return dict(
        title=dict(text=title, font=dict(size=16, color='#e2e8f0')),
        paper_bgcolor='#0f1117', plot_bgcolor='#0f1117',
        font=dict(color='#e2e8f0', family='Cairo'),
        xaxis=dict(gridcolor='#1e2738', showgrid=True, zeroline=False),
        yaxis=dict(gridcolor='#1e2738', showgrid=True, zeroline=False),
        margin=dict(l=50, r=20, t=50, b=40), showlegend=True,
        legend=dict(bgcolor='#1a1f2e', bordercolor='#3d4a63')
    )

def plot_main_chart(df: pd.DataFrame, symbol: str, show_indicators: list) -> go.Figure:
    rows = 1 + ('RSI' in show_indicators) + ('MACD' in show_indicators) + ('Volume' in show_indicators)
    row_heights = [0.55] + [0.15]*(rows-1)

    specs = [[{"secondary_y": True}]] + [[{}]]*(rows-1)
    subplot_titles = [f"سعر {symbol}"] + [i for i in ['RSI','MACD','Volume'] if i in show_indicators]

    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True,
                        row_heights=row_heights, specs=specs,
                        subplot_titles=subplot_titles, vertical_spacing=0.04)

    # ── الشموع اليابانية ──
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['open'], high=df['high'],
        low=df['low'], close=df['close'],
        name='السعر', increasing_line_color='#10b981',
        decreasing_line_color='#ef4444',
        increasing_fillcolor='#10b981', decreasing_fillcolor='#ef4444'
    ), row=1, col=1)

    colors_map = {'ema_9':'#f59e0b','ema_20':'#3b82f6','ema_50':'#8b5cf6','ema_200':'#ec4899'}
    labels_map = {'ema_9':'EMA 9','ema_20':'EMA 20','ema_50':'EMA 50','ema_200':'EMA 200'}
    if 'EMA' in show_indicators:
        for col_, clr in colors_map.items():
            if col_ in df.columns:
                fig.add_trace(go.Scatter(x=df.index, y=df[col_], name=labels_map[col_],
                    line=dict(color=clr, width=1.5), opacity=0.9), row=1, col=1)

    if 'Bollinger' in show_indicators and all(c in df.columns for c in ['bb_upper','bb_lower','bb_middle']):
        fig.add_trace(go.Scatter(x=df.index, y=df['bb_upper'], name='BB Upper',
            line=dict(color='#94a3b8', dash='dash', width=1), opacity=0.7), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['bb_lower'], name='BB Lower',
            line=dict(color='#94a3b8', dash='dash', width=1), opacity=0.7,
            fill='tonexty', fillcolor='rgba(148,163,184,0.05)'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['bb_middle'], name='BB Mid',
            line=dict(color='#64748b', width=1), opacity=0.6), row=1, col=1)

    if 'VWAP' in show_indicators and 'vwap' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['vwap'], name='VWAP (يومي)',
            line=dict(color='#fbbf24', width=2, dash='dot'), opacity=0.9), row=1, col=1)

    if 'Supertrend' in show_indicators and 'supertrend' in df.columns:
        up   = df['supertrend'].where(df['supertrend_dir'] == 1)
        down = df['supertrend'].where(df['supertrend_dir'] == -1)
        fig.add_trace(go.Scatter(x=df.index, y=up, name='Supertrend ▲',
            line=dict(color='#10b981', width=2), mode='lines'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=down, name='Supertrend ▼',
            line=dict(color='#ef4444', width=2), mode='lines'), row=1, col=1)

    if 'Ichimoku' in show_indicators:
        for col_, clr, lbl in [('ich_tenkan','#f59e0b','Tenkan'),('ich_kijun','#3b82f6','Kijun')]:
            if col_ in df.columns:
                fig.add_trace(go.Scatter(x=df.index,y=df[col_],name=lbl,
                    line=dict(color=clr,width=1.5),opacity=0.8), row=1, col=1)
        if 'ich_senkou_a' in df.columns and 'ich_senkou_b' in df.columns:
            fig.add_trace(go.Scatter(x=df.index,y=df['ich_senkou_a'],name='Senkou A',
                line=dict(color='#10b981',width=1),opacity=0.5), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index,y=df['ich_senkou_b'],name='Senkou B',
                line=dict(color='#ef4444',width=1),opacity=0.5,
                fill='tonexty',fillcolor='rgba(16,185,129,0.07)'), row=1, col=1)

    if 'PSAR' in show_indicators and 'psar' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['psar'], name='Parabolic SAR',
            mode='markers', marker=dict(size=3, color='#a78bfa', symbol='circle')), row=1, col=1)

    cur_row = 2
    if 'RSI' in show_indicators and 'rsi' in df.columns:
        fig.add_trace(go.Scatter(x=df.index,y=df['rsi'],name='RSI',
            line=dict(color='#f59e0b',width=1.5)), row=cur_row, col=1)
        for lvl, clr in [(70,'#ef4444'),(30,'#10b981'),(50,'#64748b')]:
            fig.add_hline(y=lvl, line_dash='dash', line_color=clr,
                          opacity=0.6, row=cur_row, col=1)
        fig.update_yaxes(range=[0,100], row=cur_row, col=1)
        cur_row += 1

    if 'MACD' in show_indicators and 'macd' in df.columns:
        fig.add_trace(go.Scatter(x=df.index,y=df['macd'],name='MACD',
            line=dict(color='#3b82f6',width=1.5)), row=cur_row, col=1)
        fig.add_trace(go.Scatter(x=df.index,y=df['macd_signal'],name='Signal',
            line=dict(color='#f59e0b',width=1.5)), row=cur_row, col=1)
        clrs = ['#10b981' if v>=0 else '#ef4444' for v in df['macd_hist'].fillna(0)]
        fig.add_trace(go.Bar(x=df.index,y=df['macd_hist'],name='Histogram',
            marker_color=clrs, opacity=0.7), row=cur_row, col=1)
        cur_row += 1

    if 'Volume' in show_indicators and 'volume' in df.columns:
        vol_clrs = ['#10b981' if c>=o else '#ef4444'
                    for c,o in zip(df['close'], df['open'])]
        fig.add_trace(go.Bar(x=df.index,y=df['volume'],name='الحجم',
            marker_color=vol_clrs, opacity=0.8), row=cur_row, col=1)
        if 'vol_sma' in df.columns:
            fig.add_trace(go.Scatter(x=df.index,y=df['vol_sma'],name='متوسط الحجم',
                line=dict(color='#f59e0b',width=1.5,dash='dot')), row=cur_row, col=1)

    fig.update_layout(**make_base_layout(), height=650+150*(rows-1),
                      xaxis_rangeslider_visible=False)
    for i in range(1, rows+1):
        fig.update_xaxes(gridcolor='#1e2738', row=i, col=1)
        fig.update_yaxes(gridcolor='#1e2738', row=i, col=1)
    return fig


# ═══════════════════════════════════════════════════════════════
# الصفحات
# ═══════════════════════════════════════════════════════════════

def page_home():
    st.markdown("## 📊 لوحة السوق الرئيسية")
    st.markdown("---")

    index_syms = {'EGX30': EGXDatabase.EGX30[:5], 'قطاع البنوك': ['COMI','QNBE','ADIB'],
                  'العقارات': ['TMGH','PHDC','SODC'], 'الصناعة': ['SWDY','ECIG','SKPC']}

    for idx_name, syms in index_syms.items():
        st.markdown(f"#### {idx_name}")
        cols = st.columns(len(syms))
        for col, sym in zip(cols, syms):
            df = cached_load(sym)
            info = EGXDatabase.STOCKS.get(sym, {})
            if df is not None and len(df) > 1:
                price = float(df['close'].iloc[-1])
                chg   = float(df['pct_change'].iloc[-1])
                vol   = int(df['volume'].iloc[-1])
                clr   = "#10b981" if chg >= 0 else "#ef4444"
                arrow = "▲" if chg >= 0 else "▼"
                src   = df['data_source'].iloc[-1] if 'data_source' in df.columns else '?'
                with col:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-lbl">{info.get('name','')}</div>
                        <div class="metric-val" style="color:{clr}">{price:.2f}</div>
                        <div style="color:{clr};font-size:14px">{arrow} {abs(chg):.2f}%</div>
                        <div class="metric-sub">حجم: {fmt_num(vol)}</div>
                        <span class="{'source-real' if src=='real' else 'source-sim'}">
                            {'🟢 حقيقي' if src=='real' else '🟡 محاكاة'}</span>
                    </div>""", unsafe_allow_html=True)
            else:
                with col:
                    st.markdown(f"<div class='metric-card'><div class='metric-lbl'>{sym}</div><div style='color:#64748b'>لا بيانات</div></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🔥 أعلى وأدنى أداء (قائمة المراقبة)")
    wl = st.session_state['watchlist'][:8]
    perf = []
    with st.spinner("جاري التحليل..."):
        for sym in wl:
            df = cached_load(sym)
            if df is not None and len(df) > 5:
                chg5 = float(df['close'].pct_change(5).iloc[-1] * 100)
                chg1 = float(df['pct_change'].iloc[-1])
                perf.append({'رمز':sym,'الشركة':EGXDatabase.STOCKS.get(sym,{}).get('name','')[:20],
                             'اليوم':chg1,'5 أيام':chg5})
    if perf:
        pf_df = pd.DataFrame(perf).sort_values('5 أيام', ascending=False)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**🟢 أفضل أداء**")
            top = pf_df.head(3)
            for _, row in top.iterrows():
                st.success(f"**{row['رمز']}** {row['الشركة']} | اليوم: {row['اليوم']:+.2f}% | 5 أيام: {row['5 أيام']:+.2f}%")
        with c2:
            st.markdown("**🔴 أضعف أداء**")
            bot = pf_df.tail(3).iloc[::-1]
            for _, row in bot.iterrows():
                st.error(f"**{row['رمز']}** {row['الشركة']} | اليوم: {row['اليوم']:+.2f}% | 5 أيام: {row['5 أيام']:+.2f}%")


def page_analysis():
    st.markdown("## 🔍 تحليل السهم")
    col1, col2 = st.columns([2, 1])
    with col1:
        all_syms = sorted(EGXDatabase.STOCKS.keys())
        sym = st.selectbox("اختر السهم", all_syms,
                           index=all_syms.index('COMI') if 'COMI' in all_syms else 0)
    with col2:
        days = st.slider("عدد الأيام", 60, 500, 300, 30)

    with st.spinner(f"جاري تحليل {sym}..."):
        df = cached_load(sym, days)

    if df is None or df.empty:
        st.error("⚠️ لا توجد بيانات كافية لهذا السهم")
        return

    info = EGXDatabase.STOCKS.get(sym, {})
    src  = df['data_source'].iloc[-1] if 'data_source' in df.columns else '?'
    price = float(df['close'].iloc[-1])
    chg   = float(df['pct_change'].iloc[-1])

    # ── Header ──
    clr = "#10b981" if chg >= 0 else "#ef4444"
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#1a1f2e,#2d3748);border-radius:12px;
                padding:16px;margin-bottom:16px;border:1px solid #3d4a63">
        <span style="font-size:22px;font-weight:700">{info.get('name',sym)}</span>
        <span style="color:#94a3b8;margin:0 10px">{sym} · {info.get('sector','')}</span>
        <span style="font-size:24px;font-weight:700;color:{clr}">{price:.2f} EGP</span>
        <span style="color:{clr};margin-right:8px">{"▲" if chg>=0 else "▼"} {abs(chg):.2f}%</span>
        <span class="{'source-real' if src=='real' else 'source-sim'}">
            {'🟢 بيانات حقيقية' if src=='real' else '🟡 محاكاة GARCH'}</span>
    </div>""", unsafe_allow_html=True)

    # ── مقاييس سريعة ──
    high52 = float(df['high'].tail(252).max())
    low52  = float(df['low'].tail(252).min())
    avg_vol = int(df['volume'].tail(20).mean())
    rsi_val = safe_last(df['rsi'], 50)
    atr_val = safe_last(df['atr'])
    vol20 = safe_last(df['volatility_20d'], 0) * 100

    m1,m2,m3,m4,m5,m6 = st.columns(6)
    m1.metric("أعلى 52 أسبوع", f"{high52:.2f}")
    m2.metric("أدنى 52 أسبوع", f"{low52:.2f}")
    m3.metric("متوسط الحجم 20 يوم", fmt_num(avg_vol))
    m4.metric("RSI", f"{rsi_val:.1f}")
    m5.metric("ATR", f"{atr_val:.2f}")
    m6.metric("تذبذب سنوي", f"{vol20:.1f}%")

    # ── اختيار المؤشرات ──
    st.markdown("#### 📉 إعدادات الرسم")
    ind_opts = ['EMA', 'Bollinger', 'VWAP', 'Supertrend', 'Ichimoku',
                'PSAR', 'RSI', 'MACD', 'Volume']
    show_ind = st.multiselect("المؤشرات", ind_opts,
                               default=['EMA', 'Supertrend', 'RSI', 'MACD', 'Volume'])

    fig = plot_main_chart(df, sym, show_ind)
    st.plotly_chart(fig, use_container_width=True)

    # ── الإشارة المركّبة ──
    signal, emoji, conf, sigs = get_composite_signal(df)
    sig_cls = "signal-buy" if "شراء" in signal else ("signal-sell" if "بيع" in signal else "signal-neu")
    st.markdown(f"""
    <div class="{sig_cls}" style="margin:16px 0">
        <span style="font-size:28px">{emoji}</span>
        <span style="font-size:20px;font-weight:700;margin:0 10px">{signal}</span>
        <span style="color:#94a3b8">ثقة {conf}% · مبني على 12 مؤشر</span>
    </div>""", unsafe_allow_html=True)

    with st.expander("📋 تفاصيل الإشارة (12 مؤشر)"):
        for name, desc in sigs.items():
            color = "#10b981" if "شراء" in desc or "صاعد" in desc or "▲" in desc else \
                    "#ef4444" if "بيع" in desc or "هابط" in desc or "▼" in desc else "#94a3b8"
            st.markdown(f"<div style='color:{color};padding:4px 0;border-bottom:1px solid #1e2738'>"
                        f"<b>{name}:</b> {desc}</div>", unsafe_allow_html=True)

    # ── دعم / مقاومة / فيبوناتشي ──
    col_sr, col_fib = st.columns(2)
    with col_sr:
        st.markdown("#### 📏 الدعم والمقاومة")
        sup, res = get_support_resistance(df)
        pos_pct = ((price - sup) / (res - sup) * 100) if res > sup else 50
        st.markdown(f"🔴 **مقاومة:** {res:.2f} EGP")
        st.progress(min(max(int(pos_pct), 0), 100))
        st.markdown(f"🟢 **دعم:** {sup:.2f} EGP")
        st.caption(f"السعر الحالي عند {pos_pct:.1f}% من النطاق")

    with col_fib:
        st.markdown("#### 🌀 مستويات فيبوناتشي")
        sup, res = get_support_resistance(df, 30)
        fib = get_fibonacci_levels(sup, res)
        for lvl, val in fib.items():
            dist = abs(price - val)
            closest = "⭐ " if dist/price < 0.02 else ""
            st.markdown(f"<div style='font-size:12px;padding:2px 0;border-bottom:1px solid #1e2738'>"
                        f"{closest}<b>{lvl}:</b> {val:.2f}</div>", unsafe_allow_html=True)

    # ── أنماط الشموع ──
    patterns = detect_patterns(df)
    if patterns:
        st.markdown("#### 🕯️ أنماط الشموع المكتشفة")
        for p in patterns:
            clr = "#10b981" if p['signal']=="شراء" else "#ef4444" if p['signal']=="بيع" else "#94a3b8"
            strength_stars = "⭐" * p['strength']
            st.markdown(f"""
            <div style="background:#1a1f2e;border:1px solid #3d4a63;border-right:4px solid {clr};
                        border-radius:8px;padding:10px;margin:6px 0">
                <b>{p['emoji']} {p['name']}</b> — {strength_stars}<br>
                <span style="color:#94a3b8;font-size:12px">{p['desc']}</span>
            </div>""", unsafe_allow_html=True)


def page_supertrend():
    st.markdown("## ⚡ محلل Supertrend")
    st.info("Supertrend هو المؤشر الأكثر استخداماً من محللي EGX — إشارات واضحة مع وقف خسارة ديناميكي")

    col1, col2, col3 = st.columns(3)
    with col1:
        sym = st.selectbox("السهم", sorted(EGXDatabase.STOCKS.keys()))
    with col2:
        period = st.slider("الفترة", 5, 20, 10)
    with col3:
        mult = st.slider("المضاعف", 1.0, 5.0, 3.0, 0.5)

    df = cached_load(sym, 300)
    if df is None:
        st.error("لا بيانات"); return

    from egx_engine import calc_supertrend, calc_atr

    supertrend_vals, st_dir = calc_supertrend(df['high'], df['low'], df['close'], period, mult)

    df = df.copy()
    df['st_custom'] = supertrend_vals
    df['st_dir_custom'] = st_dir

    cur_dir   = int(df['st_dir_custom'].iloc[-1])
    cur_price = float(df['close'].iloc[-1])
    cur_st    = float(df['st_custom'].iloc[-1])
    pct_from_st = (cur_price - cur_st) / cur_st * 100

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("السعر الحالي", f"{cur_price:.2f}")
    c2.metric("Supertrend", f"{cur_st:.2f}")
    c3.metric("الإشارة", "🟢 شراء" if cur_dir==1 else "🔴 بيع")
    c4.metric("% من ST", f"{pct_from_st:+.2f}%")

    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['open'], high=df['high'],
        low=df['low'], close=df['close'], name='السعر',
        increasing_line_color='#10b981', decreasing_line_color='#ef4444'))

    up   = df['st_custom'].where(df['st_dir_custom']==1)
    down = df['st_custom'].where(df['st_dir_custom']==-1)
    fig.add_trace(go.Scatter(x=df.index,y=up,name='ST صاعد (وقف خسارة)',
        line=dict(color='#10b981',width=2.5),mode='lines'))
    fig.add_trace(go.Scatter(x=df.index,y=down,name='ST هابط (مقاومة)',
        line=dict(color='#ef4444',width=2.5),mode='lines'))

    # نقاط التقاطع
    cross_up   = (df['st_dir_custom']==1) & (df['st_dir_custom'].shift(1)==-1)
    cross_down = (df['st_dir_custom']==-1) & (df['st_dir_custom'].shift(1)==1)
    if cross_up.any():
        fig.add_trace(go.Scatter(x=df.index[cross_up], y=df['close'][cross_up],
            mode='markers+text', name='إشارة شراء', text=['▲']*cross_up.sum(),
            textposition='bottom center', marker=dict(size=14,color='#10b981',symbol='triangle-up')))
    if cross_down.any():
        fig.add_trace(go.Scatter(x=df.index[cross_down], y=df['close'][cross_down],
            mode='markers+text', name='إشارة بيع', text=['▼']*cross_down.sum(),
            textposition='top center', marker=dict(size=14,color='#ef4444',symbol='triangle-down')))

    fig.update_layout(**make_base_layout(f"Supertrend — {sym} (Period={period}, Mult={mult})"),
                      height=550, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    total_signals = int(cross_up.sum()) + int(cross_down.sum())
    st.markdown(f"**إجمالي الإشارات في الفترة:** 🟢 {int(cross_up.sum())} شراء | 🔴 {int(cross_down.sum())} بيع | مجموع: {total_signals}")


def page_backtest():
    st.markdown("## 🧪 الباكتست والاختبار التاريخي")
    col1, col2, col3 = st.columns(3)
    with col1:
        sym = st.selectbox("السهم", sorted(EGXDatabase.STOCKS.keys()), key='bt_sym')
    with col2:
        capital = st.number_input("رأس المال (EGP)", 10_000, 10_000_000, 100_000, 10_000)
    with col3:
        strat_sel = st.multiselect("الاستراتيجيات", ALL_STRATEGIES, default=ALL_STRATEGIES[:5])

    if st.button("🚀 تشغيل الباكتست", type="primary"):
        with st.spinner("جاري تشغيل الاختبار التاريخي..."):
            df = cached_load(sym, 500)
            if df is None:
                st.error("لا بيانات"); return
            results = run_all_backtests(df, capital, strat_sel)
            summary = backtest_summary_df(results)

        st.success(f"✅ اكتمل الباكتست على {len(df)} يوم تداول | {len(results)} استراتيجية")

        # ── ملخص مقارن ──
        st.markdown("### 📊 مقارنة الاستراتيجيات")
        def style_df(df_s):
            def clr(val):
                if isinstance(val, str) and val.endswith('%'):
                    try:
                        v = float(val.replace('%',''))
                        if v > 10: return 'color: #10b981'
                        elif v < 0: return 'color: #ef4444'
                    except: pass
                return ''
            return df_s.style.applymap(clr)

        st.dataframe(style_df(summary), use_container_width=True, height=350)

        best = max(results, key=lambda r: r.sharpe_ratio)
        st.info(f"🏆 أفضل استراتيجية (Sharpe): **{best.strategy}** — "
                f"عائد {best.total_return*100:.1f}% | Sharpe {best.sharpe_ratio:.2f} | "
                f"Win Rate {best.win_rate*100:.1f}%")

        # ── مقارنة منحنيات الأسهم ──
        st.markdown("### 📈 منحنيات رأس المال")
        fig = go.Figure()
        colors_list = ['#3b82f6','#10b981','#f59e0b','#8b5cf6','#ef4444',
                       '#06b6d4','#ec4899','#84cc16','#f97316','#6366f1']
        for r, clr in zip(results, colors_list):
            if not r.equity_curve.empty:
                norm = r.equity_curve / r.equity_curve.iloc[0] * 100
                fig.add_trace(go.Scatter(x=norm.index, y=norm,
                    name=f"{r.strategy} ({r.total_return*100:+.1f}%)",
                    line=dict(color=clr, width=2)))
        fig.update_layout(**make_base_layout("منحنيات رأس المال — مُطبَّعة إلى 100"),
                          height=450, yaxis_title="رأس المال (100=نقطة البداية)")
        st.plotly_chart(fig, use_container_width=True)

        # ── تفاصيل الصفقات ──
        st.markdown("### 📝 تفاصيل الصفقات")
        sel_strat = st.selectbox("اختر الاستراتيجية",
                                 [r.strategy for r in results if r.total_trades > 0])
        sel_r = next((r for r in results if r.strategy == sel_strat), None)
        if sel_r and sel_r.trades:
            trades_df = pd.DataFrame([{
                'دخول': str(t.entry_date)[:10], 'خروج': str(t.exit_date)[:10],
                'سعر الدخول': f"{t.entry_price:.2f}", 'سعر الخروج': f"{t.exit_price:.2f}",
                'أسهم': t.shares, 'ربح/خسارة (EGP)': f"{t.pnl:+.0f}",
                'العائد': f"{t.pnl_pct*100:+.2f}%"
            } for t in sel_r.trades])
            st.dataframe(trades_df, use_container_width=True, height=300)


def page_ml():
    st.markdown("## 🤖 تحليل الذكاء الاصطناعي")
    st.info("✅ Walk-Forward Validation — التدريب على الماضي، الاختبار على المستقبل (بدون data leakage)")

    sym = st.selectbox("السهم", sorted(EGXDatabase.STOCKS.keys()), key='ml_sym')
    col1, col2 = st.columns(2)
    with col1:
        n_splits = st.slider("عدد الـ Folds", 3, 8, 5)
    with col2:
        days = st.slider("الفترة الزمنية", 100, 500, 300, 50, key='ml_days')

    if st.button("🧠 تدريب النموذج (Walk-Forward)", type="primary"):
        with st.spinner("جاري التدريب بـ Walk-Forward Validation..."):
            df = cached_load(sym, days)
            if df is None:
                st.error("لا بيانات"); return
            predictor = EGXMLPredictor()
            metrics = predictor.train_walk_forward(df, n_splits)

        if 'error' in metrics:
            st.error(f"خطأ: {metrics['error']}"); return

        st.success("✅ اكتمل التدريب بنجاح")

        # ── مقاييس WF ──
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("متوسط الدقة", f"{metrics['avg_accuracy']*100:.1f}%")
        c2.metric("متوسط AUC", f"{metrics['avg_auc']:.3f}")
        c3.metric("متوسط Precision", f"{metrics['avg_precision']*100:.1f}%")
        c4.metric("عدد الـ Folds", str(metrics['n_folds']))

        # ── نتائج الـ Folds ──
        st.markdown("#### نتائج كل Fold")
        folds_df = pd.DataFrame(metrics['folds'])
        st.dataframe(folds_df, use_container_width=True)

        # ── التنبؤ الحالي ──
        label, prob, clr = predictor.predict(df)
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1a1f2e,#2d3748);border-radius:12px;
                    padding:20px;text-align:center;margin:16px 0;border:2px solid #3d4a63">
            <div style="font-size:14px;color:#94a3b8;margin-bottom:8px">تنبؤ النموذج (5 أيام القادمة)</div>
            <div style="font-size:32px">{clr}</div>
            <div style="font-size:22px;font-weight:700;margin:6px 0">{label}</div>
            <div style="font-size:16px;color:#94a3b8">احتمالية الارتفاع: {prob*100:.1f}%</div>
        </div>""", unsafe_allow_html=True)

        # ── أهمية المتغيرات ──
        fi = predictor.get_feature_importance()
        if not fi.empty:
            st.markdown("#### 📊 أهم المتغيرات (Feature Importance)")
            fig = px.bar(fi, x='importance', y='feature', orientation='h',
                         color='importance', color_continuous_scale='Blues',
                         labels={'importance':'الأهمية','feature':'المتغير'})
            fig.update_layout(**make_base_layout(), height=400)
            st.plotly_chart(fig, use_container_width=True)


def page_portfolio():
    st.markdown("## 💼 إدارة المحفظة")
    pm = PortfolioManager(st.session_state['capital'])

    c1, c2 = st.columns(2)
    with c1:
        st.session_state['capital'] = st.number_input("رأس المال الكلي", 10_000.0, 10_000_000.0,
                                                        st.session_state['capital'], 10_000.0)
    with c2:
        max_risk = st.slider("نسبة المخاطرة لكل صفقة %", 0.5, 5.0, 2.0, 0.5) / 100

    sym = st.selectbox("السهم للتحليل", sorted(EGXDatabase.STOCKS.keys()), key='pm_sym')
    df  = cached_load(sym)
    if df is None:
        st.error("لا بيانات"); return

    price = float(df['close'].iloc[-1])
    atr   = safe_last(df['atr'])
    signal, _, conf, _ = get_composite_signal(df)
    wr   = 0.55
    avg_w, avg_l = 0.04, 0.02

    pos = pm.calc_position_size(price, wr, avg_w, avg_l, max_risk)
    sl  = pm.calc_stop_loss(price, atr)

    st.markdown(f"### 📊 {EGXDatabase.STOCKS.get(sym,{}).get('name',sym)} — {price:.2f} EGP")
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("عدد الأسهم (Kelly)", str(pos['shares']))
    m2.metric("رأس المال المطلوب", fmt_egp(pos['capital']))
    m3.metric("% من المحفظة", f"{pos['position_pct']:.1f}%")
    m4.metric("نسبة Kelly", f"{pos['kelly']*100:.1f}%")

    st.markdown("---")
    m5,m6,m7,m8 = st.columns(4)
    m5.metric("وقف الخسارة", fmt_egp(sl['stop_loss']))
    m6.metric("هدف الربح", fmt_egp(sl['take_profit']))
    m7.metric("% مخاطرة", f"{sl['risk_pct']:.1f}%")
    m8.metric("نسبة R:R", f"{sl['rr_ratio']:.1f}:1")

    fig = go.Figure()
    recent = df.tail(60)
    fig.add_trace(go.Candlestick(x=recent.index, open=recent['open'], high=recent['high'],
        low=recent['low'], close=recent['close'], name='السعر',
        increasing_line_color='#10b981', decreasing_line_color='#ef4444'))
    fig.add_hline(y=price, line_color='#3b82f6', line_dash='dash', line_width=2,
                  annotation_text=f"سعر الدخول {price:.2f}")
    fig.add_hline(y=sl['stop_loss'], line_color='#ef4444', line_dash='dot', line_width=2,
                  annotation_text=f"وقف خسارة {sl['stop_loss']:.2f}")
    fig.add_hline(y=sl['take_profit'], line_color='#10b981', line_dash='dot', line_width=2,
                  annotation_text=f"هدف ربح {sl['take_profit']:.2f}")
    fig.add_hrect(y0=sl['stop_loss'], y1=price, fillcolor='rgba(239,68,68,0.07)',
                  line_width=0, annotation_text="منطقة المخاطرة")
    fig.add_hrect(y0=price, y1=sl['take_profit'], fillcolor='rgba(16,185,129,0.07)',
                  line_width=0, annotation_text="منطقة الربح")
    fig.update_layout(**make_base_layout("خطة الصفقة"), height=450, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)


def page_watchlist():
    st.markdown("## 👁️ قائمة المراقبة")
    all_syms = sorted(EGXDatabase.STOCKS.keys())
    new_wl = st.multiselect("اختر الأسهم للمراقبة", all_syms,
                            default=st.session_state['watchlist'])
    if new_wl != st.session_state['watchlist']:
        st.session_state['watchlist'] = new_wl

    if not new_wl:
        st.warning("أضف أسهماً لقائمة المراقبة"); return

    with st.spinner("جاري تحليل قائمة المراقبة..."):
        rows = []
        for sym in new_wl:
            df = cached_load(sym)
            if df is not None and len(df) > 10:
                sig, emoji, conf, _ = get_composite_signal(df)
                price = float(df['close'].iloc[-1])
                chg   = float(df['pct_change'].iloc[-1])
                rsi   = safe_last(df['rsi'], 50)
                vol   = int(df['volume'].iloc[-1])
                src   = df['data_source'].iloc[-1] if 'data_source' in df.columns else '?'
                rows.append({'رمز':sym,'الشركة':EGXDatabase.STOCKS.get(sym,{}).get('name','')[:22],
                             'القطاع':EGXDatabase.STOCKS.get(sym,{}).get('sector',''),
                             'السعر':f"{price:.2f}",'تغيير%':f"{chg:+.2f}%",
                             'RSI':f"{rsi:.0f}",'إشارة':f"{emoji} {sig}",
                             'ثقة':f"{conf}%",'الحجم':fmt_num(vol),
                             'مصدر':'🟢 حقيقي' if src=='real' else '🟡 محاكاة'})

    if rows:
        df_wl = pd.DataFrame(rows)
        st.dataframe(df_wl, use_container_width=True, height=500)

        buy_count  = sum(1 for r in rows if 'شراء' in r['إشارة'])
        sell_count = sum(1 for r in rows if 'بيع' in r['إشارة'])
        st.markdown(f"**ملخص:** 🟢 {buy_count} إشارة شراء | 🔴 {sell_count} إشارة بيع | ⚪ {len(rows)-buy_count-sell_count} محايد")


def page_screener():
    st.markdown("## 🔎 فلترة الأسهم (Screener)")
    col1, col2, col3 = st.columns(3)
    with col1:
        sectors = ['الكل'] + sorted(EGXDatabase.SECTORS.keys())
        sector  = st.selectbox("القطاع", sectors)
    with col2:
        signal_filter = st.selectbox("الإشارة", ['الكل','شراء','بيع','محايد'])
    with col3:
        rsi_range = st.slider("نطاق RSI", 0, 100, (20, 80))

    min_vol = st.number_input("الحد الأدنى للحجم اليومي", 0, 10_000_000, 0, 100_000)

    syms_to_scan = EGXDatabase.STOCKS.keys() if sector=='الكل' else EGXDatabase.SECTORS.get(sector,[])

    if st.button("🔍 تشغيل الفلترة", type="primary"):
        results_scan = []
        progress = st.progress(0)
        syms_list = list(syms_to_scan)
        for idx, sym in enumerate(syms_list):
            df = cached_load(sym)
            if df is None or len(df) < 30:
                progress.progress((idx+1)/len(syms_list)); continue
            rsi = safe_last(df['rsi'], 50)
            vol = int(df['volume'].iloc[-1])
            if not (rsi_range[0] <= rsi <= rsi_range[1]): progress.progress((idx+1)/len(syms_list)); continue
            if vol < min_vol: progress.progress((idx+1)/len(syms_list)); continue
            sig, emoji, conf, _ = get_composite_signal(df)
            if signal_filter != 'الكل' and signal_filter not in sig:
                progress.progress((idx+1)/len(syms_list)); continue
            price = float(df['close'].iloc[-1])
            chg   = float(df['pct_change'].iloc[-1])
            st_d  = safe_last(df['supertrend_dir'], 0) if 'supertrend_dir' in df.columns else 0
            results_scan.append({'رمز':sym,'الشركة':EGXDatabase.STOCKS.get(sym,{}).get('name','')[:22],
                'القطاع':EGXDatabase.STOCKS.get(sym,{}).get('sector',''),
                'السعر':f"{price:.2f}",'تغيير%':f"{chg:+.2f}%",'RSI':f"{rsi:.0f}",
                'Supertrend':'🟢 صاعد' if st_d==1 else '🔴 هابط',
                'إشارة':f"{emoji} {sig}",'ثقة':f"{conf}%",'حجم':fmt_num(vol)})
            progress.progress((idx+1)/len(syms_list))

        progress.empty()
        if results_scan:
            st.success(f"✅ {len(results_scan)} سهم مطابق للشروط")
            st.dataframe(pd.DataFrame(results_scan), use_container_width=True, height=500)
        else:
            st.warning("لا توجد أسهم تطابق الشروط المحددة")


def page_sector():
    st.markdown("## 🏭 تحليل القطاعات")
    sectors_list = sorted(EGXDatabase.SECTORS.keys())
    sel_sectors = st.multiselect("اختر القطاعات", sectors_list, default=sectors_list[:5])

    if not sel_sectors: return

    sector_data = []
    with st.spinner("جاري تحليل القطاعات..."):
        for sec in sel_sectors:
            syms = EGXDatabase.SECTORS.get(sec, [])[:5]
            changes, rsi_vals, signals = [], [], []
            for sym in syms:
                df = cached_load(sym)
                if df is None: continue
                changes.append(float(df['pct_change'].iloc[-1]))
                rsi_vals.append(safe_last(df['rsi'], 50))
                sig, _, _, _ = get_composite_signal(df)
                signals.append(sig)
            if changes:
                buy_pct = sum(1 for s in signals if 'شراء' in s) / len(signals) * 100
                sector_data.append({'القطاع':sec,'أسهم':len(syms),
                    'متوسط التغيير%':np.mean(changes),'متوسط RSI':np.mean(rsi_vals),
                    'إشارات شراء%':buy_pct})

    if not sector_data: return
    df_sec = pd.DataFrame(sector_data).sort_values('متوسط التغيير%', ascending=False)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(df_sec, x='القطاع', y='متوسط التغيير%',
                     color='متوسط التغيير%', color_continuous_scale='RdYlGn',
                     title='متوسط التغيير اليومي لكل قطاع')
        fig.update_layout(**make_base_layout(), height=400)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig2 = px.scatter(df_sec, x='متوسط RSI', y='إشارات شراء%',
                          size='أسهم', color='متوسط التغيير%',
                          text='القطاع', color_continuous_scale='RdYlGn',
                          title='خريطة القطاعات: RSI vs إشارات الشراء')
        fig2.update_layout(**make_base_layout(), height=400)
        st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(df_sec.style.background_gradient(subset=['متوسط التغيير%'], cmap='RdYlGn'),
                 use_container_width=True)


def page_alerts():
    st.markdown("## 🔔 نظام التنبيهات الذكي")
    sym = st.selectbox("السهم", sorted(EGXDatabase.STOCKS.keys()), key='alert_sym')
    df  = cached_load(sym)
    if df is None:
        st.error("لا بيانات"); return
    price = float(df['close'].iloc[-1])
    st.caption(f"السعر الحالي: {price:.2f} EGP")

    with st.form("add_alert"):
        st.markdown("#### ➕ إضافة تنبيه جديد")
        c1, c2, c3 = st.columns(3)
        with c1:
            alert_type = st.selectbox("نوع التنبيه", ['سعر أعلى من','سعر أقل من',
                'RSI تشبع شراء (>70)','RSI تشبع بيع (<30)','Supertrend شراء','Supertrend بيع'])
        with c2:
            threshold = st.number_input("القيمة", value=price*1.05 if 'أعلى' in alert_type else price*0.95,
                                        format="%.2f")
        with c3:
            note = st.text_input("ملاحظة", "")
        if st.form_submit_button("➕ إضافة", type="primary"):
            st.session_state['alerts'].append({
                'sym':sym,'type':alert_type,'threshold':threshold,
                'note':note,'created':str(datetime.now())[:16],'status':'نشط'})
            st.success("✅ تمت إضافة التنبيه")

    # فحص التنبيهات
    if st.session_state['alerts']:
        st.markdown("#### 📋 التنبيهات الحالية")
        triggered = []
        for i, alert in enumerate(st.session_state['alerts']):
            a_df = cached_load(alert['sym'])
            if a_df is None: continue
            a_price = float(a_df['close'].iloc[-1])
            a_rsi   = safe_last(a_df['rsi'], 50)
            a_std   = safe_last(a_df['supertrend_dir'], 0)
            is_triggered = False
            if alert['type']=='سعر أعلى من'       and a_price > alert['threshold']: is_triggered=True
            elif alert['type']=='سعر أقل من'      and a_price < alert['threshold']: is_triggered=True
            elif 'تشبع شراء' in alert['type']     and a_rsi > 70: is_triggered=True
            elif 'تشبع بيع' in alert['type']      and a_rsi < 30: is_triggered=True
            elif 'Supertrend شراء' in alert['type'] and a_std==1: is_triggered=True
            elif 'Supertrend بيع' in alert['type']  and a_std==-1: is_triggered=True

            cls = 'alert-buy' if is_triggered else 'alert-sell'
            icon = '🔔' if is_triggered else '🔕'
            status = '✅ محقق!' if is_triggered else '⏳ منتظر'
            st.markdown(f"""
            <div class="alert-box {'alert-buy' if is_triggered else 'alert-sell'}">
                {icon} <b>{alert['sym']}</b> — {alert['type']} {alert.get('threshold',''):g}
                | الحالي: {a_price:.2f} | <b>{status}</b>
                {f"| {alert['note']}" if alert.get('note') else ''}
            </div>""", unsafe_allow_html=True)

        if st.button("🗑️ مسح جميع التنبيهات"):
            st.session_state['alerts'] = []
            st.rerun()


def page_fibonacci():
    st.markdown("## 🌀 تحليل فيبوناتشي المتقدم")
    sym  = st.selectbox("السهم", sorted(EGXDatabase.STOCKS.keys()), key='fib_sym')
    df   = cached_load(sym)
    if df is None: st.error("لا بيانات"); return

    col1, col2 = st.columns(2)
    with col1: fib_period = st.slider("فترة الحساب (يوم)", 20, 252, 60)
    with col2: auto_levels = st.checkbox("إضافة مستويات توسع", True)

    recent = df.tail(fib_period)
    sup, res = float(recent['low'].min()), float(recent['high'].max())
    fib = get_fibonacci_levels(sup, res)
    if auto_levels:
        diff = res - sup
        fib.update({'161.8%': sup+diff*1.618, '200%': sup+diff*2.0, '261.8%': sup+diff*2.618})

    price = float(df['close'].iloc[-1])
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.tail(fib_period).index, open=recent['open'],
        high=recent['high'], low=recent['low'], close=recent['close'],
        name='السعر', increasing_line_color='#10b981', decreasing_line_color='#ef4444'))

    fib_colors = {'0.0% (دعم)':'#10b981','23.6%':'#84cc16','38.2%':'#f59e0b',
                  '50.0%':'#f97316','61.8%':'#ef4444','78.6%':'#dc2626',
                  '100% (مقاومة)':'#991b1b','127.2%':'#8b5cf6','161.8%':'#6366f1',
                  '200%':'#3b82f6','261.8%':'#06b6d4'}
    for lvl, val in fib.items():
        clr = fib_colors.get(lvl, '#64748b')
        is_near = abs(price - val) / price < 0.015
        fig.add_hline(y=val, line_dash='dash' if not is_near else 'solid',
                      line_color=clr, line_width=2 if is_near else 1,
                      opacity=0.9 if is_near else 0.6,
                      annotation_text=f"{lvl}: {val:.2f}" + (" ⭐" if is_near else ""),
                      annotation_position="right")
    fig.add_hline(y=price, line_color='#ffffff', line_width=2,
                  annotation_text=f"السعر الحالي: {price:.2f}", line_dash='dot')
    fig.update_layout(**make_base_layout(f"فيبوناتشي — {sym}"), height=550, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    nearest = min(fib.items(), key=lambda x: abs(price - x[1]))
    st.info(f"📍 أقرب مستوى فيبوناتشي: **{nearest[0]}** عند **{nearest[1]:.2f} EGP** "
            f"(بُعد {abs(price-nearest[1])/price*100:.2f}% من السعر الحالي)")


def page_compare():
    st.markdown("## ⚖️ مقارنة الأسهم")
    all_s = sorted(EGXDatabase.STOCKS.keys())
    selected = st.multiselect("اختر حتى 5 أسهم", all_s, default=['COMI','TMGH','ETEL'])
    if len(selected) < 2: st.warning("اختر سهمين على الأقل"); return
    selected = selected[:5]

    norm_base = st.radio("قاعدة التطبيع", ['آخر 60 يوم','آخر 90 يوم','آخر 120 يوم','كامل الفترة'], horizontal=True)
    days_map = {'آخر 60 يوم':60,'آخر 90 يوم':90,'آخر 120 يوم':120,'كامل الفترة':300}
    n_days = days_map[norm_base]

    fig = go.Figure()
    stats_rows = []
    colors_list = ['#3b82f6','#10b981','#f59e0b','#ef4444','#8b5cf6']
    for sym, clr in zip(selected, colors_list):
        df = cached_load(sym, n_days)
        if df is None: continue
        norm = df['close'] / df['close'].iloc[0] * 100
        rsi  = safe_last(df['rsi'],50)
        chg  = (df['close'].iloc[-1]/df['close'].iloc[0]-1)*100
        vol  = df['volatility_20d'].iloc[-1]*100 if 'volatility_20d' in df.columns else 0
        sig, _, conf, _ = get_composite_signal(df)
        fig.add_trace(go.Scatter(x=df.index, y=norm, name=sym,
            line=dict(color=clr, width=2.5), hovertemplate=f"<b>{sym}</b><br>%{{y:.1f}}<extra></extra>"))
        stats_rows.append({'رمز':sym,'الشركة':EGXDatabase.STOCKS.get(sym,{}).get('name','')[:20],
            'العائد%':f"{chg:+.1f}%",'RSI':f"{rsi:.0f}",'تذبذب%':f"{vol:.1f}%",'إشارة':sig,'ثقة':f"{conf}%"})

    fig.add_hline(y=100, line_color='#64748b', line_dash='dash', opacity=0.5,
                  annotation_text="نقطة البداية (100%)")
    fig.update_layout(**make_base_layout("مقارنة الأداء النسبي"), height=500,
                      yaxis_title="الأداء (100=نقطة البداية)")
    st.plotly_chart(fig, use_container_width=True)
    if stats_rows:
        st.dataframe(pd.DataFrame(stats_rows), use_container_width=True)


def page_about():
    st.markdown("## ℹ️ عن EGX Pro Ultimate v30")
    st.markdown("""
    <div style="background:#1a1f2e;border-radius:12px;padding:24px;line-height:2">
    <h3 style="color:#f59e0b">🚀 EGX Pro Ultimate v30</h3>
    <p>منظومة تحليل احترافية متكاملة لبورصة الأوراق المالية المصرية</p>
    <hr style="border-color:#3d4a63">
    <h4>✅ ما الجديد في v30 (مقارنة بـ v29)</h4>
    <ul>
    <li>🔧 <b>VWAP يومي صحيح</b> — يُعاد حسابه من الصفر كل يوم (v29 كان cumulative خاطئ)</li>
    <li>🤖 <b>ML Walk-Forward Validation</b> — بدون data leakage (v29 كان يُدرّب ويختبر على نفس البيانات)</li>
    <li>⚡ <b>Supertrend</b> — مؤشر جديد مدمج في الإشارة المركّبة والباكتست والسكرينر</li>
    <li>🗄️ <b>قاعدة بيانات مصحّحة</b> — أُزيلت الرموز الوهمية، صُحّحت القطاعات</li>
    <li>📊 <b>10 استراتيجيات باكتست</b> بدلاً من 8</li>
    <li>💼 <b>إدارة محفظة بـ Kelly Criterion</b> مع رسم خطة الصفقة</li>
    <li>🔔 <b>نظام تنبيهات ذكي</b> يشمل Supertrend وRSI والسعر</li>
    </ul>
    <hr style="border-color:#3d4a63">
    <h4>📊 المؤشرات الفنية (16 مؤشر)</h4>
    <p>RSI | MACD | EMA 9/20/50/200 | Bollinger Bands | ADX (+DI/-DI) | Stochastic | CCI | Williams %R | OBV | ATR | VWAP (يومي) | Parabolic SAR | ROC | Momentum | Ichimoku | <b>Supertrend ✨</b></p>
    <hr style="border-color:#3d4a63">
    <h4>⚠️ تنبيه مهم</h4>
    <p>الأسهم التي لا يوجد لها رمز Yahoo Finance تعمل ببيانات محاكاة GARCH.
    البيانات المُعلَّمة 🟢 حقيقية هي فقط القادمة من Yahoo Finance مباشرة.
    هذه الأداة للأغراض التعليمية والبحثية — ليست توصية استثمارية.</p>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# الشريط الجانبي والتنقل
# ═══════════════════════════════════════════════════════════════
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:16px 0">
            <div style="font-size:32px">📈</div>
            <div style="font-size:18px;font-weight:700;color:#f59e0b">EGX Pro</div>
            <div style="font-size:12px;color:#64748b">Ultimate v30</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("---")

        pages = {
            "🏠 الرئيسية":        "الرئيسية",
            "🔍 تحليل السهم":     "تحليل",
            "⚡ Supertrend":      "supertrend",
            "🧪 الباكتست":        "backtest",
            "🤖 الذكاء الاصطناعي":"ml",
            "💼 إدارة المحفظة":   "portfolio",
            "👁️ قائمة المراقبة":  "watchlist",
            "🔎 فلترة الأسهم":    "screener",
            "🏭 تحليل القطاعات":  "sector",
            "🔔 التنبيهات":       "alerts",
            "🌀 فيبوناتشي":       "fibonacci",
            "⚖️ مقارنة الأسهم":   "compare",
            "ℹ️ عن التطبيق":      "about",
        }
        for label, key in pages.items():
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state['page'] = key

        st.markdown("---")
        st.markdown(f"""
        <div style="font-size:11px;color:#475569;text-align:center">
            📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}<br>
            🏦 {len(EGXDatabase.STOCKS)} شركة · {len(EGXDatabase.SECTORS)} قطاع<br>
            🟢 EGX30: {len(EGXDatabase.EGX30)} سهم
        </div>""", unsafe_allow_html=True)

def main():
    render_sidebar()
    page = st.session_state.get('page', 'الرئيسية')
    dispatch = {
        'الرئيسية': page_home,
        'تحليل': page_analysis,
        'supertrend': page_supertrend,
        'backtest': page_backtest,
        'ml': page_ml,
        'portfolio': page_portfolio,
        'watchlist': page_watchlist,
        'screener': page_screener,
        'sector': page_sector,
        'alerts': page_alerts,
        'fibonacci': page_fibonacci,
        'compare': page_compare,
        'about': page_about,
    }
    dispatch.get(page, page_home)()

if __name__ == "__main__":
    main()
