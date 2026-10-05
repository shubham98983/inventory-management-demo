"""Database access for sales and sale line items."""
from app.db import get_db
from app.models.sale import Sale, SaleItem


def create_sale(user_id, subtotal, tax, total, line_items):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO sales (user_id, subtotal, tax, total) VALUES (?, ?, ?, ?)",
        (user_id, subtotal, tax, total),
    )
    sale_id = cursor.lastrowid
    for item in line_items:
        db.execute(
            "INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, discount_percent) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                sale_id,
                item["product_id"],
                item["quantity"],
                item["unit_price"],
                item["discount_percent"],
            ),
        )
    db.commit()
    return sale_id


def get_sale(sale_id):
    db = get_db()
    row = db.execute("SELECT * FROM sales WHERE id = ?", (sale_id,)).fetchone()
    if row is None:
        return None
    sale = Sale.from_row(row)
    item_rows = db.execute("SELECT * FROM sale_items WHERE sale_id = ?", (sale_id,)).fetchall()
    sale.items = [SaleItem.from_row(item_row) for item_row in item_rows]
    return sale


def list_sales(start=None, end=None):
    """Return sales as dicts, optionally restricted to a date range (YYYY-MM-DD)."""
    clauses = []
    params = []
    if start:
        clauses.append("date(created_at) >= date(?)")
        params.append(start)
    if end:
        clauses.append("date(created_at) <= date(?)")
        params.append(end)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    rows = get_db().execute(
        f"SELECT * FROM sales {where} ORDER BY id DESC", params
    ).fetchall()
    return [dict(row) for row in rows]


def top_selling(limit=5):
    rows = get_db().execute(
        "SELECT p.id AS product_id, p.sku, p.name, SUM(si.quantity) AS units_sold, "
        "SUM(si.quantity * si.unit_price * (1 - si.discount_percent / 100.0)) AS revenue "
        "FROM sale_items si JOIN products p ON p.id = si.product_id "
        "GROUP BY p.id ORDER BY units_sold DESC LIMIT ?",
        (limit,),
    ).fetchall()
    return [dict(row) for row in rows]
