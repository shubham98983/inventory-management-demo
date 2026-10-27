PRODUCT = {"sku": "ABC-100", "name": "Desk Lamp", "price": 25.5, "cost": 10, "quantity": 30}


def test_create_and_get_product(client, auth_headers):
    created = client.post("/api/products", json=PRODUCT, headers=auth_headers)
    assert created.status_code == 201
    product_id = created.get_json()["id"]

    fetched = client.get(f"/api/products/{product_id}", headers=auth_headers)
    assert fetched.status_code == 200
    assert fetched.get_json()["sku"] == "ABC-100"


def test_duplicate_sku_is_rejected(client, auth_headers):
    client.post("/api/products", json=PRODUCT, headers=auth_headers)
    response = client.post("/api/products", json=PRODUCT, headers=auth_headers)
    assert response.status_code == 409


def test_invalid_payload_returns_errors(client, auth_headers):
    response = client.post("/api/products", json={"sku": "x"}, headers=auth_headers)
    assert response.status_code == 400
    assert response.get_json()["errors"]


def test_update_product(client, auth_headers):
    product_id = client.post("/api/products", json=PRODUCT, headers=auth_headers).get_json()["id"]
    response = client.put(
        f"/api/products/{product_id}", json={"price": 30.0}, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.get_json()["price"] == 30.0


def test_list_products_is_paginated(client, auth_headers):
    for index in range(5):
        payload = dict(PRODUCT, sku=f"ITEM-{index:03d}", name=f"Item {index}")
        client.post("/api/products", json=payload, headers=auth_headers)
    response = client.get("/api/products?page=1&page_size=2", headers=auth_headers)
    body = response.get_json()
    assert len(body["items"]) == 2
    assert body["meta"]["total"] == 5
    assert body["meta"]["pages"] == 3


def test_search_finds_product_by_name(client, auth_headers):
    client.post("/api/products", json=PRODUCT, headers=auth_headers)
    response = client.get("/api/products/search?q=Lamp", headers=auth_headers)
    assert [item["sku"] for item in response.get_json()] == ["ABC-100"]


def test_delete_product(client, auth_headers):
    product_id = client.post("/api/products", json=PRODUCT, headers=auth_headers).get_json()["id"]
    response = client.delete(f"/api/products/{product_id}", headers=auth_headers)
    assert response.status_code == 200
    assert client.get(f"/api/products/{product_id}", headers=auth_headers).status_code == 404


def test_delete_product_requires_authentication(client, make_product):
    product = make_product(sku="DELETE-UNAUTH")

    response = client.delete(f"/api/products/{product.id}")

    assert response.status_code == 401
    assert client.get(f"/api/products/{product.id}").status_code == 401
    # Verify persistence through the repository because the read endpoint is also protected.
    from app.repositories import product_repo

    assert product_repo.get_product(product.id) is not None


def test_delete_product_rejects_invalid_token_without_deleting(client, make_product):
    product = make_product(sku="DELETE-BAD-TOKEN")

    response = client.delete(
        f"/api/products/{product.id}",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
    from app.repositories import product_repo

    assert product_repo.get_product(product.id) is not None
