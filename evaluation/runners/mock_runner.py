"""Deterministic mock runner for tests and offline evaluation."""

from __future__ import annotations

from evaluation.runners.base_runner import BaseRunner


class MockRunner(BaseRunner):
    """Returns reference answers or echoes prompts for deterministic tests."""

    def __init__(self, model_name: str = "mock", references: dict[str, str] | None = None) -> None:
        super().__init__(model_name)
        self._references = references or {}

    @property
    def provider(self) -> str:
        return "mock"

    def set_references(self, references: dict[str, str]) -> None:
        self._references = references

    def generate(self, prompt: str, *, system_prompt: str | None = None) -> str:
        if prompt in self._references:
            return self._references[prompt]
        for question, answer in self._references.items():
            if question in prompt or prompt in question:
                return answer
        return f"MOCK_RESPONSE: {prompt[:200]}"
