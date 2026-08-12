"""阶段 4：记忆演示。"""

from __future__ import annotations

from agent_lab.llm import ChatMessage
from agent_lab.memory import ConversationMemory, LongTermMemory


def main() -> None:
    conv = ConversationMemory(session_id="s1")
    conv.add(ChatMessage(role="user", content="我叫小明"))
    conv.add(ChatMessage(role="assistant", content="你好小明"))
    for i in range(10):
        conv.add(ChatMessage(role="user", content=f"消息{i}"))
        conv.add(ChatMessage(role="assistant", content=f"回复{i}"))

    print("窗口消息数:", len(conv.get_context(max_messages=6)))
    conv.compact_with_summary("用户叫小明，正在连续对话练习。", keep_last=2)
    ctx = conv.get_context()
    print("压缩后首条:", ctx[0].content)
    print("压缩后总条数:", len(ctx))

    mem = LongTermMemory("data/long_term_demo.db")
    mem.upsert("u1", "prefer_style", "简洁中文")
    print("长期记忆:", mem.get("u1", "prefer_style"))
    print("全部:", mem.list("u1"))


if __name__ == "__main__":
    main()
