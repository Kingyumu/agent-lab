"""阶段 4：记忆演示。

【Python 语法速览】（边学 Agent 边学 Python）
- `for i in range(n)`：循环 n 次，`i` 从 0 到 n-1
- f-string `f"消息{i}"`：花括号里嵌入表达式
- `len(序列)`：元素个数；对列表/字符串都适用
"""

from __future__ import annotations

from agent_lab.llm import ChatMessage
from agent_lab.memory import ConversationMemory, LongTermMemory


def main() -> None:
    conv = ConversationMemory(session_id="s1")
    conv.add(ChatMessage(role="user", content="我叫小明"))
    conv.add(ChatMessage(role="assistant", content="你好小明"))
    # [Python] `range(10)` 产生 0..9；循环体可写多条语句
    for i in range(10):
        conv.add(ChatMessage(role="user", content=f"消息{i}"))
        conv.add(ChatMessage(role="assistant", content=f"回复{i}"))

    print("窗口消息数:", len(conv.get_context(max_messages=6)))
    conv.compact_with_summary("用户叫小明，正在连续对话练习。", keep_last=2)
    ctx = conv.get_context()
    # [Python] 下标 `[0]`：取第一个元素（从 0 开始计数）
    print("压缩后首条:", ctx[0].content)
    print("压缩后总条数:", len(ctx))

    mem = LongTermMemory("data/long_term_demo.db")
    mem.upsert("u1", "prefer_style", "简洁中文")
    print("长期记忆:", mem.get("u1", "prefer_style"))
    print("全部:", mem.list("u1"))


if __name__ == "__main__":
    main()
