"""阶段 6：Verifier 演示。

【Python 语法速览】（边学 Agent 边学 Python）
- 列表可混装不同长度的字符串（含空串 `""`）
- `for s in samples`：按元素迭代，不必手写下标
- f-string 里可嵌入多个表达式与 `!r`
"""

from __future__ import annotations

from agent_lab.agent.verifier import verify_final_answer


def main() -> None:
    samples = [
        "根据资料，Tool Loop 是核心。[tool_loop#0]",
        "随便说说而已",
        "",
    ]
    for s in samples:
        r = verify_final_answer(s, require_citation=True)
        # [Python] 一行 f-string 打印多个字段；`!r` 显示空串等边界情况
        print(f"ok={r.ok} reasons={r.reasons} text={s!r}")


if __name__ == "__main__":
    main()
