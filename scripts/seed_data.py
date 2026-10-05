"""Populate the database with sample data.

Usage:  python -m scripts.seed_data
"""
from app import create_app
from app.db import init_db
from app.repositories import category_repo, product_repo, supplier_repo
from app.services import auth_service, sales_service

CATEGORIES = [
    ("Electronics", "Phones, chargers and accessories"),
    ("Office Supplies", "Stationery and desk items"),
    ("Furniture", "Chairs, desks and storage"),
    ("Kitchen", "Appliances and utensils"),
    ("Tools", "Hand tools and hardware"),
]

SUPPLIERS = [
    {"name": "Acme Distributors", "contact_email": "sales@acme.example", "phone": "555-0101"},
    {"name": "Globex Trading", "contact_email": "orders@globex.example", "phone": "555-0102"},
    {"name": "Initech Wholesale", "contact_email": "hello@initech.example", "phone": "555-0103"},
    {"name": "Umbrella Supplies", "contact_email": "supply@umbrella.example", "phone": "555-0104"},
]

# sku, name, category index, supplier index, price, cost, quantity, reorder level
PRODUCTS = [
    ("ELEC-001", "USB-C Cable 1m", 0, 0, 9.99, 3.50, 120, 25),
    ("ELEC-002", "Wireless Mouse", 0, 0, 19.99, 8.00, 8, 15),
    ("ELEC-003", "Bluetooth Speaker", 0, 1, 49.99, 22.00, 35, 10),
    ("ELEC-004", "Phone Charger 20W", 0, 0, 14.99, 5.25, 10, 10),
    ("ELEC-005", "Webcam HD", 0, 1, 39.99, 17.50, 0, 5),
    ("OFF-001", "A4 Paper Ream", 1, 2, 5.49, 2.80, 300, 50),
    ("OFF-002", "Ballpoint Pens (12)", 1, 2, 3.99, 1.20, 90, 30),
    ("OFF-003", "Stapler", 1, 2, 7.50, 3.10, 4, 10),
    ("OFF-004", "Sticky Notes", 1, 2, 2.99, 0.90, 150, 40),
    ("FUR-001", "Office Chair", 2, 3, 129.00, 70.00, 12, 5),
    ("FUR-002", "Standing Desk", 2, 3, 349.00, 210.00, 3, 4),
    ("FUR-003", "Bookshelf", 2, 3, 89.00, 45.00, 9, 4),
    ("KIT-001", "Electric Kettle", 3, 1, 29.99, 14.00, 22, 8),
    ("KIT-002", "Coffee Maker", 3, 1, 59.99, 30.00, 7, 8),
    ("KIT-003", "Knife Set", 3, 1, 44.50, 19.00, 16, 6),
    ("TOOL-001", "Hammer", 4, 3, 12.99, 5.00, 40, 10),
    ("TOOL-002", "Screwdriver Set", 4, 3, 18.99, 8.20, 25, 10),
    ("TOOL-003", "Cordless Drill", 4, 3, 79.99, 41.00, 6, 6),
    ("TOOL-004", "Tape Measure", 4, 3, 6.49, 2.40, 55, 15),
]


def seed():
    app = create_app()
    with app.app_context():
        init_db()
        auth_service.ensure_default_admin()

        category_ids = [category_repo.create_category(n, d) for n, d in CATEGORIES]
        supplier_ids = [supplier_repo.create_supplier(s) for s in SUPPLIERS]

        product_ids = []
        for sku, name, cat, sup, price, cost, qty, reorder in PRODUCTS:
            product_ids.append(
                product_repo.create_product(
                    {
                        "sku": sku,
                        "name": name,
                        "category_id": category_ids[cat],
                        "supplier_id": supplier_ids[sup],
                        "price": price,
                        "cost": cost,
                        "quantity": qty,
                        "reorder_level": reorder,
                    }
                )
            )

        sales_service.create_sale(1, [{"product_id": product_ids[0], "quantity": 20}])
        sales_service.create_sale(
            1,
            [
                {"product_id": product_ids[5], "quantity": 60},
                {"product_id": product_ids[6], "quantity": 12},
            ],
        )
        sales_service.create_sale(1, [{"product_id": product_ids[9], "quantity": 2}])
        print(f"Seeded {len(product_ids)} products, {len(category_ids)} categories.")


if __name__ == "__main__":
    seed()
