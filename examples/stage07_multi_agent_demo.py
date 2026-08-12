"""阶段 7：多 Agent 演示。"""

from __future__ import annotations

import argparse
import asyncio

from agent_lab.llm import ChatResult, MockLLMClient, build_default_client
from agent_lab.multi_agent import ResearchWriterPipeline


async def main(mock: bool) -> None:
    if mock:
        client = MockLLMClient(
            script=[
                ChatResult(
                    content="1) 先手写 Tool Loop\n2) 再学 RAG\n3) 最后做评测与服务化",
                    tool_calls=[],
                ),
                ChatResult(
                    content=(
                        "学习 AI Agent 建议循序渐进：先掌握工具循环，"
                        "再补齐检索增强，最后用评测与服务化保证可上线。"
                    ),
                    tool_calls=[],
                ),
            ]
        )
    else:
        client = build_default_client(mock=False)

    pipe = ResearchWriterPipeline(client)
    result = await pipe.run("如何系统学习 Python AI Agent")
    print("研究员:\n", result.research)
    print("\n写作者:\n", result.article)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true")
    args = parser.parse_args()
    asyncio.run(main(mock=args.mock))
