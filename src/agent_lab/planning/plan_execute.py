"""Plan-and-Execute 最小实现。"""

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
    steps: list[PlanStep] = Field(min_length=1, max_length=8)


@dataclass
class StepResult:
    step_id: str
    ok: bool
    output: str


@dataclass
class PlanExecuteResult:
    plan: Plan
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
        return StepResult(step_id=step.id, ok=bool(text.strip()), output=text)

    async def run(self, goal: str) -> PlanExecuteResult:
        plan = await self.plan(goal)
        results: list[StepResult] = []
        for step in plan.steps:
            results.append(await self.execute_step(step))
        final = "；".join(r.output for r in results if r.ok)
        return PlanExecuteResult(plan=plan, step_results=results, final=final)
