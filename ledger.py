from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import json
import os
import re


@dataclass
class DecisionRecord:
    id: str
    task_id: str
    agent_id: str
    decision: str
    reason: str
    state: str
    created_at: str


@dataclass
class TaskRecord:
    task_id: str
    title: str
    status: str = "open"
    claimed_by: Optional[str] = None
    claimed_at: Optional[str] = None
    updated_at: Optional[str] = None
    history: List[DecisionRecord] = field(default_factory=list)

    def to_payload(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["history"] = [asdict(record) for record in self.history]
        return payload


class DecisionLedger:
    def __init__(self, storage_path: Optional[str] = None) -> None:
        self.storage_path = storage_path
        self.tasks: Dict[str, TaskRecord] = {}
        self.decisions: List[DecisionRecord] = []
        self._load()

    def _load(self) -> None:
        if not self.storage_path or not os.path.exists(self.storage_path):
            return
        with open(self.storage_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        for task_id, task_payload in payload.get("tasks", {}).items():
            task = TaskRecord(**task_payload)
            task.history = [DecisionRecord(**record) for record in task_payload.get("history", [])]
            self.tasks[task_id] = task
        self.decisions = [DecisionRecord(**record) for record in payload.get("decisions", [])]

    def _save(self) -> None:
        if not self.storage_path:
            return
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        payload = {
            "tasks": {task_id: task.to_payload() for task_id, task in self.tasks.items()},
            "decisions": [asdict(record) for record in self.decisions],
        }
        with open(self.storage_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)

    def create_task(self, task_id: str, title: str) -> Dict[str, Any]:
        if task_id in self.tasks:
            return self.tasks[task_id].to_payload()
        task = TaskRecord(task_id=task_id, title=title, updated_at=self._timestamp())
        self.tasks[task_id] = task
        self._save()
        return task.to_payload()

    def claim_task(self, task_id: str, agent_id: str) -> Dict[str, Any]:
        task = self.tasks.setdefault(task_id, TaskRecord(task_id=task_id, title="Untitled task", updated_at=self._timestamp()))
        if task.status == "claimed" and task.claimed_by != agent_id:
            raise ValueError(f"Task {task_id} is already claimed by {task.claimed_by}")
        task.status = "claimed"
        task.claimed_by = agent_id
        task.claimed_at = self._timestamp()
        task.updated_at = task.claimed_at
        self._save()
        return task.to_payload()

    def release_task(self, task_id: str) -> Dict[str, Any]:
        task = self.tasks.get(task_id)
        if task is None:
            raise KeyError(f"Task {task_id} does not exist")
        task.status = "open"
        task.claimed_by = None
        task.claimed_at = None
        task.updated_at = self._timestamp()
        self._save()
        return task.to_payload()

    def record_decision(
        self,
        task_id: str,
        agent_id: str,
        decision: str,
        reason: str,
        state: str,
    ) -> Dict[str, Any]:
        task = self.tasks.setdefault(task_id, TaskRecord(task_id=task_id, title="Untitled task", updated_at=self._timestamp()))
        created_at = self._timestamp()
        record = DecisionRecord(
            id=self._make_id(task_id, agent_id, created_at),
            task_id=task_id,
            agent_id=agent_id,
            decision=decision,
            reason=reason,
            state=state,
            created_at=created_at,
        )
        self.decisions.append(record)
        task.history.append(record)
        task.updated_at = created_at
        task.status = state
        self._save()
        return asdict(record)

    def list_tasks(self) -> List[Dict[str, Any]]:
        return [task.to_payload() for task in self.tasks.values()]

    def search_context(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        query_tokens = self._tokenize(query)
        ranked: List[tuple[float, DecisionRecord]] = []
        for record in self.decisions:
            text = " ".join([record.decision, record.reason, record.task_id, record.agent_id]).lower()
            tokens = self._tokenize(text)
            score = self._score(query_tokens, tokens)
            if score > 0:
                ranked.append((score, record))
        ranked.sort(key=lambda item: item[0], reverse=True)
        return [asdict(record) for _, record in ranked[:limit]]

    def _score(self, query_tokens: List[str], tokens: List[str]) -> float:
        if not query_tokens:
            return 0.0
        overlap = len(set(query_tokens) & set(tokens))
        if overlap == 0:
            return 0.0
        return overlap / max(1, len(query_tokens)) + (0.1 if any(token in tokens for token in query_tokens) else 0.0)

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return [token for token in re.findall(r"[a-z0-9]+", text.lower()) if len(token) > 2]

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _make_id(task_id: str, agent_id: str, timestamp: str) -> str:
        return f"{task_id}-{agent_id}-{hash(timestamp)}"
