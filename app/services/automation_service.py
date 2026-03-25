from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from app.services.db_service import DBService
from app.services.publisher_service import PublisherService


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _is_due(when: str) -> bool:
    try:
        dt = datetime.fromisoformat(when.replace("Z", "+00:00"))
    except Exception:
        return True
    return dt <= datetime.now(timezone.utc)


class AutomationService:
    def __init__(self) -> None:
        self.db = DBService()
        self.publisher = PublisherService()

    def create_draft(self, channel: str, content: str, scheduled_for: str | None) -> dict[str, Any]:
        item = {
            "id": str(uuid.uuid4()),
            "channel": channel,
            "content": content,
            "status": "pending_approval",
            "scheduled_for": scheduled_for or _now_iso(),
            "created_at": _now_iso(),
            "updated_at": _now_iso(),
        }
        with self.db.connect() as conn:
            conn.execute(
                """
                INSERT INTO drafts(id, channel, content, status, scheduled_for, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["id"],
                    item["channel"],
                    item["content"],
                    item["status"],
                    item["scheduled_for"],
                    item["created_at"],
                    item["updated_at"],
                ),
            )
            conn.commit()
        return item

    def list_drafts(self, status: str | None = None) -> list[dict[str, Any]]:
        with self.db.connect() as conn:
            if status:
                rows = conn.execute("SELECT * FROM drafts WHERE status=? ORDER BY created_at DESC", (status,)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM drafts ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]

    def list_published(self) -> list[dict[str, Any]]:
        with self.db.connect() as conn:
            rows = conn.execute("SELECT draft_id, channel, status, message, published_at FROM published ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]

    def _update_status(self, draft_id: str, status: str) -> dict[str, Any] | None:
        with self.db.connect() as conn:
            row = conn.execute("SELECT * FROM drafts WHERE id=?", (draft_id,)).fetchone()
            if not row:
                return None
            conn.execute("UPDATE drafts SET status=?, updated_at=? WHERE id=?", (status, _now_iso(), draft_id))
            conn.commit()
            updated = conn.execute("SELECT * FROM drafts WHERE id=?", (draft_id,)).fetchone()
        return dict(updated) if updated else None

    def approve(self, draft_id: str) -> dict[str, Any] | None:
        return self._update_status(draft_id, "approved")

    def reject(self, draft_id: str) -> dict[str, Any] | None:
        return self._update_status(draft_id, "rejected")

    def run(self, *, require_human_approval: bool, autopublish_enabled: bool, cfg: dict[str, Any]) -> dict[str, int]:
        processed = 0
        published = 0
        failed = 0
        with self.db.connect() as conn:
            rows = conn.execute("SELECT * FROM drafts ORDER BY created_at ASC").fetchall()
            for row in rows:
                item = dict(row)
                if item["status"] in {"published", "rejected", "failed"}:
                    continue
                if require_human_approval and item["status"] != "approved":
                    continue
                if not require_human_approval and item["status"] == "pending_approval":
                    conn.execute("UPDATE drafts SET status=?, updated_at=? WHERE id=?", ("approved", _now_iso(), item["id"]))
                    item["status"] = "approved"
                if not autopublish_enabled:
                    continue
                if not _is_due(item.get("scheduled_for", "")):
                    continue

                result = self.publisher.publish(item["channel"], item["content"], cfg)
                processed += 1
                if result["status"] == "published":
                    published += 1
                else:
                    failed += 1
                new_status = "published" if result["status"] == "published" else "failed"
                conn.execute("UPDATE drafts SET status=?, updated_at=? WHERE id=?", (new_status, _now_iso(), item["id"]))
                conn.execute(
                    "INSERT INTO published(draft_id, channel, status, message, published_at) VALUES (?, ?, ?, ?, ?)",
                    (item["id"], item["channel"], result["status"], result["message"], _now_iso()),
                )
            conn.commit()
        return {"processed": processed, "published": published, "failed": failed}

    def summary(self) -> dict[str, Any]:
        drafts = self.list_drafts()
        published_items = self.list_published()

        by_status: dict[str, int] = {}
        by_channel: dict[str, int] = {}
        for d in drafts:
            by_status[d["status"]] = by_status.get(d["status"], 0) + 1
            by_channel[d["channel"]] = by_channel.get(d["channel"], 0) + 1

        published_ok = len([p for p in published_items if p["status"] == "published"])
        published_failed = len([p for p in published_items if p["status"] == "failed"])
        return {
            "drafts_total": len(drafts),
            "published_total": len(published_items),
            "published_ok": published_ok,
            "published_failed": published_failed,
            "drafts_by_status": by_status,
            "drafts_by_channel": by_channel,
        }

