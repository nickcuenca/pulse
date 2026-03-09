"""Tests for Metrics API: POST/GET /services/{id}/metrics."""

import pytest
from fastapi.testclient import TestClient


def _create_service(client: TestClient, name: str = "test-svc"):
    r = client.post("/services", json={"name": name, "description": None})
    assert r.status_code == 200
    return r.json()["id"]


def test_ingest_metric(client: TestClient):
    sid = _create_service(client)
    r = client.post(f"/services/{sid}/metrics", json={"name": "cpu_usage", "value": 0.75})
    assert r.status_code == 200
    data = r.json()
    assert data["service_id"] == sid
    assert data["name"] == "cpu_usage"
    assert data["value"] == 0.75
    assert "id" in data
    assert "timestamp" in data


def test_ingest_metric_service_not_found(client: TestClient):
    r = client.post(
        "/services/00000000-0000-0000-0000-000000000000/metrics",
        json={"name": "x", "value": 1.0},
    )
    assert r.status_code == 404


def test_get_metrics_empty(client: TestClient):
    sid = _create_service(client)
    r = client.get(f"/services/{sid}/metrics")
    assert r.status_code == 200
    assert r.json() == []


def test_get_metrics(client: TestClient):
    sid = _create_service(client)
    client.post(f"/services/{sid}/metrics", json={"name": "cpu_usage", "value": 0.5})
    client.post(f"/services/{sid}/metrics", json={"name": "cpu_usage", "value": 0.8})
    client.post(f"/services/{sid}/metrics", json={"name": "memory_mb", "value": 512.0})
    r = client.get(f"/services/{sid}/metrics")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 3


def test_get_metrics_filter_by_name(client: TestClient):
    sid = _create_service(client)
    client.post(f"/services/{sid}/metrics", json={"name": "cpu_usage", "value": 0.5})
    client.post(f"/services/{sid}/metrics", json={"name": "memory_mb", "value": 100.0})
    r = client.get(f"/services/{sid}/metrics?metric_name=cpu_usage")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["name"] == "cpu_usage"


def test_get_metrics_limit(client: TestClient):
    sid = _create_service(client)
    for i in range(5):
        client.post(f"/services/{sid}/metrics", json={"name": "x", "value": float(i)})
    r = client.get(f"/services/{sid}/metrics?limit=2")
    assert r.status_code == 200
    assert len(r.json()) == 2
