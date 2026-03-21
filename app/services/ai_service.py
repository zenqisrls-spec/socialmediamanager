from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()


class AIService:
    """Wrapper minimale per usare OpenAI con fallback locale deterministico."""

    def __init__(self) -> None:
        self.model = os.getenv("MODEL_NAME", "gpt-4.1-mini")
        self.api_key = os.getenv("OPENAI_API_KEY")

    def generate_json(self, system_prompt: str, user_prompt: str, fallback: dict[str, Any]) -> dict[str, Any]:
        if not self.api_key:
            return fallback

        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)
            completion = client.chat.completions.create(
                model=self.model,
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
            return json.loads(content)
        except Exception:
            return fallback
