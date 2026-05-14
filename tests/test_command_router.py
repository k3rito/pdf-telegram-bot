from __future__ import annotations

import unittest
from dataclasses import dataclass

from core.prefix_parser import PrefixParser


@dataclass
class FakeEntity:
    offset: int
    length: int
    type: str


class PrefixParserTests(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = PrefixParser("@pdf")

    def test_accepts_exact_prefix(self) -> None:
        parsed = self.parser.parse("@pdf merge", None, "group", [FakeEntity(0, 4, "mention")])
        self.assertIsNotNone(parsed)
        assert parsed is not None
        self.assertEqual(parsed.command, "merge")
        self.assertEqual(parsed.args, [])

    def test_accepts_prefix_only_as_help(self) -> None:
        parsed = self.parser.parse("@pdf", None, "private", [FakeEntity(0, 4, "mention")])
        self.assertIsNotNone(parsed)
        assert parsed is not None
        self.assertEqual(parsed.command, "help")

    def test_rejects_plain_text(self) -> None:
        self.assertIsNone(self.parser.parse("merge", None, "group", []))

    def test_rejects_wrong_bot_mention(self) -> None:
        self.assertIsNone(
            self.parser.parse("@pdf@otherbot merge", "realbot", "group", [FakeEntity(0, 14, "mention")])
        )


if __name__ == "__main__":
    unittest.main()