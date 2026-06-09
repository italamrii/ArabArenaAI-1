"""Anthropic Messages API runner."""

from __future__ import annotations

import os

from evaluation.logging_config import get_logger
from evaluation.runners.base_runner import BaseRunner, RunnerError
from evaluation.runners.http_utils import post_json, require_env

logger = get_logger("anthropic_runner")


class AnthropicRunner(BaseRunner):
    """Anthropic Claude adapter."""

    def __init__(self, model_name: str | None = None) -> None:
        model = model_name or os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")
        super().__init__(model)
        self.api_key = require_env("ANTHROPIC_API_KEY")
        self.api_version = os.getenv("ANTHROPIC_VERSION", "2023-06-01")

    @property
    def provider(self) -> str:
        return "anthropic"

    def generate(self, prompt: str, *, system_prompt: str | None = None) -> str:
        payload: dict[str, object] = {
            "model": self.model_name,
            "max_tokens": int(os.getenv("ANTHROPIC_MAX_TOKENS", "1024")),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": float(os.getenv("ANTHROPIC_TEMPERATURE", "0")),
        }
        if system_prompt:
            payload["system"] = system_prompt

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": self.api_version,
            "Content-Type": "application/json",
        }
        logger.info(
            "Anthropic request",
            extra={"extra_fields": {"model": self.model_name, "prompt_chars": len(prompt)}},
        )
        data = post_json("https://api.anthropic.com/v1/messages", payload, headers)
        try:
            parts = data.get("content", [])
            texts = [str(part.get("text", "")) for part in parts if part.get("type") == "text"]
            result = "".join(texts).strip()
            if not result:
                raise RunnerError("Anthropic returned empty text content")
            return result
        except (AttributeError, TypeError) as exc:
            raise RunnerError(f"Unexpected Anthropic response format: {data}") from exc
