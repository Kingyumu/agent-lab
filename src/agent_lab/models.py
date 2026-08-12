"""通用数据模型（阶段 0 示例，后续阶段复用）。"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class RunStatus(str, Enum):
    pending = "pending"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"
    cancelled = "cancelled"


class AgentRequest(BaseModel):
    """用户发给 Agent 的一次请求。"""

    session_id: str = Field(..., min_length=1, description="会话 ID")
    message: str = Field(..., min_length=1, max_length=20_000)
    metadata: dict[str, Any] = Field(default_factory=dict)
    max_steps: int = Field(default=8, ge=1, le=30)

    @field_validator("message")
    @classmethod
    def strip_message(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("message 不能为空")
        return v


class ToolCallRecord(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    result: str | None = None
    error: str | None = None


class AgentResponse(BaseModel):
    """Agent 对外返回的标准结构。"""

    session_id: str
    reply: str
    status: RunStatus = RunStatus.succeeded
    tool_calls: list[ToolCallRecord] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PlanStep(BaseModel):
    id: str
    title: str
    depends_on: list[str] = []