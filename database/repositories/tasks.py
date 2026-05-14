from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.task import TaskRecord
from database.repositories.base import Repository


class TaskRepository(Repository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def add(self, task_id: str, user_id: int, service: str, status: str, payload: str | None = None) -> TaskRecord:
        record = TaskRecord(
            id=task_id,
            user_id=user_id,
            service=service,
            status=status,
            payload=payload,
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(record)
        return record

    async def update_status(self, task_id: str, status: str) -> None:
        record = await self.get(task_id)
        if record is None:
            return
        record.status = status
        record.finished_at = datetime.now(timezone.utc)

    async def get(self, task_id: str) -> TaskRecord | None:
        result = await self.session.execute(select(TaskRecord).where(TaskRecord.id == task_id))
        return result.scalar_one_or_none()
