from fastapi import APIRouter, HTTPException

from app.cockroach_store import CockroachStore
from app.schemas import AgentCreate

router = APIRouter()
storage = CockroachStore()


@router.post("/agents", response_model=dict)
def create_agent(payload: AgentCreate) -> dict:
    try:
        return storage.create_agent(payload).model_dump()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
