# 第5章第1节：RAG 流水线（从零看懂）

## 写在前面

把 RAG 想成「开卷考试」：

- 闭卷：全靠模型背（会瞎编）
- 开卷：先翻到相关页，再根据书页回答（可引用）

---

## 本节你将学会

1. RAG 的标准四步
2. 什么是分块（chunk）
3. 如何跑通本仓库的检索演示

---

## 一步一步讲

### 第1步：文档进来

例如 `docs/sample_knowledge/tool_loop.md`。

### 第2步：切成小块

太长的文章不好检索。切成小段，每段有 id，如 `tool_loop#0`。

### 第3步：建立索引

教学版：记住每段有哪些词。  
进阶版：把每段变成向量（embedding）存进向量库。

### 第4步：提问时检索 Top-K 段

找出和问题最相关的几段。

### 第5步：把片段塞进提示词，再生成答案

本示例为了不强制 Key，会先打印「检索到的依据」；你接 LLM 后就能生成最终回答。

---

## 打开代码一起看（对照 `src/agent_lab/rag/__init__.py`）

本仓库的 RAG **故意不用向量库**，方便你先看懂流水线。

### 1）`chunk_text`：按长度切段，带 overlap

```text
原文 ────────────────
切成： [----chunk0----]
           [----chunk1----]   ← 与上一段有重叠，避免句子被切断丢上下文
```

`chunk_size=180`、`overlap=40` 是教学默认值，可改着玩。

### 2）`add_document`：给每段一个 id

```text
doc_id = "tool_loop"
→ tool_loop#0, tool_loop#1, ...
```

存在内存字典 `_chunks[chunk_id] = (source, text)`。

### 3）`search`：词重叠打分（教学版「检索」）

```text
问题分词 → 集合 Q
每段分词 → 集合 T
score = |Q ∩ T| / |Q|
取 score>0 的前 top_k 段
```

所以问「Tool Loop」能命中含这些词的段落；问火星门牌号通常 score 全 0。

### 4）`answer_with_context`：先检索，再（可）生成

```python
if not hits:
    return "资料不足..."
# 教学版：不调用 LLM，把命中片段格式化打印出来
# 接上 LLM 时：把 format_context(hits) 塞进 Prompt 再 chat
```

### 5）演示脚本在干什么

`examples/stage05_rag_demo.py`：读取 `docs/sample_knowledge/*.md` → 建索引 → search → 打印。

```powershell
python examples/stage05_rag_demo.py
```

---

## 动手做

1. （必做）改问题为「什么是 RAG？」，看是否命中 `rag_basics`。  
2. （必做）问一个库里没有的问题，看是否走向「资料不足」路径（可阅读 `answer_with_context` 的空命中分支）。

---

## 小结

RAG = 检索 + 生成；检索质量决定上限。

## 课后阅读

- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)（先读概念，再实践）  
- [Chroma Getting Started](https://docs.trychroma.com/docs/overview/getting-started)

## 下一节

→ [02-检索质量.md](02-检索质量.md)
