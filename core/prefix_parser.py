from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(slots=True)
class ParsedCommand:
    command: str
    args: list[str]
    prefix: str
    raw_text: str
    bot_username: str | None
    chat_type: str


class PrefixParser:
    def __init__(self, prefix_token: str) -> None:
        self.prefix_token = prefix_token.lower().strip()

    def parse(
        self,
        text: str,
        bot_username: str | None,
        chat_type: str,
        entities: Iterable[object] | None = None,
    ) -> ParsedCommand | None:
        raw_text = text.strip()
        if not raw_text or raw_text.startswith("/"):
            return None

        head, *tail = raw_text.split(maxsplit=1)
        if entities is not None and not self._matches_prefix_entity(raw_text, head, entities, bot_username):
            return None
        if not self._matches_prefix(head, bot_username):
            return None

        if tail:
            tokens = tail[0].split()
            command = tokens[0].lower() if tokens else "help"
            args = tokens[1:] if len(tokens) > 1 else []
        else:
            command = "help"
            args = []

        return ParsedCommand(
            command=command,
            args=args,
            prefix=head,
            raw_text=raw_text,
            bot_username=bot_username,
            chat_type=chat_type,
        )

    def _matches_prefix(self, token: str, bot_username: str | None) -> bool:
        normalized = token.lower().strip()
        if normalized == self.prefix_token:
            return True

        if "@" not in normalized:
            return False

        base, target = normalized.split("@", 1)
        if base != self.prefix_token.lstrip("@"):
            return False

        if not bot_username:
            return False

        return target == bot_username.lower()

    def _matches_prefix_entity(
        self,
        raw_text: str,
        head: str,
        entities: Iterable[object],
        bot_username: str | None,
    ) -> bool:
        first_entity = None
        for entity in entities:
            if getattr(entity, "offset", None) == 0:
                first_entity = entity
                break

        if first_entity is None:
            return self._matches_prefix(head, bot_username)

        entity_type = getattr(first_entity, "type", None)
        if entity_type not in {"mention", "text_mention", "bot_command"}:
            return False

        token = raw_text[: getattr(first_entity, "length", 0)].strip()
        return self._matches_prefix(token, bot_username)
