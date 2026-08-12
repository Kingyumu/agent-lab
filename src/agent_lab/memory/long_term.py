"""长期记忆：SQLite 极简实现。"""

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
        self.db_path = Path(db_path)
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
            return [MemoryItem(*r) for r in rows]
