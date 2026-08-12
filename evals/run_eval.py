"""最小评测运行器。"""

from __future__ import annotations

import json
from pathlib import Path


def load_cases(path: Path) -> list[dict]:
    cases = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            cases.append(json.loads(line))
    return cases


def grade(case: dict, output: str, tools_used: list[str] | None = None) -> dict:
    reasons = []
    ok = True
    for token in case.get("expect_contains") or []:
        if token not in output:
            ok = False
            reasons.append(f"缺少: {token}")
    expect_tool = case.get("expect_tool")
    if expect_tool:
        used = tools_used or []
        if expect_tool not in used:
            ok = False
            reasons.append(f"未调用工具: {expect_tool}")
    return {"id": case["id"], "ok": ok, "reasons": reasons}


def demo_outputs() -> dict[str, tuple[str, list[str]]]:
    """离线演示用输出（真实评测应跑 Agent）。"""
    return {
        "calc_1": ("结果是 16。", ["calculator"]),
        "rag_1": ("Tool Loop 是工具循环机制。", []),
        "refuse_1": ("资料不足，没有找到相关内容。", []),
    }


def main() -> None:
    cases = load_cases(Path(__file__).parent / "datasets" / "smoke.jsonl")
    outputs = demo_outputs()
    rows = []
    for case in cases:
        out, tools = outputs.get(case["id"], ("", []))
        rows.append(grade(case, out, tools))
    passed = sum(1 for r in rows if r["ok"])
    print(json.dumps({"passed": passed, "total": len(rows), "rows": rows}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
