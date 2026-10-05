import pytest

from app.services import pricing_service


def test_calculate_tax_with_explicit_rate():
    assert pricing_service.calculate_tax(200, rate=0.1) == 20.0


def test_calculate_tax_uses_configured_rate(ctx):
    assert pricing_service.calculate_tax(100) == 18.0


def test_apply_discount():
    assert pricing_service.apply_discount(200, 25) == 150.0


def test_apply_discount_rejects_invalid_percent():
    with pytest.raises(ValueError):
        pricing_service.apply_discount(100, 120)


@pytest.mark.parametrize(
    "quantity, expected",
    [(1, 0.0), (9, 0.0), (10, 5.0), (49, 5.0), (50, 10.0), (100, 15.0)],
)
def test_bulk_discount_tiers(quantity, expected):
    assert pricing_service.bulk_discount(quantity) == expected


def test_calculate_margin():
    assert pricing_service.calculate_margin(100, 60) == 40.0


def test_margin_for_zero_price_is_zero():
    assert pricing_service.calculate_margin(0, 5) == 0.0
