"""LLM 客户端：真实 OpenAI 兼容接口 + Mock。"""

from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass
from typing import Any, Protocol

from agent_lab.config import settings


@dataclass
class ChatMessage:
    role: str
    content: str | None = None
    tool_call_id: str | None = None
    name: str | None = None
    tool_calls: list[dict[str, Any]] | None = None

    def to_openai(self) -> dict[str, Any]:
        data: dict[str, Any] = {"role": self.role}
        if self.content is not None:
            data["content"] = self.content
        if self.tool_call_id is not None:
            data["tool_call_id"] = self.tool_call_id
        if self.name is not None:
            data["name"] = self.name
        if self.tool_calls is not None:
            data["tool_calls"] = self.tool_calls
        return data


@dataclass
class ChatResult:
    content: str | None
    tool_calls: list[dict[str, Any]]
    raw: Any = None


class LLMClient(Protocol):
    async def chat(
        self,
        messages: Sequence[ChatMessage],
        *,
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.2,
    ) -> ChatResult: ...


class OpenAICompatClient:
    """兼容 OpenAI Chat Completions 的异步客户端。"""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        from openai import AsyncOpenAI

        self.model = model or settings.openai_model
        self._client = AsyncOpenAI(
            api_key=api_key or settings.openai_api_key,
            base_url=base_url or settings.openai_base_url,
            timeout=timeout,
        )

    async def chat(
        self,
        messages: Sequence[ChatMessage],
        *,
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.2,
    ) -> ChatResult:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": [m.to_openai() for m in messages],
            "temperature": temperature,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        resp = await self._client.chat.completions.create(**kwargs)
        msg = resp.choices[0].message
        tool_calls: list[dict[str, Any]] = []
        if msg.tool_calls:
            for tc in msg.tool_calls:
                tool_calls.append(
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                )
        return ChatResult(content=msg.content, tool_calls=tool_calls, raw=resp)

    async def chat_stream(
        self,
        messages: Sequence[ChatMessage],
        *,
        temperature: float = 0.2,
    ) -> AsyncIterator[str]:
        stream = await self._client.chat.completions.create(
            model=self.model,
            messages=[m.to_openai() for m in messages],
            temperature=temperature,
            stream=True,
        )
        async for event in stream:
            delta = event.choices[0].delta
            if delta.content:
                yield delta.content


class MockLLMClient:
    """无 API Key 时的规则模拟器，用于学习 Agent 循环。"""

    def __init__(self, script: list[ChatResult] | None = None) -> None:
        self._script = list(script or [])
        self._i = 0

    async def chat(
        self,
        messages: Sequence[ChatMessage],
        *,
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.2,
    ) -> ChatResult:
        if self._script:
            if self._i >= len(self._script):
                return ChatResult(content="(mock) 脚本结束", tool_calls=[])
            item = self._script[self._i]
            self._i += 1
            return item

        last = messages[-1].content or ""
        # 极简意图：遇到「算」就调用 calculator
        if tools and ("算" in last or "计算" in last or "+" in last or "*" in last):
            import json
            import re

            m = re.search(r"([\d\.\s\+\-\*/\(\)]+)", last)
            expr = (m.group(1) if m else "1+1").strip()
            return ChatResult(
                content=None,
                tool_calls=[
                    {
                        "id": "call_mock_calc",
                        "type": "function",
                        "function": {
                            "name": "calculator",
                            "arguments": json.dumps({"expression": expr}, ensure_ascii=False),
                        },
                    }
                ],
            )
        if any(m.role == "tool" for m in messages):
            tool_msgs = [m for m in messages if m.role == "tool"]
            return ChatResult(
                content=f"根据工具结果：{tool_msgs[-1].content}",
                tool_calls=[],
            )
        return ChatResult(content=f"(mock) 收到：{last}", tool_calls=[])


def build_default_client(*, mock: bool = False) -> OpenAICompatClient | MockLLMClient:
    if mock or not settings.has_api_key:
        return MockLLMClient()
    return OpenAICompatClient()
