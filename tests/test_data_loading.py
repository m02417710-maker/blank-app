"""
EGX Pro Terminal - Tests for Data Loading
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.egx_symbols import (
    get_stock_info, get_all_symbols, get_stocks_by_sector,
    get_blue_chips, get_high_dividend, get_market_stats,
    EGX_STOCKS, EGX_INDICES, DELISTED_STOCKS, SUSPENDED_STOCKS
)
from data.market_data import MarketDataFetcher, generate_mock_data

class TestEGXSymbols(unittest.TestCase):
    def test_stock_info_exists(self):
        info = get_stock_info("COMI")
        self.assertIsNotNone(info)
        self.assertEqual(info.symbol, "COMI")

    def test_all_symbols_not_empty(self):
        symbols = get_all_symbols()
        self.assertGreater(len(symbols), 0)

    def test_get_stocks_by_sector(self):
        banking = get_stocks_by_sector("Banking")
        self.assertIsInstance(banking, list)
        self.assertGreater(len(banking), 0)

    def test_blue_chips(self):
        blue_chips = get_blue_chips()
        self.assertIsInstance(blue_chips, list)
        if blue_chips:
            info = get_stock_info(blue_chips[0])
            self.assertIsNotNone(info.market_cap)
            self.assertGreaterEqual(info.market_cap, 10000)

    def test_high_dividend(self):
        high_div = get_high_dividend()
        self.assertIsInstance(high_div, list)

    def test_market_stats(self):
        stats = get_market_stats()
        self.assertIn("total_companies", stats)
        self.assertIn("total_market_cap_egp_billions", stats)
        self.assertIn("avg_pe_ratio", stats)

    def test_delisted_stocks(self):
        self.assertGreater(len(DELISTED_STOCKS), 0)
        for symbol, info in DELISTED_STOCKS.items():
            self.assertEqual(info.status.value, "delisted")

    def test_suspended_stocks(self):
        self.assertGreater(len(SUSPENDED_STOCKS), 0)
        for symbol, info in SUSPENDED_STOCKS.items():
            self.assertEqual(info.status.value, "suspended")

    def test_indices(self):
        self.assertGreater(len(EGX_INDICES), 0)
        for symbol, info in EGX_INDICES.items():
            self.assertTrue(info.is_index)

class TestMarketData(unittest.TestCase):
    def test_fetcher_initialization(self):
        fetcher = MarketDataFetcher()
        self.assertIsNotNone(fetcher)

    def test_mock_data(self):
        df = generate_mock_data("COMI", 100)
        self.assertEqual(len(df), 100)
        self.assertIn("close", df.columns)

    def test_real_time_quote(self):
        fetcher = MarketDataFetcher()
        quote = fetcher.get_real_time_quote("COMI")
        # May fail if no internet, so just check it doesn't crash
        self.assertTrue(quote is None or isinstance(quote, dict))

if __name__ == "__main__":
    unittest.main()
