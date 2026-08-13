"""阶段 8：LangGraph 最小示例（可选依赖）。

【Python 语法速览】（边学 Agent 边学 Python）
- `try/except ImportError`：依赖缺失时优雅降级，而不是直接崩
- 函数内再 `import`：可选依赖只在用到时加载
- 嵌套 `class` / `def`：定义在函数作用域内，外面访问不到
"""

from __future__ import annotations

import argparse


def main(mock: bool) -> None:
    try:
        # [Python] 函数内导入：没装 langgraph 时，只有跑到这里才失败
        from typing import Annotated, TypedDict

        from langgraph.graph import END, START, StateGraph
        from langgraph.graph.message import add_messages
    except ImportError:
        print("未安装 langgraph。请执行: pip install -e \".[graph]\"")
        # [Python] `return`：提前结束函数，后面代码不再执行
        return

    # [Python] `TypedDict`：用类语法描述「固定键」的字典形状
    class State(TypedDict):
        messages: Annotated[list, add_messages]
        answer: str

    def thinker(state: State) -> dict:
        # mock/教学：不调真实 LLM
        # [Python] 链式下标：先取列表最后一项，再取其中的 `"content"`
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
    # [Python] `default=True`：即使不传 `--mock`，args.mock 也是 True
    parser.add_argument("--mock", action="store_true", default=True)
    args = parser.parse_args()
    main(mock=args.mock)
