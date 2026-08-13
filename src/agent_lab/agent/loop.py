"""手写 Tool Agent 主循环。

【Python 语法速览】（边学 Agent 边学 Python）
- `@dataclass`：自动生成 `__init__` / `__repr__` 等样板代码
- `field(default_factory=list)`：可变默认值的正确写法
- 切片 `text[:n]`：取前 n 个字符；负数索引从末尾算
- 三元表达式 `a if cond else b`：单行条件取值
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agent_lab.llm import ChatMessage, LLMClient
from agent_lab.tools import ToolRegistry


@dataclass
class StepTrace:
    step: int
    assistant_content: str | None
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)


@dataclass
class AgentRunResult:
    reply: str
    steps: list[StepTrace] = field(default_factory=list)
    messages: list[ChatMessage] = field(default_factory=list)


def _truncate(text: str, limit: int = 4000) -> str:
    # [Python] 前缀 `_`：约定「模块内私有」，不鼓励外部依赖
    if len(text) <= limit:
        return text
    return text[: limit - 20] + "\n...[truncated]..."


class AgentLoop:
    def __init__(
        self,
        client: LLMClient,
        registry: ToolRegistry,
        *,
        system_prompt: str | None = None,
        max_steps: int = 8,
    ) -> None:
        self.client = client
        self.registry = registry
        self.max_steps = max_steps
        if system_prompt is None:
            path = Path("prompts/react_agent.txt")
            # [Python] 多行三元：条件成立取 read_text，否则用默认字符串
            system_prompt = (
                path.read_text(encoding="utf-8")
                if path.exists()
                else "你是会使用工具的助手。"
            )
        self.system_prompt = system_prompt

    async def run(self, user_message: str) -> AgentRunResult:
        messages = [
            ChatMessage(role="system", content=self.system_prompt),
            ChatMessage(role="user", content=user_message),
        ]
        traces: list[StepTrace] = []
        schemas = self.registry.list_schemas()

        for step in range(1, self.max_steps + 1):
            result = await self.client.chat(messages, tools=schemas)
            if not result.tool_calls:
                reply = result.content or ""
                messages.append(ChatMessage(role="assistant", content=reply))
                traces.append(StepTrace(step=step, assistant_content=reply))
                return AgentRunResult(reply=reply, steps=traces, messages=messages)

            messages.append(
                ChatMessage(
                    role="assistant",
                    content=result.content,
                    tool_calls=result.tool_calls,
                )
            )
            observations: list[str] = []
            for call in result.tool_calls:
                # [Python] `dict["a"]["b"]`：嵌套键访问；缺键会 KeyError
                name = call["function"]["name"]
                # [Python] `x or "{}"`：空字符串/None 时用默认 JSON 对象
                args = call["function"].get("arguments") or "{}"
                obs = await self.registry.execute(name, args)
                obs = _truncate(obs)
                observations.append(f"{name}: {obs}")
                messages.append(
                    ChatMessage(
                        role="tool",
                        content=obs,
                        # [Python] `.get("id")`：键不存在返回 None，不抛异常
                        tool_call_id=call.get("id"),
                        name=name,
                    )
                )
            traces.append(
                StepTrace(
                    step=step,
                    assistant_content=result.content,
                    tool_calls=result.tool_calls,
                    observations=observations,
                )
            )

        reply = f"已达到最大步数 {self.max_steps}，停止。"
        return AgentRunResult(reply=reply, steps=traces, messages=messages)
