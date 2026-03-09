# Pulse

Backend observability platform: register services, ingest metrics, and receive threshold-based alerts.

## Tech stack (Phase 1)

- **Backend:** Python, FastAPI, PostgreSQL, SQLAlchemy, Pydantic
- **Run:** Docker, Docker Compose
- **CI:** GitHub Actions (pytest on push)

## Quick start (backend only)

```bash
# Start API + Postgres
docker compose up --build

# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

## API overview

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check `{"status": "ok"}` |
| POST | `/services` | Register a service |
| GET | `/services` | List all services |
| GET | `/services/{id}` | Get service by id |
| POST | `/services/{id}/metrics` | Ingest a metric (triggers alert evaluation) |
| GET | `/services/{id}/metrics` | List metrics (query: `metric_name`, `start`, `end`, `limit`) |
| POST | `/services/{id}/rules` | Create an alert rule |
| GET | `/services/{id}/rules` | List rules for a service |
| GET | `/services/{id}/alerts` | List alerts for a service (query: `state=ACTIVE\|RESOLVED`) |
| GET | `/alerts` | List all alerts (query: `state=ACTIVE\|RESOLVED`) |

## Running tests

```bash
# In repo root; uses in-memory SQLite by default
pip install -r requirements.txt
pytest tests/ -v
```

## Project layout (Phase 1)

```
pulse/
├── api/
│   ├── main.py
│   ├── routers/ (services, metrics, rules, alerts)
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   └── evaluation.py   # Alert evaluation on metric ingest
├── tests/
├── Dockerfile.api
├── docker-compose.yml   # api + postgres
└── .github/workflows/ci.yml
```

Frontend, load-test, and AWS deployment are planned for later phases.
