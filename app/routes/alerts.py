from flask import Blueprint, jsonify

from app.services import alert_service
from app.utils.decorators import login_required

bp = Blueprint("alerts", __name__, url_prefix="/api/alerts")


@bp.get("/low-stock")
@login_required
def low_stock():
    alerts = alert_service.get_low_stock_alerts()
    return jsonify(
        {
            "count": len(alerts),
            "alerts": alerts,
            "messages": [alert_service.format_alert_message(alert) for alert in alerts],
        }
    )


@bp.get("/out-of-stock")
@login_required
def out_of_stock():
    alerts = alert_service.get_out_of_stock()
    return jsonify({"count": len(alerts), "alerts": alerts})
