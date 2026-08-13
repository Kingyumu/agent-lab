"""阶段 1：LLM 客户端演示。

【Python 语法速览】（边学 Agent 边学 Python）
- `argparse`：把命令行参数解析成属性，如 `args.mock`
- `action="store_true"`：出现该开关则为 True，否则默认 False
- 三元表达式 `"a" if 条件 else "b"`：按条件选字符串
"""

from __future__ import annotations

import argparse
import asyncio

from agent_lab.llm import ChatMessage, build_default_client


async def main(mock: bool) -> None:
    client = build_default_client(mock=mock)
    messages = [
        ChatMessage(role="system", content="你是简洁的助手。"),
        ChatMessage(role="user", content="用一句话介绍什么是 AI Agent。"),
    ]
    result = await client.chat(messages)
    # [Python] 条件表达式：按布尔值选两个字面量之一
    print("模式:", "mock" if mock else "live")
    print("回复:", result.content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # [Python] `store_true`：命令行带 `--mock` 时 args.mock 为 True
    parser.add_argument("--mock", action="store_true")
    args = parser.parse_args()
    asyncio.run(main(mock=args.mock))
