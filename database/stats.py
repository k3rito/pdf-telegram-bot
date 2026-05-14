from __future__ import annotations

from database.db import Database
from database.models import UserProfile


async def get_profile(db: Database, user_id: int) -> UserProfile:
    total_tasks, total_files, favorite = await db.get_user_profile(user_id)
    return UserProfile(total_tasks=total_tasks, total_files=total_files, favorite_service=favorite)


async def get_admin_overview(db: Database) -> dict:
    return await db.get_admin_stats()
