"""工具系统：注册、schema、执行。"""

from __future__ import annotations

import json
import traceback
from collections.abc import Awaitable, Callable
from typing import Any, Literal

from pydantic import BaseModel, Field

ToolHandler = Callable[[dict[str, Any]], Awaitable[str] | str]


class ToolSpec(BaseModel):
    name: str
    description: str
    parameters: dict[str, Any] = Field(
        default_factory=lambda: {"type": "object", "properties": {}}
    )
    side_effect: Literal["none", "write", "irreversible"] = "none"
    require_confirmation: bool = False


class Tool:
    def __init__(self, spec: ToolSpec, handler: ToolHandler) -> None:
        self.spec = spec
        self.handler = handler

    def openai_schema(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.spec.name,
                "description": self.spec.description,
                "parameters": self.spec.parameters,
            },
        }


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.spec.name] = tool

    def list_schemas(self) -> list[dict[str, Any]]:
        return [t.openai_schema() for t in self._tools.values()]

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(f"未知工具: {name}")
        return self._tools[name]

    async def execute(self, name: str, arguments_json: str, *, confirmed: bool = True) -> str:
        tool = self.get(name)
        if tool.spec.require_confirmation and not confirmed:
            return "ERROR: 该工具需要用户确认后才能执行。"
        try:
            args = json.loads(arguments_json or "{}")
            if not isinstance(args, dict):
                return "ERROR: 工具参数必须是 JSON 对象"
        except json.JSONDecodeError as exc:
            return f"ERROR: 参数 JSON 解析失败: {exc}"

        try:
            result = tool.handler(args)
            if hasattr(result, "__await__"):
                result = await result  # type: ignore[assignment]
            return str(result)
        except Exception as exc:  # noqa: BLE001
            return f"ERROR: {type(exc).__name__}: {exc}\n{traceback.format_exc(limit=1)}"
