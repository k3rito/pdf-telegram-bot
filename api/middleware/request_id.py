from __future__ import annotations

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from monitoring.tracing import new_trace_context


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace = new_trace_context()
        response = await call_next(request)
        response.headers["X-Trace-Id"] = trace.trace_id
        response.headers["X-Correlation-Id"] = trace.correlation_id
        return response
