import sqlite3

from flask import Blueprint, jsonify, request

from app.repositories import category_repo
from app.utils.decorators import admin_required, login_required

bp = Blueprint("categories", __name__, url_prefix="/api/categories")


@bp.get("")
@login_required
def list_categories():
    return jsonify([category.to_dict() for category in category_repo.list_categories()])


@bp.post("")
@admin_required
def create_category():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    if not name:
        return jsonify({"error": "'name' is required"}), 400
    if category_repo.get_by_name(name):
        return jsonify({"error": "Category already exists"}), 409
    category_id = category_repo.create_category(name, data.get("description", ""))
    return jsonify(category_repo.get_category(category_id).to_dict()), 201


@bp.put("/<int:category_id>")
@admin_required
def update_category(category_id):
    if category_repo.get_category(category_id) is None:
        return jsonify({"error": "Category not found"}), 404
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    if not name:
        return jsonify({"error": "'name' is required"}), 400
    category_repo.update_category(category_id, name, data.get("description", ""))
    return jsonify(category_repo.get_category(category_id).to_dict())


@bp.delete("/<int:category_id>")
@admin_required
def delete_category(category_id):
    if not category_repo.delete_category(category_id):
        return jsonify({"error": "Category not found"}), 404
    return jsonify({"deleted": category_id})
