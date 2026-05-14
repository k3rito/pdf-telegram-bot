from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/queue")
async def queue_stats() -> dict:
    return {"TODO(PRODUCTION)": "Wire queue statistics from runtime state"}
