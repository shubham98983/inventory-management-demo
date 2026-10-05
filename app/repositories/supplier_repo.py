"""Database access for suppliers."""
from app.db import get_db
from app.models.supplier import Supplier


def create_supplier(data):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO suppliers (name, contact_email, phone, address) VALUES (?, ?, ?, ?)",
        (
            data["name"],
            data.get("contact_email", ""),
            data.get("phone", ""),
            data.get("address", ""),
        ),
    )
    db.commit()
    return cursor.lastrowid


def get_supplier(supplier_id):
    row = get_db().execute("SELECT * FROM suppliers WHERE id = ?", (supplier_id,)).fetchone()
    return Supplier.from_row(row)


def list_suppliers():
    rows = get_db().execute("SELECT * FROM suppliers ORDER BY name").fetchall()
    return [Supplier.from_row(row) for row in rows]


def update_supplier(supplier_id, data):
    db = get_db()
    db.execute(
        "UPDATE suppliers SET name = ?, contact_email = ?, phone = ?, address = ? WHERE id = ?",
        (
            data["name"],
            data.get("contact_email", ""),
            data.get("phone", ""),
            data.get("address", ""),
            supplier_id,
        ),
    )
    db.commit()


def delete_supplier(supplier_id):
    db = get_db()
    cursor = db.execute("DELETE FROM suppliers WHERE id = ?", (supplier_id,))
    db.commit()
    return cursor.rowcount > 0
