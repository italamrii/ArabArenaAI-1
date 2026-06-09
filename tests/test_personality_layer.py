"""Tests for ArabArena AI beta personality layer."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from workspace.personality import (
    InteractionMode,
    apply_response_formatting,
    build_system_prompt,
    detect_interaction_mode,
    get_response_section_headers,
    has_expected_sections,
    sanitize_robotic_language,
)
from workspace.ui.simple_chat_helpers import generate_chat_response


def test_detect_founder_mode_for_business_prompt() -> None:
    assert detect_interaction_mode("اقترح نموذجاً ربحياً لمشروع SaaS") == InteractionMode.FOUNDER
    assert detect_interaction_mode("How should I price my startup product?") == InteractionMode.FOUNDER


def test_detect_engineering_mode_for_technical_prompt() -> None:
    assert detect_interaction_mode("SQLite database is locked when inserting") == InteractionMode.ENGINEERING
    assert detect_interaction_mode("كيف أصلح خطأ في كود Python؟") == InteractionMode.ENGINEERING


def test_detect_general_mode_for_neutral_prompt() -> None:
    assert detect_interaction_mode("مرحباً، كيف حالك؟") == InteractionMode.GENERAL
    assert detect_interaction_mode("") == InteractionMode.GENERAL


def test_engineering_wins_when_technical_signals_dominate() -> None:
    prompt = "عندي bug في API والـ database locked"
    assert detect_interaction_mode(prompt) == InteractionMode.ENGINEERING


def test_build_system_prompt_includes_mode_structure() -> None:
    founder = build_system_prompt(InteractionMode.FOUNDER)
    engineering = build_system_prompt(InteractionMode.ENGINEERING)
    general = build_system_prompt(InteractionMode.GENERAL)

    assert "🚀 Recommendation" in founder
    assert "📌 Why" in founder
    assert "⚠️ Risks" in founder

    assert "🔍 Root Cause" in engineering
    assert "⚙️ Solution" in engineering
    assert "✅ Validation" in engineering

    assert "💡 Answer" in general
    assert "📌 Key Point" in general

    for prompt in (founder, engineering, general):
        assert "ArabArena AI" in prompt
        assert "As an AI model" in prompt  # listed as banned behavior
        assert "Arabic" not in prompt or "بالعربية" in prompt


def test_get_response_section_headers_per_mode() -> None:
    assert get_response_section_headers(InteractionMode.FOUNDER)[0] == "🚀 Recommendation"
    assert get_response_section_headers(InteractionMode.ENGINEERING)[0] == "🔍 Root Cause"
    assert get_response_section_headers(InteractionMode.GENERAL)[0] == "💡 Answer"


def test_sanitize_robotic_language() -> None:
    raw = "As an AI model, I think you should start small."
    cleaned = sanitize_robotic_language(raw)
    assert "As an AI model" not in cleaned
    assert "start small" in cleaned


def test_apply_response_formatting_trims_and_sanitizes() -> None:
    raw = "As a language model,\n\n\nبصفتي نموذجاً لغوياً هذا مفيد."
    cleaned = apply_response_formatting(raw, InteractionMode.GENERAL)
    assert "language model" not in cleaned.lower()
    assert "نموذج" not in cleaned or "بصفتي" not in cleaned


def test_has_expected_sections() -> None:
    text = "🚀 Recommendation\n...\n📌 Why\n...\n⚠️ Risks\n..."
    assert has_expected_sections(text, InteractionMode.FOUNDER) is True
    assert has_expected_sections("short answer", InteractionMode.FOUNDER) is False


def test_generate_chat_response_uses_mode_specific_system_prompt() -> None:
    captured: dict[str, str] = {}

    class _Runner:
        model_name = "mock"
        provider = "mock"

        def generate(self, prompt: str, *, system_prompt: str | None = None) -> str:
            captured["system_prompt"] = system_prompt or ""
            captured["prompt"] = prompt
            return "🚀 Recommendation\n...\n📌 Why\n...\n⚠️ Risks\n..."

    with patch(
        "workspace.ui.simple_chat_helpers.resolve_runner_with_fallback",
        return_value=(_Runner(), None),
    ):
        text, warning = generate_chat_response("اقترح خطة تسويق لمشروع جديد")

    assert warning is None
    assert "🚀 Recommendation" in text
    assert "🚀 Recommendation" in captured["system_prompt"]
    assert "وضع المؤسس" in captured["system_prompt"]


def test_generate_chat_response_applies_formatting_hook() -> None:
    runner = MagicMock()
    runner.generate.return_value = "As an AI model, here is the answer."

    with patch(
        "workspace.ui.simple_chat_helpers.resolve_runner_with_fallback",
        return_value=(runner, None),
    ):
        text, _ = generate_chat_response("hello")

    assert "As an AI model" not in text
