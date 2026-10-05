from flask import Blueprint, g, jsonify, request

from app.repositories import user_repo
from app.services import auth_service
from app.utils.decorators import login_required
from app.utils.validators import validate_registration

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    errors = validate_registration(data)
    if errors:
        return jsonify({"errors": errors}), 400
    try:
        user = auth_service.register_user(
            data["username"], data["email"], data["password"], data.get("role", "staff")
        )
    except ValueError as error:
        return jsonify({"error": str(error)}), 409
    return jsonify(user.to_dict()), 201


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    user = auth_service.authenticate(data.get("username", ""), data.get("password", ""))
    if user is None:
        return jsonify({"error": "Invalid username or password"}), 401
    return jsonify({"token": auth_service.generate_token(user), "user": user.to_dict()})


@bp.get("/me")
@login_required
def me():
    user = user_repo.get_user(g.current_user_id)
    if user is None:
        return jsonify({"error": "User no longer exists"}), 404
    return jsonify(user.to_dict())
