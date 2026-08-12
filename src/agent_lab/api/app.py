"""最小 FastAPI 服务。"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from agent_lab.models import AgentRequest, AgentResponse, RunStatus

app = FastAPI(title="agent-lab", version="0.1.0")
_RUNS: dict[str, dict[str, Any]] = {}


class CreateRunResponse(BaseModel):
    run_id: str
    status: RunStatus


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/runs", response_model=CreateRunResponse)
async def create_run(req: AgentRequest) -> CreateRunResponse:
    run_id = str(uuid.uuid4())
    # 教学：同步 mock 完成；生产应投递队列
    resp = AgentResponse(
        session_id=req.session_id,
        reply=f"(api-mock) 已收到：{req.message}",
        status=RunStatus.succeeded,
    )
    _RUNS[run_id] = {
        "status": RunStatus.succeeded,
        "request": req.model_dump(),
        "response": resp.model_dump(mode="json"),
    }
    return CreateRunResponse(run_id=run_id, status=RunStatus.succeeded)


@app.get("/runs/{run_id}")
def get_run(run_id: str) -> dict[str, Any]:
    if run_id not in _RUNS:
        return {"error": "not_found"}
    return _RUNS[run_id]
