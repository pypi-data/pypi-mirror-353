import pytest
from mono_connect.client import MonoConnectClient, MonoConnectError


@pytest.fixture
def client():
    return MonoConnectClient("test_sk_dummy")


def test_get_account_details(monkeypatch, client):
    def mock_get(*args, **kwargs):
        return {"status": "successful", "data": {"account": {"id": "test"}}}

    client._get = mock_get
    resp = client.get_account_details("test")
    assert resp["status"] == "successful"
    assert resp["data"]["account"]["id"] == "test"


def test_get_account_identity(monkeypatch, client):
    def mock_get(*args, **kwargs):
        return {"status": "successful", "data": {"full_name": "Test User"}}

    client._get = mock_get
    resp = client.get_account_identity("test")
    assert resp["data"]["full_name"] == "Test User"


def test_unlink_account(monkeypatch, client):
    def mock_post(*args, **kwargs):
        return {"status": "successful"}

    client._post = mock_post
    resp = client.unlink_account("test")
    assert resp["status"] == "successful"
