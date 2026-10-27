"""
Unit Tests for Billing Service
"""

import pytest
from services.billing_service import BillingCalculator


@pytest.fixture
def calculator():
    return BillingCalculator(tax_rate=0.08)


def test_calculate_itemized_split_normal(calculator):
    assert calculator.calculate_itemized_split(100.0, 4) == 25.0


def test_calculate_itemized_split_zero_participants(calculator):
    """
    Should gracefully handle zero participants by returning 0.0 without ZeroDivisionError.
    """
    assert calculator.calculate_itemized_split(100.0, 0) == 0.0


def test_apply_promotional_discount_valid(calculator):
    assert calculator.apply_promotional_discount(100.0, "SAVE20") == 80.0
    assert calculator.apply_promotional_discount(100.0, "save20") == 80.0


def test_apply_promotional_discount_none_promo(calculator):
    """
    Should gracefully handle None promo code without AttributeError.
    """
    assert calculator.apply_promotional_discount(100.0, None) == 100.0


def test_generate_invoice_summary_missing_fields(calculator):
    """
    Should safely handle customer data with missing fields or empty items.
    """
    empty_data = {}
    summary = calculator.generate_invoice_summary(empty_data)
    assert summary["customer_id"] == "UNKNOWN"
    assert summary["final_total"] == 0.0
