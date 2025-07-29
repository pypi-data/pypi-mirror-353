import pytest
from mono_lookup.client import MonoLookupClient, MonoLookupError


@pytest.fixture
def client():
    return MonoLookupClient("test_sk_dummy")


def test_initiate_bvn_lookup(monkeypatch, client):
    def mock_post(*args, **kwargs):
        return {"status": "successful", "data": {"session_id": "sess_test"}}

    client.session.post = lambda *a, **k: type(
        "Resp", (), {"ok": True, "json": lambda: mock_post()}
    )()
    resp = client.initiate_bvn_lookup({"bvn": "12345678901"})
    assert resp["status"] == "successful"
    assert resp["data"]["session_id"] == "sess_test"
