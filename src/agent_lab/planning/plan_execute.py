"""Plan-and-Execute 最小实现。

【Python 语法速览】（边学 Agent 边学 Python）
- `@dataclass`：自动生成 `__init__` 等样板代码，适合内部结果对象
- Pydantic `BaseModel`：要校验/结构化输出时用；和 dataclass 各司其职
- `field(default_factory=list)`：可变默认列表每次新建
- `async for`/循环里 `await`：顺序执行多步异步任务
"""

from __future__ import annotations

from dataclasses import dataclass, field

from agent_lab.llm import ChatMessage, LLMClient
from agent_lab.structured import complete_structured
from pydantic import BaseModel, Field


class PlanStep(BaseModel):
    id: str
    title: str
    detail: str = ""


class Plan(BaseModel):
    goal: str
    # [Python] Field(min_length/max_length)：对 list 限制元素个数，不是字符串长度
    steps: list[PlanStep] = Field(min_length=1, max_length=8)


@dataclass
class StepResult:
    step_id: str
    ok: bool
    output: str


@dataclass
class PlanExecuteResult:
    plan: Plan
    # [Python] default_factory=list：每个实例自己的空 list，不会共享
    step_results: list[StepResult] = field(default_factory=list)
    final: str = ""


class PlanExecuteAgent:
    def __init__(self, client: LLMClient) -> None:
        self.client = client

    async def plan(self, goal: str) -> Plan:
        system = (
            "你是规划器。只输出 JSON："
            '{"goal":"...","steps":[{"id":"s1","title":"...","detail":"..."}]}'
        )
        return await complete_structured(
            self.client,
            system=system,
            user=goal,
            model_type=Plan,
        )

    async def execute_step(self, step: PlanStep) -> StepResult:
        # 教学默认：让模型「假装执行」并给出短结果；真实项目这里调工具/子Agent
        result = await self.client.chat(
            [
                ChatMessage(
                    role="system",
                    content="你是执行器。用 1-2 句中文描述完成本步骤的结果。",
                ),
                ChatMessage(role="user", content=f"{step.title}\n{step.detail}"),
            ]
        )
        text = result.content or ""
        # [Python] bool(text.strip())：去掉空白后非空则 True
        return StepResult(step_id=step.id, ok=bool(text.strip()), output=text)

    async def run(self, goal: str) -> PlanExecuteResult:
        plan = await self.plan(goal)
        results: list[StepResult] = []
        for step in plan.steps:
            # [Python] 循环内 await：一步完成再下一步（串行，不是并发）
            results.append(await self.execute_step(step))
        # [Python] 生成器表达式喂给 join：只拼 ok 的输出
        final = "；".join(r.output for r in results if r.ok)
        return PlanExecuteResult(plan=plan, step_results=results, final=final)
