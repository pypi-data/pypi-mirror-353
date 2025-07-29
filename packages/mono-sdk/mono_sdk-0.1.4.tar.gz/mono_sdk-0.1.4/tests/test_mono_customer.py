import pytest
from mono_customer.client import MonoCustomerClient, MonoCustomerError


@pytest.fixture
def client():
    return MonoCustomerClient("test_sk_dummy")


def test_create_customer(monkeypatch, client):
    def mock_post(*args, **kwargs):
        return {"status": "successful", "data": {"id": "cus_test"}}

    client.session.post = lambda *a, **k: type(
        "Resp", (), {"status_code": 201, "json": lambda: mock_post(), "ok": True}
    )()
    resp = client.create_customer({"email": "test@mono.co"})
    assert resp["status"] == "successful"
    assert resp["data"]["id"] == "cus_test"


def test_retrieve_customer(monkeypatch, client):
    def mock_get(*args, **kwargs):
        return {"status": "successful", "data": {"id": "cus_test"}}

    client.session.get = lambda *a, **k: type(
        "Resp", (), {"ok": True, "json": lambda: mock_get()}
    )()
    resp = client.retrieve_customer("cus_test")
    assert resp["data"]["id"] == "cus_test"
