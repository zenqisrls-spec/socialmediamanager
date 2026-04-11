from __future__ import annotations

import json
from typing import Any
from urllib import request

from app.services.campaign_service import CampaignService
from app.services.client_service import ClientService


class AdsSyncService:
    def __init__(self) -> None:
        self.campaign_service = CampaignService()
        self.client_service = ClientService()

    def sync(self, *, client_id: str, campaign_ids: list[str], platform: str, mode: str) -> list[dict[str, Any]]:
        client = self.client_service.get(client_id)
        if not client:
            return [{"campaign_id": "", "platform": platform, "mode": mode, "success": False, "message": "Cliente non trovato"}]
        campaigns = self.campaign_service.list_campaigns(client_id=client_id)
        chosen = [c for c in campaigns if not campaign_ids or c["id"] in campaign_ids]
        if platform == "meta_ads":
            return [self._sync_meta(c, client, mode) for c in chosen]
        if platform == "google_ads":
            return [self._sync_google(c, client, mode) for c in chosen]
        return [{"campaign_id": "", "platform": platform, "mode": mode, "success": False, "message": "Piattaforma non supportata"}]

    def _sync_meta(self, campaign: dict[str, Any], client: dict[str, Any], mode: str) -> dict[str, Any]:
        token = client.get("meta_access_token", "")
        ad_account_id = client.get("meta_ad_account_id", "")
        if not token or not ad_account_id:
            return {
                "campaign_id": campaign["id"],
                "platform": "meta_ads",
                "mode": mode,
                "success": False,
                "message": "Meta token o ad account id mancanti",
            }
        endpoint = f"https://graph.facebook.com/v23.0/act_{ad_account_id}/campaigns"
        status = "PAUSED" if mode == "draft" else "ACTIVE"
        body = {
            "name": campaign["campaign_name"],
            "objective": "OUTCOME_LEADS",
            "status": status,
            "special_ad_categories": "[]",
            "daily_budget": max(100, int(float(campaign.get("daily_budget_eur", 10)) * 100)),
            "access_token": token,
        }
        try:
            req = request.Request(
                endpoint,
                method="POST",
                data=json.dumps(body).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            with request.urlopen(req, timeout=20) as resp:
                payload = json.loads(resp.read().decode("utf-8") or "{}")
            return {
                "campaign_id": campaign["id"],
                "platform": "meta_ads",
                "mode": mode,
                "success": True,
                "external_id": str(payload.get("id", "")),
                "message": "Campagna inviata a Meta Marketing API",
            }
        except Exception as exc:
            return {
                "campaign_id": campaign["id"],
                "platform": "meta_ads",
                "mode": mode,
                "success": False,
                "message": f"Meta API error: {exc}",
            }

    def _sync_google(self, campaign: dict[str, Any], client: dict[str, Any], mode: str) -> dict[str, Any]:
        customer_id = client.get("google_ads_customer_id", "").replace("-", "")
        dev_token = client.get("google_ads_developer_token", "")
        refresh_token = client.get("google_ads_refresh_token", "")
        client_id = client.get("google_ads_client_id", "")
        client_secret = client.get("google_ads_client_secret", "")
        if not all([customer_id, dev_token, refresh_token, client_id, client_secret]):
            return {
                "campaign_id": campaign["id"],
                "platform": "google_ads",
                "mode": mode,
                "success": False,
                "message": "Credenziali Google Ads mancanti",
            }
        # Placeholder real-world flow: OAuth exchange + Google Ads mutate endpoint.
        # Keeping deterministic behavior with explicit status to avoid silent failures.
        return {
            "campaign_id": campaign["id"],
            "platform": "google_ads",
            "mode": mode,
            "success": False,
            "message": "Integrazione Google Ads pronta al mapping credenziali; richiede OAuth access token runtime.",
        }
