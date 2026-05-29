"""
EGX Pro Terminal v27 - Input Validators
Data validation and sanitization utilities
"""

import re
from typing import Optional, Tuple
from datetime import datetime

class InputValidator:
    @staticmethod
    def validate_symbol(symbol: str) -> Tuple[bool, str]:
        if not symbol:
            return False, "Symbol cannot be empty"

        symbol = symbol.upper().strip()

        if not re.match(r'^[A-Z]{2,8}$', symbol):
            return False, "Symbol must be 2-8 uppercase letters"

        return True, symbol

    @staticmethod
    def validate_price(price: float, min_val: float = 0.01, max_val: float = 100000) -> Tuple[bool, str]:
        if not isinstance(price, (int, float)):
            return False, "Price must be a number"

        if price < min_val:
            return False, f"Price must be at least {min_val}"

        if price > max_val:
            return False, f"Price must not exceed {max_val}"

        return True, str(price)

    @staticmethod
    def validate_period(period: str) -> Tuple[bool, str]:
        valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
        if period not in valid_periods:
            return False, f"Invalid period. Choose from: {', '.join(valid_periods)}"
        return True, period

    @staticmethod
    def validate_interval(interval: str) -> Tuple[bool, str]:
        valid_intervals = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
        if interval not in valid_intervals:
            return False, f"Invalid interval. Choose from: {', '.join(valid_intervals)}"
        return True, interval

    @staticmethod
    def validate_rsi_threshold(value: float) -> Tuple[bool, str]:
        if not 0 <= value <= 100:
            return False, "RSI threshold must be between 0 and 100"
        return True, str(value)

    @staticmethod
    def validate_capital(capital: float) -> Tuple[bool, str]:
        if capital < 1000:
            return False, "Initial capital must be at least 1,000 EGP"
        if capital > 1e9:
            return False, "Initial capital exceeds maximum limit"
        return True, str(capital)

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Invalid email format"
        return True, email

    @staticmethod
    def sanitize_input(text: str, max_length: int = 500) -> str:
        if not text:
            return ""
        text = str(text).strip()
        text = re.sub(r'[<>"']', '', text)
        return text[:max_length]

validator = InputValidator()
