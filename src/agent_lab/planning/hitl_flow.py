"""HITL 内容发布状态机（教学）。

【Python 语法速览】（边学 Agent 边学 Python）
- `Literal[...]` 类型别名：把「允许的状态字符串」收成一个名字
- `@dataclass`：状态对象用字段描述，转移时返回「新实例」更安全
- 纯函数 `next_state`：输入旧状态+事件 → 新状态，便于单测与教学
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

# [Python] 类型别名：Status 只能是这些字面量之一
Status = Literal["generate", "review", "revise", "publish", "cancelled", "done"]


@dataclass
class HitlState:
    status: Status = "generate"
    draft: str = ""
    review_note: str = ""


def next_state(state: HitlState, event: str, payload: str = "") -> HitlState:
    # [Python] 每个分支 return 新 HitlState：不改入参，状态转移更清晰
    if state.status == "generate" and event == "generated":
        return HitlState(status="review", draft=payload)
    if state.status == "review" and event == "approve":
        return HitlState(status="publish", draft=state.draft, review_note=payload)
    if state.status == "review" and event == "reject":
        return HitlState(status="revise", draft=state.draft, review_note=payload)
    if state.status == "revise" and event == "revised":
        return HitlState(status="review", draft=payload, review_note=state.review_note)
    if state.status == "publish" and event == "published":
        return HitlState(status="done", draft=state.draft, review_note=state.review_note)
    if event == "cancel":
        return HitlState(status="cancelled", draft=state.draft, review_note=payload)
    raise ValueError(f"非法转移: status={state.status}, event={event}")
