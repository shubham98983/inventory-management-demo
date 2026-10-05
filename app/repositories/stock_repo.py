"""Database access for stock movement history."""
from app.db import get_db
from app.models.stock_movement import StockMovement


def record_movement(product_id, quantity_change, reason, user_id=None):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO stock_movements (product_id, quantity_change, reason, user_id) "
        "VALUES (?, ?, ?, ?)",
        (product_id, quantity_change, reason, user_id),
    )
    db.commit()
    return cursor.lastrowid


def list_movements(product_id, limit=50):
    rows = get_db().execute(
        "SELECT * FROM stock_movements WHERE product_id = ? ORDER BY id DESC LIMIT ?",
        (product_id, limit),
    ).fetchall()
    return [StockMovement.from_row(row) for row in rows]
