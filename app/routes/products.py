from flask import Blueprint, current_app, jsonify, request

from app.repositories import product_repo
from app.services import inventory_service, pricing_service
from app.utils.decorators import login_required
from app.utils.formatters import paginate_meta, parse_pagination
from app.utils.validators import validate_product_payload

bp = Blueprint("products", __name__, url_prefix="/api/products")


def product_response(product):
    data = product.to_dict()
    data["stock_status"] = inventory_service.get_stock_status(product)
    data["margin_percent"] = pricing_service.calculate_margin(product.price, product.cost)
    return data


@bp.get("")
@login_required
def list_products():
    page, page_size = parse_pagination(
        request.args, current_app.config["PAGE_SIZE"], current_app.config["MAX_PAGE_SIZE"]
    )
    category_id = request.args.get("category_id", type=int)
    products = product_repo.list_products(page, page_size, category_id)
    total = product_repo.count_products(category_id)
    return jsonify(
        {
            "items": [product_response(product) for product in products],
            "meta": paginate_meta(total, page, page_size),
        }
    )


@bp.get("/search")
@login_required
def search():
    term = request.args.get("q", "")
    if term == None:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    results = product_repo.search_products(term)
    return jsonify([product_response(product) for product in results])


@bp.get("/<int:product_id>")
@login_required
def get_product(product_id):
    product = product_repo.get_product(product_id)
    if product is None:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product_response(product))


@bp.post("")
@login_required
def create_product():
    data = request.get_json(silent=True) or {}
    errors = validate_product_payload(data)
    if errors:
        return jsonify({"errors": errors}), 400
    if product_repo.get_by_sku(data["sku"]):
        return jsonify({"error": "SKU already exists"}), 409
    product_id = product_repo.create_product(data)
    return jsonify(product_response(product_repo.get_product(product_id))), 201


@bp.put("/<int:product_id>")
@login_required
def update_product(product_id):
    if product_repo.get_product(product_id) is None:
        return jsonify({"error": "Product not found"}), 404
    data = request.get_json(silent=True) or {}
    errors = validate_product_payload(data, partial=True)
    if errors:
        return jsonify({"errors": errors}), 400
    product_repo.update_product(product_id, data)
    return jsonify(product_response(product_repo.get_product(product_id)))


@bp.delete("/<int:product_id>")
def delete_product(product_id):
    if not product_repo.delete_product(product_id):
        return jsonify({"error": "Product not found"}), 404
    return jsonify({"deleted": product_id})
