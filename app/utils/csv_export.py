"""CSV export helpers for products and sales."""
import csv
import io


def products_to_csv(products):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "sku", "name", "price", "cost", "quantity", "reorder_level"])
    for product in products:
        writer.writerow(
            [
                product.id,
                product.sku,
                product.name,
                product.price,
                product.cost,
                product.quantity,
                product.reorder_level,
            ]
        )
    return buffer.getvalue()


def sales_to_csv(sales):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "user_id", "subtotal", "tax", "total", "created_at"])
    for sale in sales:
        writer.writerow(
            [
                sale["id"],
                sale["user_id"],
                sale["subtotal"],
                sale["tax"],
                sale["total"],
                sale["created_at"],
            ]
        )
    return buffer.getvalue()
