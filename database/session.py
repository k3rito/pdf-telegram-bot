from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from core.config.settings import AppSettings, get_settings
from database.base import Base


def _database_url(settings: AppSettings) -> str:
    if settings.database_url:
        return settings.database_url
    if settings.db_backend == "postgresql":
        password = settings.db_password.get_secret_value()
        return (
            f"postgresql+asyncpg://{settings.db_user}:{password}"
            f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
        )
    return f"sqlite+aiosqlite:///{settings.db_path.as_posix()}"


@lru_cache(maxsize=1)
def get_engine(settings: AppSettings | None = None) -> AsyncEngine:
    settings = settings or get_settings()
    url = _database_url(settings)
    engine_kwargs = {"echo": False, "pool_pre_ping": True}
    if url.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    else:
        engine_kwargs["pool_recycle"] = 1800
    return create_async_engine(url, **engine_kwargs)


@lru_cache(maxsize=1)
def get_sessionmaker(settings: AppSettings | None = None) -> async_sessionmaker[AsyncSession]:
    engine = get_engine(settings)
    return async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def session_scope(settings: AppSettings | None = None) -> AsyncIterator[AsyncSession]:
    factory = get_sessionmaker(settings)
    async with factory() as session:
        yield session


async def init_models(settings: AppSettings | None = None) -> None:
    engine = get_engine(settings)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
