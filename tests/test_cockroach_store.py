import os
import unittest
from datetime import datetime
from uuid import uuid4
from unittest.mock import patch

from app.cockroach_store import CockroachStore
from app.schemas import AgentCreate, TaskCreate


class CockroachStoreTests(unittest.TestCase):
    def test_prefers_cockroach_dsn_over_cockroachdb_url(self) -> None:
        with patch.dict(os.environ, {"COCKROACH_DSN": "dsn-from-cockroach", "COCKROACHDB_URL": "dsn-from-url"}, clear=True):
            self.assertEqual(CockroachStore().dsn, "dsn-from-cockroach")

    def test_falls_back_to_cockroachdb_url(self) -> None:
        with patch.dict(os.environ, {"COCKROACHDB_URL": "dsn-from-url"}, clear=True):
            self.assertEqual(CockroachStore().dsn, "dsn-from-url")

    def test_create_agent_uses_db_path_when_dsn_is_present(self) -> None:
        store = CockroachStore(dsn="postgresql://example")
        agent_id = uuid4()
        created_at = datetime.utcnow()
        updated_at = datetime.utcnow()

        class FakeCursor:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def execute(self, query, params):
                self.query = query
                self.params = params

            def fetchone(self):
                return (agent_id, created_at, updated_at)

        class FakeConnection:
            def __init__(self):
                self.cursor_obj = FakeCursor()
                self.closed = False

            def cursor(self):
                return self.cursor_obj

            def close(self):
                self.closed = True

        fake_connection = FakeConnection()
        store.get_connection = lambda: fake_connection  # type: ignore[assignment]

        result = store.create_agent(AgentCreate(agent_key="agent-alpha", name="Agent Alpha"))

        self.assertEqual(result.agent_id, agent_id)
        self.assertEqual(fake_connection.cursor_obj.params[0], "agent-alpha")
        self.assertTrue(result.agent_key == "agent-alpha")

    def test_create_task_uses_db_path_when_dsn_is_present(self) -> None:
        store = CockroachStore(dsn="postgresql://example")
        task_id = uuid4()
        created_at = datetime.utcnow()
        updated_at = datetime.utcnow()

        class FakeCursor:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def execute(self, query, params):
                self.query = query
                self.params = params

            def fetchone(self):
                return (task_id, created_at, updated_at)

        class FakeConnection:
            def __init__(self):
                self.cursor_obj = FakeCursor()
                self.closed = False

            def cursor(self):
                return self.cursor_obj

            def close(self):
                self.closed = True

        fake_connection = FakeConnection()
        store.get_connection = lambda: fake_connection  # type: ignore[assignment]

        result = store.create_task(TaskCreate(task_key="task-001", title="Investigate", description="desc"))

        self.assertEqual(result.task_id, task_id)
        self.assertEqual(fake_connection.cursor_obj.params[0], "task-001")
        self.assertEqual(result.title, "Investigate")


if __name__ == "__main__":
    unittest.main()
