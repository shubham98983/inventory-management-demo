from flask import Blueprint, jsonify, request

from app.repositories import supplier_repo
from app.utils.decorators import admin_required, login_required
from app.utils.validators import is_valid_email

bp = Blueprint("suppliers", __name__, url_prefix="/api/suppliers")


@bp.get("")
@login_required
def list_suppliers():
    return jsonify([supplier.to_dict() for supplier in supplier_repo.list_suppliers()])


@bp.get("/<int:supplier_id>")
@login_required
def get_supplier(supplier_id):
    supplier = supplier_repo.get_supplier(supplier_id)
    if supplier is None:
        return jsonify({"error": "Supplier not found"}), 404
    return jsonify(supplier.to_dict())


@bp.post("")
@admin_required
def create_supplier():
    data = request.get_json(silent=True) or {}
    if not str(data.get("name", "")).strip():
        return jsonify({"error": "'name' is required"}), 400
    if data.get("contact_email") and not is_valid_email(data["contact_email"]):
        return jsonify({"error": "'contact_email' is not valid"}), 400
    supplier_id = supplier_repo.create_supplier(data)
    return jsonify(supplier_repo.get_supplier(supplier_id).to_dict()), 201


@bp.put("/<int:supplier_id>")
@admin_required
def update_supplier(supplier_id):
    if supplier_repo.get_supplier(supplier_id) is None:
        return jsonify({"error": "Supplier not found"}), 404
    data = request.get_json(silent=True) or {}
    if not str(data.get("name", "")).strip():
        return jsonify({"error": "'name' is required"}), 400
    supplier_repo.update_supplier(supplier_id, data)
    return jsonify(supplier_repo.get_supplier(supplier_id).to_dict())


@bp.delete("/<int:supplier_id>")
@admin_required
def delete_supplier(supplier_id):
    if not supplier_repo.delete_supplier(supplier_id):
        return jsonify({"error": "Supplier not found"}), 404
    return jsonify({"deleted": supplier_id})
