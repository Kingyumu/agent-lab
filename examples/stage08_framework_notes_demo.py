"""阶段 8：框架对照说明（无需额外依赖）。

【Python 语法速览】（边学 Agent 边学 Python）
- 三引号多行字符串：一对三个引号包住整段文字，可含换行
- 模块级常量 `NOTES = ...`：全文件共享，习惯用全大写命名
- 函数里只做副作用（打印）时，返回类型可写 `-> None`
"""

from __future__ import annotations

# [Python] 三引号多行字符串：保留换行与缩进，适合说明文字
NOTES = """
自研 AgentLoop          →  理解 tool_calls / messages 协议
         ↓
官方 SDK 直连           →  生产最小依赖
         ↓
LangGraph               →  复杂状态、HITL、checkpoint
         ↓
LlamaIndex(可选)        →  强化 RAG 索引与查询
"""


def main() -> None:
    print(NOTES)
    print("下一步：阅读 docs/stage-08/02-LangGraph入门.md")
    print("若已安装 langgraph：python examples/stage08_langgraph_demo.py --mock")


if __name__ == "__main__":
    main()
