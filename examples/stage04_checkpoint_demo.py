"""阶段 4：Checkpoint 演示。"""

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
    assert loaded is not None
    print("恢复成功:", loaded)
    print("下一步应继续:", [x for x in loaded.data["plan"] if x not in loaded.data["done"]])


if __name__ == "__main__":
    main()
