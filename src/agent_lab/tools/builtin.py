"""内置示例工具。"""

from __future__ import annotations

import ast
import operator
from datetime import datetime, timezone
from typing import Any

import httpx

from agent_lab.tools import Tool, ToolRegistry, ToolSpec

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def _eval_expr(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _eval_expr(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_expr(node.left), _eval_expr(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_expr(node.operand))
    raise ValueError("仅支持加减乘除与幂运算的数值表达式")


def calculator(args: dict[str, Any]) -> str:
    expr = str(args.get("expression", "")).strip()
    if not expr:
        raise ValueError("expression 不能为空")
    value = _eval_expr(ast.parse(expr, mode="eval"))
    if value.is_integer():
        return str(int(value))
    return str(value)


def get_time(_: dict[str, Any]) -> str:
    return datetime.now(timezone.utc).isoformat()


async def http_get(args: dict[str, Any]) -> str:
    url = str(args.get("url", "")).strip()
    if not url.startswith(("http://", "https://")):
        raise ValueError("url 必须以 http:// 或 https:// 开头")
    timeout = float(args.get("timeout", 10))
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        text = resp.text
        return text[:4000]


def build_builtin_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(
        Tool(
            ToolSpec(
                name="calculator",
                description="计算算术表达式，例如 (3+5)*2。只支持数字与 + - * / **。",
                parameters={
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string", "description": "算术表达式"},
                    },
                    "required": ["expression"],
                },
            ),
            calculator,
        )
    )
    registry.register(
        Tool(
            ToolSpec(
                name="get_time",
                description="获取当前 UTC 时间（ISO8601）。",
                parameters={"type": "object", "properties": {}},
            ),
            get_time,
        )
    )
    registry.register(
        Tool(
            ToolSpec(
                name="http_get",
                description="GET 请求某个 URL，返回最多 4000 字符的响应文本。",
                parameters={
                    "type": "object",
                    "properties": {
                        "url": {"type": "string"},
                        "timeout": {"type": "number", "default": 10},
                    },
                    "required": ["url"],
                },
                side_effect="none",
            ),
            http_get,
        )
    )
    return registry
