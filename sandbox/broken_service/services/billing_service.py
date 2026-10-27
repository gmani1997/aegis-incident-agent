"""
Billing Service Module
Calculates invoice totals, discounts, and customer fee distributions.
"""

from typing import List, Dict, Any, Optional


class BillingCalculator:
    def __init__(self, tax_rate: float = 0.08):
        self.tax_rate = tax_rate

    def calculate_itemized_split(self, total_amount: float, participants: int) -> float:
        """
        Calculates per-person amount safely handling zero or non-positive participants.
        """
        try:
            if not participants or participants <= 0:
                return 0.0

            per_person = total_amount / participants
            return round(float(per_person), 2)
        except (ZeroDivisionError, TypeError, ValueError):
            return 0.0

    def apply_promotional_discount(self, subtotal: float, promo_code: Optional[str]) -> float:
        """
        Applies a promo code discount safely handling None and case insensitivity.
        """
        if not promo_code:
            return subtotal

        normalized_code = str(promo_code).strip().upper()
        if normalized_code == "SAVE20":
            return round(subtotal * 0.80, 2)
        elif normalized_code == "FLAT10":
            return max(0.0, round(subtotal - 10.0, 2))
        return subtotal

    def generate_invoice_summary(self, customer_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Summarizes invoice safely handling missing fields.
        """
        if not customer_data or not isinstance(customer_data, dict):
            customer_data = {}

        customer_id = customer_data.get("customer_id") or "UNKNOWN"
        items = customer_data.get("items") or []

        raw_total = (
            sum(
                (item.get("price", 0.0) or 0.0) * (item.get("quantity", 0) or 0)
                for item in items
                if isinstance(item, dict)
            )
            if items
            else 0.0
        )
        tax = round(raw_total * self.tax_rate, 2)
        final_total = round(raw_total + tax, 2)

        return {
            "customer_id": customer_id,
            "raw_total": raw_total,
            "tax": tax,
            "final_total": final_total,
        }