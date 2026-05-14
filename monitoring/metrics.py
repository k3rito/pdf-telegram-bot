from __future__ import annotations

try:  # pragma: no cover - production path
    from prometheus_client import Counter, Gauge, Histogram
except Exception:  # pragma: no cover - fallback for environments without the dependency
    class _NoOpMetric:
        def __init__(self, *args, **kwargs) -> None:
            self.args = args
            self.kwargs = kwargs

        def labels(self, *args, **kwargs):
            return self

        def inc(self, amount: int | float = 1) -> None:
            _ = amount

        def dec(self, amount: int | float = 1) -> None:
            _ = amount

        def observe(self, amount: int | float) -> None:
            _ = amount

        def set(self, value: int | float) -> None:
            _ = value

    Counter = Gauge = Histogram = _NoOpMetric  # type: ignore[assignment]

COMMAND_COUNTER = Counter("pdfbot_commands_total", "Total commands processed", ["command", "status"])
TASK_COUNTER = Counter("pdfbot_tasks_total", "Total tasks processed", ["service", "status"])
TASK_DURATION = Histogram("pdfbot_task_duration_seconds", "Task duration seconds", ["service"])
OCR_SUCCESS = Counter("pdfbot_ocr_success_total", "OCR success count")
OCR_FAILURE = Counter("pdfbot_ocr_failure_total", "OCR failure count")
ACTIVE_USERS = Gauge("pdfbot_active_users", "Active users")
QUEUE_DEPTH = Gauge("pdfbot_queue_depth", "Queue depth")
WORKER_COUNT = Gauge("pdfbot_worker_count", "Worker count")
