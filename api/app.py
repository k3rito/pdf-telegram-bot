from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from api.middleware.request_id import RequestIDMiddleware
from api.routes import admin_router, health_router
app = FastAPI(title="PDF Bot Internal API", version="1.0.0")
app.add_middleware(RequestIDMiddleware)
app.include_router(health_router, prefix="/health")
app.include_router(admin_router, prefix="/admin")

@app.get("/metrics")
async def metrics() -> PlainTextResponse:
    return PlainTextResponse(generate_latest().decode("utf-8"), media_type=CONTENT_TYPE_LATEST)


@app.get("/admin/queue")
async def admin_queue() -> dict:
    return {"TODO(PRODUCTION)": "Attach queue manager from bot state or dependency injection"}
