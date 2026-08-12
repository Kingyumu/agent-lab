"""阶段 3：手写 Tool Agent 演示。"""

from __future__ import annotations

import argparse
import asyncio

from agent_lab.agent import AgentLoop
from agent_lab.llm import build_default_client
from agent_lab.tools.builtin import build_builtin_registry


async def main(mock: bool) -> None:
    client = build_default_client(mock=mock)
    agent = AgentLoop(client, build_builtin_registry(), max_steps=6)
    question = "请计算 (3+5)*2，并告诉我结果。"
    result = await agent.run(question)
    print("问题:", question)
    print("回答:", result.reply)
    print("--- 轨迹 ---")
    for s in result.steps:
        print(f"step={s.step} content={s.assistant_content!r}")
        for obs in s.observations:
            print(f"  obs: {obs}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true")
    args = parser.parse_args()
    asyncio.run(main(mock=args.mock))
