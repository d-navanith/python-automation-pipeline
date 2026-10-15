"""
tests/test_api_rates.py - Automated QA Test Suite for API Service

Tests verify:
1. API endpoint returns HTTP 200 OK
2. Response structure contains expected keys ('base', 'date', 'rates')
3. Key world currencies are present in the dataset
4. All exchange rate values are positive numbers
5. Handling of invalid inputs
"""

import pytest
import requests
from pathlib import Path
import sys

# Add project root to sys.path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from api_reporter import fetch_live_rates


class TestCurrencyAPI:
    """Group of automated tests for the Currency API."""

    def test_api_status_success(self):
        """Verify that the API endpoint returns 200 OK and correct base."""
        data = fetch_live_rates(base_currency="USD")
        
        # QA Assertions
        assert data is not None, "API returned empty response"
        assert data.get("base") == "USD", f"Expected base 'USD', got {data.get('base')}"
        assert "rates" in data, "Response is missing 'rates' dictionary"

    def test_expected_major_currencies_exist(self):
        """Verify that critical trading currencies exist in the payload."""
        data = fetch_live_rates(base_currency="USD")
        rates = data.get("rates", {})
        
        expected_currencies = ["EUR", "GBP", "JPY", "CAD", "AUD"]
        for curr in expected_currencies:
            assert curr in rates, f"Expected currency {curr} not found in rates"

    def test_exchange_rates_are_positive(self):
        """Verify that exchange rates are valid positive numbers."""
        data = fetch_live_rates(base_currency="USD")
        rates = data.get("rates", {})
        
        assert len(rates) > 0, "No rates returned by the API"
        for currency, rate in rates.items():
            assert isinstance(rate, (int, float)), f"Rate for {currency} is not numeric: {rate}"
            assert rate > 0, f"Rate for {currency} must be greater than zero, got {rate}"

    def test_invalid_currency_handling(self):
        """Verify behavior when requesting an invalid 3-letter currency code."""
        # 'ZZZ' is not a real currency
        data = fetch_live_rates(base_currency="ZZZ")
        # Our function gracefully returns an empty dict on error
        assert data == {}, "Expected empty dict when querying an invalid currency"
