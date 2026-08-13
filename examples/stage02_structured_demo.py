"""阶段 2：结构化输出演示。

【Python 语法速览】（边学 Agent 边学 Python）
- `class X(BaseModel)`：继承；子类自动获得父类能力
- `字段: 类型 = 默认值`：声明属性类型与缺省
- 括号内隐式字符串拼接：相邻字面量会自动连成一条长字符串
"""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from pydantic import BaseModel, Field

from agent_lab.llm import ChatResult, MockLLMClient, build_default_client
from agent_lab.structured import complete_structured


class PlanStep(BaseModel):
    id: str
    title: str
    detail: str = ""


class TaskPlan(BaseModel):
    goal: str
    # [Python] `Field(...)`：给字段加校验约束（最小/最大长度等）
    steps: list[PlanStep] = Field(min_length=2, max_length=6)


async def main(mock: bool) -> None:
    # [Python] `Path(...).read_text(...)`：按路径读整个文本文件
    system = Path("prompts/task_decomposer.txt").read_text(encoding="utf-8")
    user = "我想系统学习 Python AI Agent，请拆解成可执行步骤。"

    if mock:
        client = MockLLMClient(
            script=[
                ChatResult(
                    # [Python] 括号内多个相邻字符串字面量会自动拼接
                    content=(
                        '{"goal":"学习 Python AI Agent",'
                        '"steps":['
                        '{"id":"s1","title":"打好工程基础","detail":"类型/异步/项目结构"},'
                        '{"id":"s2","title":"手写 Tool Loop","detail":"ReAct + Function Calling"},'
                        '{"id":"s3","title":"补齐 RAG 与评测","detail":"检索+回归集"}'
                        "]}"
                    ),
                    tool_calls=[],
                )
            ]
        )
    else:
        client = build_default_client(mock=False)

    plan = await complete_structured(
        client,
        system=system,
        user=user,
        model_type=TaskPlan,
    )
    # [Python] 关键字参数可跨行，末尾逗号合法，方便增删
    print(plan.model_dump_json(indent=2, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true")
    args = parser.parse_args()
    asyncio.run(main(mock=args.mock))
