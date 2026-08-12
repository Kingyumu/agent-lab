"""阶段 0：Pydantic 模型演示。"""

from __future__ import annotations

from pydantic import ValidationError

from agent_lab.models import AgentRequest, AgentResponse, RunStatus, PlanStep


def main() -> None:
    req = AgentRequest(session_id="s1", message="  帮我算 1+1  ")
    print("请求 OK:", req.model_dump())

    resp = AgentResponse(session_id=req.session_id, reply="2", status=RunStatus.succeeded)
    print("响应 OK:", resp.model_dump(mode="json"))

    req2 = AgentRequest(message="你好", session_id='demo')
    print("请求 OK:", req2.model_dump())
    print("steps:", req2.max_steps)

    resp2 = AgentResponse(session_id=req2.session_id, reply="calling error", status=RunStatus.failed)
    print("响应 Error:", resp2.model_dump(mode="json"))

    step = PlanStep(id="1", title="计划", depends_on=['a', 'b', 'c'])
    print(step.model_dump(mode="json"))

    try:
        AgentRequest(session_id="s1", message="   ")
    except ValidationError as e:
        print("空消息会被拒绝：")
        print(e)


if __name__ == "__main__":
    main()
