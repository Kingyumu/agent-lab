"""阶段 4：Checkpoint 演示。

【Python 语法速览】（边学 Agent 边学 Python）
- `assert 条件`：条件为假则抛 AssertionError（教学/测试常用）
- 列表推导 `[x for x in xs if 条件]`：边过滤边生成新列表
- 字典字面量 `{"k": v}`：用花括号写键值对
"""

from __future__ import annotations

from agent_lab.runtime import Checkpoint, FileCheckpointStore


def main() -> None:
    store = FileCheckpointStore(".checkpoints")
    cp = Checkpoint(
        run_id="demo-run-1",
        step=2,
        status="interrupted",
        data={"plan": ["搜集资料", "写总结"], "done": ["搜集资料"]},
    )
    store.save(cp)
    loaded = store.load("demo-run-1")
    # [Python] `assert`：确信「不应为 None」；失败会立刻中断并报错
    assert loaded is not None
    print("恢复成功:", loaded)
    # [Python] 列表推导 + `not in`：筛出 plan 里尚未完成的项
    print("下一步应继续:", [x for x in loaded.data["plan"] if x not in loaded.data["done"]])


if __name__ == "__main__":
    main()
