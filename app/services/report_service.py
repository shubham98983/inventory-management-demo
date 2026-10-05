"""Sales and inventory reporting."""
from app.repositories import product_repo, sale_repo


def sales_report(start=None, end=None):
    sales = sale_repo.list_sales(start, end)
    total_revenue = round(sum(sale["total"] for sale in sales), 2)
    total_tax = round(sum(sale["tax"] for sale in sales), 2)
    order_count = len(sales)
    average_order_value = round(total_revenue / order_count, 2)
    return {
        "start": start,
        "end": end,
        "order_count": order_count,
        "total_revenue": total_revenue,
        "total_tax": total_tax,
        "average_order_value": average_order_value,
    }


def inventory_valuation():
    totals = product_repo.valuation_totals()
    totals["potential_profit"] = round(totals["retail_value"] - totals["cost_value"], 2)
    return totals


def top_selling_products(limit=5):
    return sale_repo.top_selling(limit)


def category_breakdown():
    return product_repo.category_totals()
