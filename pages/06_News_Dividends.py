"""
EGX Pro Terminal - News & Dividends Page
"""

import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.news_dividends import news_engine, NewsCategory, NewsPriority
from data.egx_symbols import get_stock_info, get_all_symbols
import pandas as pd

st.set_page_config(page_title="News & Dividends", page_icon="📰", layout="wide")

st.title("📰 Market News & Dividends")

tab1, tab2, tab3 = st.tabs(["📰 News", "💰 Dividends", "📅 Calendar"])

with tab1:
    st.subheader("Latest Market News")

    # Filters
    col1, col2 = st.columns(2)
    with col1:
        filter_cat = st.selectbox("Category", 
            ["all", "earnings", "dividend", "ipo", "merger", "market_update", "economic", "sector_news"],
            key="news_cat_filter")
    with col2:
        filter_priority = st.selectbox("Priority", ["all", "high", "medium", "low"], key="news_prio_filter")

    news_items = news_engine.get_all_news(50)

    if filter_cat != "all":
        cat_map = {
            "earnings": NewsCategory.EARNINGS, "dividend": NewsCategory.DIVIDEND,
            "ipo": NewsCategory.IPO, "merger": NewsCategory.MERGER,
            "market_update": NewsCategory.MARKET_UPDATE, "economic": NewsCategory.ECONOMIC,
            "sector_news": NewsCategory.SECTOR_NEWS
        }
        news_items = [n for n in news_items if n.category == cat_map.get(filter_cat)]

    if filter_priority != "all":
        prio_map = {"high": NewsPriority.HIGH, "medium": NewsPriority.MEDIUM, "low": NewsPriority.LOW}
        news_items = [n for n in news_items if n.priority == prio_map.get(filter_priority)]

    for news in news_items:
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(news.priority.value, "⚪")
        time_ago = _time_ago(news.published_at)

        with st.expander(f"{priority_emoji} {news.title} [{time_ago}]"):
            st.write(news.content)
            st.caption(f"Source: {news.source} | Category: {news.category.value} | Published: {news.published_at.strftime('%Y-%m-%d %H:%M')}")
            if news.related_symbols:
                st.write(f"Related: {', '.join(news.related_symbols)}")

    # Market Summary
    st.subheader("📊 Market Summary")
    summary = news_engine.get_market_summary()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total News", summary["total_news"])
    with col2:
        st.metric("High Priority", summary["high_priority"])
    with col3:
        st.metric("Earnings", summary["earnings_reports"])
    with col4:
        st.metric("Dividends", summary["dividend_announcements"])

with tab2:
    st.subheader("💰 Dividend Distributions")

    dividends = news_engine.get_dividends()

    # Summary metrics
    total_dividends = sum(d.amount_per_share * d.total_amount for d in dividends if d.amount_per_share > 0)
    upcoming = len(news_engine.get_upcoming_dividends())

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Distributions", len(dividends))
    with col2:
        st.metric("Upcoming", upcoming)

    for div in dividends:
        status_emoji = {"announced": "🟡", "approved": "🟢", "distributed": "🔵"}.get(div.status, "⚪")

        with st.container():
            col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
            with col1:
                st.write(f"**{div.symbol}**")
            with col2:
                st.write(f"{status_emoji} {div.amount_per_share:.2f} {div.currency}")
            with col3:
                st.write(f"Type: {div.dividend_type}")
            with col4:
                st.write(f"Record: {div.record_date.strftime('%Y-%m-%d')}")
        st.divider()

with tab3:
    st.subheader("📅 Dividend Calendar")

    calendar = news_engine.get_dividend_calendar()
    for month, divs in sorted(calendar.items()):
        with st.expander(f"📅 {month} ({len(divs)} distributions)"):
            for div in divs:
                info = get_stock_info(div.symbol)
                name = info.name if info else div.symbol
                st.write(f"• **{div.symbol}** ({name}): {div.amount_per_share:.2f} {div.currency} — {div.dividend_type} — Dist: {div.distribution_date.strftime('%Y-%m-%d')}")

    # Upcoming dividends
    st.subheader("⏰ Upcoming Ex-Dividend Dates")
    upcoming_divs = news_engine.get_upcoming_dividends()
    if upcoming_divs:
        for div in upcoming_divs:
            days_left = (div.ex_dividend_date - pd.Timestamp.now()).days
            st.write(f"• **{div.symbol}**: Ex-date {div.ex_dividend_date.strftime('%Y-%m-%d')} ({days_left} days)")
    else:
        st.info("No upcoming ex-dividend dates in the near future.")

def _time_ago(dt):
    diff = pd.Timestamp.now() - dt
    if diff.days > 0:
        return f"{diff.days}d ago"
    hours = diff.seconds // 3600
    if hours > 0:
        return f"{hours}h ago"
    return f"{(diff.seconds % 3600) // 60}m ago"
