"""工具系统：注册、schema、执行。

【Python 语法速览】（边学 Agent 边学 Python）
- 类型别名：`ToolHandler = Callable[...]` 给复杂类型起短名，读代码更轻松
- `Awaitable[str] | str`：用 `|` 表示「异步或同步都能返回」
- `Field(default_factory=...)`：可变默认值（如 dict）每次新建，避免共享坑
- `async def` + `await`：协程；遇到可 await 对象才真正挂起等待
- 仅关键字参数：`*, confirmed=True` 强制调用时写名字，防传参搞混
"""

from __future__ import annotations

import json
import traceback
from collections.abc import Awaitable, Callable
from typing import Any, Literal

from pydantic import BaseModel, Field

# [Python] 类型别名：把「接收 dict、返回 str 或可 await 的 str」缩成一个名字
ToolHandler = Callable[[dict[str, Any]], Awaitable[str] | str]


class ToolSpec(BaseModel):
    name: str
    description: str
    parameters: dict[str, Any] = Field(
        # [Python] default_factory：每次实例化都新建空 schema，避免类属性共享同一 dict
        default_factory=lambda: {"type": "object", "properties": {}}
    )
    # [Python] Literal：值只能是列出的这几个字符串之一（静态检查友好）
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
        # [Python] 前缀 `_`：约定「内部用」；类型注解 dict[键, 值]
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.spec.name] = tool

    def list_schemas(self) -> list[dict[str, Any]]:
        # [Python] 列表推导：遍历 values()，对每个工具调 openai_schema()
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
            # [Python] `or "{}"`：空字符串也当没有参数，避免 json.loads("") 报错
            args = json.loads(arguments_json or "{}")
            if not isinstance(args, dict):
                return "ERROR: 工具参数必须是 JSON 对象"
        except json.JSONDecodeError as exc:
            return f"ERROR: 参数 JSON 解析失败: {exc}"

        try:
            result = tool.handler(args)
            # [Python] 鸭子类型：有 __await__ 就当协程/awaitable，统一 await
            if hasattr(result, "__await__"):
                result = await result  # type: ignore[assignment]
            return str(result)
        except Exception as exc:  # noqa: BLE001
            # [Python] type(exc).__name__ 取异常类名；traceback 限 1 层便于教学阅读
            return f"ERROR: {type(exc).__name__}: {exc}\n{traceback.format_exc(limit=1)}"
