from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from app.services.db_service import DBService


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class CampaignService:
    def __init__(self) -> None:
        self.db = DBService()

    def create_batch(self, *, name: str, notes: str, created_by: str, campaigns: list[dict[str, Any]]) -> dict[str, Any]:
        batch_id = str(uuid.uuid4())
        created_at = _now_iso()
        saved_campaigns: list[dict[str, Any]] = []
        with self.db.connect() as conn:
            conn.execute(
                "INSERT INTO campaign_batches(id, name, created_by, notes, created_at) VALUES (?, ?, ?, ?, ?)",
                (batch_id, name, created_by, notes, created_at),
            )
            for c in campaigns:
                campaign_id = str(uuid.uuid4())
                item = {
                    "id": campaign_id,
                    "batch_id": batch_id,
                    "platform": c["platform"],
                    "campaign_name": c["campaign_name"],
                    "objective": c["objective"],
                    "target_audience": c["target_audience"],
                    "daily_budget_eur": c["daily_budget_eur"],
                    "ad_copy": c["ad_copy"],
                    "creative_direction": c["creative_direction"],
                    "kpi_target": c["kpi_target"],
                    "creative_brief_image": c.get("creative_brief_image", ""),
                    "status": "draft",
                    "created_at": created_at,
                    "updated_at": created_at,
                }
                conn.execute(
                    """
                    INSERT INTO campaigns(
                        id, batch_id, platform, campaign_name, objective, target_audience,
                        daily_budget_eur, ad_copy, creative_direction, kpi_target, creative_brief_image,
                        status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        item["id"],
                        item["batch_id"],
                        item["platform"],
                        item["campaign_name"],
                        item["objective"],
                        item["target_audience"],
                        item["daily_budget_eur"],
                        item["ad_copy"],
                        item["creative_direction"],
                        item["kpi_target"],
                        item["creative_brief_image"],
                        item["status"],
                        item["created_at"],
                        item["updated_at"],
                    ),
                )
                saved_campaigns.append(item)
            conn.commit()
        return {
            "batch_id": batch_id,
            "name": name,
            "notes": notes,
            "created_by": created_by,
            "created_at": created_at,
            "campaigns": saved_campaigns,
        }

    def list_batches(self) -> list[dict[str, Any]]:
        with self.db.connect() as conn:
            rows = conn.execute("SELECT * FROM campaign_batches ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]

    def list_campaigns(self, *, batch_id: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM campaigns WHERE 1=1"
        params: list[Any] = []
        if batch_id:
            query += " AND batch_id=?"
            params.append(batch_id)
        if status:
            query += " AND status=?"
            params.append(status)
        query += " ORDER BY created_at DESC"
        with self.db.connect() as conn:
            rows = conn.execute(query, tuple(params)).fetchall()
        return [dict(r) for r in rows]

    def update_campaign_status(self, campaign_id: str, status: str) -> dict[str, Any] | None:
        with self.db.connect() as conn:
            row = conn.execute("SELECT * FROM campaigns WHERE id=?", (campaign_id,)).fetchone()
            if not row:
                return None
            conn.execute("UPDATE campaigns SET status=?, updated_at=? WHERE id=?", (status, _now_iso(), campaign_id))
            conn.commit()
            updated = conn.execute("SELECT * FROM campaigns WHERE id=?", (campaign_id,)).fetchone()
        return dict(updated) if updated else None
