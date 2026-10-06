"""Stock level rules and adjustments."""
from app.repositories import product_repo, stock_repo


def is_low_stock(product):
    """A product is low on stock when its quantity is at or below its reorder level."""
    return product.quantity <= product.reorder_level


def get_stock_status(product):
    if product.quantity <= 0:
        return "out_of_stock"
    if is_low_stock(product):
        return "low_stock"
    return "in_stock"


def reorder_suggestion(product):
    """Suggest an order size that brings stock back to twice the reorder level."""
    target = product.reorder_level * 2
    return max(target - product.quantity, 0)


def adjust_stock(product_id, delta, reason, user_id=None):
    """Change stock by delta (positive or negative) and record the movement."""
    product = product_repo.get_product(product_id)
    if product is None:
        raise LookupError(f"Product {product_id} not found")

    new_quantity = product.quantity + delta
    if new_quantity < 0:
        raise ValueError(f"Insufficient stock for {product.sku}: have {product.quantity}")

    product_repo.set_quantity(product_id, new_quantity)
    stock_repo.record_movement(product_id, delta, reason, user_id)
    return new_quantity


def restock(product_id, quantity, user_id=None):
    if quantity <= 0:
        raise ValueError("Restock quantity must be positive")
    return adjust_stock(product_id, quantity, "restock", user_id)
