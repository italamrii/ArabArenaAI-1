"""Future ArabArena model runner stub."""

from __future__ import annotations

import os

from evaluation.runners.base_runner import BaseRunner, RunnerError


class ArabArenaRunner(BaseRunner):
    """Placeholder for future ArabArenaAI-1 fine-tuned model serving."""

    def __init__(self, model_name: str | None = None) -> None:
        model = model_name or os.getenv("ARABARENA_MODEL", "ArabArenaAI-1")
        super().__init__(model)

    @property
    def provider(self) -> str:
        return "arabarena"

    def generate(self, prompt: str, *, system_prompt: str | None = None) -> str:
        raise RunnerError(
            "ArabArena model runner is not configured yet. "
            "Connect inference endpoint after Phase 5 fine-tuning."
        )
