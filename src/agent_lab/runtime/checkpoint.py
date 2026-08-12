"""文件型 Checkpoint（教学用）。"""

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
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, run_id: str) -> Path:
        return self.root / f"{run_id}.json"

    def save(self, cp: Checkpoint) -> None:
        self._path(cp.run_id).write_text(
            json.dumps(asdict(cp), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def load(self, run_id: str) -> Checkpoint | None:
        path = self._path(run_id)
        if not path.exists():
            return None
        raw = json.loads(path.read_text(encoding="utf-8"))
        return Checkpoint(**raw)
