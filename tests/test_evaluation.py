"""Tests for alert evaluation pipeline (trigger and resolve)."""

import pytest
from fastapi.testclient import TestClient


def _create_service(client: TestClient, name: str = "eval-svc"):
    r = client.post("/services", json={"name": name, "description": None})
    assert r.status_code == 200
    return r.json()["id"]


def test_alert_triggered_above(client: TestClient):
    sid = _create_service(client)
    client.post(
        f"/services/{sid}/rules",
        json={"metric_name": "cpu_usage", "threshold": 80.0, "condition": "ABOVE"},
    )
    client.post(f"/services/{sid}/metrics", json={"name": "cpu_usage", "value": 95.0})
    r = client.get(f"/services/{sid}/alerts?state=ACTIVE")
    assert r.status_code == 200
    alerts = r.json()
    assert len(alerts) == 1
    assert alerts[0]["metric_value"] == 95.0
    assert alerts[0]["state"] == "ACTIVE"
    assert alerts[0]["resolved_at"] is None


def test_alert_not_triggered_below_threshold(client: TestClient):
    sid = _create_service(client)
    client.post(
        f"/services/{sid}/rules",
        json={"metric_name": "cpu_usage", "threshold": 80.0, "condition": "ABOVE"},
    )
    client.post(f"/services/{sid}/metrics", json={"name": "cpu_usage", "value": 50.0})
    r = client.get(f"/services/{sid}/alerts?state=ACTIVE")
    assert r.status_code == 200
    assert len(r.json()) == 0


def test_alert_triggered_below(client: TestClient):
    sid = _create_service(client)
    client.post(
        f"/services/{sid}/rules",
        json={"metric_name": "free_mb", "threshold": 100.0, "condition": "BELOW"},
    )
    client.post(f"/services/{sid}/metrics", json={"name": "free_mb", "value": 50.0})
    r = client.get(f"/services/{sid}/alerts?state=ACTIVE")
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["metric_value"] == 50.0


def test_alert_resolved_when_value_returns_below(client: TestClient):
    sid = _create_service(client)
    client.post(
        f"/services/{sid}/rules",
        json={"metric_name": "cpu", "threshold": 90.0, "condition": "ABOVE"},
    )
    client.post(f"/services/{sid}/metrics", json={"name": "cpu", "value": 95.0})
    r1 = client.get(f"/services/{sid}/alerts?state=ACTIVE")
    assert len(r1.json()) == 1
    # Send value below threshold
    client.post(f"/services/{sid}/metrics", json={"name": "cpu", "value": 50.0})
    r_active = client.get(f"/services/{sid}/alerts?state=ACTIVE")
    r_resolved = client.get(f"/services/{sid}/alerts?state=RESOLVED")
    assert len(r_active.json()) == 0
    assert len(r_resolved.json()) == 1
    assert r_resolved.json()[0]["resolved_at"] is not None


def test_no_duplicate_active_alert_for_same_rule(client: TestClient):
    sid = _create_service(client)
    client.post(
        f"/services/{sid}/rules",
        json={"metric_name": "x", "threshold": 10.0, "condition": "ABOVE"},
    )
    client.post(f"/services/{sid}/metrics", json={"name": "x", "value": 20.0})
    client.post(f"/services/{sid}/metrics", json={"name": "x", "value": 30.0})
    r = client.get(f"/services/{sid}/alerts?state=ACTIVE")
    assert len(r.json()) == 1


def test_metric_name_mismatch_does_not_trigger(client: TestClient):
    sid = _create_service(client)
    client.post(
        f"/services/{sid}/rules",
        json={"metric_name": "cpu_usage", "threshold": 80.0, "condition": "ABOVE"},
    )
    client.post(f"/services/{sid}/metrics", json={"name": "memory_usage", "value": 95.0})
    r = client.get(f"/services/{sid}/alerts?state=ACTIVE")
    assert len(r.json()) == 0
