"""长期记忆：SQLite 极简实现。

【Python 语法速览】（边学 Agent 边学 Python）
- `str | Path`：参数既可传字符串路径也可传 Path 对象
- `with`：上下文管理器，退出时自动 commit/close（视连接实现而定）
- `MemoryItem(*r)`：把元组/行按位置拆成构造参数
- `row[0] if row else None`：有查询结果取首列，否则返回 None
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass
class MemoryItem:
    user_id: str
    key: str
    value: str


class LongTermMemory:
    def __init__(self, db_path: str | Path = "data/long_term.db") -> None:
        # [Python] `Path(...)`：统一路径类型；字符串也会被转成 Path
        self.db_path = Path(db_path)
        # [Python] `parents=True` 可建多级目录；`exist_ok=True` 已存在不报错
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    user_id TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    PRIMARY KEY (user_id, key)
                )
                """
            )

    def upsert(self, user_id: str, key: str, value: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO memories(user_id, key, value) VALUES(?,?,?)
                ON CONFLICT(user_id, key) DO UPDATE SET value=excluded.value
                """,
                # [Python] 参数化查询：用 `?` 占位 + 元组传值，防 SQL 注入
                (user_id, key, value),
            )

    def get(self, user_id: str, key: str) -> str | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT value FROM memories WHERE user_id=? AND key=?",
                (user_id, key),
            ).fetchone()
            return row[0] if row else None

    def list(self, user_id: str) -> list[MemoryItem]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT user_id, key, value FROM memories WHERE user_id=?",
                (user_id,),
            ).fetchall()
            # [Python] `*r`：把每一行 (user_id, key, value) 拆成位置参数
            return [MemoryItem(*r) for r in rows]
