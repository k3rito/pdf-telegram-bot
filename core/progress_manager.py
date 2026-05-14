from __future__ import annotations

import asyncio
from typing import Iterable


class ProgressManager:
    def __init__(self, frames: Iterable[str], messages: Iterable[str], interval: float = 2.0) -> None:
        self.frames = list(frames)
        self.messages = list(messages)
        self.interval = interval

    async def animate(self, message) -> None:
        index = 0
        while True:
            try:
                frame = self.frames[index % len(self.frames)]
                text = self.messages[index % len(self.messages)]
                await message.edit_text(f"{frame} {text}")
                index += 1
                await asyncio.sleep(self.interval)
            except Exception:
                break
