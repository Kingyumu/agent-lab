"""结构化输出：JSON 提取 + Pydantic 校验 + 重试。"""

from __future__ import annotations

import json
import re
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from agent_lab.llm import ChatMessage, LLMClient

T = TypeVar("T", bound=BaseModel)


class StructuredOutputError(Exception):
    pass


def parse_json_object(text: str) -> dict:
    """从模型文本中提取第一个 JSON 对象。"""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise StructuredOutputError("未找到 JSON 对象")
    data = json.loads(match.group(0))
    if not isinstance(data, dict):
        raise StructuredOutputError("JSON 根节点必须是对象")
    return data


def parse_as_model(text: str, model_type: type[T]) -> T:
    data = parse_json_object(text)
    return model_type.model_validate(data)


async def complete_structured(
    client: LLMClient,
    *,
    system: str,
    user: str,
    model_type: type[T],
    retries: int = 2,
) -> T:
    messages = [
        ChatMessage(role="system", content=system),
        ChatMessage(role="user", content=user),
    ]
    last_error = ""
    for attempt in range(retries + 1):
        if attempt > 0:
            messages.append(
                ChatMessage(
                    role="user",
                    content=(
                        "上次输出无法通过校验。请只输出合法 JSON 对象，不要 Markdown。\n"
                        f"错误：{last_error}"
                    ),
                )
            )
        result = await client.chat(messages)
        content = result.content or ""
        messages.append(ChatMessage(role="assistant", content=content))
        try:
            return parse_as_model(content, model_type)
        except (StructuredOutputError, ValidationError, json.JSONDecodeError) as exc:
            last_error = str(exc)
    raise StructuredOutputError(f"结构化输出失败：{last_error}")
