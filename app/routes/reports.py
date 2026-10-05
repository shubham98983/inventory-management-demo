from flask import Blueprint, Response, jsonify, request

from app.repositories import product_repo, sale_repo
from app.services import report_service
from app.utils import backup
from app.utils.csv_export import products_to_csv, sales_to_csv
from app.utils.decorators import admin_required, login_required

bp = Blueprint("reports", __name__, url_prefix="/api/reports")


@bp.get("/sales")
@login_required
def sales_report():
    report = report_service.sales_report(request.args.get("start"), request.args.get("end"))
    return jsonify(report)


@bp.get("/inventory-value")
@login_required
def inventory_value():
    return jsonify(report_service.inventory_valuation())


@bp.get("/top-products")
@login_required
def top_products():
    limit = request.args.get("limit", 5, type=int)
    return jsonify(report_service.top_selling_products(limit))


@bp.get("/categories")
@login_required
def categories():
    return jsonify(report_service.category_breakdown())


@bp.get("/export/products")
@login_required
def export_products():
    csv_data = products_to_csv(product_repo.list_all_products())
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=products.csv"},
    )


@bp.get("/export/sales")
@login_required
def export_sales():
    csv_data = sales_to_csv(sale_repo.list_sales())
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=sales.csv"},
    )


@bp.post("/backup")
@admin_required
def create_backup():
    data = request.get_json(silent=True) or {}
    filename = data.get("filename", "inventory-backup.db")
    try:
        path = backup.create_backup(filename)
    except Exception as error:
        return jsonify({"error": str(error)}), 500
    return jsonify({"backup": path})
