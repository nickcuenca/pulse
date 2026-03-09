"""FastAPI application entrypoint."""

import time
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .database import engine
from .models import Base
from .routers import services, metrics, rules, alerts


@asynccontextmanager
async def lifespan(app: FastAPI):
    for attempt in range(10):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            break
        except Exception:
            if attempt == 9:
                raise
            time.sleep(2)
    Base.metadata.create_all(bind=engine)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Pulse",
        description="Backend observability platform",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health():
        return {"status": "ok"}

    app.include_router(services.router)
    app.include_router(metrics.router)
    app.include_router(rules.router)
    app.include_router(alerts.router)

    return app


app = create_app()