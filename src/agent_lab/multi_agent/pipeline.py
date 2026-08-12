"""多 Agent 流水线：Researcher → Writer。"""

from __future__ import annotations

from dataclasses import dataclass

from agent_lab.llm import ChatMessage, LLMClient


@dataclass
class MultiAgentResult:
    research: str
    article: str


class ResearchWriterPipeline:
    def __init__(self, client: LLMClient, *, max_rounds: int = 2) -> None:
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
