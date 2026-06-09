"""DeepSeek OpenAI-compatible API runner."""

from __future__ import annotations

import os

from evaluation.logging_config import get_logger
from evaluation.runners.base_runner import BaseRunner, RunnerError
from evaluation.runners.http_utils import post_json, require_env

logger = get_logger("deepseek_runner")


class DeepSeekRunner(BaseRunner):
    """DeepSeek chat completions adapter (OpenAI-compatible)."""

    def __init__(self, model_name: str | None = None) -> None:
        model = model_name or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        super().__init__(model)
        self.api_key = require_env("DEEPSEEK_API_KEY")
        self.base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

    @property
    def provider(self) -> str:
        return "deepseek"

    def generate(self, prompt: str, *, system_prompt: str | None = None) -> str:
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": float(os.getenv("DEEPSEEK_TEMPERATURE", "0")),
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        logger.info(
            "DeepSeek request",
            extra={"extra_fields": {"model": self.model_name, "prompt_chars": len(prompt)}},
        )
        data = post_json(f"{self.base_url.rstrip('/')}/chat/completions", payload, headers)
        try:
            return str(data["choices"][0]["message"]["content"]).strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise RunnerError(f"Unexpected DeepSeek response format: {data}") from exc
