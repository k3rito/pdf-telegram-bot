from __future__ import annotations

import unittest

from monitoring.health import liveness, readiness


class HealthTests(unittest.TestCase):
    def test_liveness(self) -> None:
        self.assertTrue(liveness().ok)

    def test_readiness(self) -> None:
        self.assertTrue(readiness({"database": True, "queue": True}).ok)


if __name__ == "__main__":
    unittest.main()
