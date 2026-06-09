"""Google Gemini API runner."""

from __future__ import annotations

import os

from evaluation.logging_config import get_logger
from evaluation.runners.base_runner import BaseRunner, RunnerError
from evaluation.runners.http_utils import post_json, require_env

logger = get_logger("google_runner")


class GoogleRunner(BaseRunner):
    """Google Gemini generateContent adapter."""

    def __init__(self, model_name: str | None = None) -> None:
        model = model_name or os.getenv("GOOGLE_MODEL", "gemini-1.5-flash")
        super().__init__(model)
        self.api_key = require_env("GOOGLE_API_KEY")

    @property
    def provider(self) -> str:
        return "google"

    def generate(self, prompt: str, *, system_prompt: str | None = None) -> str:
        full_prompt = prompt if not system_prompt else f"{system_prompt}\n\n{prompt}"
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model_name}:generateContent?key={self.api_key}"
        )
        payload = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {
                "temperature": float(os.getenv("GOOGLE_TEMPERATURE", "0")),
            },
        }
        headers = {"Content-Type": "application/json"}
        logger.info(
            "Google request",
            extra={"extra_fields": {"model": self.model_name, "prompt_chars": len(full_prompt)}},
        )
        data = post_json(url, payload, headers)
        try:
            return str(data["candidates"][0]["content"]["parts"][0]["text"]).strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise RunnerError(f"Unexpected Google response format: {data}") from exc
