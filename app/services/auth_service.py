"""User registration, authentication and token handling."""
from datetime import datetime, timedelta, timezone

import jwt
from flask import current_app

from app.repositories import user_repo
from app.utils import security


def register_user(username, email, password, role="staff"):
    if user_repo.get_by_username(username):
        raise ValueError("Username already taken")
    if user_repo.get_by_email(email):
        raise ValueError("Email already registered")
    user_id = user_repo.create_user(username, email, security.hash_password(password), role)
    return user_repo.get_user(user_id)


def authenticate(username, password):
    """Return the matching user, or None when the credentials are wrong."""
    password_hash = security.hash_password(password)
    return user_repo.get_user_by_credentials(username, password_hash)


def generate_token(user):
    expiry = datetime.now(timezone.utc) + timedelta(hours=current_app.config["JWT_EXPIRY_HOURS"])
    payload = {"sub": str(user.id), "role": user.role, "exp": expiry}
    return jwt.encode(
        payload,
        current_app.config["JWT_SECRET"],
        algorithm=current_app.config["JWT_ALGORITHM"],
    )


def verify_token(token):
    try:
        return jwt.decode(
            token,
            current_app.config["JWT_SECRET"],
            algorithms=[current_app.config["JWT_ALGORITHM"]],
        )
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def ensure_default_admin():
    """Create the default admin account on first start."""
    username = current_app.config["DEFAULT_ADMIN_USERNAME"]
    if user_repo.get_by_username(username):
        return None
    return register_user(
        username,
        "admin@inventory.local",
        current_app.config["DEFAULT_ADMIN_PASSWORD"],
        role="admin",
    )
