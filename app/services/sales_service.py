"""Creating and retrieving sales."""
from app.repositories import product_repo, sale_repo
from app.services import inventory_service, pricing_service


def create_sale(user_id, items):
    """Record a sale, apply discounts and tax, and reduce stock."""
    if not items:
        raise ValueError("A sale needs at least one item")

    subtotal = 0.0
    line_items = []
    for item in items:
        product = product_repo.get_product(item["product_id"])
        if product is None:
            raise LookupError(f"Product {item['product_id']} not found")

        quantity = item["quantity"]
        if product.quantity < quantity:
            raise ValueError(f"Insufficient stock for {product.sku}")

        discount = item.get("discount_percent")
        if discount is None:
            discount = pricing_service.bulk_discount(quantity)
        unit_price = pricing_service.apply_discount(product.price, discount)
        subtotal += unit_price * quantity
        line_items.append(
            {
                "product_id": product.id,
                "quantity": quantity,
                "unit_price": product.price,
                "discount_percent": discount,
            }
        )

    subtotal = round(subtotal, 2)
    tax = pricing_service.calculate_tax(subtotal)
    total = round(subtotal + tax, 2)
    sale_id = sale_repo.create_sale(user_id, subtotal, tax, total, line_items)

    for line in line_items:
        inventory_service.adjust_stock(
            line["product_id"], -line["quantity"], f"sale #{sale_id}", user_id
        )
    return sale_repo.get_sale(sale_id)


def get_sale_details(sale_id):
    sale = sale_repo.get_sale(sale_id)
    if sale is None:
        raise LookupError(f"Sale {sale_id} not found")
    return sale
