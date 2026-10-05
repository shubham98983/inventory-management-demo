"""Input validation for API payloads. Each validator returns a list of error strings."""
import re

SKU_PATTERN = re.compile(r"^[A-Z0-9\-]{3,20}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
VALID_ROLES = ("admin", "staff")


def is_valid_email(email):
    return bool(email) and bool(EMAIL_PATTERN.match(email))


def is_valid_sku(sku):
    return bool(sku) and bool(SKU_PATTERN.match(sku))


def validate_product_payload(data, partial=False):
    errors = []
    if not isinstance(data, dict):
        return ["Request body must be a JSON object"]

    if not partial:
        for required in ("sku", "name", "price"):
            if required not in data:
                errors.append(f"'{required}' is required")

    if "sku" in data and not is_valid_sku(data["sku"]):
        errors.append("'sku' must be 3-20 characters: A-Z, 0-9 and dashes")
    if "name" in data and not str(data["name"]).strip():
        errors.append("'name' cannot be empty")
    if "price" in data and (not isinstance(data["price"], (int, float)) or data["price"] < 0):
        errors.append("'price' must be a non-negative number")
    if "cost" in data and (not isinstance(data["cost"], (int, float)) or data["cost"] < 0):
        errors.append("'cost' must be a non-negative number")
    if "quantity" in data and (not isinstance(data["quantity"], int) or data["quantity"] < 0):
        errors.append("'quantity' must be a non-negative integer")
    if "reorder_level" in data and (
        not isinstance(data["reorder_level"], int) or data["reorder_level"] < 0
    ):
        errors.append("'reorder_level' must be a non-negative integer")
    return errors


def validate_sale_payload(data):
    errors = []
    if not isinstance(data, dict) or not isinstance(data.get("items"), list):
        return ["'items' must be a list"]
    if not data["items"]:
        return ["A sale needs at least one item"]

    for index, item in enumerate(data["items"]):
        if not isinstance(item.get("product_id"), int):
            errors.append(f"items[{index}].product_id must be an integer")
        quantity = item.get("quantity")
        if not isinstance(quantity, int) or quantity <= 0:
            errors.append(f"items[{index}].quantity must be a positive integer")
        discount = item.get("discount_percent")
        if discount is not None and not 0 <= discount <= 100:
            errors.append(f"items[{index}].discount_percent must be between 0 and 100")
    return errors


def validate_registration(data):
    errors = []
    username = data.get("username", "")
    password = data.get("password", "")
    if len(username) < 3:
        errors.append("'username' must be at least 3 characters")
    if not is_valid_email(data.get("email", "")):
        errors.append("'email' is not a valid email address")
    if len(password) < 8:
        errors.append("'password' must be at least 8 characters")
    if data.get("role", "staff") not in VALID_ROLES:
        errors.append("'role' must be 'admin' or 'staff'")
    return errors


def validate_stock_adjustment(data):
    errors = []
    if not isinstance(data.get("change"), int) or data.get("change") == 0:
        errors.append("'change' must be a non-zero integer")
    if not str(data.get("reason", "")).strip():
        errors.append("'reason' is required")
    return errors
