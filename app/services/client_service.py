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
            "openai_api_key": payload.get("openai_api_key", "").strip(),
            "model_name": payload.get("model_name", "gpt-4.1-mini").strip() or "gpt-4.1-mini",
            "require_human_approval": bool(payload.get("require_human_approval", True)),
            "autopublish_enabled": bool(payload.get("autopublish_enabled", False)),
            "whatsapp_enabled": bool(payload.get("whatsapp_enabled", False)),
            "meta_access_token": payload.get("meta_access_token", "").strip(),
            "meta_page_id": payload.get("meta_page_id", "").strip(),
            "meta_ad_account_id": payload.get("meta_ad_account_id", "").strip(),
            "whatsapp_token": payload.get("whatsapp_token", "").strip(),
            "whatsapp_phone_number_id": payload.get("whatsapp_phone_number_id", "").strip(),
            "whatsapp_to": payload.get("whatsapp_to", "").strip(),
            "google_ads_customer_id": payload.get("google_ads_customer_id", "").strip(),
            "google_ads_developer_token": payload.get("google_ads_developer_token", "").strip(),
            "google_ads_refresh_token": payload.get("google_ads_refresh_token", "").strip(),
            "google_ads_client_id": payload.get("google_ads_client_id", "").strip(),
            "google_ads_client_secret": payload.get("google_ads_client_secret", "").strip(),
            "created_at": now,
            "updated_at": now,
        }
        with self.db.connect() as conn:
            conn.execute(
                """
                INSERT INTO clients(
                    id, name, website, industry, city, unique_value, notes,
                    openai_api_key, model_name, require_human_approval, autopublish_enabled, whatsapp_enabled,
                    meta_access_token, meta_page_id, meta_ad_account_id, whatsapp_token, whatsapp_phone_number_id, whatsapp_to,
                    google_ads_customer_id, google_ads_developer_token, google_ads_refresh_token, google_ads_client_id, google_ads_client_secret,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["id"],
                    item["name"],
                    item["website"],
                    item["industry"],
                    item["city"],
                    item["unique_value"],
                    item["notes"],
                    item["openai_api_key"],
                    item["model_name"],
                    int(item["require_human_approval"]),
                    int(item["autopublish_enabled"]),
                    int(item["whatsapp_enabled"]),
                    item["meta_access_token"],
                    item["meta_page_id"],
                    item["meta_ad_account_id"],
                    item["whatsapp_token"],
                    item["whatsapp_phone_number_id"],
                    item["whatsapp_to"],
                    item["google_ads_customer_id"],
                    item["google_ads_developer_token"],
                    item["google_ads_refresh_token"],
                    item["google_ads_client_id"],
                    item["google_ads_client_secret"],
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
                SET name=?, website=?, industry=?, city=?, unique_value=?, notes=?,
                    openai_api_key=?, model_name=?, require_human_approval=?, autopublish_enabled=?, whatsapp_enabled=?,
                    meta_access_token=?, meta_page_id=?, meta_ad_account_id=?, whatsapp_token=?, whatsapp_phone_number_id=?, whatsapp_to=?,
                    google_ads_customer_id=?, google_ads_developer_token=?, google_ads_refresh_token=?, google_ads_client_id=?, google_ads_client_secret=?,
                    updated_at=?
                WHERE id=?
                """,
                (
                    merged["name"].strip(),
                    merged.get("website", "").strip(),
                    merged.get("industry", "").strip(),
                    merged.get("city", "").strip(),
                    merged.get("unique_value", "").strip(),
                    merged.get("notes", "").strip(),
                    merged.get("openai_api_key", "").strip(),
                    merged.get("model_name", "gpt-4.1-mini").strip() or "gpt-4.1-mini",
                    int(bool(merged.get("require_human_approval", True))),
                    int(bool(merged.get("autopublish_enabled", False))),
                    int(bool(merged.get("whatsapp_enabled", False))),
                    merged.get("meta_access_token", "").strip(),
                    merged.get("meta_page_id", "").strip(),
                    merged.get("meta_ad_account_id", "").strip(),
                    merged.get("whatsapp_token", "").strip(),
                    merged.get("whatsapp_phone_number_id", "").strip(),
                    merged.get("whatsapp_to", "").strip(),
                    merged.get("google_ads_customer_id", "").strip(),
                    merged.get("google_ads_developer_token", "").strip(),
                    merged.get("google_ads_refresh_token", "").strip(),
                    merged.get("google_ads_client_id", "").strip(),
                    merged.get("google_ads_client_secret", "").strip(),
                    merged["updated_at"],
                    client_id,
                ),
            )
            conn.commit()
        return self.get(client_id)

    def get(self, client_id: str) -> dict[str, Any] | None:
        with self.db.connect() as conn:
            row = conn.execute("SELECT * FROM clients WHERE id=?", (client_id,)).fetchone()
        if not row:
            return None
        item = dict(row)
        item["require_human_approval"] = bool(item.get("require_human_approval"))
        item["autopublish_enabled"] = bool(item.get("autopublish_enabled"))
        item["whatsapp_enabled"] = bool(item.get("whatsapp_enabled"))
        return item

    def list(self) -> list[dict[str, Any]]:
        with self.db.connect() as conn:
            rows = conn.execute("SELECT * FROM clients ORDER BY updated_at DESC").fetchall()
        result = []
        for r in rows:
            item = dict(r)
            item["require_human_approval"] = bool(item.get("require_human_approval"))
            item["autopublish_enabled"] = bool(item.get("autopublish_enabled"))
            item["whatsapp_enabled"] = bool(item.get("whatsapp_enabled"))
            result.append(item)
        return result
