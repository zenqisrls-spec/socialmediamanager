from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from app.services.db_service import DBService


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ClientService:
    def __init__(self) -> None:
        self.db = DBService()

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        now = _now_iso()
        item = {
            "id": str(uuid.uuid4()),
            "name": payload["name"].strip(),
            "website": payload.get("website", "").strip(),
            "industry": payload.get("industry", "").strip(),
            "city": payload.get("city", "").strip(),
            "unique_value": payload.get("unique_value", "").strip(),
            "notes": payload.get("notes", "").strip(),
            "created_at": now,
            "updated_at": now,
        }
        with self.db.connect() as conn:
            conn.execute(
                """
                INSERT INTO clients(id, name, website, industry, city, unique_value, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["id"],
                    item["name"],
                    item["website"],
                    item["industry"],
                    item["city"],
                    item["unique_value"],
                    item["notes"],
                    item["created_at"],
                    item["updated_at"],
                ),
            )
            conn.commit()
        return item

    def update(self, client_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        current = self.get(client_id)
        if not current:
            return None
        merged = {**current, **payload, "updated_at": _now_iso()}
        with self.db.connect() as conn:
            conn.execute(
                """
                UPDATE clients
                SET name=?, website=?, industry=?, city=?, unique_value=?, notes=?, updated_at=?
                WHERE id=?
                """,
                (
                    merged["name"].strip(),
                    merged.get("website", "").strip(),
                    merged.get("industry", "").strip(),
                    merged.get("city", "").strip(),
                    merged.get("unique_value", "").strip(),
                    merged.get("notes", "").strip(),
                    merged["updated_at"],
                    client_id,
                ),
            )
            conn.commit()
        return self.get(client_id)

    def get(self, client_id: str) -> dict[str, Any] | None:
        with self.db.connect() as conn:
            row = conn.execute("SELECT * FROM clients WHERE id=?", (client_id,)).fetchone()
        return dict(row) if row else None

    def list(self) -> list[dict[str, Any]]:
        with self.db.connect() as conn:
            rows = conn.execute("SELECT * FROM clients ORDER BY updated_at DESC").fetchall()
        return [dict(r) for r in rows]
