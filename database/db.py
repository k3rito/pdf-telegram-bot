from __future__ import annotations

from pathlib import Path

from core.config.settings import AppSettings, get_settings
from database.models import User
from database.repositories import unit_of_work
from database.session import get_sessionmaker, init_models
from sqlalchemy import text


class Database:
    def __init__(self, path: Path, settings: AppSettings | None = None) -> None:
        self.path = path
        self.settings = settings or get_settings()
        self._session_factory = get_sessionmaker(self.settings)
        self._initialized = False

    async def connect(self) -> None:
        if not self._initialized:
            await init_models(self.settings)
            self._initialized = True

    async def close(self) -> None:
        return None

    async def ensure_user(self, user_id: int, username: str) -> None:
        async with self._session_factory() as session:
            async with unit_of_work(session) as uow:
                await uow.users.ensure(user_id, username)

    async def is_banned(self, user_id: int) -> bool:
        async with self._session_factory() as session:
            user = await session.get(User, user_id)
            return bool(user and user.banned)

    async def set_ban(self, user_id: int, banned: bool) -> None:
        async with self._session_factory() as session:
            async with unit_of_work(session) as uow:
                await uow.users.ban(user_id, banned)

    async def add_stat(self, user_id: int, service: str, status: str, file_count: int, total_size: int) -> None:
        async with self._session_factory() as session:
            async with unit_of_work(session) as uow:
                await uow.stats.add(user_id, service, status, file_count, total_size)

    async def add_task(self, task_id: str, user_id: int, service: str, status: str) -> None:
        async with self._session_factory() as session:
            async with unit_of_work(session) as uow:
                await uow.tasks.add(task_id, user_id, service, status)

    async def update_task_status(self, task_id: str, status: str) -> None:
        async with self._session_factory() as session:
            async with unit_of_work(session) as uow:
                await uow.tasks.update_status(task_id, status)

    async def get_user_profile(self, user_id: int) -> tuple[int, int, str | None]:
        async with self._session_factory() as session:
            total_tasks_result = await session.execute(text("SELECT COUNT(*) FROM stats WHERE user_id = :user_id"), {"user_id": user_id})
            total_files_result = await session.execute(
                text("SELECT COALESCE(SUM(file_count), 0) FROM stats WHERE user_id = :user_id AND status = 'success'"),
                {"user_id": user_id},
            )
            favorite_result = await session.execute(
                text(
                    """
                    SELECT service
                    FROM stats
                    WHERE user_id = :user_id AND status = 'success'
                    GROUP BY service
                    ORDER BY COUNT(*) DESC
                    LIMIT 1
                    """
                ),
                {"user_id": user_id},
            )
            total_tasks = total_tasks_result.scalar_one_or_none() or 0
            total_files = total_files_result.scalar_one_or_none() or 0
            favorite = favorite_result.scalar_one_or_none()
            return int(total_tasks), int(total_files), favorite

    async def get_admin_stats(self) -> dict:
        async with self._session_factory() as session:
            users = await session.execute(text("SELECT COUNT(*) FROM users"))
            files = await session.execute(text("SELECT COALESCE(SUM(file_count), 0) FROM stats WHERE status = 'success'"))
            banned = await session.execute(text("SELECT COUNT(*) FROM users WHERE banned = 1"))
            top_service = await session.execute(
                text(
                    """
                    SELECT service
                    FROM stats
                    WHERE status = 'success'
                    GROUP BY service
                    ORDER BY COUNT(*) DESC
                    LIMIT 1
                    """
                )
            )
            return {
                "users": int(users.scalar_one_or_none() or 0),
                "files": int(files.scalar_one_or_none() or 0),
                "top_service": top_service.scalar_one_or_none() or "-",
                "banned": int(banned.scalar_one_or_none() or 0),
            }

    async def get_all_user_ids(self) -> list[int]:
        async with self._session_factory() as session:
            rows = await session.execute(text("SELECT user_id FROM users"))
            return [int(row[0]) for row in rows.fetchall()]
