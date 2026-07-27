from fastapi import APIRouter

from app.cockroach_store import CockroachStore
from app.bedrock_embeddings import BedrockEmbeddingClient

router = APIRouter()
storage = CockroachStore()
embeddings = BedrockEmbeddingClient()


@router.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "cockroach_configured": storage.is_configured(),
        "bedrock_configured": embeddings.is_configured(),
    }
