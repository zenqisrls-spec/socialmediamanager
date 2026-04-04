from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from app.services.db_service import DBService


class AuthService:
    def __init__(self) -> None:
        self.db = DBService()

    def login(self, username: str, password: str) -> dict[str, str] | None:
        with self.db.connect() as conn:
            row = conn.execute(
                "SELECT username, role FROM users WHERE username=? AND password=?",
                (username, password),
            ).fetchone()
        if not row:
            return None
        token = secrets.token_urlsafe(32)
        expires_at = (datetime.now(timezone.utc) + timedelta(hours=8)).isoformat()
        with self.db.connect() as conn:
            conn.execute("DELETE FROM sessions WHERE expires_at < ?", (datetime.now(timezone.utc).isoformat(),))
            conn.execute(
                "INSERT OR REPLACE INTO sessions(token, username, role, expires_at) VALUES (?, ?, ?, ?)",
                (token, row["username"], row["role"], expires_at),
            )
            conn.commit()
        return {"access_token": token, "role": row["role"]}

    def validate(self, token: str) -> dict[str, Any] | None:
        with self.db.connect() as conn:
            conn.execute("DELETE FROM sessions WHERE expires_at < ?", (datetime.now(timezone.utc).isoformat(),))
            row = conn.execute(
                "SELECT username, role, expires_at FROM sessions WHERE token=?",
                (token,),
            ).fetchone()
            conn.commit()
        if not row:
            return None
        expires_at = datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00"))
        if expires_at < datetime.now(timezone.utc):
            with self.db.connect() as conn:
                conn.execute("DELETE FROM sessions WHERE token=?", (token,))
                conn.commit()
            return None
        return {"username": row["username"], "role": row["role"], "expires_at": expires_at}
