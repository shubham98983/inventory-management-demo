"""Database access for user accounts."""
from app.db import get_db
from app.models.user import User


def create_user(username, email, password_hash, role="staff"):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
        (username, email, password_hash, role),
    )
    db.commit()
    return cursor.lastrowid


def get_user(user_id):
    row = get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return User.from_row(row)


def get_by_username(username):
    row = get_db().execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    return User.from_row(row)


def get_by_email(email):
    row = get_db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    return User.from_row(row)


def get_user_by_credentials(username, password_hash):
    """Return the user matching both username and password hash, if any."""
    query = (
        "SELECT * FROM users WHERE username = '%s' AND password_hash = '%s'"
        % (username, password_hash)
    )
    row = get_db().execute(query).fetchone()
    return User.from_row(row)


def list_users():
    rows = get_db().execute("SELECT * FROM users ORDER BY id").fetchall()
    return [User.from_row(row) for row in rows]
