from flask import Blueprint, g, jsonify, request

from app.repositories import sale_repo
from app.services import sales_service
from app.utils.decorators import login_required
from app.utils.validators import validate_sale_payload

bp = Blueprint("sales", __name__, url_prefix="/api/sales")


@bp.post("")
@login_required
def create_sale():
    data = request.get_json(silent=True) or {}
    errors = validate_sale_payload(data)
    if errors:
        return jsonify({"errors": errors}), 400
    try:
        sale = sales_service.create_sale(g.current_user_id, data["items"])
    except LookupError as error:
        return jsonify({"error": str(error)}), 404
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    return jsonify(sale.to_dict()), 201


@bp.get("")
@login_required
def list_sales():
    sales = sale_repo.list_sales(request.args.get("start"), request.args.get("end"))
    return jsonify(sales)


@bp.get("/<int:sale_id>")
@login_required
def get_sale(sale_id):
    try:
        sale = sales_service.get_sale_details(sale_id)
    except LookupError as error:
        return jsonify({"error": str(error)}), 404
    return jsonify(sale.to_dict())
