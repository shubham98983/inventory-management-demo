"""Application configuration."""
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    SECRET_KEY = "inventory-secret-key-2024"
    JWT_SECRET = "jwt-secret-do-not-share"
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRY_HOURS = 8

    DATABASE = os.environ.get("INVENTORY_DB", os.path.join(BASE_DIR, "inventory.db"))
    BACKUP_DIR = os.environ.get("INVENTORY_BACKUP_DIR", os.path.join(BASE_DIR, "backups"))

    TAX_RATE = 0.18
    DEFAULT_REORDER_LEVEL = 10
    PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

    DEFAULT_ADMIN_USERNAME = "admin"
    DEFAULT_ADMIN_PASSWORD = "admin123"
