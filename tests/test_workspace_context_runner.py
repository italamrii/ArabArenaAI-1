"""Tests for workspace context-aware runner wrapper."""

from __future__ import annotations

from evaluation.runners.mock_runner import MockRunner
from workspace.context.context_aware_runner import ContextAwareRunner


def test_prepends_context_to_system_prompt() -> None:
    runner = MockRunner("mock")
    captured: dict[str, str | None] = {}

    def _generate(prompt: str, *, system_prompt: str | None = None) -> str:
        captured["system"] = system_prompt
        return "ok"

    runner.generate = _generate  # type: ignore[method-assign]
    wrapped = ContextAwareRunner(runner, "سياق المشروع: اختبار")
    response = wrapped.generate("مرحبا", system_prompt="Base prompt")

    assert response == "ok"
    assert captured["system"] is not None
    assert "سياق المشروع: اختبار" in captured["system"]
    assert "Base prompt" in captured["system"]
