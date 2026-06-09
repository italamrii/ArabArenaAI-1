"""Tests for simple chat helper logic."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from evaluation.runners.base_runner import RunnerError
from evaluation.runners.mock_runner import MockRunner
from workspace.services.attachment_service import IMAGE_UNSUPPORTED_MESSAGE, PDF_LIMITED_MESSAGE
from workspace.ui.simple_chat_helpers import (
    MOCK_FALLBACK_WARNING,
    build_prompt_with_attachments,
    generate_chat_response,
    is_allowed_upload,
    process_upload_bytes,
    resolve_runner_with_fallback,
)


def test_is_allowed_upload() -> None:
    assert is_allowed_upload("notes.txt") is True
    assert is_allowed_upload("photo.png") is True
    assert is_allowed_upload("archive.zip") is False


def test_process_upload_bytes_text_file() -> None:
    result = process_upload_bytes("notes.txt", b"hello world")
    assert result["text_snippet"] == "hello world"
    assert result["user_notice"] is None


def test_process_upload_bytes_image_notice() -> None:
    result = process_upload_bytes("photo.png", b"\x89PNG")
    assert result["user_notice"] == IMAGE_UNSUPPORTED_MESSAGE


def test_process_upload_bytes_rejects_invalid_type() -> None:
    with pytest.raises(ValueError, match="غير مدعوم"):
        process_upload_bytes("bad.exe", b"data")


def test_build_prompt_with_attachments() -> None:
    prompt = build_prompt_with_attachments(
        "ما الملخص؟",
        [
            {"filename": "notes.txt", "text_snippet": "Important line"},
            {"filename": "pic.png", "user_notice": IMAGE_UNSUPPORTED_MESSAGE},
        ],
    )
    assert "ما الملخص؟" in prompt
    assert "[مرفق: notes.txt]" in prompt
    assert "Important line" in prompt
    assert IMAGE_UNSUPPORTED_MESSAGE in prompt


def test_resolve_runner_with_fallback_to_mock_on_provider_error() -> None:
    with patch(
        "workspace.ui.simple_chat_helpers.create_runner",
        side_effect=[RunnerError("fail"), MockRunner("mock")],
    ):
        runner, warning = resolve_runner_with_fallback("qwen", "qwen3:8b")
    assert isinstance(runner, MockRunner)
    assert warning == MOCK_FALLBACK_WARNING


def test_generate_chat_response_falls_back_when_generate_fails() -> None:
    failing = MockRunner("mock")

    def _boom(prompt: str, *, system_prompt: str | None = None) -> str:
        raise RunnerError("offline")

    failing.generate = _boom  # type: ignore[method-assign]
    mock = MockRunner("mock")

    with patch(
        "workspace.ui.simple_chat_helpers.resolve_runner_with_fallback",
        return_value=(failing, None),
    ), patch(
        "workspace.ui.simple_chat_helpers.create_runner",
        return_value=mock,
    ):
        text, warning = generate_chat_response("مرحباً")

    assert text
    assert warning == MOCK_FALLBACK_WARNING


def test_process_upload_bytes_pdf_without_text_uses_notice(monkeypatch) -> None:
    monkeypatch.setattr(
        "workspace.ui.simple_chat_helpers.extract_pdf_text",
        lambda _data: None,
    )
    result = process_upload_bytes("doc.pdf", b"%PDF-1.4")
    assert result["text_snippet"] is None
    assert result["user_notice"] == PDF_LIMITED_MESSAGE


def test_suggestion_chips_count_and_shape() -> None:
    from workspace.ui.simple_chat_helpers import QUICK_ACTION_CHIPS, SUGGESTION_CHIPS

    assert 4 <= len(QUICK_ACTION_CHIPS) <= 6
    assert SUGGESTION_CHIPS is QUICK_ACTION_CHIPS
    assert all("label" in chip and "prompt" in chip for chip in QUICK_ACTION_CHIPS)


def test_search_messages_finds_content() -> None:
    from workspace.ui.simple_chat_helpers import search_messages

    messages = [
        {"role": "user", "content": "أريد خطة تسويق"},
        {"role": "assistant", "content": "إليك خطة تسويق مختصرة"},
    ]
    hits = search_messages(messages, "تسويق")
    assert len(hits) == 2
    assert "تسويق" in hits[0]["snippet"]


def test_search_messages_empty_query() -> None:
    from workspace.ui.simple_chat_helpers import search_messages

    assert search_messages([{"role": "user", "content": "hello"}], "  ") == []


def test_empty_state_greeting() -> None:
    from workspace.ui.simple_chat_helpers import empty_state_greeting

    assert "مرحباً" in empty_state_greeting()


def test_chunk_text_for_stream_progressive() -> None:
    from workspace.ui.simple_chat_helpers import chunk_text_for_stream

    text = "ArabArena AI"
    chunks = list(chunk_text_for_stream(text, chunk_size=4))
    assert chunks[-1] == text
