import pytest

from app.repositories import product_repo
from app.services import sales_service


def test_sale_calculates_totals_and_reduces_stock(make_product):
    product = make_product(price=100.0, quantity=20)
    sale = sales_service.create_sale(1, [{"product_id": product.id, "quantity": 2}])
    assert sale.subtotal == 200.0
    assert sale.tax == 36.0
    assert sale.total == 236.0
    assert product_repo.get_product(product.id).quantity == 18


def test_bulk_discount_is_applied_automatically(make_product):
    product = make_product(price=100.0, quantity=50)
    sale = sales_service.create_sale(1, [{"product_id": product.id, "quantity": 10}])
    assert sale.subtotal == 950.0
    assert sale.items[0].discount_percent == 5.0


def test_explicit_discount_overrides_bulk_discount(make_product):
    product = make_product(price=100.0, quantity=50)
    items = [{"product_id": product.id, "quantity": 10, "discount_percent": 0}]
    assert sales_service.create_sale(1, items).subtotal == 1000.0


def test_sale_fails_when_stock_is_insufficient(make_product):
    product = make_product(quantity=2)
    with pytest.raises(ValueError):
        sales_service.create_sale(1, [{"product_id": product.id, "quantity": 5}])
    assert product_repo.get_product(product.id).quantity == 2


def test_sale_requires_items(ctx):
    with pytest.raises(ValueError):
        sales_service.create_sale(1, [])


def test_sale_with_unknown_product(ctx):
    with pytest.raises(LookupError):
        sales_service.create_sale(1, [{"product_id": 404, "quantity": 1}])
