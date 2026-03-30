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

    def create_batch(
        self, *, client_id: str, name: str, notes: str, created_by: str, campaigns: list[dict[str, Any]]
    ) -> dict[str, Any]:
        batch_id = str(uuid.uuid4())
        created_at = _now_iso()
        saved_campaigns: list[dict[str, Any]] = []
        with self.db.connect() as conn:
            conn.execute(
                "INSERT INTO campaign_batches(id, client_id, name, created_by, notes, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (batch_id, client_id, name, created_by, notes, created_at),
            )
            for c in campaigns:
                campaign_id = str(uuid.uuid4())
                item = {
                    "id": campaign_id,
                    "client_id": client_id,
                    "batch_id": batch_id,
                    "platform": c.get("platform", "Meta Ads"),
                    "campaign_name": c.get("campaign_name", "Campagna"),
                    "objective": c.get("objective", "Lead generation"),
                    "target_audience": c.get("target_audience", "Pubblico target"),
                    "daily_budget_eur": float(c.get("daily_budget_eur", 20.0)),
                    "ad_copy": c.get("ad_copy", "Messaggio campagna"),
                    "creative_direction": c.get("creative_direction", "Creatività standard"),
                    "kpi_target": c.get("kpi_target", "CTR > 3%"),
                    "creative_brief_image": c.get("creative_brief_image", ""),
                    "status": "draft",
                    "created_at": created_at,
                    "updated_at": created_at,
                }
                conn.execute(
                    """
                    INSERT INTO campaigns(
                        id, client_id, batch_id, platform, campaign_name, objective, target_audience,
                        daily_budget_eur, ad_copy, creative_direction, kpi_target, creative_brief_image,
                        status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        item["id"],
                        item["client_id"],
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
            "client_id": client_id,
            "name": name,
            "notes": notes,
            "created_by": created_by,
            "created_at": created_at,
            "campaigns": saved_campaigns,
        }

    def list_batches(self, *, client_id: str | None = None) -> list[dict[str, Any]]:
        with self.db.connect() as conn:
            if client_id:
                rows = conn.execute(
                    "SELECT * FROM campaign_batches WHERE client_id=? ORDER BY created_at DESC",
                    (client_id,),
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM campaign_batches ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]

    def list_campaigns(
        self, *, client_id: str | None = None, batch_id: str | None = None, status: str | None = None
    ) -> list[dict[str, Any]]:
        query = "SELECT * FROM campaigns WHERE 1=1"
        params: list[Any] = []
        if client_id:
            query += " AND client_id=?"
            params.append(client_id)
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
