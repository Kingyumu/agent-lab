"""多 Agent 流水线：Researcher → Writer。

【Python 语法速览】（边学 Agent 边学 Python）
- `*` 后的参数：仅关键字传入，如 `max_rounds=2`，防位置参数搞混
- `@dataclass`：轻量结果容器，字段即构造参数
- 两次 `await client.chat`：串行流水线——先研究再写作
"""

from __future__ import annotations

from dataclasses import dataclass

from agent_lab.llm import ChatMessage, LLMClient


@dataclass
class MultiAgentResult:
    research: str
    article: str


class ResearchWriterPipeline:
    def __init__(self, client: LLMClient, *, max_rounds: int = 2) -> None:
        # [Python] `*, max_rounds=...`：max_rounds 只能关键字传，不能位置传
        self.client = client
        self.max_rounds = max_rounds

    async def run(self, topic: str) -> MultiAgentResult:
        research = await self.client.chat(
            [
                ChatMessage(
                    role="system",
                    content="你是研究员。列出 3 条要点，每条一行，不要扩写。",
                ),
                ChatMessage(role="user", content=topic),
            ]
        )
        # [Python] `or ""`：content 可能是 None，统一成空字符串
        findings = research.content or ""
        article = await self.client.chat(
            [
                ChatMessage(
                    role="system",
                    content="你是写作者。根据要点写 120 字以内短文，不要编造要点外事实。",
                ),
                ChatMessage(role="user", content=f"主题：{topic}\n要点：\n{findings}"),
            ]
        )
        return MultiAgentResult(research=findings, article=article.content or "")
