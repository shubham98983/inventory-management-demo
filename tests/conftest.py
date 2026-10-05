import pytest

from app import create_app
from app.db import init_db
from app.repositories import product_repo
from app.services import auth_service


@pytest.fixture
def app(tmp_path):
    application = create_app(
        {
            "TESTING": True,
            "DATABASE": str(tmp_path / "test.db"),
            "BACKUP_DIR": str(tmp_path / "backups"),
        }
    )
    with application.app_context():
        init_db()
    return application


@pytest.fixture
def ctx(app):
    with app.app_context():
        yield


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(app, client):
    with app.app_context():
        auth_service.register_user("tester", "tester@example.com", "password123", role="admin")
    response = client.post("/api/auth/login", json={"username": "tester", "password": "password123"})
    token = response.get_json()["token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def make_product(ctx):
    def _make(**overrides):
        data = {
            "sku": "TEST-001",
            "name": "Test Widget",
            "price": 100.0,
            "cost": 60.0,
            "quantity": 50,
            "reorder_level": 10,
        }
        data.update(overrides)
        return product_repo.get_product(product_repo.create_product(data))

    return _make
