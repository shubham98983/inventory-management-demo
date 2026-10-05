"""Pricing rules: tax, discounts and margins."""
from flask import current_app


def calculate_tax(amount, rate=None):
    if rate is None:
        rate = current_app.config["TAX_RATE"]
    return round(amount * rate, 2)


def apply_discount(price, percent):
    """Return the price after taking percent off."""
    if percent < 0 or percent > 100:
        raise ValueError("Discount must be between 0 and 100 percent")
    return round(price * (1 - percent / 100), 2)


def bulk_discount(quantity):
    """Automatic discount percentage for large orders of a single product."""
    if quantity >= 100:
        return 15.0
    if quantity >= 50:
        return 10.0
    if quantity >= 10:
        return 5.0
    return 0.0


def calculate_margin(price, cost):
    """Gross margin as a percentage of the selling price."""
    if price == 0:
        return 0.0
    return round((price - cost) / price * 100, 2)
