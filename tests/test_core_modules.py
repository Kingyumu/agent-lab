"""核心模块单元测试（计算器 / 校验 / RAG）。

【Python 语法速览】（边学 Agent 边学 Python）
- `assert A == B`：比较相等；测试失败时 pytest 会高亮差异
- `assert 列表`：空列表为假，非空为真（真值测试）
- `or`：短路或，左边为真就不算右边
"""

from agent_lab.agent.verifier import verify_final_answer
from agent_lab.rag import InMemoryLexicalIndex
from agent_lab.tools.builtin import calculator


def test_calculator() -> None:
    assert calculator({"expression": "(3+5)*2"}) == "16"


def test_verifier_citation() -> None:
    bad = verify_final_answer("没有引用的回答哦", require_citation=True)
    # [Python] `is False`：身份比较；对布尔字面量比 `== False` 更明确
    assert bad.ok is False
    good = verify_final_answer("依据在此 [doc#0]", require_citation=True)
    assert good.ok is True


def test_rag_search() -> None:
    idx = InMemoryLexicalIndex()
    idx.add_document("a", "Tool Loop 是工具循环，先手写再学框架。")
    hits = idx.search("什么是 Tool Loop", top_k=1)
    # [Python] 非空序列在布尔上下文中为 True
    assert hits
    # [Python] `or`：任一子串命中即可
    assert "Tool Loop" in hits[0].text or "工具" in hits[0].text
