from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from database.repositories.stats import StatsRepository
from database.repositories.tasks import TaskRepository
from database.repositories.users import UserRepository


class UnitOfWork:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)
        self.tasks = TaskRepository(session)
        self.stats = StatsRepository(session)

    async def __aenter__(self) -> "UnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if exc:
            await self.session.rollback()
        else:
            try:
                await self.session.commit()
            except OperationalError:
                await self.session.rollback()
                raise


@asynccontextmanager
async def unit_of_work(session: AsyncSession) -> AsyncIterator[UnitOfWork]:
    uow = UnitOfWork(session)
    try:
        yield uow
        await session.commit()
    except Exception:
        await session.rollback()
        raise
