"""阶段 5：RAG 演示（本地词法检索）。

【Python 语法速览】（边学 Agent 边学 Python）
- `Path.glob("*.md")`：按通配符枚举目录下匹配的文件
- `for path in sorted(...)`：先排序再遍历，结果可复现
- `path.stem`：文件名去掉后缀；`read_text` 读全文
"""

from __future__ import annotations

from pathlib import Path

from agent_lab.rag import InMemoryLexicalIndex, answer_with_context


def main() -> None:
    docs_dir = Path("docs/sample_knowledge")
    index = InMemoryLexicalIndex()
    # [Python] `glob` 找匹配文件；`stem` 是不含扩展名的文件名
    for path in sorted(docs_dir.glob("*.md")):
        index.add_document(path.stem, path.read_text(encoding="utf-8"))

    question = "什么是 Tool Loop？为什么先手写再学框架？"
    hits = index.search(question, top_k=3)
    print(answer_with_context(question, hits))


if __name__ == "__main__":
    main()
