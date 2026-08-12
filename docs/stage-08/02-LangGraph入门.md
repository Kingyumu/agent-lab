# 第8章第2节：LangGraph 入门（对照着学）

## 一句话

LangGraph 用「图」管理状态：节点写逻辑，边决定下一步。

## 对照表（请抄到笔记）

| 你已会的自研概念 | LangGraph |
|------------------|-----------|
| messages 列表 | State 里的字段 |
| while tool loop | 条件边形成的环 |
| HITL 暂停 | interrupt / 人工节点 |
| 文件 checkpoint | Checkpointer |

## 官方建议路径

1. Introduction 教程  
2. Low-level concepts（State/Node/Edge）  
3. persistence 与 HITL how-to  
4. 把 calculator Agent 用 Graph 重写  

---

## 打开代码一起看（本仓库最小图）

打开 `examples/stage08_langgraph_demo.py`（需 `pip install -e ".[graph]"`）。

### 1）状态

```python
class State(TypedDict):
    messages: Annotated[list, add_messages]  # 追加消息用 reducer
    answer: str
```

`add_messages`：多次写入 messages 时自动合并列表，而不是整表覆盖。

### 2）节点 = 一个函数

```python
def thinker(state: State) -> dict:
    last = state["messages"][-1]["content"]
    return {"answer": f"(graph) 已处理：{last}"}
```

节点返回的是「要更新的字段」，不是整个世界状态。

### 3）边 = 固定流向

```python
g = StateGraph(State)
g.add_node("thinker", thinker)
g.add_edge(START, "thinker")
g.add_edge("thinker", END)
app = g.compile()
```

教学版没有条件边；真实 Tool Agent 会在「要不要再调工具」上分叉。

### 4）调用

```python
result = app.invoke({
    "messages": [{"role": "user", "content": "你好，LangGraph"}],
    "answer": "",
})
```

```powershell
pip install -e ".[graph]"
python examples/stage08_langgraph_demo.py --mock
```

未安装时脚本会提示——先读代码也行。

### 5）和自研 Loop 的关系

`stage08_framework_notes_demo.py` 打印的路线图：

```text
自研 AgentLoop → 官方 SDK → LangGraph →（可选）LlamaIndex
```

---

## 动手做

（必做）用自己的话解释：为什么 HITL 很适合用图，而不是深层 if-else。

## 课后阅读

1. https://langchain-ai.github.io/langgraph/tutorials/introduction/  
2. https://langchain-ai.github.io/langgraph/concepts/low_level/

## 下一节

→ [03-框架选型.md](03-框架选型.md)
