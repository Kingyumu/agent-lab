"""规则型 Verifier。"""

from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass
class VerifyResult:
    ok: bool
    reasons: list[str]


def verify_final_answer(text: str, *, require_citation: bool = False) -> VerifyResult:
    reasons: list[str] = []
    if not text or not text.strip():
        reasons.append("答案为空")
    if len(text.strip()) < 5:
        reasons.append("答案过短")
    if require_citation and not re.search(r"\[[\w\-#\.]+\]", text):
        reasons.append("缺少引用（期望类似 [doc#0]）")
    return VerifyResult(ok=not reasons, reasons=reasons)
