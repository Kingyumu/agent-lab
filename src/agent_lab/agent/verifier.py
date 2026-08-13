"""规则型 Verifier。

【Python 语法速览】（边学 Agent 边学 Python）
- `not reasons`：空列表为假；`ok=not reasons` 表示「无失败原因即通过」
- `re.search`：在字符串中找第一个正则匹配
- 关键字专用参数 `*`：`require_citation` 必须写成 `require_citation=True`
"""

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
    # [Python] 原始字符串里 `\[` 匹配字面量 `[`；`\w` 匹配字母数字下划线
    if require_citation and not re.search(r"\[[\w\-#\.]+\]", text):
        reasons.append("缺少引用（期望类似 [doc#0]）")
    return VerifyResult(ok=not reasons, reasons=reasons)
