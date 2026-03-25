from __future__ import annotations

from typing import Any

from app.services.db_service import DBService


DEFAULT_CONFIG: dict[str, Any] = {
    "openai_api_key": "",
    "model_name": "gpt-4.1-mini",
    "require_human_approval": True,
    "autopublish_enabled": False,
    "whatsapp_enabled": False,
    "meta_access_token": "",
    "meta_page_id": "",
    "whatsapp_token": "",
    "whatsapp_phone_number_id": "",
    "whatsapp_to": "",
}


class AppConfigService:
    def __init__(self) -> None:
        self.db = DBService()

    def load(self) -> dict[str, Any]:
        with self.db.connect() as conn:
            row = conn.execute("SELECT * FROM app_config WHERE id=1").fetchone()
            if not row:
                return DEFAULT_CONFIG.copy()
            data = dict(row)
            data["require_human_approval"] = bool(data["require_human_approval"])
            data["autopublish_enabled"] = bool(data["autopublish_enabled"])
            data["whatsapp_enabled"] = bool(data["whatsapp_enabled"])
            return data

    def save(self, payload: dict[str, Any]) -> dict[str, Any]:
        cfg = DEFAULT_CONFIG.copy()
        cfg.update(payload)
        with self.db.connect() as conn:
            conn.execute(
                """
                UPDATE app_config
                SET openai_api_key=?,
                    model_name=?,
                    require_human_approval=?,
                    autopublish_enabled=?,
                    whatsapp_enabled=?,
                    meta_access_token=?,
                    meta_page_id=?,
                    whatsapp_token=?,
                    whatsapp_phone_number_id=?,
                    whatsapp_to=?
                WHERE id=1
                """,
                (
                    cfg["openai_api_key"],
                    cfg["model_name"],
                    int(bool(cfg["require_human_approval"])),
                    int(bool(cfg["autopublish_enabled"])),
                    int(bool(cfg["whatsapp_enabled"])),
                    cfg.get("meta_access_token", ""),
                    cfg.get("meta_page_id", ""),
                    cfg.get("whatsapp_token", ""),
                    cfg.get("whatsapp_phone_number_id", ""),
                    cfg.get("whatsapp_to", ""),
                ),
            )
            conn.commit()
        return self.load()

