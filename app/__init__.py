"""Inventory Management application factory."""
from flask import Flask, jsonify

from app import db
from app.routes import (
    alerts,
    auth,
    categories,
    health,
    products,
    reports,
    sales,
    stock,
    suppliers,
)
from config import Config


def create_app(overrides=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if overrides:
        app.config.update(overrides)

    db.init_app(app)

    for module in (health, auth, products, categories, suppliers, stock, sales, alerts, reports):
        app.register_blueprint(module.bp)

    register_error_handlers(app)
    return app


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({"error": "Internal server error"}), 500
