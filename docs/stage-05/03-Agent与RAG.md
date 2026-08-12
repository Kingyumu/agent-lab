# 第5章第3节：把 RAG 接到 Agent 上

## 写在前面

两种接法：

1. **固定流程**：每次先检索再回答（稳）  
2. **Agentic RAG**：把 `search` / `read` 当工具，由模型决定何时查（活）

初学先理解 1，再做 2。

---

## 本节你将学会

1. 为什么工具要拆成 search 和 read  
2. 如何对照第3章 `ToolRegistry` 写出伪代码/真代码骨架  
3. 无依据时如何拒答（代码里已有分支）

---

## 一步一步讲

### 固定流程

```text
问题 → index.search → format_context →（可选）LLM 生成
```

对应现成函数：`search` + `answer_with_context`。

### Agentic RAG

```text
模型可调用：
  search(query) → 候选列表（id/score/摘要）
  read(chunk_id) → 完整片段
  然后生成最终答案，带 [chunk_id]
```

---

## 打开代码一起看（接 Agent 的落地写法）

### 1）拒答已经写在 RAG 层

```python
# rag/__init__.py
def answer_with_context(question, hits):
    if not hits:
        return "资料不足，知识库中没有找到相关内容。"
```

Agent 版也应：search 为空 → 直接最终回答「资料不足」，不要硬编。

### 2）把 `search` 包成工具（对照第3章）

伪代码（建议你真的写进 `builtin.py` 练手）：

```python
def search_knowledge(args: dict) -> str:
    query = args["query"]
    hits = INDEX.search(query, top_k=3)
    if not hits:
        return "NO_HITS"
    # 返回给模型看的短列表，不要一次 dump 全文
    return "\n".join(f"{h.chunk_id} score={h.score:.2f} | {h.text[:80]}" for h in hits)
```

schema 大意：

```json
{
  "name": "search_knowledge",
  "description": "在本地知识库检索相关片段。回答制度/文档问题前必须先调用。",
  "parameters": {
    "type": "object",
    "properties": {"query": {"type": "string"}},
    "required": ["query"]
  }
}
```

`read_chunk` 可再做一个：参数 `chunk_id`，从 `INDEX` 取全文。

### 3）和 Verifier 联动（第6章预告）

最终答案要求带 `[tool_loop#0]` 这种引用时，可用 `verify_final_answer(..., require_citation=True)` 拦一道。

### 4）当前仓库演示边界

`stage05_rag_demo.py` 仍是固定流程、不调 AgentLoop。  
本节目标是：**你能画出/写出如何接到第3章**，不一定本仓库已接线完毕。

---

## 动手做

1. （必做）把上面 `search_knowledge` 伪代码抄进笔记，补全 `Tool(...)` 注册三行。  
2. （必做）规定最终答案格式：结论 + `[chunk_id]`。  
3. （选做）真的改代码接入 `AgentLoop` 跑一个问答。

---

## 小结 / 第5章收束

开卷考试 + 工具化检索 = 知识库助手雏形。

## 课后阅读

- [Anthropic Citations](https://docs.anthropic.com/en/docs/build-with-claude/citations)

## 下一章

→ [../stage-06/README.md](../stage-06/README.md)
