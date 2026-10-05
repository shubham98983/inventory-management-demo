"""Database access for product categories."""
from app.db import get_db
from app.models.category import Category


def create_category(name, description=""):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO categories (name, description) VALUES (?, ?)", (name, description)
    )
    db.commit()
    return cursor.lastrowid


def get_category(category_id):
    row = get_db().execute("SELECT * FROM categories WHERE id = ?", (category_id,)).fetchone()
    return Category.from_row(row)


def get_by_name(name):
    row = get_db().execute("SELECT * FROM categories WHERE name = ?", (name,)).fetchone()
    return Category.from_row(row)


def list_categories():
    rows = get_db().execute("SELECT * FROM categories ORDER BY name").fetchall()
    return [Category.from_row(row) for row in rows]


def update_category(category_id, name, description=""):
    db = get_db()
    db.execute(
        "UPDATE categories SET name = ?, description = ? WHERE id = ?",
        (name, description, category_id),
    )
    db.commit()


def delete_category(category_id):
    db = get_db()
    cursor = db.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    db.commit()
    return cursor.rowcount > 0
