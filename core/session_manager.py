from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path

from utils.temp_files import cleanup_dir, create_temp_dir


@dataclass
class UserSession:
    chat_id: int
    user_id: int
    service: str
    temp_dir: Path
    files: list[dict] = field(default_factory=list)
    params: dict = field(default_factory=dict)
    awaiting_input: str | None = None
    locked: bool = False
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    last_message_id: int | None = None

    def touch(self) -> None:
        self.last_activity = time.time()


class SessionManager:
    def __init__(self, temp_root: Path, ttl_seconds: int = 7200) -> None:
        self.temp_root = temp_root
        self.ttl_seconds = ttl_seconds
        self._sessions: dict[tuple[int, int], UserSession] = {}

    def create(self, chat_id: int, user_id: int, service: str) -> UserSession:
        self.clear(chat_id, user_id)
        temp_dir = create_temp_dir(self.temp_root, chat_id, user_id)
        session = UserSession(chat_id=chat_id, user_id=user_id, service=service, temp_dir=temp_dir)
        self._sessions[(chat_id, user_id)] = session
        return session

    def get(self, chat_id: int, user_id: int) -> UserSession | None:
        return self._sessions.get((chat_id, user_id))

    def clear(self, chat_id: int, user_id: int) -> None:
        session = self._sessions.pop((chat_id, user_id), None)
        if session:
            cleanup_dir(session.temp_dir)

    def cleanup_expired(self) -> int:
        now = time.time()
        expired = [
            key
            for key, session in self._sessions.items()
            if (now - session.last_activity) > self.ttl_seconds
        ]
        for chat_id, user_id in expired:
            self.clear(chat_id, user_id)
        return len(expired)
