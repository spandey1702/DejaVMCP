from fastapi import APIRouter, HTTPException

from app.cockroach_store import CockroachStore
from app.schemas import TaskClaimCreate, TaskCreate, TaskDecisionCreate, TaskEventCreate
from ledger import DecisionLedger

router = APIRouter()
storage = CockroachStore()
ledger = DecisionLedger(storage_path="data/ledger.json")


@router.post("/init/cockroach")
def initialize_cockroach() -> dict:
    try:
        return storage.initialize_schema()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/tasks", response_model=dict)
def create_task(payload: TaskCreate) -> dict:
    task = storage.create_task(payload)
    ledger.create_task(str(task.task_id), task.title)
    return task.model_dump()


@router.post("/tasks/{task_id}/claim", response_model=dict)
def claim_task(task_id: str, payload: TaskClaimCreate) -> dict:
    try:
        claimed = storage.create_claim(payload)
        ledger.claim_task(task_id, str(claimed.agent_id))
        return claimed.model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/tasks/{task_id}/decision", response_model=dict)
def record_decision(task_id: str, payload: TaskDecisionCreate) -> dict:
    decision = storage.create_decision(payload)
    ledger.record_decision(task_id, str(decision.agent_id), decision.decision_text, decision.reason or "", decision.state)
    return decision.model_dump()


@router.post("/tasks/{task_id}/events", response_model=dict)
def record_event(task_id: str, payload: TaskEventCreate) -> dict:
    event = storage.create_event(payload)
    return event.model_dump()


@router.get("/tasks")
def list_tasks() -> list[dict]:
    return ledger.list_tasks()


@router.get("/tasks/{task_id}/context")
def task_context(task_id: str) -> list[dict]:
    return [record for record in ledger.search_context(task_id) if record.get("task_id") == task_id]
