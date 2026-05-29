
                fig = chart_engine.create_sector_heatmap(
                    dict(zip(sector_perf['sector'], sector_perf['avg_change']))
                )
                st.plotly_chart(fig, use_container_width=True, key="sector_heatmap")
    except Exception as e:
        st.warning(f"Market overview temporarily unavailable: {e}")

    # Stock Comparison
    st.markdown("### 📈 Stock Comparison")
    comparison_symbols = st.multiselect(
        "Select stocks to compare",
        egx_config.TOP_STOCKS,
        default=st.session_state.comparison_symbols[:4],
        max_selections=8
    )

    if comparison_symbols:
        st.session_state.comparison_symbols = comparison_symbols

        comparison_data = {}
        for sym in comparison_symbols:
            sym_df = market_engine.fetch(sym, period='1y', interval='1d')
            if sym_df is not None and not sym_df.empty:
                comparison_data[sym] = sym_df

        if comparison_data:
            fig_comp = chart_engine.create_comparison_chart(comparison_data, normalize=True)
            st.plotly_chart(fig_comp, use_container_width=True, key="comparison_chart")

            # Correlation Matrix
            st.markdown("### 🔗 Correlation Matrix")
            corr_symbols = list(comparison_data.keys())
            if len(corr_symbols) >= 2:
                corr_matrix = market_engine.get_correlation_matrix(corr_symbols, period='1y')
                if not corr_matrix.empty:
                    fig_corr = chart_engine.create_correlation_heatmap(corr_matrix)
                    st.plotly_chart(fig_corr, use_container_width=True, key="correlation_matrix")

    # Top Performers
    st.markdown("### 🏆 Top Performers")
    try:
        if not quotes.empty:
            tabs = st.tabs(["Top Gainers", "Top Losers", "Most Active", "High Dividend"])

            with tabs[0]:
                gainers = quotes.nlargest(10, 'change_pct')[['symbol', 'price', 'change_pct', 'volume']]
                gainers.columns = ['Symbol', 'Price', 'Change %', 'Volume']
                st.dataframe(gainers, use_container_width=True, hide_index=True)

            with tabs[1]:
                losers = quotes.nsmallest(10, 'change_pct')[['symbol', 'price', 'change_pct', 'volume']]
                losers.columns = ['Symbol', 'Price', 'Change %', 'Volume']
                st.dataframe(losers, use_container_width=True, hide_index=True)

            with tabs[2]:
                active = quotes.nlargest(10, 'volume')[['symbol', 'price', 'change_pct', 'volume']]
                active.columns = ['Symbol', 'Price', 'Change %', 'Volume']
                st.dataframe(active, use_container_width=True, hide_index=True)

            with tabs[3]:
                div_stocks = get_high_dividend()
                div_data = []
                for sym in div_stocks[:10]:
                    info = get_stock_info(sym)
                    quote = market_engine.get_realtime_quote(sym)
                    if info and quote:
                        div_data.append({
                            'Symbol': sym,
                            'Price': quote['price'],
                            'Dividend Yield': f"{info.dividend_yield:.1f}%" if info.dividend_yield else 'N/A',
                            'P/E': f"{info.pe_ratio:.1f}" if info.pe_ratio else 'N/A',
                            'P/B': f"{info.pb_ratio:.1f}" if info.pb_ratio else 'N/A'
                        })
                if div_data:
                    st.dataframe(pd.DataFrame(div_data), use_container_width=True, hide_index=True)
    except Exception as e:
        st.info("Market data loading...")

def render_settings():
    st.markdown("## ⚙️ Settings")

    # Theme
    st.markdown("### 🎨 Appearance")
    theme = st.radio("Theme", ["Dark (Default)", "Light"], horizontal=True)

    # Language
    st.markdown("### 🌐 Language")
    lang = st.radio("Language", ["English", "العربية"], horizontal=True)

    # Default Indicators
    st.markdown("### 📊 Default Indicators")
    default_indicators = st.multiselect(
        "Show on charts by default",
        ['EMA 9', 'EMA 21', 'EMA 50', 'EMA 200', 'SMA 20', 'SMA 50', 'Bollinger Bands', 'VWAP'],
        default=['EMA 9', 'EMA 21', 'EMA 50']
    )

    # Data Settings
    st.markdown("### 💾 Data Settings")
    st.session_state.refresh_interval = st.slider(
        "Auto-refresh interval (seconds)", 30, 600,
        st.session_state.refresh_interval, 30
    )

    # Database
    st.markdown("### 🗄️ Database")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💾 Backup Database", use_container_width=True):
            path = local_storage.backup()
            if path:
                st.success(f"✅ Backup created: {path}")
            else:
                st.error("❌ Backup failed")
    with col2:
        if st.button("🧹 Vacuum Database", use_container_width=True):
            if local_storage.vacuum():
                st.success("✅ Database optimized")
            else:
                st.error("❌ Vacuum failed")
    with col3:
        if st.button("🗑️ Clear Old Data", use_container_width=True):
            if local_storage.clear_old_data(days=90):
                st.success("✅ Old data cleared")
            else:
                st.error("❌ Clear failed")

    # Database Stats
    try:
        stats = local_storage.get_stats()
        if stats:
            st.markdown("### 📊 Database Statistics")
            cols = st.columns(5)
            stat_items = [
                ("Watchlist", stats.get('watchlist', 0)),
                ("Alerts", stats.get('alerts', 0)),
                ("Backtests", stats.get('backtest_results', 0)),
                ("Predictions", stats.get('predictions', 0)),
                ("Size (MB)", stats.get('size_mb', 0))
            ]
            for (label, value), col in zip(stat_items, cols):
                with col:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="color: #888; font-size: 12px;">{label}</div>
                        <div style="color: #00d4ff; font-size: 24px; font-weight: bold;">{value}</div>
                    </div>
                    """, unsafe_allow_html=True)
    except Exception as e:
        st.info("Database statistics loading...")

    # About
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown(f"""
    **EGX Pro Terminal v{app_config.APP_VERSION}**

    - **Codename:** {app_config.APP_CODENAME}
    - **Description:** {app_config.APP_DESCRIPTION}
    - **Author:** {app_config.AUTHOR}
    - **License:** {app_config.LICENSE}

    **Features:**
    - 150+ Egyptian stocks with full sector classification
    - 20+ technical indicators (RSI, MACD, ADX, Bollinger Bands, Ichimoku, etc.)
    - Advanced pattern recognition (20+ candlestick patterns)
    - AI-powered predictions with Monte Carlo simulation
    - Multi-strategy backtesting with walk-forward analysis
    - Smart alert system with severity levels
    - Portfolio tracking and watchlist management
    - Sector performance analysis
    - Correlation matrix
    - Fibonacci retracement levels
    - Volume profile analysis

    **Disclaimer:** This platform is for educational purposes only. 
    It does not constitute investment advice. Always consult a licensed 
    financial advisor before making investment decisions.
    """)

# ═══════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════
def main():
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
        render_dashboard()

if __name__ == "__main__":
    main()
