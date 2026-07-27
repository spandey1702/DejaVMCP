from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class AgentStatus(str, Enum):
    active = "active"
    inactive = "inactive"


class TaskStatus(str, Enum):
    open = "open"
    claimed = "claimed"
    completed = "completed"
    blocked = "blocked"
    failed = "failed"


class ClaimStatus(str, Enum):
    active = "active"
    released = "released"


class AgentBase(BaseModel):
    agent_key: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    role: Optional[str] = None
    status: AgentStatus = AgentStatus.active


class AgentCreate(AgentBase):
    pass


class AgentRead(AgentBase):
    model_config = ConfigDict(from_attributes=True)
    agent_id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskBase(BaseModel):
    task_key: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.open
    created_by_agent_id: Optional[UUID] = None


class TaskCreate(TaskBase):
    pass


class TaskRead(TaskBase):
    model_config = ConfigDict(from_attributes=True)
    task_id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskClaimBase(BaseModel):
    task_id: UUID
    agent_id: UUID
    status: ClaimStatus = ClaimStatus.active
    note: Optional[str] = None


class TaskClaimCreate(TaskClaimBase):
    pass


class TaskClaimRead(TaskClaimBase):
    model_config = ConfigDict(from_attributes=True)
    claim_id: UUID = Field(default_factory=uuid4)
    claimed_at: datetime = Field(default_factory=datetime.utcnow)
    released_at: Optional[datetime] = None


class TaskDecisionBase(BaseModel):
    task_id: UUID
    agent_id: UUID
    decision_text: str = Field(..., min_length=1)
    reason: Optional[str] = None
    state: str = "proposed"
    decision_rank: int = 0


class TaskDecisionCreate(TaskDecisionBase):
    pass


class TaskDecisionRead(TaskDecisionBase):
    model_config = ConfigDict(from_attributes=True)
    decision_id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TaskEventBase(BaseModel):
    task_id: UUID
    agent_id: Optional[UUID] = None
    event_type: str = Field(..., min_length=1)
    event_payload: Optional[dict[str, Any]] = None


class TaskEventCreate(TaskEventBase):
    pass


class TaskEventRead(TaskEventBase):
    model_config = ConfigDict(from_attributes=True)
    event_id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
