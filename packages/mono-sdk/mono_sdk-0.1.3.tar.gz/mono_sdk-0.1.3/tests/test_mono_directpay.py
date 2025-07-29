import pytest
from mono_directpay.client import MonoDirectpayClient, MonoDirectpayError


@pytest.fixture
def client():
    return MonoDirectpayClient("test_sk_dummy")


def test_initiate_payment(monkeypatch, client):
    def mock_post(*args, **kwargs):
        return {"status": "successful", "data": {"id": "pay_test"}}

    client.session.post = lambda *a, **k: type(
        "Resp", (), {"ok": True, "json": lambda: mock_post()}
    )()
    resp = client.initiate_payment({"amount": 1000})
    assert resp["status"] == "successful"
    assert resp["data"]["id"] == "pay_test"


def test_verify_transaction(monkeypatch, client):
    def mock_get(*args, **kwargs):
        return {"status": "successful", "data": {"id": "pay_test"}}

    client.session.get = lambda *a, **k: type(
        "Resp", (), {"ok": True, "json": lambda: mock_get()}
    )()
    resp = client.verify_transaction("pay_test")
    assert resp["data"]["id"] == "pay_test"
