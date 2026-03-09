"""Tests for Services API: POST/GET /services."""

import pytest
from fastapi.testclient import TestClient


def test_register_service(client: TestClient):
    r = client.post("/services", json={"name": "api-gateway", "description": "Main gateway"})
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "api-gateway"
    assert data["description"] == "Main gateway"
    assert "id" in data
    assert "created_at" in data


def test_register_service_duplicate_name(client: TestClient):
    client.post("/services", json={"name": "dup", "description": None})
    r = client.post("/services", json={"name": "dup", "description": "Again"})
    assert r.status_code == 409


def test_list_services_empty(client: TestClient):
    r = client.get("/services")
    assert r.status_code == 200
    assert r.json() == []


def test_list_services(client: TestClient):
    client.post("/services", json={"name": "s1", "description": None})
    client.post("/services", json={"name": "s2", "description": "Second"})
    r = client.get("/services")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2
    names = {s["name"] for s in data}
    assert names == {"s1", "s2"}


def test_get_service(client: TestClient):
    create = client.post("/services", json={"name": "my-svc", "description": "Mine"})
    assert create.status_code == 200
    sid = create.json()["id"]
    r = client.get(f"/services/{sid}")
    assert r.status_code == 200
    assert r.json()["name"] == "my-svc"
    assert r.json()["description"] == "Mine"


def test_get_service_not_found(client: TestClient):
    r = client.get("/services/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404
