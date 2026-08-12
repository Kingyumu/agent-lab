"""阶段 6：Verifier 演示。"""

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
        print(f"ok={r.ok} reasons={r.reasons} text={s!r}")


if __name__ == "__main__":
    main()
