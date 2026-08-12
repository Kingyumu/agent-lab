"""阶段 1：LLM 客户端演示。"""

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
    print("模式:", "mock" if mock else "live")
    print("回复:", result.content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true")
    args = parser.parse_args()
    asyncio.run(main(mock=args.mock))
