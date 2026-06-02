"""
EGX Pro Ultimate v30 — واجهة Streamlit الكاملة
النسخة المحسّنة والمصحّحة بالكامل
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import logging
from typing import Optional, List, Dict
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

# ── استيراد الوحدات ──────────────────────────────────────────
try:
    from egx_engine import (
        EGXDatabase, load_and_compute, get_composite_signal,
        detect_patterns, get_support_resistance, get_fibonacci_levels,
        fmt_num, fmt_egp, safe_last, get_cairo_time
    )
    from egx_ml_backtest import (
        train_ml_model, run_backtest, run_all_backtests,
        alert_manager, build_market_dashboard, BacktestResult
    )
except ImportError as e:
    st.error(f"خطأ في استيراد الوحدات: {e}")
    st.stop()

# ═══════════════════════════════════════════════════════════════
# الإعدادات العامة
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="EGX Pro v30 | محلل البورصة المصرية",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

DARK_THEME = {
    'bg': '#0a0e1a', 'card': '#111827', 'accent': '#f0b429',
    'green': '#10b981', 'red': '#ef4444', 'blue': '#3b82f6',
    'text': '#e2e8f0', 'sub': '#94a3b8', 'border': '#1e2d3d',
    'chart_bg': '#0d1321'
}

LIGHT_THEME = {
    'bg': '#f8fafc', 'card': '#ffffff', 'accent': '#d97706',
    'green': '#059669', 'red': '#dc2626', 'blue': '#2563eb',
    'text': '#1e293b', 'sub': '#64748b', 'border': '#e2e8f0',
    'chart_bg': '#ffffff'
}

def get_theme() -> Dict:
    return DARK_THEME if st.session_state.get('dark_mode', True) else LIGHT_THEME

def apply_css():
    T = get_theme()
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700;800&family=Tajawal:wght@300;400;500;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Cairo', 'Tajawal', sans-serif !important;
        direction: rtl;
    }}
    .stApp {{ background: {T['bg']} !important; color: {T['text']} !important; }}
    .main .block-container {{ padding: 1rem 1.5rem; max-width: 1400px; }}
    section[data-testid="stSidebar"] {{ background: {T['card']} !important; border-left: 1px solid {T['border']}; }}
    .kpi-card {{
        background: {T['card']}; border: 1px solid {T['border']}; border-radius: 12px;
        padding: 16px 20px; margin-bottom: 8px; transition: transform 0.2s;
    }}
    .kpi-card:hover {{ transform: translateY(-2px); border-color: {T['accent']}; }}
    .kpi-label {{ font-size: 12px; color: {T['sub']}; margin-bottom: 4px; }}
    .kpi-value {{ font-size: 22px; font-weight: 700; }}
    .kpi-delta {{ font-size: 12px; margin-top: 4px; }}
    .signal-box {{
        border-radius: 8px; padding: 12px 18px; margin: 8px 0;
        font-size: 15px; font-weight: 600; text-align: center; border: 1px solid;
    }}
    .section-header {{
        font-size: 18px; font-weight: 700; color: {T['accent']};
        border-bottom: 2px solid {T['border']}; padding-bottom: 8px; margin: 16px 0 12px;
    }}
    .pattern-card {{
        background: {T['card']}; border: 1px solid {T['border']};
        border-radius: 10px; padding: 12px 16px; margin: 6px 0;
    }}
    .data-source-badge {{
        display: inline-block; font-size: 11px; padding: 2px 10px;
        border-radius: 12px; font-weight: 500;
    }}
    .real-badge {{ background: #065f46; color: #6ee7b7; }}
    .sim-badge {{ background: #1e3a5f; color: #93c5fd; }}
    div[data-testid="stMetricValue"] {{ font-family: 'Cairo' !important; }}
    .stSelectbox > div > div {{ background: {T['card']} !important; color: {T['text']} !important; }}
    .stTab [data-baseweb="tab"] {{ font-family: 'Cairo' !important; font-size: 14px; }}
    footer {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)

def kpi(label, value, delta=None, delta_color=None, prefix="", suffix="", col=None):
    T = get_theme()
    if delta is not None:
        color = delta_color or (T['green'] if float(str(delta).replace('%','').replace('+','') or 0) >= 0 else T['red'])
        delta_html = f'<div class="kpi-delta" style="color:{color}">{delta}</div>'
    else:
        delta_html = ''
    html = f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{prefix}{value}{suffix}</div>
        {delta_html}
    </div>"""
    (col or st).markdown(html, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# مخطط الشموع الرئيسي
# ═══════════════════════════════════════════════════════════════
def plot_candlestick(df: pd.DataFrame, symbol: str, show_indicators: List[str]) -> go.Figure:
    T = get_theme()
    has_st = 'supertrend' in show_indicators and 'supertrend' in df.columns

    rows_count = 1
    row_heights = [0.5]
    specs_list = [{"secondary_y": True}]

    if 'rsi' in show_indicators:
        rows_count += 1; row_heights.append(0.15); specs_list.append({"secondary_y": False})
    if 'macd' in show_indicators:
        rows_count += 1; row_heights.append(0.15); specs_list.append({"secondary_y": False})
    if 'volume' in show_indicators:
        rows_count += 1; row_heights.append(0.12); specs_list.append({"secondary_y": False})

    fig = make_subplots(
        rows=rows_count, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=row_heights,
        specs=specs_list
    )

    # ── الشموع ──
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['open'], high=df['high'],
        low=df['low'], close=df['close'],
        name=symbol,
        increasing_line_color=T['green'],
        decreasing_line_color=T['red'],
        increasing_fillcolor=T['green'],
        decreasing_fillcolor=T['red'],
    ), row=1, col=1)

    # ── EMAs ──
    if 'ema' in show_indicators:
        for col, color, name in [
            ('ema_9', '#f59e0b', 'EMA 9'),
            ('ema_20', '#60a5fa', 'EMA 20'),
            ('ema_50', '#a78bfa', 'EMA 50'),
            ('ema_200', '#f97316', 'EMA 200'),
        ]:
            if col in df.columns:
                fig.add_trace(go.Scatter(
                    x=df.index, y=df[col], name=name, mode='lines',
                    line=dict(color=color, width=1.2)
                ), row=1, col=1)

    # ── Bollinger ──
    if 'bollinger' in show_indicators and 'bb_upper' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['bb_upper'], name='BB Upper', mode='lines',
            line=dict(color='rgba(96,165,250,0.5)', width=1, dash='dot')
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=df['bb_lower'], name='BB Lower', mode='lines',
            fill='tonexty', fillcolor='rgba(96,165,250,0.05)',
            line=dict(color='rgba(96,165,250,0.5)', width=1, dash='dot')
        ), row=1, col=1)

    # ── VWAP ──
    if 'vwap' in show_indicators and 'vwap' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['vwap'], name='VWAP ✅', mode='lines',
            line=dict(color='#f0b429', width=1.5, dash='dash')
        ), row=1, col=1)

    # ── Ichimoku ──
    if 'ichimoku' in show_indicators and 'ich_senkou_a' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['ich_senkou_a'], name='Senkou A', mode='lines',
            line=dict(color='rgba(16,185,129,0.6)', width=1)
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=df['ich_senkou_b'], name='Senkou B', mode='lines',
            fill='tonexty', fillcolor='rgba(100,100,200,0.08)',
            line=dict(color='rgba(239,68,68,0.6)', width=1)
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=df['ich_tenkan'], name='Tenkan', mode='lines',
            line=dict(color='#22d3ee', width=1, dash='dot')
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=df['ich_kijun'], name='Kijun', mode='lines',
            line=dict(color='#c084fc', width=1, dash='dot')
        ), row=1, col=1)

    # ── Supertrend ──
    if has_st:
        st_vals = df['supertrend'].copy()
        dirs = df['supertrend_dir'].copy()
        buy_mask = dirs == 1
        sell_mask = dirs == -1

        fig.add_trace(go.Scatter(
            x=df.index[buy_mask], y=st_vals[buy_mask],
            name='Supertrend 🟢', mode='lines',
            line=dict(color=T['green'], width=2)
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df.index[sell_mask], y=st_vals[sell_mask],
            name='Supertrend 🔴', mode='lines',
            line=dict(color=T['red'], width=2)
        ), row=1, col=1)

        # إشارات الشراء/البيع على الشارت
        for j in range(1, len(dirs)):
            if dirs.iloc[j] == 1 and dirs.iloc[j-1] == -1:
                fig.add_annotation(
                    x=df.index[j], y=df['low'].iloc[j] * 0.99,
                    text="BUY", showarrow=False,
                    font=dict(color=T['green'], size=9),
                    bgcolor='rgba(16,185,129,0.2)'
                )
            elif dirs.iloc[j] == -1 and dirs.iloc[j-1] == 1:
                fig.add_annotation(
                    x=df.index[j], y=df['high'].iloc[j] * 1.01,
                    text="SELL", showarrow=False,
                    font=dict(color=T['red'], size=9),
                    bgcolor='rgba(239,68,68,0.2)'
                )

    # ── Parabolic SAR ──
    if 'sar' in show_indicators and 'psar' in df.columns:
        sar_color = [T['green'] if df['close'].iloc[k] > df['psar'].iloc[k] else T['red']
                     for k in range(len(df))]
        fig.add_trace(go.Scatter(
            x=df.index, y=df['psar'], name='Parabolic SAR',
            mode='markers', marker=dict(size=3, color=sar_color)
        ), row=1, col=1)

    # ── حجم التداول ──
    current_row = 2
    if 'volume' in show_indicators:
        colors = [T['green'] if df['close'].iloc[k] >= df['open'].iloc[k] else T['red']
                  for k in range(len(df))]
        fig.add_trace(go.Bar(
            x=df.index, y=df['volume'], name='الحجم',
            marker_color=colors, opacity=0.7
        ), row=current_row, col=1)
        if 'vol_sma' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, y=df['vol_sma'], name='متوسط الحجم',
                mode='lines', line=dict(color=T['accent'], width=1.5)
            ), row=current_row, col=1)
        current_row += 1

    # ── RSI ──
    if 'rsi' in show_indicators and 'rsi' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['rsi'], name='RSI',
            mode='lines', line=dict(color='#a78bfa', width=1.5)
        ), row=current_row, col=1)
        if 'rsi_ema' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, y=df['rsi_ema'], name='RSI EMA',
                mode='lines', line=dict(color='#fcd34d', width=1, dash='dot')
            ), row=current_row, col=1)
        for lvl, clr in [(70, T['red']), (30, T['green']), (50, T['sub'])]:
            fig.add_hline(y=lvl, line_color=clr, line_dash='dot', line_width=0.8, row=current_row, col=1)
        current_row += 1

    # ── MACD ──
    if 'macd' in show_indicators and 'macd' in df.columns:
        hist = df['macd_hist']
        bar_colors = [T['green'] if v >= 0 else T['red'] for v in hist]
        fig.add_trace(go.Bar(
            x=df.index, y=hist, name='MACD Histogram',
            marker_color=bar_colors, opacity=0.7
        ), row=current_row, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=df['macd'], name='MACD',
            mode='lines', line=dict(color='#60a5fa', width=1.5)
        ), row=current_row, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=df['macd_signal'], name='Signal',
            mode='lines', line=dict(color='#f97316', width=1.5)
        ), row=current_row, col=1)

    fig.update_layout(
        template='plotly_dark' if st.session_state.get('dark_mode', True) else 'plotly_white',
        paper_bgcolor=T['chart_bg'], plot_bgcolor=T['chart_bg'],
        font=dict(family='Cairo, Tajawal, sans-serif', color=T['text']),
        legend=dict(
            orientation='h', yanchor='bottom', y=1.01,
            xanchor='right', x=1, bgcolor='rgba(0,0,0,0)',
            font=dict(size=10)
        ),
        height=700 + rows_count * 80,
        xaxis_rangeslider_visible=False,
        margin=dict(l=10, r=10, t=30, b=10),
        hovermode='x unified',
    )
    for i in range(1, rows_count + 1):
        fig.update_xaxes(gridcolor=T['border'], row=i, col=1, showgrid=True)
        fig.update_yaxes(gridcolor=T['border'], row=i, col=1, showgrid=True)

    return fig

def plot_equity_curve(results: List[BacktestResult]) -> go.Figure:
    T = get_theme()
    colors = ['#10b981', '#f59e0b', '#60a5fa', '#a78bfa', '#f97316', '#22d3ee', '#ef4444', '#84cc16']
    fig = go.Figure()
    for idx, r in enumerate(results):
        if r.equity_curve:
            fig.add_trace(go.Scatter(
                y=r.equity_curve, mode='lines', name=r.strategy_name,
                line=dict(color=colors[idx % len(colors)], width=1.8),
                hovertemplate=f"{r.strategy_name}: %{{y:,.0f}} EGP"
            ))
    fig.update_layout(
        template='plotly_dark' if st.session_state.get('dark_mode', True) else 'plotly_white',
        paper_bgcolor=T['chart_bg'], plot_bgcolor=T['chart_bg'],
        font=dict(family='Cairo', color=T['text']),
        yaxis_title='رأس المال (EGP)', xaxis_title='أيام التداول',
        height=380, margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation='h', y=1.02),
        hovermode='x unified',
    )
    return fig

# ═══════════════════════════════════════════════════════════════
# الشريط الجانبي
# ═══════════════════════════════════════════════════════════════
def render_sidebar():
    T = get_theme()

    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center;padding:12px 0 8px">
            <div style="font-size:28px">📈</div>
            <div style="font-size:16px;font-weight:700;color:{T['accent']}">EGX Pro v30</div>
            <div style="font-size:11px;color:{T['sub']}">محلل البورصة المصرية</div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # وضع الإضاءة
        cols = st.columns(2)
        if cols[0].button("🌙 داكن" if not st.session_state.get('dark_mode', True) else "☀️ فاتح"):
            st.session_state.dark_mode = not st.session_state.get('dark_mode', True)
            st.rerun()

        st.divider()

        # الصفحة
        page = st.radio("📑 الأقسام", [
            "🏠 لوحة السوق",
            "📊 تحليل السهم",
            "🤖 توقعات AI",
            "⚡ الباكتست",
            "🔍 مقارنة الأسهم",
            "🎯 الأفضل والأسوأ",
            "🔔 التنبيهات",
            "ℹ️ عن التطبيق",
        ], label_visibility='collapsed')

        st.divider()

        # فلتر القطاع
        all_sectors = ['الكل'] + sorted(EGXDatabase.SECTORS.keys())
        selected_sector = st.selectbox("🏢 القطاع", all_sectors)

        # قائمة الأسهم
        if selected_sector == 'الكل':
            symbols_pool = list(EGXDatabase.STOCKS.keys())
        else:
            symbols_pool = EGXDatabase.SECTORS.get(selected_sector, [])

        symbol_options = []
        for s in symbols_pool:
            info = EGXDatabase.STOCKS.get(s, {})
            symbol_options.append(f"{s} — {info.get('name', s)}")

        selected_display = st.selectbox("📌 السهم", symbol_options)
        symbol = selected_display.split(' — ')[0] if symbol_options else "COMI"

        # فترة البيانات
        period_map = {"شهر": 30, "3 أشهر": 90, "6 أشهر": 180, "سنة": 365, "سنتان": 730}
        period_label = st.select_slider("📅 الفترة", options=list(period_map.keys()), value="6 أشهر")
        days = period_map[period_label]

        # المؤشرات
        st.markdown("**📐 المؤشرات الفنية**")
        ind_opts = {
            'ema': 'المتوسطات EMA', 'bollinger': 'بولينجر', 'vwap': 'VWAP ✅',
            'ichimoku': 'إيشيموكو', 'supertrend': 'Supertrend 🆕',
            'sar': 'Parabolic SAR', 'rsi': 'RSI', 'macd': 'MACD', 'volume': 'الحجم'
        }
        selected_inds = []
        for k, v in ind_opts.items():
            if st.checkbox(v, value=k in ['ema', 'rsi', 'macd', 'volume', 'supertrend']):
                selected_inds.append(k)

        # وقت القاهرة
        now = get_cairo_time()
        market_open = 10 <= now.hour < 15 and now.weekday() < 5
        status = f"🟢 السوق مفتوح" if market_open else "🔴 السوق مغلق"
        st.markdown(f"""
        <div style="text-align:center;font-size:12px;color:{T['sub']};margin-top:8px">
            {status}<br>{now.strftime('%I:%M %p')} | القاهرة
        </div>
        """, unsafe_allow_html=True)

    return page, symbol, days, selected_inds

# ═══════════════════════════════════════════════════════════════
# الصفحات
# ═══════════════════════════════════════════════════════════════
def page_dashboard():
    T = get_theme()
    st.markdown('<div class="section-header">🏠 لوحة القيادة — ملخص السوق المصري</div>', unsafe_allow_html=True)

    # مؤشرات EGX30
    col1, col2, col3 = st.columns(3)
    col1.info("📊 EGX30 — يتم تحديثه عند اختيار الأسهم")
    col2.info("🕙 جلسة اليوم — بيانات من Yahoo Finance أو محاكاة")
    col3.info(f"⏰ {get_cairo_time().strftime('%Y-%m-%d %H:%M')} | Cairo")

    # جدول أسهم EGX30
    with st.spinner("جارٍ تحميل بيانات EGX30..."):
        watchlist = EGXDatabase.EGX30[:20]
        df_market = build_market_dashboard(watchlist)

    if not df_market.empty:
        # تلوين الخلايا
        def color_change(val):
            try:
                v = float(val)
                c = T['green'] if v > 0 else (T['red'] if v < 0 else T['sub'])
                return f'color: {c}; font-weight: 500'
            except:
                return ''

        def color_signal(val):
            s = str(val)
            if 'شراء' in s: return f'color: {T["green"]}'
            if 'بيع' in s: return f'color: {T["red"]}'
            return ''

        styled = df_market.style \
            .applymap(color_change, subset=['التغير%']) \
            .applymap(color_signal, subset=['الإشارة', 'Supertrend']) \
            .format({'السعر': '{:.2f}', 'التغير%': '{:+.2f}%', 'الثقة%': '{:.0f}%',
                     'RSI': '{:.1f}', 'حجم×': '{:.1f}x', 'P/E': '{:.1f}', 'توزيعات%': '{:.1f}%'})

        st.dataframe(styled, use_container_width=True, height=500)

        # إحصائيات سريعة
        if 'التغير%' in df_market.columns:
            c1, c2, c3, c4 = st.columns(4)
            gainers = (df_market['التغير%'] > 0).sum()
            losers = (df_market['التغير%'] < 0).sum()
            kpi("🟢 الرابحون", gainers, col=c1)
            kpi("🔴 الخاسرون", losers, col=c2)
            kpi("📊 متوسط التغير", f"{df_market['التغير%'].mean():.2f}%", col=c3)
            kpi("⚡ إشارات شراء", (df_market['الإشارة'].str.contains('شراء', na=False)).sum(), col=c4)
    else:
        st.warning("تعذّر تحميل البيانات")

def page_analysis(symbol: str, days: int, show_indicators: List[str]):
    T = get_theme()
    info = EGXDatabase.STOCKS.get(symbol, {})

    st.markdown(f'<div class="section-header">📊 تحليل {info.get("name", symbol)} ({symbol})</div>', unsafe_allow_html=True)

    with st.spinner(f"جارٍ تحليل {symbol}..."):
        df = load_and_compute(symbol, days)

    if df is None or df.empty:
        st.error("تعذّر تحميل البيانات")
        return

    source = df['data_source'].iloc[-1] if 'data_source' in df.columns else 'simulated'
    badge_class = 'real-badge' if source == 'real' else 'sim-badge'
    badge_text = '📡 بيانات حقيقية — Yahoo Finance' if source == 'real' else '🔮 بيانات محاكاة — GARCH'
    st.markdown(f'<span class="data-source-badge {badge_class}">{badge_text}</span>', unsafe_allow_html=True)

    # ── KPIs ──
    price = float(df['close'].iloc[-1])
    prev_price = float(df['close'].iloc[-2]) if len(df) > 1 else price
    change = price - prev_price
    change_pct = (change / prev_price * 100) if prev_price else 0
    high52 = float(df['high'].max())
    low52 = float(df['low'].min())
    rsi = safe_last(df['rsi'], 50)
    adx = safe_last(df['adx'], 20)
    vol_today = int(df['volume'].iloc[-1])
    vol_avg = int(df['vol_sma'].iloc[-1]) if 'vol_sma' in df.columns else 0
    vol_ratio = float(df['vol_ratio'].iloc[-1]) if 'vol_ratio' in df.columns else 1.0

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    kpi("💰 السعر الحالي", f"{price:.2f}", delta=f"{change:+.2f} ({change_pct:+.2f}%)", col=c1)
    kpi("📈 أعلى 52 أسبوع", f"{high52:.2f}", col=c2)
    kpi("📉 أدنى 52 أسبوع", f"{low52:.2f}", col=c3)
    kpi("⚡ RSI", f"{rsi:.1f}", delta="تشبع شراء" if rsi > 70 else ("تشبع بيع" if rsi < 30 else "محايد"), col=c4)
    kpi("💪 ADX (قوة الاتجاه)", f"{adx:.1f}", delta="اتجاه قوي" if adx > 25 else "اتجاه ضعيف", col=c5)
    kpi("📦 حجم×المتوسط", f"{vol_ratio:.1f}x", col=c6)

    # ── الإشارة المركّبة ──
    signal, emoji, confidence, sig_details = get_composite_signal(df)
    color = T['green'] if 'شراء' in signal else (T['red'] if 'بيع' in signal else T['accent'])
    border_color = color

    st.markdown(f"""
    <div class="signal-box" style="background:rgba(0,0,0,0.3);border-color:{border_color};color:{color}">
        {emoji} الإشارة: <strong>{signal}</strong> &nbsp;|&nbsp; الثقة: <strong>{confidence}%</strong>
    </div>
    """, unsafe_allow_html=True)

    # ── Supertrend Status ──
    if 'supertrend_dir' in df.columns:
        st_dir = safe_last(df['supertrend_dir'], 0)
        st_val = safe_last(df['supertrend'])
        st_color = T['green'] if st_dir == 1 else T['red']
        st_txt = "🟢 Supertrend: إشارة شراء نشطة" if st_dir == 1 else "🔴 Supertrend: إشارة بيع نشطة"
        st.markdown(f'<div style="color:{st_color};font-weight:600;font-size:14px;margin:4px 0">{st_txt} | المستوى: {st_val:.2f}</div>', unsafe_allow_html=True)

    # ── المخطط الرئيسي ──
    fig = plot_candlestick(df, symbol, show_indicators)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})

    # ── تبويبات التفاصيل ──
    tab1, tab2, tab3, tab4 = st.tabs(["📐 تفاصيل المؤشرات", "🕯️ أنماط الشموع", "🎯 الدعم والمقاومة", "📋 بيانات الشركة"])

    with tab1:
        cols = st.columns(3)
        indicators_data = [
            ("RSI (14)", f"{rsi:.1f}", "تشبع شراء" if rsi > 70 else "تشبع بيع" if rsi < 30 else "محايد"),
            ("MACD", f"{safe_last(df['macd']):.3f}", "صاعد" if safe_last(df['macd']) > safe_last(df['macd_signal']) else "هابط"),
            ("EMA 20", f"{safe_last(df['ema_20']):.2f}", ""),
            ("EMA 50", f"{safe_last(df['ema_50']):.2f}", ""),
            ("EMA 200", f"{safe_last(df['ema_200']):.2f}", ""),
            ("ADX", f"{adx:.1f}", "قوي" if adx > 25 else "ضعيف"),
            ("Stochastic K", f"{safe_last(df['stoch_k']):.1f}", ""),
            ("CCI", f"{safe_last(df['cci']):.0f}", ""),
            ("Williams %R", f"{safe_last(df['williams_r']):.1f}", ""),
            ("VWAP (يومي ✅)", f"{safe_last(df['vwap']):.2f}", ""),
            ("ATR", f"{safe_last(df['atr']):.3f}", ""),
            ("ROC 12", f"{safe_last(df['roc']):.2f}%", ""),
        ]
        for idx, (name, val, note) in enumerate(indicators_data):
            with cols[idx % 3]:
                st.metric(name, val, note if note else None)

        if sig_details:
            st.markdown("**تفاصيل الإشارات:**")
            for ind, detail in sig_details.items():
                st.markdown(f"- **{ind}:** {detail}")

    with tab2:
        patterns = detect_patterns(df)
        if patterns:
            for p in patterns:
                strength_stars = '⭐' * p['strength']
                color_txt = T['green'] if p['signal'] == 'شراء' else (T['red'] if p['signal'] == 'بيع' else T['accent'])
                st.markdown(f"""
                <div class="pattern-card">
                    <span style="font-size:20px">{p['emoji']}</span>
                    <strong> {p['name']}</strong>
                    <span style="color:{color_txt};margin-right:8px"> {p['signal']}</span>
                    <span style="font-size:12px">{strength_stars}</span>
                    <div style="font-size:13px;color:{T['sub']};margin-top:4px">{p['desc']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("لا توجد أنماط شموع بارزة حالياً")

    with tab3:
        support, resistance = get_support_resistance(df)
        fib = get_fibonacci_levels(support, resistance)

        c1, c2 = st.columns(2)
        c1.metric("🟢 دعم", f"{support:.2f} EGP")
        c2.metric("🔴 مقاومة", f"{resistance:.2f} EGP")

        st.markdown("**مستويات فيبوناتشي:**")
        fib_data = [{"المستوى": k, "السعر": f"{v:.2f}"} for k, v in fib.items()]
        st.table(pd.DataFrame(fib_data))

    with tab4:
        st.markdown(f"""
        | البيان | القيمة |
        |--------|--------|
        | الاسم العربي | {info.get('name', 'N/A')} |
        | الاسم الإنجليزي | {info.get('name_en', 'N/A')} |
        | القطاع | {info.get('sector', 'N/A')} |
        | رمز Yahoo Finance | {info.get('yf', 'غير متوفر')} |
        | سعر القاعدة (EGP) | {info.get('base', 'N/A')} |
        | مضاعف الأرباح P/E | {info.get('pe', 'N/A')} |
        | عائد التوزيعات | {info.get('div_yield', 0):.1f}% |
        """)

def page_ai_forecast(symbol: str, days: int):
    T = get_theme()
    info = EGXDatabase.STOCKS.get(symbol, {})
    st.markdown(f'<div class="section-header">🤖 توقعات AI — {info.get("name", symbol)}</div>', unsafe_allow_html=True)

    with st.spinner("جارٍ تدريب نموذج الذكاء الاصطناعي... قد يستغرق 20-30 ثانية"):
        df = load_and_compute(symbol, days)
        if df is None:
            st.error("تعذّر تحميل البيانات")
            return
        result = train_ml_model(df)

    if result.warning:
        st.warning(f"⚠️ {result.warning}")

    if result.confidence > 0:
        # نتيجة التوقع
        direction_color = T['green'] if 'صعود' in result.predicted_direction else T['red']
        st.markdown(f"""
        <div class="signal-box" style="background:rgba(0,0,0,0.3);border-color:{direction_color};color:{direction_color}">
            {result.predicted_direction}<br>
            <span style="font-size:14px">السعر المتوقع: {result.predicted_price:.2f} EGP</span><br>
            <span style="font-size:13px;opacity:0.8">دقة النموذج على بيانات الاختبار: {result.model_accuracy:.1f}% | ثقة حقيقية: {result.confidence:.1f}%</span>
        </div>
        """, unsafe_allow_html=True)

        # تفاصيل النموذج
        c1, c2, c3 = st.columns(3)
        kpi("🎯 دقة Walk-Forward", f"{result.model_accuracy:.1f}%",
            delta="✅ قياس حقيقي على بيانات غير مرئية", col=c1)
        kpi("📊 حجم التدريب", f"{result.train_size} يوم", col=c2)
        kpi("🧪 حجم الاختبار", f"{result.test_size} يوم", col=c3)

        # تحذير مهم
        st.warning("""
        ⚠️ **تنبيه مهم للمستثمر:**
        هذه التوقعات للمساعدة التحليلية فقط وليست نصيحة استثمارية.
        دقة النموذج المعروضة هي على بيانات اختبار حقيقية (Walk-Forward)
        ولا تضمن الأداء المستقبلي. دائماً استخدم إدارة المخاطر.
        """)

        # أهمية المتغيرات
        if result.features_importance:
            st.markdown("**أهم المؤشرات المؤثرة في التوقع:**")
            feat_df = pd.DataFrame(
                list(result.features_importance.items()),
                columns=['المؤشر', 'الأهمية']
            ).sort_values('الأهمية', ascending=True)

            fig = go.Figure(go.Bar(
                x=feat_df['الأهمية'],
                y=feat_df['المؤشر'],
                orientation='h',
                marker_color=T['accent'],
                text=[f"{v:.3f}" for v in feat_df['الأهمية']],
                textposition='outside'
            ))
            fig.update_layout(
                template='plotly_dark' if st.session_state.get('dark_mode', True) else 'plotly_white',
                paper_bgcolor=T['chart_bg'], plot_bgcolor=T['chart_bg'],
                font=dict(family='Cairo', color=T['text']),
                height=320, margin=dict(l=10, r=10, t=10, b=10),
                xaxis_title='الأهمية النسبية'
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("لم يُكتمل النموذج. تأكد من توفر بيانات كافية (150+ يوم)")

def page_backtest(symbol: str, days: int):
    T = get_theme()
    info = EGXDatabase.STOCKS.get(symbol, {})
    st.markdown(f'<div class="section-header">⚡ الباكتست — {info.get("name", symbol)}</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    initial_capital = c1.number_input("💰 رأس المال (EGP)", min_value=10_000, max_value=10_000_000,
                                       value=100_000, step=10_000)
    sl_pct = c2.slider("🛑 وقف الخسارة %", 1, 20, 5)
    tp_pct = c3.slider("🎯 هدف الربح %", 2, 40, 10)

    run_btn = st.button("▶️ تشغيل الباكتست لجميع الاستراتيجيات", type="primary", use_container_width=True)

    if run_btn:
        with st.spinner("جارٍ تشغيل الباكتست..."):
            df = load_and_compute(symbol, days)
            if df is None:
                st.error("تعذّر تحميل البيانات")
                return
            results = run_all_backtests(df, initial_capital)
            st.session_state['bt_results'] = results

    if 'bt_results' in st.session_state:
        results = st.session_state['bt_results']

        # جدول المقارنة
        rows = []
        for r in results:
            rows.append({
                'الاستراتيجية': r.strategy_name,
                'العائد الإجمالي': f"{r.total_return:+.1f}%",
                'العائد السنوي': f"{r.annual_return:+.1f}%",
                'Sharpe': f"{r.sharpe_ratio:.2f}",
                'Calmar': f"{r.calmar_ratio:.2f}",
                'أقصى هبوط': f"{r.max_drawdown:.1f}%",
                'معدل الربح': f"{r.win_rate:.0f}%",
                'الصفقات': r.total_trades,
                'رأس المال النهائي': f"{r.final_capital:,.0f}",
                'عمولة EGX': f"{r.commission_total:,.0f}",
                'Kelly%': f"{r.kelly_fraction:.1f}%",
            })

        df_res = pd.DataFrame(rows)

        def highlight_best(col):
            if col.name in ['العائد الإجمالي', 'العائد السنوي', 'Sharpe', 'Calmar', 'معدل الربح']:
                return ['background-color: rgba(16,185,129,0.15)' if i == 0 else '' for i in range(len(col))]
            return ['' for _ in col]

        st.dataframe(
            df_res.style.apply(highlight_best),
            use_container_width=True
        )

        # أفضل استراتيجية
        best = results[0]
        st.success(f"🏆 أفضل استراتيجية: **{best.strategy_name}** | Sharpe: {best.sharpe_ratio:.2f} | عائد: {best.total_return:+.1f}%")

        # منحنى رأس المال
        st.markdown("**📈 منحنى رأس المال لجميع الاستراتيجيات:**")
        st.plotly_chart(plot_equity_curve(results), use_container_width=True)

        # تفاصيل الصفقات لأفضل استراتيجية
        if best.trades_log:
            st.markdown(f"**📋 آخر 10 صفقات — {best.strategy_name}:**")
            trades_df = pd.DataFrame(best.trades_log[-10:])
            trades_df['النتيجة'] = trades_df['pnl'].apply(lambda x: '✅ ربح' if x > 0 else '❌ خسارة')
            trades_df['pnl'] = trades_df['pnl'].apply(lambda x: f"{x:+.2f}")
            st.dataframe(trades_df[['date', 'entry', 'exit', 'pnl', 'type', 'النتيجة']], use_container_width=True)

def page_compare(days: int):
    T = get_theme()
    st.markdown('<div class="section-header">🔍 مقارنة الأسهم</div>', unsafe_allow_html=True)

    all_syms = list(EGXDatabase.STOCKS.keys())
    options = [f"{s} — {EGXDatabase.STOCKS[s].get('name','')}" for s in all_syms]
    selected = st.multiselect("اختر 2-5 أسهم للمقارنة", options, max_selections=5,
                               default=options[:3])

    if len(selected) < 2:
        st.info("اختر سهمين على الأقل للمقارنة")
        return

    syms = [s.split(' — ')[0] for s in selected]

    with st.spinner("جارٍ تحميل البيانات..."):
        dfs = {}
        for sym in syms:
            df = load_and_compute(sym, days)
            if df is not None and not df.empty:
                dfs[sym] = df

    if len(dfs) < 2:
        st.error("تعذّر تحميل البيانات الكافية")
        return

    # الأداء النسبي
    fig = go.Figure()
    colors = ['#10b981', '#f59e0b', '#60a5fa', '#a78bfa', '#ef4444']
    for idx, (sym, df) in enumerate(dfs.items()):
        norm = df['close'] / df['close'].iloc[0] * 100
        fig.add_trace(go.Scatter(
            x=df.index, y=norm,
            name=f"{sym} — {EGXDatabase.STOCKS[sym].get('name', '')}",
            mode='lines', line=dict(color=colors[idx], width=2)
        ))
    fig.add_hline(y=100, line_dash='dot', line_color=T['sub'], line_width=1)
    fig.update_layout(
        template='plotly_dark' if st.session_state.get('dark_mode', True) else 'plotly_white',
        paper_bgcolor=T['chart_bg'], plot_bgcolor=T['chart_bg'],
        font=dict(family='Cairo', color=T['text']),
        yaxis_title='الأداء (قاعدة 100)', height=380,
        margin=dict(l=10, r=10, t=20, b=10), hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    # جدول مقارنة تفصيلي
    compare_rows = []
    for sym, df in dfs.items():
        info = EGXDatabase.STOCKS.get(sym, {})
        signal, emoji, conf, _ = get_composite_signal(df)
        price = float(df['close'].iloc[-1])
        rtn_1m = (price / float(df['close'].iloc[max(-22, -len(df))]) - 1) * 100
        rtn_3m = (price / float(df['close'].iloc[max(-66, -len(df))]) - 1) * 100
        compare_rows.append({
            'السهم': sym,
            'الشركة': info.get('name', ''),
            'السعر': f"{price:.2f}",
            'عائد شهر': f"{rtn_1m:+.1f}%",
            'عائد 3 أشهر': f"{rtn_3m:+.1f}%",
            'RSI': f"{safe_last(df['rsi'], 50):.0f}",
            'ADX': f"{safe_last(df['adx'], 20):.0f}",
            'التقلب%': f"{float(df['volatility_20d'].iloc[-1])*100:.1f}%" if 'volatility_20d' in df.columns else 'N/A',
            'الإشارة': f"{emoji} {signal}",
        })

    st.dataframe(pd.DataFrame(compare_rows), use_container_width=True)

def page_top_bottom(days: int):
    T = get_theme()
    st.markdown('<div class="section-header">🎯 أفضل وأسوأ الأسهم</div>', unsafe_allow_html=True)

    n_filter = st.slider("عدد الأسهم", 5, 20, 10)

    with st.spinner("جارٍ تحليل السوق..."):
        watchlist = EGXDatabase.EGX30 + EGXDatabase.EGX70[:10]
        df_market = build_market_dashboard(watchlist)

    if df_market.empty:
        st.error("تعذّر تحميل البيانات")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**🟢 أفضل {n_filter} أسهم (التغير اليومي)**")
        top = df_market.nlargest(n_filter, 'التغير%')[['رمز', 'الشركة', 'السعر', 'التغير%', 'الإشارة', 'RSI']]
        st.dataframe(top.style.format({'السعر': '{:.2f}', 'التغير%': '{:+.2f}%', 'RSI': '{:.0f}'}),
                     use_container_width=True)

    with col2:
        st.markdown(f"**🔴 أسوأ {n_filter} أسهم (التغير اليومي)**")
        bottom = df_market.nsmallest(n_filter, 'التغير%')[['رمز', 'الشركة', 'السعر', 'التغير%', 'الإشارة', 'RSI']]
        st.dataframe(bottom.style.format({'السعر': '{:.2f}', 'التغير%': '{:+.2f}%', 'RSI': '{:.0f}'}),
                     use_container_width=True)

    # فرص الشراء — RSI < 35 مع Supertrend صاعد
    if 'Supertrend' in df_market.columns and 'RSI' in df_market.columns:
        opps = df_market[
            (df_market['RSI'] < 40) & (df_market['Supertrend'].str.contains('شراء', na=False))
        ]
        if not opps.empty:
            st.markdown("**💡 فرص محتملة — RSI منخفض + Supertrend شراء:**")
            st.dataframe(opps[['رمز', 'الشركة', 'السعر', 'التغير%', 'RSI', 'Supertrend', 'الإشارة']],
                         use_container_width=True)

def page_alerts(symbol: str):
    T = get_theme()
    st.markdown(f'<div class="section-header">🔔 نظام التنبيهات</div>', unsafe_allow_html=True)

    # إضافة تنبيه جديد
    with st.expander("➕ إضافة تنبيه جديد", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        sym = c1.selectbox("السهم", list(EGXDatabase.STOCKS.keys()), index=list(EGXDatabase.STOCKS.keys()).index(symbol))
        condition = c2.selectbox("الشرط", [
            'above — سعر أعلى من',
            'below — سعر أقل من',
            'rsi_above — RSI أعلى من',
            'rsi_below — RSI أقل من',
            'supertrend_buy — Supertrend شراء',
            'supertrend_sell — Supertrend بيع',
            'volume_spike — ارتفاع الحجم ×'
        ])
        cond_key = condition.split(' — ')[0]
        value = c3.number_input("القيمة", min_value=0.0, value=0.0, step=0.5)
        note = c4.text_input("ملاحظة", "")

        if st.button("💾 حفظ التنبيه", type="primary"):
            a = alert_manager.add_alert(sym, cond_key, value, note)
            st.success(f"✅ تم حفظ التنبيه — {sym} | {condition}")

    # فحص التنبيهات على السهم المحدد
    df = load_and_compute(symbol, 30)
    if df is not None:
        triggered = alert_manager.check_alerts(df, symbol)
        if triggered:
            for a in triggered:
                st.error(f"🚨 تنبيه محقق! {a.symbol} — {a.condition} عند {a.value}")

    # قائمة التنبيهات
    active = alert_manager.get_active_alerts()
    if active:
        st.markdown("**📋 التنبيهات النشطة:**")
        for idx, a in enumerate(active):
            c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
            c1.write(f"**{a.symbol}**")
            c2.write(a.condition)
            c3.write(f"{a.value} | {a.note or '—'}")
            if c4.button("🗑️", key=f"del_{idx}"):
                alert_manager.remove_alert(idx)
                st.rerun()
    else:
        st.info("لا توجد تنبيهات نشطة حالياً")

    st.info("""
    💡 **ملاحظة:** التنبيهات تعمل عند فتح التطبيق فقط.
    للحصول على إشعارات فورية، يُوصى بدمج Telegram Bot API.
    راجع التوثيق في: https://core.telegram.org/bots
    """)

def page_about():
    T = get_theme()
    st.markdown(f"""
    <div class="section-header">ℹ️ عن EGX Pro Ultimate v30</div>

    <div style="background:{T['card']};border-radius:12px;padding:20px 24px;border:1px solid {T['border']}">

    ## 📈 EGX Pro Ultimate v30 — محلل البورصة المصرية

    ### ✅ التحسينات في v30

    | الميزة | v29 | v30 |
    |--------|-----|-----|
    | VWAP | Cumulative ❌ | يومي صحيح ✅ |
    | نموذج ML | Data Leakage ❌ | Walk-Forward ✅ |
    | Supertrend | غير موجود ❌ | موجود ✅ |
    | ADX | حلقة Python ❌ | Vectorized ✅ |
    | Parabolic SAR | بطيء ❌ | محسّن ✅ |
    | قاعدة البيانات | أخطاء قطاعية ❌ | مصحّحة ✅ |
    | شفافية المصدر | غير واضح ❌ | واضح تماماً ✅ |
    | إشارة ML | وهمية ❌ | حقيقية ✅ |

    ### 📊 المؤشرات الفنية (17)
    RSI | EMA 9/20/50/200 | SMA | Bollinger Bands | MACD | ADX+DI | Stochastic |
    OBV | ATR | CCI | Williams %R | **VWAP يومي** | Parabolic SAR | ROC |
    Momentum | **Supertrend** | Ichimoku Cloud

    ### ⚙️ المتطلبات
    ```bash
    pip install streamlit pandas numpy plotly yfinance scikit-learn pytz
    streamlit run egx_app.py
    ```

    ### ⚠️ إخلاء المسؤولية
    هذا التطبيق للأغراض التعليمية والتحليلية فقط.
    لا يُعدّ نصيحة استثمارية. المحاكاة ليست بيانات حقيقية.
    الاستثمار ينطوي على مخاطر.

    ---
    **EGX Pro v30** | بُني بـ Python + Streamlit
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# الدالة الرئيسية
# ═══════════════════════════════════════════════════════════════
def main():
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = True

    apply_css()
    page, symbol, days, show_indicators = render_sidebar()

    if page == "🏠 لوحة السوق":
        page_dashboard()
    elif page == "📊 تحليل السهم":
        page_analysis(symbol, days, show_indicators)
    elif page == "🤖 توقعات AI":
        page_ai_forecast(symbol, days)
    elif page == "⚡ الباكتست":
        page_backtest(symbol, days)
    elif page == "🔍 مقارنة الأسهم":
        page_compare(days)
    elif page == "🎯 الأفضل والأسوأ":
        page_top_bottom(days)
    elif page == "🔔 التنبيهات":
        page_alerts(symbol)
    elif page == "ℹ️ عن التطبيق":
        page_about()

if __name__ == "__main__":
    main()
