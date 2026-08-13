"""阶段 7：多 Agent 演示。

【Python 语法速览】（边学 Agent 边学 Python）
- 多行字符串用括号拼接：相邻字面量自动连成一条
- `\\n`：字符串里的换行转义，打印时会换行
- `print("标签:\\n", 值)`：先打标签再打内容
"""

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
                    # [Python] 括号包裹的相邻字符串字面量会拼成一个长串
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
