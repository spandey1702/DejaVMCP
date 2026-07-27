# Agentic Fleet Decision Ledger

This project is now structured as a service scaffold for the Agentic Fleet Decision Ledger concept.

## What it includes

- A FastAPI service for creating tasks, claiming them, recording agent decisions, and retrieving decision context.
- A Python ledger layer that preserves fresh reasoning while storing task state and historical decisions.
- A CockroachDB-backed persistence path with typed Pydantic models.
- A deployment-oriented structure for Docker, CockroachDB, and AWS integration.

## Current stack

- Python 3.11+
- FastAPI + Pydantic
- JSON-backed persistence for local development and a CockroachDB path for real persistence
- Docker and AWS deployment scaffolding

## Local development

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Run the API:

```bash
uvicorn app.main:app --reload
```

Example endpoints:

- GET /health
- POST /tasks
- POST /tasks/{task_id}/claim
- POST /tasks/{task_id}/decision
- GET /tasks
- GET /tasks/{task_id}/context

## Production direction

The production version should extend this scaffold with:

- CockroachDB for transactional task claiming and durable audit records
- AWS services such as ECS, App Runner, S3, and Secrets Manager
- A semantic/vector search layer for historical decision retrieval
- Bedrock or another LLM endpoint for assistant-driven reasoning

## Tests

```bash
python3 -m unittest discover -s tests -v
```
