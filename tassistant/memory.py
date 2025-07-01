"""SQLite-based memory for storing trading plans."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class PlanRecord:
    id: int
    ticker: str
    timestamp: datetime
    plan: str
    status: str


class Memory:
    def __init__(self, db_path: str = "memory.db") -> None:
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self._init_db()

    def _init_db(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                plan TEXT NOT NULL,
                status TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def add_plan(self, ticker: str, plan: str, status: str = "active") -> int:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO plans (ticker, timestamp, plan, status) VALUES (?, ?, ?, ?)",
            (ticker, datetime.utcnow().isoformat(), plan, status),
        )
        self.conn.commit()
        return cur.lastrowid

    def update_status(self, plan_id: int, status: str) -> None:
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE plans SET status=? WHERE id=?",
            (status, plan_id),
        )
        self.conn.commit()

    def latest_plan(self, ticker: str) -> Optional[PlanRecord]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id, ticker, timestamp, plan, status FROM plans WHERE ticker=? ORDER BY id DESC LIMIT 1",
            (ticker,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return PlanRecord(
            id=row[0],
            ticker=row[1],
            timestamp=datetime.fromisoformat(row[2]),
            plan=row[3],
            status=row[4],
        )

    def close(self) -> None:
        self.conn.close()
