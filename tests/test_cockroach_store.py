import os
import unittest
from unittest.mock import patch

from app.cockroach_store import CockroachStore


class CockroachStoreTests(unittest.TestCase):
    def test_prefers_cockroach_dsn_over_cockroachdb_url(self) -> None:
        with patch.dict(os.environ, {"COCKROACH_DSN": "dsn-from-cockroach", "COCKROACHDB_URL": "dsn-from-url"}, clear=True):
            self.assertEqual(CockroachStore().dsn, "dsn-from-cockroach")

    def test_falls_back_to_cockroachdb_url(self) -> None:
        with patch.dict(os.environ, {"COCKROACHDB_URL": "dsn-from-url"}, clear=True):
            self.assertEqual(CockroachStore().dsn, "dsn-from-url")


if __name__ == "__main__":
    unittest.main()
