"""Pydantic 模型行为测试。

【Python 语法速览】（边学 Agent 边学 Python）
- `with pytest.raises(异常类型):`：期望缩进块内代码抛出该异常
- 函数内再 `import`：把仅此用例需要的依赖放局部，减负顶层
- 默认值断言：构造时未传的字段应等于模型声明的默认
"""

from agent_lab.models import AgentRequest, AgentResponse, RunStatus


def test_agent_request_strips_message() -> None:
    req = AgentRequest(session_id="s", message="  hello  ")
    assert req.message == "hello"


def test_agent_request_rejects_blank() -> None:
    # [Python] 局部 import：只在本测试用到 pytest / ValidationError
    import pytest
    from pydantic import ValidationError

    # [Python] 上下文管理器：块内必须抛出 ValidationError，否则测试失败
    with pytest.raises(ValidationError):
        AgentRequest(session_id="s", message="  ")


def test_agent_response_defaults() -> None:
    resp = AgentResponse(session_id="s", reply="ok")
    assert resp.status == RunStatus.succeeded
    assert resp.tool_calls == []
