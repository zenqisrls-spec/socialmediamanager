from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_CONFIG: dict[str, Any] = {
    "openai_api_key": "",
    "model_name": "gpt-4.1-mini",
    "require_human_approval": True,
    "autopublish_enabled": False,
    "whatsapp_enabled": False,
}


class AppConfigService:
    def __init__(self) -> None:
        self.config_path = Path(__file__).resolve().parents[2] / "data" / "app_config.json"
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> dict[str, Any]:
        if not self.config_path.exists():
            return DEFAULT_CONFIG.copy()
        try:
            data = json.loads(self.config_path.read_text(encoding="utf-8"))
        except Exception:
            return DEFAULT_CONFIG.copy()

        merged = DEFAULT_CONFIG.copy()
        merged.update(data)
        return merged

    def save(self, payload: dict[str, Any]) -> dict[str, Any]:
        merged = DEFAULT_CONFIG.copy()
        merged.update(payload)
        self.config_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
        return merged

