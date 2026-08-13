"""阶段 3：手写 Tool Agent 演示。

【Python 语法速览】（边学 Agent 边学 Python）
- 嵌套 `for`：外层一步、内层遍历该步的观测列表
- `!r` 格式说明符：用 `repr()` 打印，字符串会带引号，便于看空白
- 位置参数 + 关键字参数混用：前面按位置，后面用 `名=值`
"""

from __future__ import annotations

import argparse
import asyncio

from agent_lab.agent import AgentLoop
from agent_lab.llm import build_default_client
from agent_lab.tools.builtin import build_builtin_registry


async def main(mock: bool) -> None:
    client = build_default_client(mock=mock)
    # [Python] 位置参数在前，关键字参数 `max_steps=` 写名字更清晰
    agent = AgentLoop(client, build_builtin_registry(), max_steps=6)
    question = "请计算 (3+5)*2，并告诉我结果。"
    result = await agent.run(question)
    print("问题:", question)
    print("回答:", result.reply)
    print("--- 轨迹 ---")
    for s in result.steps:
        # [Python] `{s.assistant_content!r}`：`!r` 调用 repr，便于调试
        print(f"step={s.step} content={s.assistant_content!r}")
        for obs in s.observations:
            print(f"  obs: {obs}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true")
    args = parser.parse_args()
    asyncio.run(main(mock=args.mock))
