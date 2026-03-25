from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from app.services.db_service import DBService


class AuthService:
    def __init__(self) -> None:
        self.db = DBService()
        self.sessions: dict[str, dict[str, Any]] = {}

    def login(self, username: str, password: str) -> dict[str, str] | None:
        with self.db.connect() as conn:
            row = conn.execute(
                "SELECT username, role FROM users WHERE username=? AND password=?",
                (username, password),
            ).fetchone()
        if not row:
            return None
        token = secrets.token_urlsafe(32)
        self.sessions[token] = {
            "username": row["username"],
            "role": row["role"],
            "expires_at": datetime.now(timezone.utc) + timedelta(hours=8),
        }
        return {"access_token": token, "role": row["role"]}

    def validate(self, token: str) -> dict[str, Any] | None:
        session = self.sessions.get(token)
        if not session:
            return None
        if session["expires_at"] < datetime.now(timezone.utc):
            self.sessions.pop(token, None)
            return None
        return session

