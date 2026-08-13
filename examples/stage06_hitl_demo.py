"""阶段 6：HITL 状态机演示。

【Python 语法速览】（边学 Agent 边学 Python）
- 不可变「流转」习惯：`state = next_state(state, ...)` 用新值覆盖变量名
- 函数可有可选参数：这里最后一次调用只传事件名
- 打印自定义对象：依赖其 `__repr__`/`__str__` 展示可读内容
"""

from __future__ import annotations

from agent_lab.planning import HitlState, next_state


def main() -> None:
    state = HitlState()
    # [Python] 把返回的新状态重新赋给同名变量，表示「推进一拍」
    state = next_state(state, "generated", "这是一篇待审核文案")
    print("待审核:", state)
    state = next_state(state, "reject", "语气太绝对")
    print("驳回修订:", state)
    state = next_state(state, "revised", "这是一篇更谨慎的文案")
    print("再次审核:", state)
    state = next_state(state, "approve", "LGTM")
    # [Python] 少传一个可选参数：函数内部会用默认值
    state = next_state(state, "published")
    print("完成:", state)


if __name__ == "__main__":
    main()
