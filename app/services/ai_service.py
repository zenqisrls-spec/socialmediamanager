from __future__ import annotations

import json
import importlib.util
import os
from urllib.parse import quote_plus
from typing import Any

from app.services.app_config_service import AppConfigService


class AIService:
    """Wrapper minimale per usare OpenAI con fallback locale deterministico."""

    def __init__(self) -> None:
        self.config_service = AppConfigService()

    def _resolve_runtime_config(self) -> tuple[str, str]:
        config = self.config_service.load()
        model = os.getenv("MODEL_NAME") or config.get("model_name", "gpt-4.1-mini")
        api_key = os.getenv("OPENAI_API_KEY") or config.get("openai_api_key", "")
        return model, api_key

    @staticmethod
    def _normalize_json_content(content: str) -> str:
        raw = content.strip()
        if raw.startswith("```"):
            lines = raw.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            raw = "\n".join(lines).strip()
        return raw

    @staticmethod
    def _create_client(api_key: str) -> Any:
        from openai import OpenAI

        return OpenAI(api_key=api_key)

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        fallback: dict[str, Any],
        runtime_config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        model, api_key = self._resolve_runtime_config()
        if runtime_config:
            model = runtime_config.get("model_name", model)
            api_key = runtime_config.get("openai_api_key", api_key)
        if not api_key:
            return fallback

        try:
            client = self._create_client(api_key=api_key)
            completion = client.chat.completions.create(
                model=model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
            )
            content = completion.choices[0].message.content
            if not content:
                return fallback
            normalized = self._normalize_json_content(content)
            return json.loads(normalized)
        except Exception:
            return fallback

    def generate_image_url(self, prompt: str, runtime_config: dict[str, Any] | None = None) -> str:
        model, api_key = self._resolve_runtime_config()
        if runtime_config:
            model = runtime_config.get("model_name", model)
            api_key = runtime_config.get("openai_api_key", api_key)
        if api_key:
            try:
                client = self._create_client(api_key=api_key)
                response = client.images.generate(model="gpt-image-1", prompt=prompt, size="1024x1024")
                data = getattr(response, "data", None) or []
                if data and getattr(data[0], "url", None):
                    return str(data[0].url)
            except Exception:
                pass
        return f"https://picsum.photos/seed/{quote_plus(prompt)}/1024/1024"

    def status(self) -> dict[str, bool]:
        _, api_key = self._resolve_runtime_config()
        return {
            "api_key_configured": bool(api_key),
            "openai_package_available": importlib.util.find_spec("openai") is not None,
        }
