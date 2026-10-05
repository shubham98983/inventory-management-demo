from app.utils import validators


def test_valid_product_payload_has_no_errors():
    assert validators.validate_product_payload({"sku": "ABC-1", "name": "Thing", "price": 5}) == []


def test_missing_required_fields():
    errors = validators.validate_product_payload({})
    assert len(errors) == 3


def test_partial_payload_does_not_require_fields():
    assert validators.validate_product_payload({"price": 9}, partial=True) == []


def test_negative_price_is_rejected():
    errors = validators.validate_product_payload({"sku": "ABC-1", "name": "T", "price": -1})
    assert any("price" in error for error in errors)


def test_invalid_sku_is_rejected():
    assert not validators.is_valid_sku("bad sku!")
    assert validators.is_valid_sku("GOOD-123")


def test_email_validation():
    assert validators.is_valid_email("a@b.co")
    assert not validators.is_valid_email("not-an-email")


def test_sale_payload_validation():
    assert validators.validate_sale_payload({"items": []})
    assert validators.validate_sale_payload({"items": [{"product_id": 1, "quantity": 0}]})
    assert validators.validate_sale_payload({"items": [{"product_id": 1, "quantity": 2}]}) == []
