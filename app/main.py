from fastapi import FastAPI

from app.routes.agents import router as agents_router
from app.routes.health import router as health_router
from app.routes.tasks import router as tasks_router

app = FastAPI(title="Agentic Fleet Decision Ledger")

app.include_router(health_router)
app.include_router(agents_router)
app.include_router(tasks_router)
