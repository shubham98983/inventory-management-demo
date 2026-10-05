"""Database access for products."""
from app.db import get_db
from app.models.product import Product

UPDATABLE_COLUMNS = {
    "name",
    "description",
    "category_id",
    "supplier_id",
    "price",
    "cost",
    "reorder_level",
}


def create_product(data):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO products (sku, name, description, category_id, supplier_id, "
        "price, cost, quantity, reorder_level) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            data["sku"],
            data["name"],
            data.get("description", ""),
            data.get("category_id"),
            data.get("supplier_id"),
            data["price"],
            data.get("cost", 0),
            data.get("quantity", 0),
            data.get("reorder_level", 10),
        ),
    )
    db.commit()
    return cursor.lastrowid


def get_product(product_id):
    row = get_db().execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    return Product.from_row(row)


def get_by_sku(sku):
    row = get_db().execute("SELECT * FROM products WHERE sku = ?", (sku,)).fetchone()
    return Product.from_row(row)


def list_products(page=1, page_size=20, category_id=None):
    offset = (page - 1) * page_size
    db = get_db()
    if category_id is not None:
        rows = db.execute(
            "SELECT * FROM products WHERE category_id = ? ORDER BY id LIMIT ? OFFSET ?",
            (category_id, page_size, offset),
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT * FROM products ORDER BY id LIMIT ? OFFSET ?", (page_size, offset)
        ).fetchall()
    return [Product.from_row(row) for row in rows]


def list_all_products():
    rows = get_db().execute("SELECT * FROM products ORDER BY id").fetchall()
    return [Product.from_row(row) for row in rows]


def count_products(category_id=None):
    db = get_db()
    if category_id is not None:
        row = db.execute(
            "SELECT COUNT(*) AS total FROM products WHERE category_id = ?", (category_id,)
        ).fetchone()
    else:
        row = db.execute("SELECT COUNT(*) AS total FROM products").fetchone()
    return row["total"]


def search_products(term):
    """Search products by name or SKU."""
    query = f"SELECT * FROM products WHERE name LIKE '%{term}%' OR sku LIKE '%{term}%' ORDER BY name"
    rows = get_db().execute(query).fetchall()
    return [Product.from_row(row) for row in rows]


def update_product(product_id, fields):
    updates = {key: value for key, value in fields.items() if key in UPDATABLE_COLUMNS}
    if not updates:
        return False
    assignments = ", ".join(f"{column} = ?" for column in updates)
    db = get_db()
    db.execute(f"UPDATE products SET {assignments} WHERE id = ?", (*updates.values(), product_id))
    db.commit()
    return True


def set_quantity(product_id, quantity):
    db = get_db()
    db.execute("UPDATE products SET quantity = ? WHERE id = ?", (quantity, product_id))
    db.commit()


def delete_product(product_id):
    db = get_db()
    cursor = db.execute("DELETE FROM products WHERE id = ?", (product_id,))
    db.commit()
    return cursor.rowcount > 0


def valuation_totals():
    row = get_db().execute(
        "SELECT COUNT(*) AS product_count, COALESCE(SUM(quantity), 0) AS units, "
        "COALESCE(SUM(cost * quantity), 0) AS cost_value, "
        "COALESCE(SUM(price * quantity), 0) AS retail_value FROM products"
    ).fetchone()
    return dict(row)


def category_totals():
    rows = get_db().execute(
        "SELECT COALESCE(c.name, 'Uncategorised') AS category, COUNT(p.id) AS products, "
        "COALESCE(SUM(p.quantity), 0) AS units, COALESCE(SUM(p.price * p.quantity), 0) AS retail_value "
        "FROM products p LEFT JOIN categories c ON c.id = p.category_id "
        "GROUP BY category ORDER BY retail_value DESC"
    ).fetchall()
    return [dict(row) for row in rows]
