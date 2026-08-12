from agent_lab.agent.verifier import verify_final_answer
from agent_lab.rag import InMemoryLexicalIndex
from agent_lab.tools.builtin import calculator


def test_calculator() -> None:
    assert calculator({"expression": "(3+5)*2"}) == "16"


def test_verifier_citation() -> None:
    bad = verify_final_answer("没有引用的回答哦", require_citation=True)
    assert bad.ok is False
    good = verify_final_answer("依据在此 [doc#0]", require_citation=True)
    assert good.ok is True


def test_rag_search() -> None:
    idx = InMemoryLexicalIndex()
    idx.add_document("a", "Tool Loop 是工具循环，先手写再学框架。")
    hits = idx.search("什么是 Tool Loop", top_k=1)
    assert hits
    assert "Tool Loop" in hits[0].text or "工具" in hits[0].text
