"""Tests for Alert Rules API: POST/GET /services/{id}/rules."""

import pytest
from fastapi.testclient import TestClient


def _create_service(client: TestClient, name: str = "test-svc"):
    r = client.post("/services", json={"name": name, "description": None})
    assert r.status_code == 200
    return r.json()["id"]


def test_create_rule(client: TestClient):
    sid = _create_service(client)
    r = client.post(
        f"/services/{sid}/rules",
        json={"metric_name": "cpu_usage", "threshold": 90.0, "condition": "ABOVE"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["service_id"] == sid
    assert data["metric_name"] == "cpu_usage"
    assert data["threshold"] == 90.0
    assert data["condition"] == "ABOVE"
    assert "id" in data
    assert "created_at" in data


def test_create_rule_below(client: TestClient):
    sid = _create_service(client)
    r = client.post(
        f"/services/{sid}/rules",
        json={"metric_name": "free_memory_mb", "threshold": 100.0, "condition": "BELOW"},
    )
    assert r.status_code == 200
    assert r.json()["condition"] == "BELOW"


def test_create_rule_service_not_found(client: TestClient):
    r = client.post(
        "/services/00000000-0000-0000-0000-000000000000/rules",
        json={"metric_name": "x", "threshold": 1.0, "condition": "ABOVE"},
    )
    assert r.status_code == 404


def test_list_rules_empty(client: TestClient):
    sid = _create_service(client)
    r = client.get(f"/services/{sid}/rules")
    assert r.status_code == 200
    assert r.json() == []


def test_list_rules(client: TestClient):
    sid = _create_service(client)
    client.post(
        f"/services/{sid}/rules",
        json={"metric_name": "cpu", "threshold": 80.0, "condition": "ABOVE"},
    )
    client.post(
        f"/services/{sid}/rules",
        json={"metric_name": "mem", "threshold": 50.0, "condition": "BELOW"},
    )
    r = client.get(f"/services/{sid}/rules")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2
