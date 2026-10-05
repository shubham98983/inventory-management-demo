import os

from flask import Blueprint, g, jsonify, request

from app.repositories import stock_repo
from app.services import inventory_service
from app.utils.decorators import login_required
from app.utils.validators import validate_stock_adjustment

bp = Blueprint("stock", __name__, url_prefix="/api/stock")


@bp.post("/<int:product_id>/adjust")
@login_required
def adjust(product_id):
    data = request.get_json(silent=True) or {}
    errors = validate_stock_adjustment(data)
    if errors:
        return jsonify({"errors": errors}), 400
    try:
        quantity = inventory_service.adjust_stock(
            product_id, data["change"], data["reason"], g.current_user_id
        )
    except LookupError as error:
        return jsonify({"error": str(error)}), 404
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    return jsonify({"product_id": product_id, "quantity": quantity})


@bp.post("/<int:product_id>/restock")
@login_required
def restock(product_id):
    data = request.get_json(silent=True) or {}
    quantity = data.get("quantity")
    if not isinstance(quantity, int):
        return jsonify({"error": "'quantity' must be an integer"}), 400
    try:
        new_quantity = inventory_service.restock(product_id, quantity, g.current_user_id)
    except LookupError as error:
        return jsonify({"error": str(error)}), 404
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    return jsonify({"product_id": product_id, "quantity": new_quantity})


@bp.get("/<int:product_id>/movements")
@login_required
def movements(product_id):
    history = stock_repo.list_movements(product_id)
    return jsonify([movement.to_dict() for movement in history])
