from __future__ import annotations

import contextvars
import uuid
from dataclasses import dataclass

trace_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("trace_id", default="")
correlation_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("correlation_id", default="")


@dataclass(slots=True)
class TraceContext:
    trace_id: str
    correlation_id: str


def new_trace_context() -> TraceContext:
    trace_id = uuid.uuid4().hex
    correlation_id = uuid.uuid4().hex
    trace_id_var.set(trace_id)
    correlation_id_var.set(correlation_id)
    return TraceContext(trace_id=trace_id, correlation_id=correlation_id)
