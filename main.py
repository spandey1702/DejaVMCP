from __future__ import annotations

import json
import os
from pathlib import Path

from ledger import DecisionLedger


def run_demo() -> None:
    storage_path = Path(__file__).resolve().parent / "data" / "ledger.json"
    ledger = DecisionLedger(storage_path=str(storage_path))
    ledger.create_task("task-001", "Investigate deployment timeout")
    ledger.claim_task("task-001", "agent-alpha")
    ledger.record_decision(
        "task-001",
        "agent-alpha",
        "Reproduce the timeout in staging",
        "The failure seems to happen after the warm-start phase and before the health check completes.",
        "investigating",
    )
    ledger.record_decision(
        "task-001",
        "agent-alpha",
        "Use a circuit breaker for the downstream dependency",
        "The previous run points to a repeated dependency outage and the system should degrade gracefully.",
        "recommended",
    )
    print(json.dumps({
        "tasks": ledger.list_tasks(),
        "context": ledger.search_context("circuit breaker downstream dependency"),
    }, indent=2))


if __name__ == "__main__":
    run_demo()
