"""Create tables and the default admin account. Safe to run on every start.

Usage:  python -m scripts.init_db
"""
from app import create_app
from app.db import init_db
from app.services import auth_service


def main():
    app = create_app()
    with app.app_context():
        init_db()
        auth_service.ensure_default_admin()
    print("Database ready.")


if __name__ == "__main__":
    main()
