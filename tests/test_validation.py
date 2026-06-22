"""
EGX Pro Terminal - Tests for Input Validation
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.validators import (
    validate_symbol, validate_price, validate_quantity,
    validate_alert_type, validate_email, validate_timeframe,
    validate_strategy, validate_watchlist, validate_capital,
    sanitize_input
)

class TestValidators(unittest.TestCase):
    def test_valid_symbol(self):
        valid, msg = validate_symbol("COMI")
        self.assertTrue(valid)
        self.assertEqual(msg, "Valid")

    def test_invalid_symbol(self):
        valid, msg = validate_symbol("INVALID12345")
        self.assertFalse(valid)

    def test_empty_symbol(self):
        valid, msg = validate_symbol("")
        self.assertFalse(valid)

    def test_valid_price(self):
        valid, msg = validate_price(50.5)
        self.assertTrue(valid)

    def test_invalid_price(self):
        valid, msg = validate_price(-10)
        self.assertFalse(valid)

    def test_valid_quantity(self):
        valid, msg = validate_quantity(100)
        self.assertTrue(valid)

    def test_invalid_quantity(self):
        valid, msg = validate_quantity(0)
        self.assertFalse(valid)

    def test_valid_alert_type(self):
        valid, msg = validate_alert_type("PRICE_ABOVE")
        self.assertTrue(valid)

    def test_invalid_alert_type(self):
        valid, msg = validate_alert_type("INVALID_TYPE")
        self.assertFalse(valid)

    def test_valid_email(self):
        valid, msg = validate_email("test@example.com")
        self.assertTrue(valid)

    def test_invalid_email(self):
        valid, msg = validate_email("invalid-email")
        self.assertFalse(valid)

    def test_valid_timeframe(self):
        valid, msg = validate_timeframe("1M")
        self.assertTrue(valid)

    def test_invalid_timeframe(self):
        valid, msg = validate_timeframe("INVALID")
        self.assertFalse(valid)

    def test_valid_strategy(self):
        valid, msg = validate_strategy("trend_following")
        self.assertTrue(valid)

    def test_invalid_strategy(self):
        valid, msg = validate_strategy("invalid")
        self.assertFalse(valid)

    def test_valid_capital(self):
        valid, msg = validate_capital(100000)
        self.assertTrue(valid)

    def test_invalid_capital(self):
        valid, msg = validate_capital(500)
        self.assertFalse(valid)

    def test_sanitize_input(self):
        clean = sanitize_input("<script>alert('xss')</script>")
        self.assertNotIn("<", clean)
        self.assertNotIn(">", clean)

    def test_validate_watchlist(self):
        valid, msg, invalid = validate_watchlist(["COMI", "HRHO", "ETEL"])
        self.assertTrue(valid)
        self.assertEqual(len(invalid), 0)

if __name__ == "__main__":
    unittest.main()
