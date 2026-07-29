import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg.connect(os.environ["COCKROACHDB_URL"])

def run_query(sql: str, params: tuple):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            if cur.description:
                columns = [desc[0] for desc in cur.description]
                rows = cur.fetchall()
                return columns, rows
            return None, None

def create_agent(agent_key: str, name: str, role: str = None) -> str:
    _, rows = run_query(
        "INSERT INTO agents (agent_key, name, role) VALUES (%s, %s, %s) RETURNING agent_id",
        (agent_key, name, role),
    )
    return rows[0][0]

def create_task(task_key: str, title: str, description: str = None, created_by_agent_id: str = None) -> str:
    _, rows = run_query(
        "INSERT INTO tasks (task_key, title, description, created_by_agent_id) VALUES (%s, %s, %s, %s) RETURNING task_id",
        (task_key, title, description, created_by_agent_id),
    )
    return rows[0][0]

def claim_task(task_id: str, agent_id: str, note: str = None) -> str:
    try:
        _, rows = run_query(
            "INSERT INTO task_claims (task_id, agent_id, note) VALUES (%s, %s, %s) RETURNING claim_id",
            (task_id, agent_id, note),
        )
        return rows[0][0]
    except psycopg.errors.UniqueViolation:
        raise ValueError(f"Task {task_id} is already claimed")

def log_decision(task_id: str, agent_id: str, decision_text: str, embedding: list[float], reason: str = None, state: str = "proposed") -> str:
    embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"
    _, rows = run_query(
        """
        INSERT INTO task_decisions (task_id, agent_id, decision_text, reason, state, embedding)
        VALUES (%s, %s, %s, %s, %s, %s::VECTOR)
        RETURNING decision_id
        """,
        (task_id, agent_id, decision_text, reason, state, embedding_str),
    )
    return rows[0][0]

def search_past_decisions(query_embedding: list[float], limit: int = 5) -> list[dict]:
    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
    columns, rows = run_query(
        """
        SELECT decision_id, task_id, agent_id, decision_text, reason,
               1 - (embedding <=> %s::VECTOR) AS similarity
        FROM task_decisions
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> %s::VECTOR
        LIMIT %s
        """,
        (embedding_str, embedding_str, limit),
    )
    return [dict(zip(columns, row)) for row in rows]
