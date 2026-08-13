"""文件型 Checkpoint（教学用）。

【Python 语法速览】（边学 Agent 边学 Python）
- `pathlib.Path`：跨平台路径对象，比纯字符串好用
- `str | Path`：联合类型，两种都能传
- `asdict(dataclass)`：数据类 → dict，方便 `json.dumps`
- `Checkpoint(**raw)`：字典拆包成关键字参数还原对象
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Checkpoint:
    run_id: str
    step: int
    status: str
    data: dict[str, Any] = field(default_factory=dict)


class FileCheckpointStore:
    def __init__(self, root: str | Path = ".checkpoints") -> None:
        # [Python] Path(root)：无论传入 str 还是 Path 都统一成 Path
        self.root = Path(root)
        # [Python] exist_ok=True：目录已存在不报错；parents=True 可建多级
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, run_id: str) -> Path:
        # [Python] `/` 运算符在 Path 上拼接路径段
        return self.root / f"{run_id}.json"

    def save(self, cp: Checkpoint) -> None:
        self._path(cp.run_id).write_text(
            # [Python] asdict 把 dataclass 变成可 JSON 的 dict
            json.dumps(asdict(cp), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def load(self, run_id: str) -> Checkpoint | None:
        path = self._path(run_id)
        if not path.exists():
            return None
        raw = json.loads(path.read_text(encoding="utf-8"))
        # [Python] **raw：把 dict 的键值拆成关键字参数传给构造函数
        return Checkpoint(**raw)
