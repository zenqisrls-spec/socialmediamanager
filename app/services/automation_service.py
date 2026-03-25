from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any


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
        self.path = Path(__file__).resolve().parents[2] / "data" / "automation_state.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def _read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"drafts": [], "published": []}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return {"drafts": [], "published": []}

    def _write(self, data: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def create_draft(self, channel: str, content: str, scheduled_for: str | None) -> dict[str, Any]:
        with self._lock:
            state = self._read()
            item = {
                "id": str(uuid.uuid4()),
                "channel": channel,
                "content": content,
                "status": "pending_approval",
                "scheduled_for": scheduled_for or _now_iso(),
                "created_at": _now_iso(),
                "updated_at": _now_iso(),
            }
            state["drafts"].append(item)
            self._write(state)
            return item

    def list_drafts(self, status: str | None = None) -> list[dict[str, Any]]:
        state = self._read()
        drafts = state.get("drafts", [])
        if status:
            return [d for d in drafts if d.get("status") == status]
        return drafts

    def list_published(self) -> list[dict[str, Any]]:
        return self._read().get("published", [])

    def _update_status(self, draft_id: str, status: str) -> dict[str, Any] | None:
        with self._lock:
            state = self._read()
            for item in state["drafts"]:
                if item["id"] == draft_id:
                    item["status"] = status
                    item["updated_at"] = _now_iso()
                    self._write(state)
                    return item
            return None

    def approve(self, draft_id: str) -> dict[str, Any] | None:
        return self._update_status(draft_id, "approved")

    def reject(self, draft_id: str) -> dict[str, Any] | None:
        return self._update_status(draft_id, "rejected")

    def _simulate_publish(self, channel: str, content: str, whatsapp_enabled: bool) -> dict[str, Any]:
        message = f"Pubblicato su {channel} (simulato)."
        if channel.lower() == "whatsapp" and not whatsapp_enabled:
            return {"status": "failed", "message": "WhatsApp non abilitato in configurazione."}
        return {"status": "published", "message": message, "content_preview": content[:120]}

    def run(self, *, require_human_approval: bool, autopublish_enabled: bool, whatsapp_enabled: bool) -> dict[str, int]:
        with self._lock:
            state = self._read()
            processed = 0
            published = 0
            failed = 0

            for item in state.get("drafts", []):
                if item.get("status") in {"published", "rejected"}:
                    continue
                if require_human_approval and item.get("status") != "approved":
                    continue
                if not require_human_approval and item.get("status") == "pending_approval":
                    item["status"] = "approved"

                if not autopublish_enabled:
                    continue
                if not _is_due(item.get("scheduled_for", "")):
                    continue

                result = self._simulate_publish(item["channel"], item["content"], whatsapp_enabled)
                processed += 1
                if result["status"] == "published":
                    published += 1
                    item["status"] = "published"
                else:
                    failed += 1
                    item["status"] = "failed"
                item["updated_at"] = _now_iso()
                state["published"].append(
                    {
                        "draft_id": item["id"],
                        "channel": item["channel"],
                        "status": result["status"],
                        "message": result["message"],
                        "published_at": _now_iso(),
                    }
                )

            self._write(state)
            return {"processed": processed, "published": published, "failed": failed}

