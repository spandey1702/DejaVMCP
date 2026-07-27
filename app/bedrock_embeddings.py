from __future__ import annotations

import os
from typing import Optional


class BedrockEmbeddingClient:
    def __init__(self, region: Optional[str] = None) -> None:
        self.region = region or os.getenv("AWS_REGION", "us-east-1")

    def is_configured(self) -> bool:
        return bool(self.region)

    def embed_text(self, text: str) -> list[float]:
        raise NotImplementedError(
            "Bedrock embedding integration is intentionally stubbed until you provide your AWS setup."
        )
