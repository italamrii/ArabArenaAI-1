"""Local inference runners — Ollama (Qwen) and Hugging Face placeholders."""

from __future__ import annotations

import os
from typing import Any

import httpx

from evaluation.logging_config import get_logger
from evaluation.runners.base_runner import BaseRunner, RunnerError

logger = get_logger("ollama_runner")

DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_QWEN_OLLAMA_MODEL = "qwen3:8b"


class OllamaRunner(BaseRunner):
    """
    Ollama local inference via POST /api/generate.

    Configure with environment variables:
    - OLLAMA_BASE_URL (default http://localhost:11434)
    - OLLAMA_MODEL or QWEN_MODEL (default qwen3:8b)
    - OLLAMA_TIMEOUT seconds (default 120)
    - OLLAMA_TEMPERATURE (default 0)
    """

    def __init__(
        self,
        model_name: str | None = None,
        *,
        provider: str = "ollama",
        base_url: str | None = None,
        timeout: float | None = None,
    ) -> None:
        resolved_model = (
            model_name
            or os.getenv("OLLAMA_MODEL")
            or os.getenv("QWEN_MODEL")
            or DEFAULT_QWEN_OLLAMA_MODEL
        )
        super().__init__(resolved_model)
        self._provider = provider
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL") or DEFAULT_OLLAMA_BASE_URL).rstrip(
            "/"
        )
        self.timeout = float(timeout if timeout is not None else os.getenv("OLLAMA_TIMEOUT", "120"))

    @property
    def provider(self) -> str:
        return self._provider

    def generate(self, prompt: str, *, system_prompt: str | None = None) -> str:
        full_prompt = self._build_prompt(prompt, system_prompt)
        payload: dict[str, Any] = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": False,
        }
        temperature = os.getenv("OLLAMA_TEMPERATURE", "0")
        payload["options"] = {"temperature": float(temperature)}

        url = f"{self.base_url}/api/generate"
        logger.info(
            "Ollama generate request",
            extra={
                "extra_fields": {
                    "model": self.model_name,
                    "url": url,
                    "prompt_chars": len(full_prompt),
                    "timeout_s": self.timeout,
                }
            },
        )

        try:
            timeout_cfg = httpx.Timeout(self.timeout, connect=10.0)
            with httpx.Client(timeout=timeout_cfg) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.TimeoutException as exc:
            logger.error(
                "Ollama request timed out",
                extra={"extra_fields": {"model": self.model_name, "timeout_s": self.timeout}},
            )
            raise RunnerError(
                f"Ollama request timed out after {self.timeout}s for model '{self.model_name}'"
            ) from exc
        except httpx.HTTPError as exc:
            logger.error(
                "Ollama HTTP error",
                extra={"extra_fields": {"model": self.model_name, "error": str(exc)}},
            )
            raise RunnerError(f"Ollama HTTP request failed: {exc}") from exc

        text = self._extract_response_text(data)
        if not text:
            raise RunnerError(f"Ollama returned empty response for model '{self.model_name}'")

        logger.info(
            "Ollama generate complete",
            extra={
                "extra_fields": {
                    "model": self.model_name,
                    "response_chars": len(text),
                }
            },
        )
        return text

    @staticmethod
    def _build_prompt(prompt: str, system_prompt: str | None) -> str:
        if system_prompt:
            return f"{system_prompt.strip()}\n\n{prompt.strip()}"
        return prompt.strip()

    @staticmethod
    def _extract_response_text(data: dict[str, Any]) -> str:
        """Parse Ollama /api/generate JSON response."""
        if not isinstance(data, dict):
            return ""
        response = data.get("response")
        if isinstance(response, str) and response.strip():
            return response.strip()
        return ""


class QwenRunner(OllamaRunner):
    """Qwen models served locally via Ollama (e.g. qwen3:8b, qwen3:14b)."""

    def __init__(self, model_name: str | None = None) -> None:
        default = os.getenv("QWEN_MODEL", os.getenv("OLLAMA_MODEL", DEFAULT_QWEN_OLLAMA_MODEL))
        super().__init__(model_name or default, provider="qwen")


class LocalHFRunner(BaseRunner):
    """Placeholder for Hugging Face local inference integration."""

    def __init__(self, provider: str, model_name: str | None = None) -> None:
        default_models = {
            "llama": os.getenv("LLAMA_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct"),
        }
        model = model_name or default_models.get(provider, "unknown")
        super().__init__(model)
        self._provider = provider

    @property
    def provider(self) -> str:
        return self._provider

    def generate(self, prompt: str, *, system_prompt: str | None = None) -> str:
        raise RunnerError(
            f"Local {self._provider} runner is not configured. "
            "Set up inference endpoint or extend LocalHFRunner in a future phase."
        )


class LlamaRunner(LocalHFRunner):
    def __init__(self, model_name: str | None = None) -> None:
        super().__init__("llama", model_name)
