from __future__ import annotations

from api.routes.admin import router as admin_router
from api.routes.health import router as health_router

__all__ = ["admin_router", "health_router"]
