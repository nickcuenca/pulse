# Pulse

Pulse is a full-stack observability platform for registering services, ingesting metrics, and receiving threshold-based alerts. A React/TypeScript dashboard visualizes real-time metrics, alert states, and service health.

---

## Tech Stack

- **Backend:** Python, FastAPI, PostgreSQL, SQLAlchemy, Pydantic
- **Frontend:** React, TypeScript, Recharts
- **Infrastructure:** Docker, Docker Compose, GitHub Actions

---

## Quick Start

```bash
docker compose up --build
```

- API: http://localhost:8000
- Dashboard: http://localhost:3000
- API Docs: http://localhost:8000/docs

---

## API Overview

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/services` | Register a service |
| GET | `/services` | List all services |
| GET | `/services/{id}` | Get service by id |
| POST | `/services/{id}/metrics` | Ingest a metric (triggers alert evaluation) |
| GET | `/services/{id}/metrics` | List metrics (query: `metric_name`, `start`, `end`, `limit`) |
| POST | `/services/{id}/rules` | Create an alert rule |
| GET | `/services/{id}/rules` | List rules for a service |
| GET | `/services/{id}/alerts` | List alerts for a service (query: `state=ACTIVE\|RESOLVED`) |
| GET | `/alerts` | List all alerts |

---

## Alert Evaluation

After every metric ingestion, Pulse runs an evaluation pipeline:
- Fetches all alert rules matching the service and metric name
- Creates an `ACTIVE` alert if the threshold is breached and no active alert exists
- Resolves the alert automatically when the value returns within bounds

---

## 📊 Performance

Load tested with [Artillery](https://www.artillery.io/) across warm-up (10 req/s), sustained (50 req/s), and peak (100 req/s) phases.

| Metric | Result |
|---|---|
| Sustained throughput | **1,500+ datapoints/min** |
| p95 API latency | **<20ms** |
| Alert detection time | **<1 second** |
| Error rate (sustained) | **0%** |

---

## Running Tests

```bash
pip install -r requirements.txt
PYTHONPATH=. pytest tests/ -v
```

28 tests covering all endpoints, alert evaluation logic, and edge cases.

---

## Project Layout

```
pulse/
├── api/
│   ├── main.py
│   ├── routers/         # services, metrics, rules, alerts
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   └── evaluation.py    # Alert evaluation pipeline
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── MetricsChart.tsx   # Recharts time-series, polls every 5s
│   │   │   ├── ServiceList.tsx
│   │   │   └── AlertsPanel.tsx    # ACTIVE/RESOLVED alerts, polls every 5s
│   │   └── api.ts
│   └── vite.config.ts
├── tests/
├── load-test/
│   └── load-test.yml
├── Dockerfile.api
├── Dockerfile.frontend
├── docker-compose.yml
└── .github/workflows/ci.yml
```
