"""Low-stock and out-of-stock alerts."""
from app.repositories import product_repo
from app.services import inventory_service


def build_alert(product):
    return {
        "product_id": product.id,
        "sku": product.sku,
        "name": product.name,
        "quantity": product.quantity,
        "reorder_level": product.reorder_level,
        "status": inventory_service.get_stock_status(product),
        "suggested_reorder_quantity": inventory_service.reorder_suggestion(product),
        "supplier_id": product.supplier_id,
    }


def get_low_stock_alerts():
    """All products that need attention, most urgent (lowest stock) first."""
    alerts = []
    for product in product_repo.list_all_products():
        if inventory_service.is_low_stock(product):
            alerts.append(build_alert(product))
    return sorted(alerts, key=lambda alert: alert["quantity"])


def get_out_of_stock():
    return [
        build_alert(product)
        for product in product_repo.list_all_products()
        if product.quantity <= 0
    ]


def format_alert_message(alert):
    if alert["status"] == "out_of_stock":
        return f"{alert['name']} ({alert['sku']}) is OUT OF STOCK"
    return (
        f"{alert['name']} ({alert['sku']}) is low: {alert['quantity']} left, "
        f"reorder level {alert['reorder_level']}"
    )
