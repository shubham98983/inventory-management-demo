def test_register_and_login(client):
    response = client.post(
        "/api/auth/register",
        json={"username": "alice", "email": "alice@example.com", "password": "secret123"},
    )
    assert response.status_code == 201
    assert "password_hash" not in response.get_json()

    login = client.post("/api/auth/login", json={"username": "alice", "password": "secret123"})
    assert login.status_code == 200
    assert "token" in login.get_json()


def test_login_with_wrong_password_fails(client):
    client.post(
        "/api/auth/register",
        json={"username": "bob", "email": "bob@example.com", "password": "secret123"},
    )
    response = client.post("/api/auth/login", json={"username": "bob", "password": "wrong"})
    assert response.status_code == 401


def test_register_rejects_duplicate_username(client):
    payload = {"username": "carol", "email": "carol@example.com", "password": "secret123"}
    assert client.post("/api/auth/register", json=payload).status_code == 201
    payload["email"] = "other@example.com"
    assert client.post("/api/auth/register", json=payload).status_code == 409


def test_protected_route_requires_token(client):
    assert client.get("/api/products").status_code == 401


def test_me_returns_current_user(client, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()["username"] == "tester"
