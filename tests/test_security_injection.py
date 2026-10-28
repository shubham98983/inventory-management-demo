def test_login_username_injection_does_not_bypass_password_check(client, auth_headers):
    injected_login = client.post(
        "/api/auth/login",
        json={"username": "tester' --", "password": "wrong-password"},
    )
    assert injected_login.status_code == 401

    normal_login = client.post(
        "/api/auth/login", json={"username": "tester", "password": "password123"}
    )
    assert normal_login.status_code == 200
    assert "token" in normal_login.get_json()


def test_product_search_injection_returns_no_products(client, auth_headers, make_product):
    product = make_product()

    injected_search = client.get(
        "/api/products/search", query_string={"q": "zzz' OR 1=1 --"}, headers=auth_headers
    )
    assert injected_search.status_code == 200
    assert injected_search.get_json() == []

    normal_search = client.get(
        "/api/products/search", query_string={"q": "Test Widget"}, headers=auth_headers
    )
    assert normal_search.status_code == 200
    assert [item["id"] for item in normal_search.get_json()] == [product.id]
