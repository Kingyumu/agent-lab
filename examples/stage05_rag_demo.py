"""阶段 5：RAG 演示（本地词法检索）。"""

from __future__ import annotations

from pathlib import Path

from agent_lab.rag import InMemoryLexicalIndex, answer_with_context


def main() -> None:
    docs_dir = Path("docs/sample_knowledge")
    index = InMemoryLexicalIndex()
    for path in sorted(docs_dir.glob("*.md")):
        index.add_document(path.stem, path.read_text(encoding="utf-8"))

    question = "什么是 Tool Loop？为什么先手写再学框架？"
    hits = index.search(question, top_k=3)
    print(answer_with_context(question, hits))


if __name__ == "__main__":
    main()
