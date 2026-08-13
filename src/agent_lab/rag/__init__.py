"""简易 RAG：分块 + 词法检索（教学用，零向量依赖）。

【Python 语法速览】（边学 Agent 边学 Python）
- `re.sub` / `re.findall`：正则清洗空白、抽词（含中文 Unicode 范围）
- `while` + 滑动窗口：按 chunk_size/overlap 切文本
- 集合运算 `q & tokens`：交集大小当简易相关分
- `hits.sort(key=..., reverse=True)`：按分数降序再切片取 top_k
"""

from __future__ import annotations

import re
from dataclasses import dataclass


def chunk_text(text: str, chunk_size: int = 180, overlap: int = 40) -> list[str]:
    # [Python] re.sub：把任意空白压成单个空格
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
        # [Python] max(0, ...)：防止 overlap 过大时 start 变负
        start = max(0, end - overlap)
    return chunks


def _tokenize(text: str) -> set[str]:
    # [Python] findall + set：抽词并去重；`\u4e00-\u9fff` 覆盖常用汉字
    return set(re.findall(r"[\w\u4e00-\u9fff]+", text.lower()))


@dataclass
class ChunkHit:
    chunk_id: str
    text: str
    score: float
    source: str


class InMemoryLexicalIndex:
    def __init__(self) -> None:
        # [Python] dict 值用元组打包 (source, text)
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
            # [Python] `&` 对 set 是交集；len 即重叠词数
            overlap = len(q & tokens)
            score = overlap / max(1, len(q))
            if score > 0:
                hits.append(ChunkHit(chunk_id=cid, text=text, score=score, source=source))
        # [Python] key=lambda：按 score 排序；reverse=True 从高到低
        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:top_k]


def format_context(hits: list[ChunkHit]) -> str:
    blocks = []
    for h in hits:
        # [Python] f-string 里 `{h.score:.2f}`：浮点保留两位
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
