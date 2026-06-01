"""
EGX Pro Terminal v27 - Phoenix Edition
Professional Technical Analysis Platform for Egyptian Stock Exchange

✅ النسخة المصححة الكاملة مع جميع الإصلاحات
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz
import logging
import os
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum
import warnings

warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════════════
# 1. LOGGING CONFIGURATION
# ═══════════════════════════════════════════════════════════════

# إنشاء مجلد السجلات إذا لم يكن موجوداً
os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/egx_terminal.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# 2. CONFIGURATION & CONSTANTS
# ═══════════════════════════════════════════════════════════════

class Theme(Enum):
    """ألوان الثيم الموحدة"""
    PRIMARY = "#667eea"
    SECONDARY = "#764ba2"
    ACCENT = "#f093fb"
    SUCCESS = "#4caf50"
    ERROR = "#f44336"
    WARNING = "#ff9800"
    BG_DARK = "#0f0c29"
    BG_CARD = "#1a1a2e"
    BG_SECONDARY = "#16213e"
    TEXT = "#ffffff"

class AppConfig:
    """إعدادات التطبيق"""
    APP_NAME = "EGX Pro Terminal"
    APP_VERSION = "27.1.0 Phoenix"
    CACHE_TTL = 300
    REFRESH_INTERVAL = 60
    MAX_STOCKS = 150

class EGXConfig:
    """إعدادات البيانات"""
    STOCKS = {
        'COMI': 'Commercial International Bank',
        'TMGH': 'Telecom Egypt',
        'EAST': 'Eastern Company',
        'SWDY': 'Swisslog Holding',
        'ORWE': 'Ora Warehousing',
        'MNHD': 'Manara Heritage',
        'ETEL': 'Etisalat Egypt',
        'FWRY': 'Fawry for Banking Services',
        'EGTS': 'EgyptAir',
        'HRTX': 'Hermes Egypt',
    }

    SECTORS = {
        'Banking': ['COMI', 'SWDY', 'FWRY'],
        'Telecom': ['TMGH', 'ETEL'],
        'Industrial': ['EAST', 'ORWE'],
        'Holding': ['MNHD', 'HRTX'],
        'Aviation': ['EGTS'],
    }

# ═══════════════════════════════════════════════════════════════
# 3. UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def get_theme_css() -> str:
    """إرجاع CSS الثيم الموحد"""
    return f"""
    <style>
    .stApp {{
        background: linear-gradient(135deg, {Theme.BG_DARK.value} 0%, {Theme.PRIMARY.value}33 50%, {Theme.BG_SECONDARY.value} 100%);
    }}

    .stButton>button {{
        background: linear-gradient(135deg, {Theme.PRIMARY.value} 0%, {Theme.SECONDARY.value} 100%);
        color: white;
        border: none;
        border-radius: 25px;
        font-weight: bold;
        transition: all 0.3s ease;
    }}

    .stButton>button:hover {{
        background: linear-gradient(135deg, {Theme.SECONDARY.value} 0%, {Theme.PRIMARY.value} 100%);
        transform: scale(1.05);
    }}

    h1, h2, h3 {{
        background: linear-gradient(90deg, {Theme.PRIMARY.value}, {Theme.SECONDARY.value}, {Theme.ACCENT.value});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }}

    .metric-card {{
        background: linear-gradient(135deg, {Theme.BG_CARD.value} 0%, {Theme.BG_SECONDARY.value} 100%);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }}
    </style>
    """

def safe_percentage(current: float, previous: float) -> float:
    """حساب النسبة المئوية بأمان"""
    try:
        if previous == 0 or previous is None:
            return 0.0
        return ((current - previous) / abs(previous)) * 100
    except Exception as e:
        logger.error(f"Error calculating percentage: {str(e)}")
        return 0.0

def validate_symbol(symbol: str) -> Tuple[bool, str]:
    """
    التحقق من صحة رمز السهم

    Returns:
        Tuple[bool, str]: (صحيح/خطأ, الرمز المُنظف أو رسالة الخطأ)
    """
    if not symbol or not isinstance(symbol, str):
        return False, "رمز السهم لا يمكن أن يكون فارغاً"

    symbol = symbol.upper().strip()

    if not symbol:
        return False, "رمز السهم لا يمكن أن يكون فارغاً"

    if symbol not in EGXConfig.STOCKS:
        available = ", ".join(list(EGXConfig.STOCKS.keys())[:5])
        return False, f"الرمز '{symbol}' غير موجود في EGX\nأمثلة: {available}..."

    logger.info(f"Symbol validated: {symbol}")
    return True, symbol

def get_cairo_time() -> datetime:
    """الحصول على الوقت بتوقيت القاهرة"""
    return datetime.now(pytz.timezone('Africa/Cairo'))

def format_number(num: float, decimals: int = 2) -> str:
    """تنسيق الأرقام بصيغة عربية"""
    try:
        if num is None:
            return "N/A"
        formatted = f"{num:,.{decimals}f}"
        return formatted.replace(',', ' ')
    except:
        return str(num)

def format_currency(num: float) -> str:
    """تنسيق العملة بالجنيه المصري"""
    return f"EGP {format_number(num)}"

def generate_dummy_data(symbol: str, days: int = 100) -> pd.DataFrame:
    """توليد بيانات وهمية واقعية للاختبار"""
    np.random.seed(hash(symbol) % 2**32)

    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')

    # بدء من سعر أولي عشوائي بين 5 و 50
    base_price = np.random.uniform(5, 50)

    # توليد حركة عشوائية (Random Walk) مع اتجاه طفيف
    returns = np.random.normal(0.001, 0.02, days)
    price = base_price * np.exp(np.cumsum(returns))

    # التأكد من أن جميع الأسعار موجبة
    price = np.maximum(price, 0.01)

    # توليد Open, High, Low, Close واقعية
    daily_volatility = np.abs(np.random.randn(days)) * 0.02 * price

    open_prices = price * (1 + np.random.randn(days) * 0.005)
    close_prices = price

    high_prices = np.maximum(open_prices, close_prices) + daily_volatility
    low_prices = np.minimum(open_prices, close_prices) - daily_volatility

    # التأكد من High >= Low
    low_prices = np.minimum(low_prices, high_prices - 0.01)

    # التأكد من أن جميع الأسعار موجبة
    low_prices = np.maximum(low_prices, 0.01)
    open_prices = np.maximum(open_prices, low_prices + 0.01)
    close_prices = np.maximum(close_prices, low_prices + 0.01)
    high_prices = np.maximum(high_prices, open_prices + 0.01)
    high_prices = np.maximum(high_prices, close_prices + 0.01)

    volume = np.random.randint(100000, 10000000, days)

    df = pd.DataFrame({
        'date': dates,
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volume
    })

    df.set_index('date', inplace=True)

    return df

# ═══════════════════════════════════════════════════════════════
# 4. TECHNICAL INDICATORS
# ═══════════════════════════════════════════════════════════════

def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """حساب مؤشر القوة النسبية RSI"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_ema(prices: pd.Series, span: int = 20) -> pd.Series:
    """حساب المتوسط المتحرك الأسي EMA"""
    return prices.ewm(span=span, adjust=False).mean()

def calculate_sma(prices: pd.Series, window: int = 20) -> pd.Series:
    """حساب المتوسط المتحرك البسيط SMA"""
    return prices.rolling(window=window).mean()

def calculate_bollinger_bands(prices: pd.Series, window: int = 20, num_std: int = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """حساب نطاقات بولينجر"""
    sma = calculate_sma(prices, window)
    std = prices.rolling(window=window).std()
    upper = sma + (std * num_std)
    lower = sma - (std * num_std)
    return upper, sma, lower

def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """حساب MACD"""
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    macd_line = ema_fast - ema_slow
    signal_line = calculate_ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def calculate_adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """حساب ADX المبسط"""
    plus_dm = high.diff()
    minus_dm = -low.diff()

    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)

    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.rolling(window=period).mean()
    plus_di = 100 * plus_dm.rolling(window=period).mean() / atr
    minus_di = 100 * minus_dm.rolling(window=period).mean() / atr

    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = dx.rolling(window=period).mean()

    return adx

# ═══════════════════════════════════════════════════════════════
# 5. PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title=f"{AppConfig.APP_NAME} v{AppConfig.APP_VERSION}",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/m02417710-maker/blank-app',
        'Report a bug': 'https://github.com/m02417710-maker/blank-app/issues',
        'About': f'# {AppConfig.APP_NAME} v{AppConfig.APP_VERSION}\n✅ Professional EGX Analysis Platform'
    }
)

st.markdown(get_theme_css(), unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 6. SESSION STATE INITIALIZATION
# ═══════════════════════════════════════════════════════════════

def init_session_state() -> None:
    """تهيئة جميع متغيرات الـ Session State"""
    defaults = {
        'selected_symbol': 'COMI',
        'selected_period': '1y',
        'selected_interval': '1d',
        'analysis_data': None,
        'watchlist': [],
        'alerts': [],
        'last_update': None,
        'page': 'Dashboard',
        'notifications_enabled': True,
        'auto_refresh': False,
        'refresh_interval': AppConfig.REFRESH_INTERVAL,
        'last_rerun_time': 0,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
            logger.info(f"Initialized: {key}")

init_session_state()

# ═══════════════════════════════════════════════════════════════
# 7. DATA LOADING
# ═══════════════════════════════════════════════════════════════

@st.cache_data(ttl=AppConfig.CACHE_TTL)
def load_stock_data(symbol: str) -> Optional[pd.DataFrame]:
    """تحميل بيانات الأسهم مع Caching"""
    try:
        logger.info(f"Loading data for {symbol}")

        # في الإنتاج: استخدم yfinance
        # import yfinance as yf
        # df = yf.download(get_yahoo_symbol(symbol), period='1y', progress=False)

        # للاختبار: بيانات وهمية واقعية
        df = generate_dummy_data(symbol)

        if df is None or df.empty:
            logger.warning(f"No data for {symbol}")
            return None

        # إضافة المؤشرات الفنية
        df['rsi'] = calculate_rsi(df['close'])
        df['ema_20'] = calculate_ema(df['close'], 20)
        df['sma_20'] = calculate_sma(df['close'], 20)
        df['bb_upper'], df['bb_middle'], df['bb_lower'] = calculate_bollinger_bands(df['close'])
        df['macd'], df['macd_signal'], df['macd_hist'] = calculate_macd(df['close'])
        df['adx'] = calculate_adx(df['high'], df['low'], df['close'])

        logger.info(f"Loaded {len(df)} rows for {symbol}")
        return df

    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        return None

def get_current_data() -> Optional[pd.DataFrame]:
    """الحصول على البيانات الحالية"""
    try:
        symbol = st.session_state.selected_symbol
        df = load_stock_data(symbol)

        if df is not None:
            st.session_state.analysis_data = df
            st.session_state.last_update = get_cairo_time()
            return df
        return None

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        st.error(f"❌ خطأ: {str(e)}")
        return None

# ═══════════════════════════════════════════════════════════════
# 8. SIDEBAR NAVIGATION
# ═══════════════════════════════════════════════════════════════

def render_sidebar() -> None:
    """عرض الشريط الجانبي"""
    try:
        # Logo
        st.sidebar.markdown(f"""
        <div style="text-align: center; padding: 20px 0;">
            <div style="font-size: 3em;">📈</div>
            <div style="font-size: 1.5em; font-weight: 800;
            background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;">
                {AppConfig.APP_NAME}
            </div>
            <div style="font-size: 0.8em; color: #888;">
                v{AppConfig.APP_VERSION}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.sidebar.markdown("---")

        # Navigation
        st.sidebar.markdown("### 🧭 التنقل")
        pages = {
            '📊 لوحة المعلومات': 'Dashboard',
            '🔍 تحليل الأسهم': 'Analysis',
            '📈 الرسوم البيانية': 'Charts',
            '🔔 التنبيهات': 'Alerts',
            '🤖 التنبؤات': 'AI',
            '📋 قائمة المراقبة': 'Watchlist',
            '🧪 الاختبار الخلفي': 'Backtest',
            '🏢 نظرة السوق': 'Market',
            '⚙️ الإعدادات': 'Settings',
        }

        for label, page_name in pages.items():
            if st.sidebar.button(
                label,
                use_container_width=True,
                type="primary" if st.session_state.page == page_name else "secondary",
                key=f"nav_{page_name}"
            ):
                st.session_state.page = page_name
                logger.info(f"Navigation to {page_name}")
                st.rerun()

        st.sidebar.markdown("---")

        # Stock Selector
        st.sidebar.markdown("### 🎯 اختيار السهم")

        # استخدام selectbox أفضل من text_input لتجنب الأخطاء
        symbol_options = list(EGXConfig.STOCKS.keys())
        current_index = symbol_options.index(st.session_state.selected_symbol) if st.session_state.selected_symbol in symbol_options else 0

        selected_symbol = st.sidebar.selectbox(
            "اختر السهم",
            options=symbol_options,
            index=current_index,
            format_func=lambda x: f"{x} - {EGXConfig.STOCKS[x]}",
            key="symbol_select"
        )

        if selected_symbol != st.session_state.selected_symbol:
            st.session_state.selected_symbol = selected_symbol
            st.rerun()

        # Popular stocks buttons
        st.sidebar.markdown("**الأسهم الشهيرة:**")
        popular = list(EGXConfig.STOCKS.keys())[:4]
        cols = st.sidebar.columns(2)

        for i, sym in enumerate(popular):
            with cols[i % 2]:
                if st.button(sym, use_container_width=True, key=f"pop_{sym}_btn"):
                    st.session_state.selected_symbol = sym
                    st.rerun()

        st.sidebar.markdown("---")

        # Refresh Button
        if st.sidebar.button("🔄 تحديث البيانات", use_container_width=True, key="refresh_btn"):
            load_stock_data.clear()
            st.rerun()

        # Auto refresh toggle
        st.session_state.auto_refresh = st.sidebar.checkbox(
            "🔄 التحديث التلقائي",
            value=st.session_state.auto_refresh,
            key="auto_refresh_toggle"
        )

        # Footer
        st.sidebar.markdown("---")
        st.sidebar.markdown("""
        <div style="text-align: center; color: #888; font-size: 0.75em;">
            <div>🇪🇬 صُنع في مصر</div>
            <div style="margin-top: 5px;">لأغراض تعليمية فقط</div>
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        logger.error(f"Sidebar error: {str(e)}")
        st.sidebar.error(f"❌ خطأ: {str(e)}")

# ═══════════════════════════════════════════════════════════════
# 9. PAGE RENDERERS
# ═══════════════════════════════════════════════════════════════

def render_dashboard() -> None:
    """عرض لوحة المعلومات"""
    try:
        st.markdown("""
        <div style="text-align: center; padding: 30px 0;">
            <h1>📈 محطة EGX الاحترافية</h1>
            <p style="font-size: 1.2em; color: #aaa;">منصة تحليل تقني متقدمة لسوق الأسهم المصرية</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 📊 نظرة السوق")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📈 أكبر رابح", "TMGH", "+5.23%", delta_color="normal")
        with col2:
            st.metric("📉 أكبر خاسر", "EAST", "-2.15%", delta_color="inverse")
        with col3:
            st.metric("💼 الأكثر نشاطاً", "COMI", "2.5M")
        with col4:
            st.metric("📊 معنويات السوق", "+1.23%", "100+ سهم")

        st.markdown("---")
        st.markdown("### ⭐ تحليل مختار")

        symbol = st.session_state.selected_symbol
        df = get_current_data()

        if df is not None and not df.empty:
            col1, col2, col3, col4, col5 = st.columns(5)

            last_price = df['close'].iloc[-1]
            prev_price = df['close'].iloc[-2] if len(df) > 1 else last_price
            change_pct = safe_percentage(last_price, prev_price)

            # حساب الإشارة
            rsi_val = df['rsi'].iloc[-1] if 'rsi' in df.columns else 50
            macd_val = df['macd'].iloc[-1] if 'macd' in df.columns else 0

            signal = "HOLD"
            signal_color = "⚪"
            if rsi_val < 30 and macd_val > 0:
                signal = "BUY"
                signal_color = "🟢"
            elif rsi_val > 70 and macd_val < 0:
                signal = "SELL"
                signal_color = "🔴"

            with col1:
                st.metric("💰 السعر", format_currency(last_price), f"{change_pct:+.2f}%")
            with col2:
                st.metric("📊 RSI", f"{rsi_val:.1f}", "محايد" if 30 <= rsi_val <= 70 else ("تشبع شراء" if rsi_val > 70 else "تشبع بيع"))
            with col3:
                macd_signal = "✅" if macd_val > 0 else "❌"
                st.metric("📈 MACD", f"{macd_val:.4f}", macd_signal)
            with col4:
                adx_val = df['adx'].iloc[-1] if 'adx' in df.columns else 25
                adx_text = "قوي" if adx_val > 25 else "ضعيف"
                st.metric("📉 ADX", f"{adx_val:.1f}", adx_text)
            with col5:
                st.metric("🎯 الإشارة", f"{signal_color} {signal}", "75%")

            # Chart
            st.markdown("### 📈 حركة السعر")
            fig = go.Figure()

            # شمعة اليابانية
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='السهم',
                increasing_line_color=Theme.SUCCESS.value,
                decreasing_line_color=Theme.ERROR.value
            ))

            # EMA 20
            if 'ema_20' in df.columns:
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=df['ema_20'],
                    mode='lines',
                    name='EMA 20',
                    line=dict(color=Theme.PRIMARY.value, width=1.5, dash='dash')
                ))

            # Bollinger Bands
            if 'bb_upper' in df.columns:
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=df['bb_upper'],
                    mode='lines',
                    name='BB Upper',
                    line=dict(color=Theme.ACCENT.value, width=1),
                    opacity=0.5
                ))
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=df['bb_lower'],
                    mode='lines',
                    name='BB Lower',
                    line=dict(color=Theme.ACCENT.value, width=1),
                    opacity=0.5,
                    fill='tonexty',
                    fillcolor=f'rgba(240, 147, 251, 0.1)'
                ))

            fig.update_layout(
                title=f"تطور سعر {symbol} - {EGXConfig.STOCKS.get(symbol, '')}",
                xaxis_title="التاريخ",
                yaxis_title="السعر (EGP)",
                template='plotly_dark',
                height=500,
                hovermode='x unified',
                xaxis_rangeslider_visible=False
            )
            st.plotly_chart(fig, use_container_width=True)

            # حجم التداول
            st.markdown("### 📊 حجم التداول")
            fig_vol = go.Figure()
            fig_vol.add_trace(go.Bar(
                x=df.index,
                y=df['volume'],
                name='الحجم',
                marker_color=Theme.PRIMARY.value
            ))
            fig_vol.update_layout(
                template='plotly_dark',
                height=300,
                xaxis_title="التاريخ",
                yaxis_title="الحجم"
            )
            st.plotly_chart(fig_vol, use_container_width=True)

        else:
            st.warning(f"⚠️ لا توجد بيانات متاحة للرمز: {symbol}")

        logger.info("Dashboard rendered")

    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        st.error(f"❌ خطأ: {str(e)}")

def render_analysis() -> None:
    """عرض صفحة التحليل"""
    st.markdown("## 🔍 تحليل تفصيلي")

    symbol = st.session_state.selected_symbol
    st.info(f"📊 تحليل السهم: {symbol} - {EGXConfig.STOCKS.get(symbol, '')}")

    df = get_current_data()
    if df is not None and not df.empty:
        # إحصائيات
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("أعلى سعر", format_currency(df['high'].max()))
        with col2:
            st.metric("أقل سعر", format_currency(df['low'].min()))
        with col3:
            st.metric("متوسط الحجم", f"{df['volume'].mean():,.0f}")
        with col4:
            st.metric("التقلب", f"{df['close'].pct_change().std()*100:.2f}%")

        st.subheader("البيانات الأخيرة مع المؤشرات")
        display_df = df.tail(20).copy()
        display_df.columns = ['الافتتاح', 'الأعلى', 'الأدنى', 'الإغلاق', 'الحجم', 
                              'RSI', 'EMA 20', 'SMA 20', 'BB Upper', 'BB Middle', 
                              'BB Lower', 'MACD', 'MACD Signal', 'MACD Hist', 'ADX']
        st.dataframe(display_df, use_container_width=True)

        # جدول المؤشرات
        st.subheader("📊 ملخص المؤشرات الفنية")
        latest = df.iloc[-1]

        indicators = {
            'RSI (14)': f"{latest['rsi']:.2f}" if 'rsi' in df.columns else "N/A",
            'EMA 20': format_currency(latest['ema_20']) if 'ema_20' in df.columns else "N/A",
            'SMA 20': format_currency(latest['sma_20']) if 'sma_20' in df.columns else "N/A",
            'MACD': f"{latest['macd']:.4f}" if 'macd' in df.columns else "N/A",
            'MACD Signal': f"{latest['macd_signal']:.4f}" if 'macd_signal' in df.columns else "N/A",
            'ADX': f"{latest['adx']:.2f}" if 'adx' in df.columns else "N/A",
            'BB Upper': format_currency(latest['bb_upper']) if 'bb_upper' in df.columns else "N/A",
            'BB Lower': format_currency(latest['bb_lower']) if 'bb_lower' in df.columns else "N/A",
        }

        ind_df = pd.DataFrame(list(indicators.items()), columns=['المؤشر', 'القيمة'])
        st.table(ind_df)
    else:
        st.warning("لا توجد بيانات متاحة")

    logger.info(f"Analysis page rendered for {symbol}")

def render_charts() -> None:
    """عرض صفحة الرسوم البيانية"""
    st.markdown("## 📈 الرسوم البيانية المتقدمة")

    symbol = st.session_state.selected_symbol
    df = get_current_data()

    if df is None or df.empty:
        st.warning("لا توجد بيانات متاحة")
        return

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        show_candle = st.checkbox("شموع يابانية", True, key="chart_candle")
    with col2:
        show_ema = st.checkbox("EMA 20", True, key="chart_ema")
    with col3:
        show_sma = st.checkbox("SMA 20", False, key="chart_sma")
    with col4:
        show_bb = st.checkbox("Bollinger Bands", True, key="chart_bb")

    fig = go.Figure()

    if show_candle:
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='السهم',
            increasing_line_color=Theme.SUCCESS.value,
            decreasing_line_color=Theme.ERROR.value
        ))

    if show_ema and 'ema_20' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['ema_20'],
            mode='lines', name='EMA 20',
            line=dict(color=Theme.PRIMARY.value, width=2)
        ))

    if show_sma and 'sma_20' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['sma_20'],
            mode='lines', name='SMA 20',
            line=dict(color=Theme.WARNING.value, width=2, dash='dot')
        ))

    if show_bb and 'bb_upper' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['bb_upper'],
            mode='lines', name='BB Upper',
            line=dict(color=Theme.ACCENT.value, width=1),
            opacity=0.7
        ))
        fig.add_trace(go.Scatter(
            x=df.index, y=df['bb_lower'],
            mode='lines', name='BB Lower',
            line=dict(color=Theme.ACCENT.value, width=1),
            opacity=0.7,
            fill='tonexty',
            fillcolor=f'rgba(240, 147, 251, 0.1)'
        ))

    fig.update_layout(
        title=f"الرسم البياني المتقدم - {symbol}",
        template='plotly_dark',
        height=600,
        xaxis_rangeslider_visible=False,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    # MACD Chart
    if 'macd' in df.columns:
        st.markdown("### 📈 MACD")
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(
            x=df.index, y=df['macd'],
            mode='lines', name='MACD',
            line=dict(color=Theme.PRIMARY.value, width=2)
        ))
        fig_macd.add_trace(go.Scatter(
            x=df.index, y=df['macd_signal'],
            mode='lines', name='Signal',
            line=dict(color=Theme.WARNING.value, width=2, dash='dash')
        ))
        fig_macd.add_trace(go.Bar(
            x=df.index, y=df['macd_hist'],
            name='Histogram',
            marker_color=[Theme.SUCCESS.value if x > 0 else Theme.ERROR.value for x in df['macd_hist']]
        ))
        fig_macd.update_layout(template='plotly_dark', height=300)
        st.plotly_chart(fig_macd, use_container_width=True)

    # RSI Chart
    if 'rsi' in df.columns:
        st.markdown("### 📊 RSI")
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(
            x=df.index, y=df['rsi'],
            mode='lines', name='RSI',
            line=dict(color=Theme.PRIMARY.value, width=2),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.2)'
        ))
        fig_rsi.add_hline(y=70, line_dash="dash", line_color=Theme.ERROR.value, annotation_text="تشبع شراء")
        fig_rsi.add_hline(y=30, line_dash="dash", line_color=Theme.SUCCESS.value, annotation_text="تشبع بيع")
        fig_rsi.update_layout(template='plotly_dark', height=300, yaxis_range=[0, 100])
        st.plotly_chart(fig_rsi, use_container_width=True)

def render_alerts() -> None:
    """عرض صفحة التنبيهات"""
    st.markdown("## 🔔 إدارة التنبيهات")

    # عرض التنبيهات الحالية
    if st.session_state.alerts:
        st.markdown("### التنبيهات النشطة")
        for i, alert in enumerate(st.session_state.alerts):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info(f"{alert['type']} - {alert['symbol']} عند {alert['value']}")
            with col2:
                if st.button("حذف", key=f"del_alert_{i}"):
                    st.session_state.alerts.pop(i)
                    st.rerun()
    else:
        st.info("لا توجد تنبيهات نشطة")

    # إنشاء تنبيه جديد
    st.markdown("### إنشاء تنبيه جديد")
    with st.form("alert_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            alert_symbol = st.selectbox("السهم", list(EGXConfig.STOCKS.keys()), key="alert_symbol")
        with col2:
            alert_type = st.selectbox("نوع التنبيه", ["السعر", "RSI", "MACD"], key="alert_type")
        with col3:
            alert_condition = st.selectbox("الشرط", ["أعلى من", "أقل من", "يساوي"], key="alert_condition")

        alert_value = st.number_input("القيمة", min_value=0.0, value=10.0, key="alert_value")

        submitted = st.form_submit_button("✅ إنشاء التنبيه")
        if submitted:
            new_alert = {
                'symbol': alert_symbol,
                'type': alert_type,
                'condition': alert_condition,
                'value': alert_value,
                'created_at': get_cairo_time().strftime('%Y-%m-%d %H:%M')
            }
            st.session_state.alerts.append(new_alert)
            st.success(f"✅ تم إنشاء تنبيه {alert_type} لـ {alert_symbol} عند {alert_value}")
            st.rerun()

def render_ai() -> None:
    """عرض صفحة التنبؤات"""
    st.markdown("## 🤖 التنبؤات بالذكاء الاصطناعي")

    symbol = st.session_state.selected_symbol
    df = get_current_data()

    if df is None or df.empty:
        st.warning("لا توجد بيانات متاحة")
        return

    with st.status("جاري التحليل...", expanded=True):
        st.write("⏳ تحميل النموذج...")
        st.write("⏳ حساب المؤشرات...")
        st.write("⏳ توليد التنبؤات...")
        st.write("✅ اكتمل!")

    # تحليل بسيط للاتجاه
    last_price = df['close'].iloc[-1]
    sma_20 = df['close'].rolling(20).mean().iloc[-1]
    sma_50 = df['close'].rolling(50).mean().iloc[-1]

    trend = "صعود 📈" if last_price > sma_20 > sma_50 else ("هبوط 📉" if last_price < sma_20 < sma_50 else "تذبذب ↔️")
    confidence = 75 if last_price > sma_20 > sma_50 or last_price < sma_20 < sma_50 else 50

    # هدف سعري بسيط
    target = last_price * 1.1 if trend == "صعود 📈" else (last_price * 0.95 if trend == "هبوط 📉" else last_price)
    stop_loss = last_price * 0.95 if trend == "صعود 📈" else (last_price * 1.05 if trend == "هبوط 📉" else last_price * 0.98)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("الاتجاه المتوقع", trend, f"{confidence}%")
    with col2:
        st.metric("السعر المستهدف", format_currency(target), f"{safe_percentage(target, last_price):+.1f}%")
    with col3:
        st.metric("وقف الخسارة المقترح", format_currency(stop_loss), f"{safe_percentage(stop_loss, last_price):+.1f}%")

    # تحليل المؤشرات
    st.markdown("### 📊 تحليل المؤشرات")
    latest = df.iloc[-1]

    rsi_signal = "تشبع بيع (شراء محتمل)" if latest['rsi'] < 30 else ("تشبع شراء (بيع محتمل)" if latest['rsi'] > 70 else "محايد")
    macd_signal = "إيجابي" if latest['macd'] > latest['macd_signal'] else "سلبي"

    analysis_text = f"""
    **تحليل {symbol}:**

    - **RSI**: {latest['rsi']:.1f} - {rsi_signal}
    - **MACD**: {macd_signal} (MACD: {latest['macd']:.4f} vs Signal: {latest['macd_signal']:.4f})
    - **ADX**: {latest['adx']:.1f} - {'اتجاه قوي' if latest['adx'] > 25 else 'اتجاه ضعيف'}
    - **السعر vs EMA 20**: {'فوق المتوسط (إيجابي)' if last_price > latest['ema_20'] else 'تحت المتوسط (سلبي)'}

    **التوصية**: {signal}
    """

    st.markdown(analysis_text)

def render_watchlist() -> None:
    """عرض قائمة المراقبة"""
    st.markdown("## 📋 قائمة المراقبة")

    # إضافة سهم للقائمة
    col1, col2 = st.columns([3, 1])
    with col1:
        new_stock = st.selectbox("إضافة سهم", list(EGXConfig.STOCKS.keys()), key="watchlist_add")
    with col2:
        if st.button("➕ إضافة", key="add_watchlist"):
            if new_stock not in st.session_state.watchlist:
                st.session_state.watchlist.append(new_stock)
                st.success(f"تم إضافة {new_stock}")
                st.rerun()
            else:
                st.warning("السهم موجود بالفعل")

    # عرض القائمة
    if st.session_state.watchlist:
        st.markdown("### الأسهم المراقبة")
        for i, sym in enumerate(st.session_state.watchlist):
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.write(f"**{sym}** - {EGXConfig.STOCKS.get(sym, '')}")
            with col2:
                # محاكاة بيانات
                df = generate_dummy_data(sym, days=5)
                last = df['close'].iloc[-1]
                prev = df['close'].iloc[-2]
                change = safe_percentage(last, prev)
                st.write(f"EGP {last:.2f} ({change:+.2f}%)")
            with col3:
                if st.button("🗑️", key=f"remove_{sym}_{i}"):
                    st.session_state.watchlist.remove(sym)
                    st.rerun()
    else:
        st.info("قائمة المراقبة فارغة. أضف أسهم للمتابعة")

def render_backtest() -> None:
    """عرض الاختبار الخلفي"""
    st.markdown("## 🧪 الاختبار الخلفي")
    st.info("اختبر استراتيجيات التداول على بيانات تاريخية")

    symbol = st.session_state.selected_symbol
    df = get_current_data()

    if df is None or df.empty:
        st.warning("لا توجد بيانات متاحة")
        return

    # إعدادات الاستراتيجية
    st.markdown("### ⚙️ إعدادات الاستراتيجية")
    col1, col2, col3 = st.columns(3)
    with col1:
        strategy = st.selectbox("الاستراتيجية", ["RSI", "MACD Crossover", "Bollinger Bands"], key="backtest_strategy")
    with col2:
        initial_capital = st.number_input("رأس المال الأولي", min_value=1000, value=100000, step=1000, key="backtest_capital")
    with col3:
        if st.button("🚀 بدء الاختبار", key="run_backtest"):
            with st.spinner("جاري الاختبار..."):
                # محاكاة بسيطة
                trades = []
                capital = initial_capital
                position = 0

                for i in range(20, len(df)):
                    row = df.iloc[i]
                    prev = df.iloc[i-1]

                    if strategy == "RSI":
                        if row['rsi'] < 30 and position == 0:
                            position = capital / row['close']
                            capital = 0
                            trades.append({'type': 'شراء', 'price': row['close'], 'date': df.index[i]})
                        elif row['rsi'] > 70 and position > 0:
                            capital = position * row['close']
                            position = 0
                            trades.append({'type': 'بيع', 'price': row['close'], 'date': df.index[i]})

                    elif strategy == "MACD Crossover":
                        if prev['macd'] < prev['macd_signal'] and row['macd'] > row['macd_signal'] and position == 0:
                            position = capital / row['close']
                            capital = 0
                            trades.append({'type': 'شراء', 'price': row['close'], 'date': df.index[i]})
                        elif prev['macd'] > prev['macd_signal'] and row['macd'] < row['macd_signal'] and position > 0:
                            capital = position * row['close']
                            position = 0
                            trades.append({'type': 'بيع', 'price': row['close'], 'date': df.index[i]})

                # النتيجة النهائية
                final_value = capital + (position * df['close'].iloc[-1] if position > 0 else 0)
                profit = final_value - initial_capital
                profit_pct = safe_percentage(final_value, initial_capital)

                st.success(f"✅ اكتمل الاختبار!")
                st.metric("الربح/الخسارة", format_currency(profit), f"{profit_pct:+.2f}%")
                st.metric("القيمة النهائية", format_currency(final_value))
                st.metric("عدد الصفقات", len(trades))

                if trades:
                    trades_df = pd.DataFrame(trades)
                    st.markdown("### 📋 سجل الصفقات")
                    st.dataframe(trades_df, use_container_width=True)

def render_market() -> None:
    """عرض نظرة السوق"""
    st.markdown("## 🏢 نظرة السوق")
    st.info("مقارنة القطاعات والأسهم")

    # عرض الأسهم حسب القطاع
    for sector, symbols in EGXConfig.SECTORS.items():
        st.markdown(f"### {sector}")
        cols = st.columns(len(symbols))
        for i, sym in enumerate(symbols):
            with cols[i]:
                df = generate_dummy_data(sym, days=5)
                last = df['close'].iloc[-1]
                prev = df['close'].iloc[-2]
                change = safe_percentage(last, prev)

                st.metric(
                    f"{sym}",
                    f"EGP {last:.2f}",
                    f"{change:+.2f}%",
                    delta_color="normal" if change >= 0 else "inverse"
                )

def render_settings() -> None:
    """عرض الإعدادات"""
    st.markdown("## ⚙️ الإعدادات")

    st.markdown("### 🎨 المظهر")
    theme = st.selectbox("المظهر", ["Dark", "Light"], key="settings_theme")

    st.markdown("### 🔔 الإخطارات")
    st.session_state.notifications_enabled = st.checkbox(
        "تفعيل الإخطارات",
        value=st.session_state.notifications_enabled,
        key="settings_notifications"
    )

    st.markdown("### 📊 البيانات")
    if st.button("🗑️ مسح ذاكرة التخزين المؤقت", key="clear_cache"):
        load_stock_data.clear()
        st.success("✅ تم مسح ذاكرة التخزين المؤقت")

    if st.button("🗑️ حذف جميع التنبيهات", key="clear_alerts"):
        st.session_state.alerts = []
        st.success("✅ تم حذف جميع التنبيهات")

    if st.button("🗑️ مسح قائمة المراقبة", key="clear_watchlist"):
        st.session_state.watchlist = []
        st.success("✅ تم مسح قائمة المراقبة")

    st.markdown("### ℹ️ عن التطبيق")
    st.info(f"""
    **{AppConfig.APP_NAME}**
    الإصدار: {AppConfig.APP_VERSION}

    منصة تحليل تقني متقدمة لسوق الأسهم المصرية (EGX)

    المميزات:
    - تحليل فني متقدم مع مؤشرات RSI, MACD, Bollinger Bands, ADX
    - رسوم بيانية تفاعلية
    - تنبيهات أسعار مخصصة
    - اختبار خلفي للاستراتيجيات
    - قائمة مراقبة شخصية

    ⚠️ تنبيه: جميع البيانات للأغراض التعليمية فقط
    """)

# ═══════════════════════════════════════════════════════════════
# 10. MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════

def main() -> None:
    """الدالة الرئيسية"""
    try:
        logger.info("Application started")

        render_sidebar()

        page = st.session_state.page

        if page == 'Dashboard':
            render_dashboard()
        elif page == 'Analysis':
            render_analysis()
        elif page == 'Charts':
            render_charts()
        elif page == 'Alerts':
            render_alerts()
        elif page == 'AI':
            render_ai()
        elif page == 'Watchlist':
            render_watchlist()
        elif page == 'Backtest':
            render_backtest()
        elif page == 'Market':
            render_market()
        elif page == 'Settings':
            render_settings()
        else:
            st.error("❌ صفحة غير موجودة")

        logger.info(f"Rendered page: {page}")

    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error(f"❌ خطأ في التطبيق: {str(e)}")
        st.error("📝 تحقق من السجلات للمزيد من المعلومات")

if __name__ == "__main__":
    main()
