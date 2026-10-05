"""Authentication and authorisation decorators for route handlers."""
from functools import wraps

from flask import g, jsonify, request

from app.services import auth_service


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify({"error": "Missing or malformed Authorization header"}), 401
        payload = auth_service.verify_token(header[len("Bearer "):])
        if payload is None:
            return jsonify({"error": "Invalid or expired token"}), 401
        g.current_user_id = int(payload["sub"])
        g.current_role = payload.get("role", "staff")
        return view(*args, **kwargs)

    return wrapper


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapper(*args, **kwargs):
        if g.current_role != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return view(*args, **kwargs)

    return wrapper
