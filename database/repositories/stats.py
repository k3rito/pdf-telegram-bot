from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.stat import StatRecord
from database.repositories.base import Repository


class StatsRepository(Repository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def add(self, user_id: int, service: str, status: str, file_count: int, total_size: int) -> StatRecord:
        record = StatRecord(
            user_id=user_id,
            service=service,
            status=status,
            file_count=file_count,
            total_size=total_size,
        )
        self.session.add(record)
        return record

    async def user_summary(self, user_id: int) -> tuple[int, int, str | None]:
        total_tasks = await self.session.scalar(select(func.count()).select_from(StatRecord).where(StatRecord.user_id == user_id))
        total_files = await self.session.scalar(select(func.coalesce(func.sum(StatRecord.file_count), 0)).where(StatRecord.user_id == user_id, StatRecord.status == "success"))
        favorite = await self.session.scalar(
            select(StatRecord.service)
            .where(StatRecord.user_id == user_id, StatRecord.status == "success")
            .group_by(StatRecord.service)
            .order_by(func.count().desc())
            .limit(1)
        )
        return int(total_tasks or 0), int(total_files or 0), favorite
