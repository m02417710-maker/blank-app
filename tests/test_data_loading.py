"""
EGX Pro Terminal v27 - Data Loading Tests
"""

import unittest
import pandas as pd
from data.market_data import market_engine
from data.egx_symbols import get_stock_info, get_all_symbols

class TestDataLoading(unittest.TestCase):
    def test_get_stock_info(self):
        info = get_stock_info("COMI")
        self.assertIsNotNone(info)
        self.assertEqual(info.symbol, "COMI")

    def test_get_all_symbols(self):
        symbols = get_all_symbols()
        self.assertTrue(len(symbols) > 0)
        self.assertIn("COMI", symbols)

    def test_fetch_data(self):
        df = market_engine.fetch("COMI", period="1mo", interval="1d")
        self.assertIsNotNone(df)
        self.assertFalse(df.empty)
        self.assertIn("close", df.columns)

    def test_get_quote(self):
        quote = market_engine.get_realtime_quote("COMI")
        self.assertIsNotNone(quote)
        self.assertIn("price", quote)

if __name__ == '__main__':
    unittest.main()
