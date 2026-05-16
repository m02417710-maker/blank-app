"""
EGX Pro Terminal v26 - Main Application
Professional Technical Analysis Platform for Egyptian Stock Exchange
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config.settings import *
from data.egx_symbols import get_all_symbols, get_stock_info, search_stocks
from core.analysis import EGXAnalyzer
from core.alerts import AlertEngine, SignalType

# Page Configuration
st.set_page_config(
    page_title=f"{APP_NAME} {APP_VERSION}",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
    .bullish {
        color: #26a69a;
        font-weight: bold;
    }
    .bearish {
        color: #ef5350;
        font-weight: bold;
    }
    .alert-high {
        background-color: #ffebee;
        border-left: 4px solid #ef5350;
        padding: 10px;
        margin: 5px 0;
    }
    .alert-medium {
        background-color: #fff8e1;
        border-left: 4px solid #ffc107;
        padding: 10px;
        margin: 5px 0;
    }
    .alert-low {
        background-color: #e8f5e9;
        border-left: 4px solid #66bb6a;
        padding: 10px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown(f"<h1 style='text-align: center;'>{APP_NAME}</h1>", unsafe_allow_html=True)
st.sidebar.markdown(f"<p style='text-align: center; color: gray;'>{APP_VERSION}</p>", unsafe_allow_html=True)
st.sidebar.divider()

# Navigation
page = st.sidebar.radio(
    "القائمة الرئيسية / Main Menu",
    ["🏠 الرئيسية", "🔍 تحليل سهم", "📋 قائمة المراقبة", "🔔 التنبيهات", "ℹ️ حول"]
)

# Initialize session state
if 'alert_engine' not in st.session_state:
    st.session_state.alert_engine = AlertEngine()
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ["COMI", "TMGH", "ETEL", "ESRS"]

# Load symbols
all_symbols = get_all_symbols()

# ==================== HOME PAGE ====================
if page == "🏠 الرئيسية":
    st.markdown("<h1 class='main-header'>📈 EGX Pro Terminal</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>منصة التحليل الفني الاحترافية للبورصة المصرية</h3>", unsafe_allow_html=True)

    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 الأسهم المدعومة", len(all_symbols))
    with col2:
        st.metric("🔔 التنبيهات اليوم", len(st.session_state.alert_engine.get_recent_alerts(24)))
    with col3:
        st.metric("📈 مؤشر EGX30", "تحديث مباشر")

    st.divider()

    st.subheader("🔥 الأسهم الأكثر نشاطاً")
    st.info("يتم تحديث هذه البيانات بشكل مباشر من البورصة المصرية عبر Yahoo Finance")

    # Quick analysis of top stocks
    top_stocks = ["COMI", "TMGH", "ETEL", "ESRS", "JUHO"]
    cols = st.columns(len(top_stocks))

    for i, symbol in enumerate(top_stocks):
        with cols[i]:
            try:
                analyzer = EGXAnalyzer(symbol, period="5d")
                analyzer.fetch_data()
                close = analyzer.data['Close'].iloc[-1]
                prev = analyzer.data['Close'].iloc[-2]
                change = ((close - prev) / prev) * 100

                info = get_stock_info(symbol)
                color = "bullish" if change > 0 else "bearish"
                arrow = "▲" if change > 0 else "▼"

                st.markdown(f"""
                <div class='metric-card'>
                    <h4>{info['name_ar']}</h4>
                    <h3>{symbol}</h3>
                    <p style='font-size: 1.2rem;'>{close:.2f}</p>
                    <p class='{color}'>{arrow} {abs(change):.2f}%</p>
                </div>
                """, unsafe_allow_html=True)
            except:
                st.warning(f"لا يمكن تحميل {symbol}")

# ==================== STOCK ANALYSIS ====================
elif page == "🔍 تحليل سهم":
    st.header("🔍 تحليل فني متقدم")

    col1, col2 = st.columns([2, 1])

    with col1:
        search_query = st.text_input("البحث عن سهم (اسم عربي/إنجليزي أو الرمز)", placeholder="مثال: التجاري الدولي أو COMI")

        if search_query:
            results = search_stocks(search_query)
            if results:
                selected = st.selectbox("اختر السهم:", [f"{s} - {i['name_ar']}" for s, i in results])
                symbol = selected.split(" - ")[0]
            else:
                st.warning("لا توجد نتائج مطابقة")
                symbol = None
        else:
            symbol = st.selectbox("أو اختر من القائمة:", all_symbols, format_func=lambda x: f"{x} - {get_stock_info(x)['name_ar']}")

    with col2:
        period = st.selectbox("الفترة", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
        interval = st.selectbox("الفاصل الزمني", ["1d", "1wk", "1mo"], index=0)

    if symbol and st.button("🚀 بدء التحليل", type="primary"):
        with st.spinner("جاري جلب البيانات وتحليلها..."):
            try:
                analyzer = EGXAnalyzer(symbol, period=period, interval=interval)
                analyzer.fetch_data()
                analyzer.calculate_all_indicators()

                info = get_stock_info(symbol)
                summary = analyzer.get_summary()
                trend = analyzer.get_trend_analysis()

                # Header Info
                st.subheader(f"{info['name_ar']} ({symbol})")
                st.caption(f"القطاع: {info['sector']} | آخر تحديث: {summary['date']}")

                # Metrics Row
                m1, m2, m3, m4, m5 = st.columns(5)
                with m1:
                    delta_color = "normal" if summary['change_pct'] >= 0 else "inverse"
                    st.metric("السعر الحالي", f"{summary['price']:.2f} EGP", f"{summary['change_pct']:.2f}%", delta_color=delta_color)
                with m2:
                    st.metric("حجم التداول", f"{summary['volume']:,}")
                with m3:
                    rsi_color = "inverse" if summary['rsi'] > RSI_OVERBOUGHT else "normal" if summary['rsi'] < RSI_OVERSOLD else "off"
                    st.metric("RSI", f"{summary['rsi']:.1f}")
                with m4:
                    st.metric("ADX", f"{summary['adx']:.1f}")
                with m5:
                    st.metric("ATR", f"{summary['atr']:.2f}")

                st.divider()

                # Main Chart
                fig = make_subplots(
                    rows=3, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.05,
                    row_heights=[0.6, 0.2, 0.2],
                    subplot_titles=(f"{symbol} - Price Action", "Volume", "RSI / MACD")
                )

                # Candlestick
                fig.add_trace(go.Candlestick(
                    x=analyzer.data.index,
                    open=analyzer.data['Open'],
                    high=analyzer.data['High'],
                    low=analyzer.data['Low'],
                    close=analyzer.data['Close'],
                    name="Price",
                    increasing_line_color=THEME_BULLISH,
                    decreasing_line_color=THEME_BEARISH
                ), row=1, col=1)

                # EMAs
                fig.add_trace(go.Scatter(x=analyzer.data.index, y=analyzer.indicators['EMA_9'], 
                                        name="EMA 9", line=dict(color="yellow", width=1)), row=1, col=1)
                fig.add_trace(go.Scatter(x=analyzer.data.index, y=analyzer.indicators['EMA_20'], 
                                        name="EMA 20", line=dict(color="orange", width=1)), row=1, col=1)
                fig.add_trace(go.Scatter(x=analyzer.data.index, y=analyzer.indicators['EMA_50'], 
                                        name="EMA 50", line=dict(color="blue", width=1.5)), row=1, col=1)
                fig.add_trace(go.Scatter(x=analyzer.data.index, y=analyzer.indicators['EMA_200'], 
                                        name="EMA 200", line=dict(color="red", width=2)), row=1, col=1)

                # Bollinger Bands
                fig.add_trace(go.Scatter(x=analyzer.data.index, y=analyzer.indicators['BB_Upper'], 
                                        name="BB Upper", line=dict(color="gray", width=0.5, dash="dash")), row=1, col=1)
                fig.add_trace(go.Scatter(x=analyzer.data.index, y=analyzer.indicators['BB_Lower'], 
                                        name="BB Lower", line=dict(color="gray", width=0.5, dash="dash")), row=1, col=1)

                # Volume
                colors = [THEME_BULLISH if c >= o else THEME_BEARISH 
                         for c, o in zip(analyzer.data['Close'], analyzer.data['Open'])]
                fig.add_trace(go.Bar(x=analyzer.data.index, y=analyzer.data['Volume'], 
                                    name="Volume", marker_color=colors), row=2, col=1)

                # RSI
                fig.add_trace(go.Scatter(x=analyzer.data.index, y=analyzer.indicators['RSI'], 
                                        name="RSI", line=dict(color="purple", width=1.5)), row=3, col=1)
                fig.add_hline(y=RSI_OVERBOUGHT, line_dash="dash", line_color="red", row=3, col=1)
                fig.add_hline(y=RSI_OVERSOLD, line_dash="dash", line_color="green", row=3, col=1)

                fig.update_layout(
                    height=CHART_HEIGHT,
                    showlegend=True,
                    xaxis_rangeslider_visible=False,
                    template="plotly_dark",
                    title_text=f"Technical Analysis - {info['name_ar']}",
                    hovermode="x unified"
                )

                st.plotly_chart(fig, use_container_width=True)

                # Trend Analysis
                st.subheader("📊 تقييم الاتجاه")
                trend_col1, trend_col2 = st.columns(2)

                with trend_col1:
                    st.markdown(f"**الاتجاه:** {trend['direction']}")
                    st.markdown(f"**القوة:** {trend['strength']}")
                    st.markdown(f"**النقاط:** {trend['score']}")

                with trend_col2:
                    for signal in trend['signals']:
                        st.markdown(f"- {signal}")

                # Support/Resistance
                levels = summary['levels']
                st.subheader("🎯 مستويات الدعم والمقاومة")
                l1, l2, l3 = st.columns(3)
                with l1:
                    st.metric("الدعم", f"{levels['support']:.2f}")
                with l2:
                    st.metric("المحور", f"{levels['pivot']:.2f}")
                with l3:
                    st.metric("المقاومة", f"{levels['resistance']:.2f}")

                st.caption(f"نطاق التداول: {levels['range_pct']:.2f}%")

                # Add to Watchlist
                if st.button("➕ إضافة إلى قائمة المراقبة"):
                    st.session_state.watchlist.append(symbol)
                    st.success(f"تمت إضافة {symbol} إلى قائمة المراقبة!")

            except Exception as e:
                st.error(f"حدث خطأ: {str(e)}")
                st.info("تأكد من صحة رمز السهم واتصالك بالإنترنت")

# ==================== WATCHLIST ====================
elif page == "📋 قائمة المراقبة":
    st.header("📋 قائمة المراقبة")

    if not st.session_state.watchlist:
        st.info("قائمة المراقبة فارغة. أضف أسماً من صفحة التحليل.")
    else:
        for symbol in st.session_state.watchlist:
            try:
                analyzer = EGXAnalyzer(symbol, period="1mo")
                analyzer.fetch_data()
                analyzer.calculate_all_indicators()
                summary = analyzer.get_summary()
                info = get_stock_info(symbol)

                change_color = "bullish" if summary['change_pct'] >= 0 else "bearish"

                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                    with col1:
                        st.markdown(f"**{info['name_ar']}** ({symbol})")
                    with col2:
                        st.markdown(f"<span class='{change_color}'>{summary['price']:.2f} ({summary['change_pct']:+.2f}%)</span>", 
                                  unsafe_allow_html=True)
                    with col3:
                        st.caption(f"RSI: {summary['rsi']:.1f}")
                    with col4:
                        st.caption(f"ADX: {summary['adx']:.1f}")
                    with col5:
                        if st.button("❌", key=f"remove_{symbol}"):
                            st.session_state.watchlist.remove(symbol)
                            st.rerun()
                    st.divider()
            except:
                st.warning(f"لا يمكن تحميل بيانات {symbol}")

# ==================== ALERTS ====================
elif page == "🔔 التنبيهات":
    st.header("🔔 مركز التنبيهات الذكية")

    alert_engine = st.session_state.alert_engine

    # Update alerts for watchlist
    if st.button("🔄 تحديث التنبيهات", type="primary"):
        with st.spinner("جاري مسح الأسهم..."):
            for symbol in st.session_state.watchlist:
                alert_engine.add_to_watchlist(symbol)
            results = alert_engine.scan_watchlist()

            total = sum(len(v) for v in results.values())
            st.success(f"تم العثور على {total} إشارة جديدة!")

    # Display alerts
    recent = alert_engine.get_recent_alerts(24)

    if recent:
        st.subheader(f"التنبيهات الأخيرة ({len(recent)})")

        for alert in sorted(recent, key=lambda x: x.priority.value, reverse=True):
            priority_class = "alert-high" if "عالي" in alert.priority.value else "alert-medium" if "متوسط" in alert.priority.value else "alert-low"

            with st.container():
                st.markdown(f"""
                <div class='{priority_class}'>
                    <strong>{alert.symbol}</strong> - {alert.signal.value} | {alert.priority.value}<br>
                    <small>{alert.timestamp} | السعر: {alert.price:.2f}</small><br>
                    {alert.message}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("لا توجد تنبيهات حالياً. أضف أسماً إلى قائمة المراقبة واضغط تحديث.")

    # Summary
    summary = alert_engine.get_alert_summary()
    if summary['total'] > 0:
        st.divider()
        st.subheader("📊 إحصائيات التنبيهات")
        c1, c2 = st.columns(2)
        with c1:
            st.json(summary['by_signal'])
        with c2:
            st.json(summary['by_priority'])

# ==================== ABOUT ====================
elif page == "ℹ️ حول":
    st.header("ℹ️ حول المنصة")

    st.markdown(f"""
    ### {APP_NAME} {APP_VERSION}

    **EGX Pro Terminal** هي منصة تحليل فني احترافية مفتوحة المصدر مخصصة للبورصة المصرية.

    #### المميزات:
    - تحليل فني متقدم بأكثر من 10 مؤشرات
    - تنبيهات آلية ذكية
    - رسوم بيانية تفاعلية
    - دعم كامل للعربية

    #### التقنيات:
    - Python 3.10+
    - Streamlit
    - Plotly
    - TA-Lib (Technical Analysis)
    - Yahoo Finance API

    #### التحذير:
    > **البيانات والتحليلات المعروضة هي للأغراض التعليمية والبحثية فقط.**
    > **لا تعتبر نصيحة استثمارية. يجب استشارة مستشار مالي مرخص قبل اتخاذ أي قرار استثماري.**

    ---
    **المطور:** {APP_AUTHOR}  
    **الترخيص:** MIT License  
    **آخر تحديث:** مايو 2026
    """)

# Footer
st.sidebar.divider()
st.sidebar.caption(f"© 2026 {APP_NAME} | MIT License")
st.sidebar.caption("البيانات للأغراض التعليمية فقط")
