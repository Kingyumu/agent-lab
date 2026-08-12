import json

import pytest

from agent_lab.agent import AgentLoop
from agent_lab.llm import ChatResult, MockLLMClient
from agent_lab.tools.builtin import build_builtin_registry


@pytest.mark.asyncio
async def test_tool_agent_calculator_flow() -> None:
    client = MockLLMClient(
        script=[
            ChatResult(
                content=None,
                tool_calls=[
                    {
                        "id": "c1",
                        "type": "function",
                        "function": {
                            "name": "calculator",
                            "arguments": json.dumps({"expression": "(3+5)*2"}),
                        },
                    }
                ],
            ),
            ChatResult(content="结果是 16。", tool_calls=[]),
        ]
    )
    agent = AgentLoop(client, build_builtin_registry(), system_prompt="test", max_steps=5)
    result = await agent.run("算一下 (3+5)*2")
    assert "16" in result.reply
    assert len(result.steps) == 2
    assert result.steps[0].observations[0].startswith("calculator:")
