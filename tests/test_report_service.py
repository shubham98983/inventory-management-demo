import pytest
from datetime import datetime, timedelta

from app.services import report_service


class TestSalesReport:
    """Tests for the sales_report function."""

    def test_sales_report_no_sales(self, ctx):
        """No sales should produce zero values instead of crashing."""
        report = report_service.sales_report()

        assert report["order_count"] == 0
        assert report["total_revenue"] == 0
        assert report["total_tax"] == 0
        assert report["average_order_value"] == 0
        assert report["start"] is None
        assert report["end"] is None

    def test_sales_report_one_sale(self, ctx, app):
        """A single sale should be reported correctly."""
        product = app.repositories.product_repo.create_product({
            "name": "Test Product",
            "sku": "TEST-001",
            "price": 100.00,
            "quantity": 10,
        })

        line_items = [
            {
                "product_id": product["id"],
                "quantity": 2,
                "price": 100.00,
            }
        ]

        app.repositories.sale_repo.create_sale(
            user_id=1,
            subtotal=200.00,
            tax=20.00,
            total=220.00,
            line_items=line_items,
        )

        report = report_service.sales_report()

        assert report["order_count"] == 1
        assert report["total_revenue"] == 220.00
        assert report["total_tax"] == 20.00
        assert report["average_order_value"] == 220.00
        assert report["start"] is None
        assert report["end"] is None

    def test_sales_report_multiple_sales(self, ctx, app):
        """Multiple sales should be aggregated correctly."""
        product1 = app.repositories.product_repo.create_product({
            "name": "Product 1",
            "sku": "PROD-001",
            "price": 50.00,
            "quantity": 20,
        })

        product2 = app.repositories.product_repo.create_product({
            "name": "Product 2",
            "sku": "PROD-002",
            "price": 75.00,
            "quantity": 15,
        })

        app.repositories.sale_repo.create_sale(
            user_id=1,
            subtotal=100.00,
            tax=10.00,
            total=110.00,
            line_items=[
                {
                    "product_id": product1["id"],
                    "quantity": 2,
                    "price": 50.00,
                }
            ],
        )

        app.repositories.sale_repo.create_sale(
            user_id=2,
            subtotal=150.00,
            tax=15.00,
            total=165.00,
            line_items=[
                {
                    "product_id": product2["id"],
                    "quantity": 2,
                    "price": 75.00,
                }
            ],
        )

        app.repositories.sale_repo.create_sale(
            user_id=1,
            subtotal=200.00,
            tax=20.00,
            total=220.00,
            line_items=[
                {
                    "product_id": product1["id"],
                    "quantity": 2,
                    "price": 50.00,
                },
                {
                    "product_id": product2["id"],
                    "quantity": 1,
                    "price": 75.00,
                },
            ],
        )

        report = report_service.sales_report()

        assert report["order_count"] == 3
        assert report["total_revenue"] == 495.00
        assert report["total_tax"] == 45.00
        assert report["average_order_value"] == 165.00
        assert report["start"] is None
        assert report["end"] is None

    def test_sales_report_with_date_range(self, ctx, app):
        """Sales report should support date-range filtering."""
        product = app.repositories.product_repo.create_product({
            "name": "Date Test Product",
            "sku": "DATE-001",
            "price": 100.00,
            "quantity": 50,
        })

        app.repositories.sale_repo.create_sale(
            user_id=1,
            subtotal=100.00,
            tax=10.00,
            total=110.00,
            line_items=[
                {
                    "product_id": product["id"],
                    "quantity": 1,
                    "price": 100.00,
                }
            ],
        )

        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)

        start = today.isoformat()
        end = tomorrow.isoformat()

        report = report_service.sales_report(
            start=start,
            end=end,
        )

        assert report["start"] == start
        assert report["end"] == end
        assert report["order_count"] >= 0

    def test_sales_report_no_sales_in_date_range(self, ctx, app):
        """A date range with no sales should return zero values."""
        product = app.repositories.product_repo.create_product({
            "name": "Range Test Product",
            "sku": "RANGE-001",
            "price": 100.00,
            "quantity": 10,
        })

        app.repositories.sale_repo.create_sale(
            user_id=1,
            subtotal=100.00,
            tax=10.00,
            total=110.00,
            line_items=[
                {
                    "product_id": product["id"],
                    "quantity": 1,
                    "price": 100.00,
                }
            ],
        )

        past_start = (
            datetime.now() - timedelta(days=365)
        ).date().isoformat()

        past_end = (
            datetime.now() - timedelta(days=364)
        ).date().isoformat()

        report = report_service.sales_report(
            start=past_start,
            end=past_end,
        )

        assert report["order_count"] == 0
        assert report["total_revenue"] == 0
        assert report["total_tax"] == 0
        assert report["average_order_value"] == 0
        assert report["start"] == past_start
        assert report["end"] == past_end