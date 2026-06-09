"""Wrapper that prepends project context to prompts without modifying BaseRunner."""

from __future__ import annotations

from evaluation.runners.base_runner import BaseRunner

CONTEXT_HEADER = (
    "=== سياق المشروع (استخدمه عند الإجابة؛ لا تذكر أنك تلقيت سياقاً إلا إذا طُلب) ==="
)
CONTEXT_FOOTER = "=== نهاية سياق المشروع ==="


class ContextAwareRunner:
    """Delegates to an existing runner while injecting project context safely."""

    def __init__(self, runner: BaseRunner, context_block: str) -> None:
        self._runner = runner
        self._context_block = (context_block or "").strip()

    @property
    def provider(self) -> str:
        return self._runner.provider

    @property
    def model_name(self) -> str:
        return self._runner.model_name

    @property
    def inner_runner(self) -> BaseRunner:
        return self._runner

    def _augment_system_prompt(self, system_prompt: str | None) -> str:
        if not self._context_block:
            return system_prompt or "You are a helpful assistant."
        context_section = f"{CONTEXT_HEADER}\n{self._context_block}\n{CONTEXT_FOOTER}"
        base = (system_prompt or "You are a helpful assistant.").strip()
        return f"{base}\n\n{context_section}"

    def generate(self, prompt: str, *, system_prompt: str | None = None) -> str:
        """Send the prompt to the underlying runner with context prepended."""
        augmented = self._augment_system_prompt(system_prompt)
        return self._runner.generate(prompt, system_prompt=augmented)
