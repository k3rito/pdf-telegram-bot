from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.user import User
from database.repositories.base import Repository


class UserRepository(Repository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get(self, user_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.user_id == user_id))
        return result.scalar_one_or_none()

    async def ensure(self, user_id: int, username: str) -> User:
        user = await self.get(user_id)
        if user is None:
            user = User(user_id=user_id, username=username, banned=False)
            self.session.add(user)
        else:
            user.username = username
        return user

    async def ban(self, user_id: int, banned: bool) -> None:
        user = await self.get(user_id)
        if user is None:
            return
        user.banned = banned
