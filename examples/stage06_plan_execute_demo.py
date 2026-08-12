"""阶段 6：Plan-and-Execute 演示。"""

from __future__ import annotations

import argparse
import asyncio
import json

from agent_lab.llm import ChatResult, MockLLMClient, build_default_client
from agent_lab.planning import PlanExecuteAgent


async def main(mock: bool) -> None:
    if mock:
        client = MockLLMClient(
            script=[
                ChatResult(
                    content=json.dumps(
                        {
                            "goal": "写一份 Agent 学习周报",
                            "steps": [
                                {"id": "s1", "title": "列出本周主题", "detail": "Tool/RAG"},
                                {"id": "s2", "title": "总结收获", "detail": "各写两点"},
                            ],
                        },
                        ensure_ascii=False,
                    ),
                    tool_calls=[],
                ),
                ChatResult(content="本周主题：Tool Loop 与 RAG。", tool_calls=[]),
                ChatResult(content="收获：先手写循环；检索质量优先。", tool_calls=[]),
            ]
        )
    else:
        client = build_default_client(mock=False)

    agent = PlanExecuteAgent(client)
    result = await agent.run("写一份 Agent 学习周报")
    print("计划:", result.plan.model_dump())
    print("最终:", result.final)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true")
    args = parser.parse_args()
    asyncio.run(main(mock=args.mock))
