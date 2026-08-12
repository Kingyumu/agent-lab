"""HITL 内容发布状态机（教学）。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Status = Literal["generate", "review", "revise", "publish", "cancelled", "done"]


@dataclass
class HitlState:
    status: Status = "generate"
    draft: str = ""
    review_note: str = ""


def next_state(state: HitlState, event: str, payload: str = "") -> HitlState:
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
