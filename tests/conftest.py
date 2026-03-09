"""Pytest fixtures: test client and DB session."""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

# Use in-memory SQLite for tests so CI doesn't require Postgres.
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from pulse.api.main import app
from pulse.api.database import Base, get_db, engine
from sqlalchemy.orm import sessionmaker

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def _clean_db():
    """Delete all data in dependency order so each test has a clean slate."""
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM alerts"))
        conn.execute(text("DELETE FROM metrics"))
        conn.execute(text("DELETE FROM alert_rules"))
        conn.execute(text("DELETE FROM services"))
        conn.commit()


@pytest.fixture(scope="session")
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def clean_db(setup_db):
    """Clean DB before each test for isolation."""
    _clean_db()
    yield


@pytest.fixture
def client(setup_db):
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
