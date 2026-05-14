from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
