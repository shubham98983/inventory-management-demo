import pytest

from app.models.product import Product
from app.repositories import stock_repo
from app.services import inventory_service


def make(quantity, reorder_level=10):
    return Product(id=1, sku="T-1", name="T", price=1.0, quantity=quantity, reorder_level=reorder_level)


def test_stock_status_in_stock():
    assert inventory_service.get_stock_status(make(50)) == "in_stock"


def test_stock_status_out_of_stock():
    assert inventory_service.get_stock_status(make(0)) == "out_of_stock"


def test_is_low_stock_below_threshold():
    assert inventory_service.is_low_stock(make(3)) is True


def test_is_low_stock_at_threshold():
    """Stock equal to the reorder level should already trigger a low-stock alert."""
    assert inventory_service.is_low_stock(make(10, reorder_level=10)) is True


def test_is_low_stock_above_threshold():
    assert inventory_service.is_low_stock(make(11)) is False


def test_reorder_suggestion_tops_up_to_double_the_level():
    assert inventory_service.reorder_suggestion(make(4, reorder_level=10)) == 16
    assert inventory_service.reorder_suggestion(make(40, reorder_level=10)) == 0


def test_adjust_stock_records_movement(make_product):
    product = make_product(quantity=20)
    new_quantity = inventory_service.adjust_stock(product.id, -5, "damaged goods")
    assert new_quantity == 15
    history = stock_repo.list_movements(product.id)
    assert history[0].quantity_change == -5
    assert history[0].reason == "damaged goods"


def test_adjust_stock_cannot_go_negative(make_product):
    product = make_product(quantity=3)
    with pytest.raises(ValueError):
        inventory_service.adjust_stock(product.id, -4, "oversold")


def test_adjust_stock_unknown_product(ctx):
    with pytest.raises(LookupError):
        inventory_service.adjust_stock(999, 1, "restock")


def test_restock_requires_positive_quantity(make_product):
    product = make_product()
    with pytest.raises(ValueError):
        inventory_service.restock(product.id, 0)
