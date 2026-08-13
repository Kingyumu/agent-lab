"""会话短期记忆。

【Python 语法速览】（边学 Agent 边学 Python）
- 负切片 `messages[-n:]`：取列表最后 n 条
- `*recent`：列表解包，把元素铺进外层列表字面量
- `list(x)`：浅拷贝可迭代对象，避免调用方改到内部缓存
"""

from __future__ import annotations

from dataclasses import dataclass, field

from agent_lab.llm import ChatMessage


@dataclass
class ConversationMemory:
    session_id: str
    messages: list[ChatMessage] = field(default_factory=list)
    summary: str | None = None

    def add(self, message: ChatMessage) -> None:
        self.messages.append(message)

    def get_context(self, max_messages: int = 12) -> list[ChatMessage]:
        """返回可发送给模型的上下文：可选 summary + 最近消息。"""
        # [Python] `[-n:]`：从倒数第 n 个一直到末尾
        recent = self.messages[-max_messages:]
        if not self.summary:
            return list(recent)
        return [
            ChatMessage(
                role="system",
                content=f"此前对话摘要：{self.summary}",
            ),
            # [Python] `*recent`：展开列表元素，等价于逐个写入
            *recent,
        ]

    def compact_with_summary(self, summary: str, keep_last: int = 4) -> None:
        self.summary = summary
        self.messages = self.messages[-keep_last:]
