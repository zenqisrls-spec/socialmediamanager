from __future__ import annotations

from datetime import datetime, timezone

from app.services.db_service import DBService


class AuditService:
    def __init__(self) -> None:
        self.db = DBService()

    def log(self, username: str, action: str, details: str) -> None:
        with self.db.connect() as conn:
            conn.execute(
                "INSERT INTO audit_logs(ts, username, action, details) VALUES (?, ?, ?, ?)",
                (datetime.now(timezone.utc).isoformat(), username, action, details),
            )
            conn.commit()

    def list_recent(self, limit: int = 100) -> list[dict]:
        with self.db.connect() as conn:
            rows = conn.execute(
                "SELECT ts, username, action, details FROM audit_logs ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]
