"""
EGX Pro Terminal v27 - Validation Tests
"""

import unittest
from utils.validators import validator

class TestValidators(unittest.TestCase):
    def test_validate_symbol(self):
        self.assertTrue(validator.validate_symbol("COMI")[0])
        self.assertTrue(validator.validate_symbol("TMGH")[0])
        self.assertFalse(validator.validate_symbol("")[0])
        self.assertFalse(validator.validate_symbol("A")[0])
        self.assertFalse(validator.validate_symbol("123")[0])

    def test_validate_price(self):
        self.assertTrue(validator.validate_price(15.5)[0])
        self.assertFalse(validator.validate_price(-1)[0])
        self.assertFalse(validator.validate_price(0)[0])

    def test_validate_period(self):
        self.assertTrue(validator.validate_period("1y")[0])
        self.assertTrue(validator.validate_period("1mo")[0])
        self.assertFalse(validator.validate_period("invalid")[0])

    def test_validate_capital(self):
        self.assertTrue(validator.validate_capital(100000)[0])
        self.assertFalse(validator.validate_capital(100)[0])
        self.assertFalse(validator.validate_capital(1e10)[0])

    def test_sanitize_input(self):
        self.assertEqual(validator.sanitize_input("<script>alert(1)</script>"), "scriptalert(1)/script")
        self.assertEqual(validator.sanitize_input("normal text"), "normal text")

if __name__ == '__main__':
    unittest.main()
