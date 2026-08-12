from agent_lab.models import AgentRequest, AgentResponse, RunStatus


def test_agent_request_strips_message() -> None:
    req = AgentRequest(session_id="s", message="  hello  ")
    assert req.message == "hello"


def test_agent_request_rejects_blank() -> None:
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        AgentRequest(session_id="s", message="  ")


def test_agent_response_defaults() -> None:
    resp = AgentResponse(session_id="s", reply="ok")
    assert resp.status == RunStatus.succeeded
    assert resp.tool_calls == []
