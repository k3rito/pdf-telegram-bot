from __future__ import annotations

import unittest

from core.config.settings import AppSettings


class SettingsTests(unittest.TestCase):
    def test_masking_hides_secret(self) -> None:
        settings = AppSettings(
            BOT_TOKEN="token",
            ADMIN_IDS="1",
            PREFIX_TOKEN="@pdf",
        )
        masked = settings.masked()
        self.assertEqual(masked["bot_token"], "***")


if __name__ == "__main__":
    unittest.main()
