"""简易 RAG：分块 + 词法检索（教学用，零向量依赖）。"""

from __future__ import annotations

import re
from dataclasses import dataclass


def chunk_text(text: str, chunk_size: int = 180, overlap: int = 40) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = max(0, end - overlap)
    return chunks


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[\w\u4e00-\u9fff]+", text.lower()))


@dataclass
class ChunkHit:
    chunk_id: str
    text: str
    score: float
    source: str


class InMemoryLexicalIndex:
    def __init__(self) -> None:
        self._chunks: dict[str, tuple[str, str]] = {}

    def add_document(self, doc_id: str, text: str, *, chunk_size: int = 180) -> int:
        parts = chunk_text(text, chunk_size=chunk_size)
        for i, part in enumerate(parts):
            cid = f"{doc_id}#{i}"
            self._chunks[cid] = (doc_id, part)
        return len(parts)

    def search(self, query: str, top_k: int = 3) -> list[ChunkHit]:
        q = _tokenize(query)
        hits: list[ChunkHit] = []
        for cid, (source, text) in self._chunks.items():
            tokens = _tokenize(text)
            if not tokens:
                continue
            overlap = len(q & tokens)
            score = overlap / max(1, len(q))
            if score > 0:
                hits.append(ChunkHit(chunk_id=cid, text=text, score=score, source=source))
        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:top_k]


def format_context(hits: list[ChunkHit]) -> str:
    blocks = []
    for h in hits:
        blocks.append(f"[{h.chunk_id} source={h.source} score={h.score:.2f}]\n{h.text}")
    return "\n\n".join(blocks)


def answer_with_context(question: str, hits: list[ChunkHit]) -> str:
    if not hits:
        return "资料不足，知识库中没有找到相关内容。"
    ctx = format_context(hits)
    # 教学：不调用 LLM，直接返回可引用的检索结果摘要
    cites = ", ".join(h.chunk_id for h in hits)
    return (
        f"问题：{question}\n"
        f"检索到 {len(hits)} 条依据（{cites}）。\n"
        f"可将其送入 LLM 生成最终答案。上下文如下：\n\n{ctx}"
    )
