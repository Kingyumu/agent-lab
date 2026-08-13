"""工具 Agent 异步集成测试。

【Python 语法速览】（边学 Agent 边学 Python）
- `@pytest.mark.asyncio`：装饰器，把异步测试交给 pytest-asyncio 调度
- `assert 条件`：测试断言；不成立则用例失败
- `json.dumps(dict)`：把参数字典编码成工具调用需要的 JSON 字符串
"""

import json

import pytest

from agent_lab.agent import AgentLoop
from agent_lab.llm import ChatResult, MockLLMClient
from agent_lab.tools.builtin import build_builtin_registry


# [Python] 装饰器：先交给 pytest 识别「这是异步测试」
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
                            # [Python] 工具参数常以 JSON 字符串传递，不是 Python dict
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
    # [Python] `in`：子串/成员包含判断
    assert "16" in result.reply
    assert len(result.steps) == 2
    assert result.steps[0].observations[0].startswith("calculator:")
