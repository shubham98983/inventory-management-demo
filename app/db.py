"""SQLite connection handling for the Flask application."""
import sqlite3
from pathlib import Path

import click
from flask import current_app, g

SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_db():
    """Return the per-request SQLite connection, creating it if needed."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(error=None):
    """Close the connection at the end of the application context."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create all tables from schema.sql (safe to run repeatedly)."""
    db = get_db()
    with open(SCHEMA_PATH) as schema_file:
        db.executescript(schema_file.read())
    db.commit()


@click.command("init-db")
def init_db_command():
    """Flask CLI command: flask init-db."""
    init_db()
    click.echo("Database initialised.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
