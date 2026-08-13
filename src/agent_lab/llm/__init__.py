"""LLM 客户端：真实 OpenAI 兼容接口 + Mock。

【Python 语法速览】（边学 Agent 边学 Python）
- `Protocol`：结构化类型（鸭子类型接口），实现同名方法即可匹配
- `Sequence[T]`：只读序列抽象（list/tuple 等都能传入）
- `AsyncIterator`：异步迭代协议，配合 `async for` / `yield`
- `**kwargs`：把字典拆成关键字参数传给函数
- `A | B`：联合类型，函数可返回其中任一种
- `cast(T, x)`：仅给类型检查器用，运行时原样返回 `x`
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass
from typing import Any, Protocol, cast

from openai.types.chat import ChatCompletionMessageParam

from agent_lab.config import settings


@dataclass
class ChatMessage:
    role: str
    content: str | None = None
    tool_call_id: str | None = None
    name: str | None = None
    tool_calls: list[dict[str, Any]] | None = None

    def to_openai(self) -> ChatCompletionMessageParam:
        data: dict[str, Any] = {"role": self.role}
        # [Python] `is not None`：保留空字符串；不要用 `if self.content` 误伤 ""
        if self.content is not None:
            data["content"] = self.content
        if self.tool_call_id is not None:
            data["tool_call_id"] = self.tool_call_id
        if self.name is not None:
            data["name"] = self.name
        if self.tool_calls is not None:
            data["tool_calls"] = self.tool_calls
        # [Python] cast：告诉类型检查器「把 dict 当作 SDK 要求的消息类型」
        # 运行时不做转换；只消掉 create(messages=...) 的 overload 报错
        return cast(ChatCompletionMessageParam, data)


@dataclass
class ChatResult:
    content: str | None
    tool_calls: list[dict[str, Any]]
    raw: Any = None


class LLMClient(Protocol):
    # [Python] Protocol 方法体用 `...`（Ellipsis）占位，只描述签名不实现
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
        # [Python] 函数内 import：推迟加载重依赖，未用到真实客户端时可不装/不载
        from openai import AsyncOpenAI

        # [Python] `a or b`：a 为假（含 None、""）时用 b
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
            # [Python] 列表推导：把每个 message 转成 OpenAI 字典
            "messages": [m.to_openai() for m in messages],
            "temperature": temperature,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        # [Python] `**kwargs`：字典键值展开为命名参数
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
        # [Python] `async for`：迭代异步流；`yield` 把本函数变成异步生成器
        async for event in stream:
            delta = event.choices[0].delta
            if delta.content:
                yield delta.content


class MockLLMClient:
    """无 API Key 时的规则模拟器，用于学习 Agent 循环。"""

    def __init__(self, script: list[ChatResult] | None = None) -> None:
        # [Python] `list(x or [])`：复制一份，避免外部改动影响内部脚本
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
            # [Python] 局部 import：仅该分支需要 json/re，减小冷路径开销
            import json
            import re

            m = re.search(r"([\d\.\s\+\-\*/\(\)]+)", last)
            # [Python] 条件表达式：有匹配用 group(1)，否则用 "1+1"
            expr = (m.group(1) if m else "1+1").strip()
            return ChatResult(
                content=None,
                tool_calls=[
                    {
                        "id": "call_mock_calc",
                        "type": "function",
                        "function": {
                            "name": "calculator",
                            # [Python] `ensure_ascii=False`：中文等不以 \uXXXX 转义
                            "arguments": json.dumps({"expression": expr}, ensure_ascii=False),
                        },
                    }
                ],
            )
        # [Python] 生成器表达式配 `any`：存在一条即 True，常短路
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
