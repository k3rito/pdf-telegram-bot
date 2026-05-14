from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from time import time
from typing import Any, Protocol


class QueueStatus(StrEnum):
    pending = "pending"
    delayed = "delayed"
    reserved = "reserved"
    success = "success"
    failed = "failed"
    canceled = "canceled"


@dataclass(slots=True)
class QueueTask:
    id: str
    user_id: int
    chat_id: int
    chat_type: str
    reply_to_message_id: int | None
    service: str
    file_paths: list[str]
    params: dict[str, Any]
    temp_dir: str
    priority: int = 0
    run_at: float = field(default_factory=time)
    retries_left: int = 1
    correlation_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = QueueStatus.pending.value
        return data

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "QueueTask":
        return cls(
            id=str(payload["id"]),
            user_id=int(payload["user_id"]),
            chat_id=int(payload["chat_id"]),
            chat_type=str(payload.get("chat_type", "private")),
            reply_to_message_id=payload.get("reply_to_message_id"),
            service=str(payload["service"]),
            file_paths=[str(item) for item in payload.get("file_paths", [])],
            params=dict(payload.get("params", {})),
            temp_dir=str(payload["temp_dir"]),
            priority=int(payload.get("priority", 0)),
            run_at=float(payload.get("run_at", time())),
            retries_left=int(payload.get("retries_left", 1)),
            correlation_id=payload.get("correlation_id"),
        )


@dataclass(slots=True)
class QueueLease:
    task: QueueTask
    backend_name: str
    leased_at: float = field(default_factory=time)
    lease_token: str | None = None


class QueueBackend(Protocol):
    name: str

    async def start(self) -> None:
        ...

    async def stop(self) -> None:
        ...

    async def enqueue(self, task: QueueTask) -> str:
        ...

    async def reserve(self, timeout: float | None = None) -> QueueLease | None:
        ...

    async def ack(self, task_id: str) -> None:
        ...

    async def nack(self, task_id: str, delay_seconds: int = 0) -> None:
        ...

    async def cancel(self, task_id: str) -> bool:
        ...

    def qsize(self) -> int:
        ...

    def snapshot(self) -> dict[str, int]:
        ...
