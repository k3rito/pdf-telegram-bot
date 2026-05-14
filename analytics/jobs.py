from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta

from database.db import Database


@dataclass(slots=True)
class AnalyticsJobResult:
    day: date
    total_users: int
    total_files: int
    top_service: str


class AnalyticsJobs:
    def __init__(self, db: Database) -> None:
        self.db = db

    async def build_daily_summary(self) -> AnalyticsJobResult:
        stats = await self.db.get_admin_stats()
        return AnalyticsJobResult(
            day=datetime.utcnow().date(),
            total_users=stats.get("users", 0),
            total_files=stats.get("files", 0),
            top_service=stats.get("top_service", "-"),
        )
