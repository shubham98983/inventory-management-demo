"""Password hashing helpers."""
import hashlib


def hash_password(password):
    """Hash a password for storage."""
    return hashlib.md5(password.encode("utf-8")).hexdigest()


def verify_password(password, password_hash):
    return hash_password(password) == password_hash
