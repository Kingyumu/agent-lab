"""阶段 8：LangGraph 最小示例（可选依赖）。"""

from __future__ import annotations

import argparse


def main(mock: bool) -> None:
    try:
        from typing import Annotated, TypedDict

        from langgraph.graph import END, START, StateGraph
        from langgraph.graph.message import add_messages
    except ImportError:
        print("未安装 langgraph。请执行: pip install -e \".[graph]\"")
        return

    class State(TypedDict):
        messages: Annotated[list, add_messages]
        answer: str

    def thinker(state: State) -> dict:
        # mock/教学：不调真实 LLM
        last = state["messages"][-1]["content"]
        return {"answer": f"(graph) 已处理：{last}"}

    g = StateGraph(State)
    g.add_node("thinker", thinker)
    g.add_edge(START, "thinker")
    g.add_edge("thinker", END)
    app = g.compile()

    result = app.invoke({"messages": [{"role": "user", "content": "你好，LangGraph"}], "answer": ""})
    print("mock=" , mock)
    print(result["answer"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true", default=True)
    args = parser.parse_args()
    main(mock=args.mock)
