"""Tests for Alerts API: GET /services/{id}/alerts, GET /alerts."""

import pytest
from fastapi.testclient import TestClient


def _create_service(client: TestClient, name: str = "test-svc"):
    r = client.post("/services", json={"name": name, "description": None})
    assert r.status_code == 200
    return r.json()["id"]


def test_list_service_alerts_empty(client: TestClient):
    sid = _create_service(client)
    r = client.get(f"/services/{sid}/alerts")
    assert r.status_code == 200
    assert r.json() == []


def test_list_service_alerts_filter_state(client: TestClient):
    sid = _create_service(client)
    # Create rule and trigger alert
    client.post(
        f"/services/{sid}/rules",
        json={"metric_name": "cpu", "threshold": 10.0, "condition": "ABOVE"},
    )
    client.post(f"/services/{sid}/metrics", json={"name": "cpu", "value": 50.0})
    r_active = client.get(f"/services/{sid}/alerts?state=ACTIVE")
    assert r_active.status_code == 200
    assert len(r_active.json()) >= 1
    r_resolved = client.get(f"/services/{sid}/alerts?state=RESOLVED")
    assert r_resolved.status_code == 200


def test_list_all_alerts_empty(client: TestClient):
    r = client.get("/alerts")
    assert r.status_code == 200
    assert r.json() == []


def test_list_all_alerts(client: TestClient):
    sid = _create_service(client)
    client.post(
        f"/services/{sid}/rules",
        json={"metric_name": "x", "threshold": 0.0, "condition": "ABOVE"},
    )
    client.post(f"/services/{sid}/metrics", json={"name": "x", "value": 1.0})
    r = client.get("/alerts")
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 1
    assert data[0]["state"] == "ACTIVE"
    assert data[0]["metric_value"] == 1.0
