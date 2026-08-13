"""内置示例工具。

【Python 语法速览】（边学 Agent 边学 Python）
- `ast` 解析表达式：把字符串变成语法树，再递归求值（比 eval 可控）
- `dict` 映射「节点类型 → 运算符函数」：用类型当键做分发
- `async with`：异步上下文管理器，退出时自动关闭 HTTP 客户端
- `startswith((a, b))`：元组表示「匹配任一前缀」
"""

from __future__ import annotations

import ast
import operator
from datetime import datetime, timezone
from typing import Any

import httpx

from agent_lab.tools import Tool, ToolRegistry, ToolSpec

# [Python] 用 AST 节点类当 key，值是真正的加减乘除函数
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
    # [Python] isinstance 第二参可为元组：int 或 float 都算数
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        # [Python] type(node.op) 取运算符节点的类，再查表得到函数
        return _OPS[type(node.op)](_eval_expr(node.left), _eval_expr(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_expr(node.operand))
    raise ValueError("仅支持加减乘除与幂运算的数值表达式")


def calculator(args: dict[str, Any]) -> str:
    expr = str(args.get("expression", "")).strip()
    if not expr:
        raise ValueError("expression 不能为空")
    # [Python] mode="eval" 只允许表达式，不能是赋值等语句
    value = _eval_expr(ast.parse(expr, mode="eval"))
    if value.is_integer():
        return str(int(value))
    return str(value)


def get_time(_: dict[str, Any]) -> str:
    # [Python] 参数名 `_`：表示「用不到但不删签名」（工具 handler 接口统一）
    return datetime.now(timezone.utc).isoformat()


async def http_get(args: dict[str, Any]) -> str:
    url = str(args.get("url", "")).strip()
    if not url.startswith(("http://", "https://")):
        raise ValueError("url 必须以 http:// 或 https:// 开头")
    timeout = float(args.get("timeout", 10))
    # [Python] async with：进入拿客户端，离开自动 aclose，防连接泄漏
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
