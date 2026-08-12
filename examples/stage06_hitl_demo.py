"""阶段 6：HITL 状态机演示。"""

from __future__ import annotations

from agent_lab.planning import HitlState, next_state


def main() -> None:
    state = HitlState()
    state = next_state(state, "generated", "这是一篇待审核文案")
    print("待审核:", state)
    state = next_state(state, "reject", "语气太绝对")
    print("驳回修订:", state)
    state = next_state(state, "revised", "这是一篇更谨慎的文案")
    print("再次审核:", state)
    state = next_state(state, "approve", "LGTM")
    state = next_state(state, "published")
    print("完成:", state)


if __name__ == "__main__":
    main()
