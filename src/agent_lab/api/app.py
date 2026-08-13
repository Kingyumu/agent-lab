"""最小 FastAPI 服务。

【Python 语法速览】（边学 Agent 边学 Python）
- 装饰器 `@app.get/post`：用函数注册 HTTP 路由，不必手写 URL 分发
- 路径参数 `/runs/{run_id}`：花括号里的名字变成函数参数
- 模块级 dict `_RUNS`：进程内「假数据库」；教学用，重启会丢
- `model_dump`：Pydantic 模型 → 普通 dict，便于 JSON 序列化
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from agent_lab.models import AgentRequest, AgentResponse, RunStatus

app = FastAPI(title="agent-lab", version="0.1.0")
# [Python] 模块全局可变 dict：所有请求共享同一块内存状态
_RUNS: dict[str, dict[str, Any]] = {}


class CreateRunResponse(BaseModel):
    run_id: str
    status: RunStatus


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/runs", response_model=CreateRunResponse)
async def create_run(req: AgentRequest) -> CreateRunResponse:
    # [Python] uuid4() 生成随机 UUID；str(...) 转成可当 dict 键的字符串
    run_id = str(uuid.uuid4())
    # 教学：同步 mock 完成；生产应投递队列
    resp = AgentResponse(
        session_id=req.session_id,
        reply=f"(api-mock) 已收到：{req.message}",
        status=RunStatus.succeeded,
    )
    _RUNS[run_id] = {
        "status": RunStatus.succeeded,
        # [Python] model_dump：模型 → dict；mode="json" 让 datetime 等变成 JSON 友好类型
        "request": req.model_dump(),
        "response": resp.model_dump(mode="json"),
    }
    return CreateRunResponse(run_id=run_id, status=RunStatus.succeeded)


@app.get("/runs/{run_id}")
def get_run(run_id: str) -> dict[str, Any]:
    if run_id not in _RUNS:
        return {"error": "not_found"}
    return _RUNS[run_id]
