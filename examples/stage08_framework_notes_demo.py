"""阶段 8：框架对照说明（无需额外依赖）。"""

from __future__ import annotations

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
