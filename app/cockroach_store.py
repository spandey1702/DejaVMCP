from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

try:
    import psycopg
except ImportError:  # pragma: no cover - exercised in test environment
    psycopg = None

from app.schemas import AgentCreate, AgentRead, TaskClaimCreate, TaskClaimRead, TaskCreate, TaskDecisionCreate, TaskDecisionRead, TaskEventCreate, TaskEventRead, TaskRead


class CockroachStore:
    def __init__(self, dsn: Optional[str] = None) -> None:
        self.dsn = dsn or os.getenv("COCKROACH_DSN") or os.getenv("COCKROACHDB_URL")

    def is_configured(self) -> bool:
        return bool(self.dsn)

    def get_connection(self):
        if not self.dsn:
            raise RuntimeError("COCKROACH_DSN is not set")
        if psycopg is None:
            raise RuntimeError("Install psycopg to connect to CockroachDB")
        return psycopg.connect(self.dsn)

    def initialize_schema(self) -> dict:
        schema_path = Path(__file__).resolve().parent.parent / "infra" / "cockroach_schema.sql"
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found at {schema_path}")

        connection = self.get_connection()
        connection.autocommit = True
        try:
            with connection.cursor() as cursor:
                for statement in self._split_sql(schema_path.read_text(encoding="utf-8")):
                    if statement:
                        cursor.execute(statement)
        finally:
            connection.close()

        return {"status": "ok", "schema": str(schema_path)}

    def create_agent(self, payload: AgentCreate) -> AgentRead:
        return AgentRead.model_validate(payload.model_dump())

    def create_task(self, payload: TaskCreate) -> TaskRead:
        return TaskRead.model_validate(payload.model_dump())

    def create_claim(self, payload: TaskClaimCreate) -> TaskClaimRead:
        return TaskClaimRead.model_validate(payload.model_dump())

    def create_decision(self, payload: TaskDecisionCreate) -> TaskDecisionRead:
        return TaskDecisionRead.model_validate(payload.model_dump())

    def create_event(self, payload: TaskEventCreate) -> TaskEventRead:
        return TaskEventRead.model_validate(payload.model_dump())

    @staticmethod
    def _split_sql(sql_text: str) -> list[str]:
        statements = []
        for fragment in sql_text.split(";"):
            cleaned = fragment.strip()
            if cleaned:
                statements.append(cleaned)
        return statements
