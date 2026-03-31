from __future__ import annotations

import json
import time
from urllib import request
from urllib.error import HTTPError, URLError
from typing import Any


class PublisherService:
    def publish(self, channel: str, content: str, cfg: dict[str, Any]) -> dict[str, str]:
        name = channel.lower()
        if name in {"facebook", "instagram"}:
            return self._publish_meta(content, cfg)
        if name == "whatsapp":
            return self._publish_whatsapp(content, cfg)
        if name == "tiktok":
            return {
                "status": "failed",
                "message": "Integrazione TikTok API da configurare (credentials/app setup mancanti).",
            }
        if name == "google_ads":
            return {
                "status": "failed",
                "message": "Integrazione Google Ads API da configurare (developer token/OAuth mancanti).",
            }
        return {"status": "failed", "message": f"Canale non supportato: {channel}"}

    def _retry_post(self, url: str, *, headers: dict[str, str], json_payload: dict[str, Any]) -> tuple[int, str]:
        delays = [1, 2, 4]
        last_err: Exception | None = None
        for delay in delays:
            try:
                req = request.Request(
                    url=url,
                    method="POST",
                    headers={**headers, "Content-Type": "application/json"},
                    data=json.dumps(json_payload).encode("utf-8"),
                )
                with request.urlopen(req, timeout=20) as resp:
                    body = resp.read().decode("utf-8")
                    return resp.status, body
            except HTTPError as exc:
                body = exc.read().decode("utf-8") if exc.fp else str(exc)
                if exc.code < 500:
                    return exc.code, body
                last_err = exc
            except Exception as exc:
                last_err = exc
            time.sleep(delay)
        if last_err:
            raise last_err
        return 599, "Unknown publish error"

    def _publish_meta(self, content: str, cfg: dict[str, Any]) -> dict[str, str]:
        token = cfg.get("meta_access_token", "")
        page_id = cfg.get("meta_page_id", "")
        if not token or not page_id:
            return {"status": "failed", "message": "Meta access token o page id non configurati."}
        url = f"https://graph.facebook.com/v23.0/{page_id}/feed"
        status_code, body = self._retry_post(
            url,
            headers={"Authorization": f"Bearer {token}"},
            json_payload={"message": content},
        )
        if 200 <= status_code < 300:
            return {"status": "published", "message": "Pubblicato via Meta Graph API."}
        return {"status": "failed", "message": f"Meta API error: {body[:200]}"}

    def _publish_whatsapp(self, content: str, cfg: dict[str, Any]) -> dict[str, str]:
        token = cfg.get("whatsapp_token", "")
        phone_id = cfg.get("whatsapp_phone_number_id", "")
        to = cfg.get("whatsapp_to", "")
        if not token or not phone_id or not to:
            return {"status": "failed", "message": "WhatsApp token/phone_number_id/to non configurati."}
        url = f"https://graph.facebook.com/v23.0/{phone_id}/messages"
        status_code, body = self._retry_post(
            url,
            headers={"Authorization": f"Bearer {token}"},
            json_payload={
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {"body": content},
            },
        )
        if 200 <= status_code < 300:
            return {"status": "published", "message": "Messaggio inviato via WhatsApp Business API."}
        return {"status": "failed", "message": f"WhatsApp API error: {body[:200]}"}
