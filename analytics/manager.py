from __future__ import annotations

from analytics.jobs import AnalyticsJobs
from analytics.retention import RetentionPolicy
from database.db import Database


class AnalyticsManager:
    def __init__(self, db: Database) -> None:
        self.jobs = AnalyticsJobs(db)
        self.retention = RetentionPolicy()

    async def daily_summary(self):
        return await self.jobs.build_daily_summary()
