"""Tests for workspace dashboard helpers and theme."""

from __future__ import annotations

import uuid

from workspace.ui.helpers import (
    AI_DISCLAIMER_TEXT,
    CHAT_INPUT_PLACEHOLDER,
    DEFAULT_LOCAL_USER_ID,
    DEFAULT_VIEW,
    QUICK_ACTION_CHIPS,
    THINKING_MESSAGE,
    attachment_chip_html,
    disclaimer_footer_html,
    format_model_display,
    format_relative_time_ar,
    is_local_provider,
    onboarding_html,
    resolve_user_id,
    sidebar_brand_html,
    sidebar_chat_item_html,
    sidebar_footer_html,
    welcome_greeting,
    welcome_html,
    make_send_fingerprint,
    is_duplicate_send,
    conversation_display_title,
)
from workspace.ui.theme import ARABARENA_COLORS, ARABARENA_GRADIENTS, dashboard_css


def test_resolve_user_id_default() -> None:
    assert resolve_user_id() == uuid.UUID(DEFAULT_LOCAL_USER_ID)


def test_default_view() -> None:
    assert DEFAULT_VIEW == "chat"


def test_welcome_greeting() -> None:
    greeting = welcome_greeting()
    assert "مرحباً" in greeting
    html = welcome_html(greeting)
    assert "aa-welcome-compact" in html
    assert greeting in html


def test_send_dedupe_helpers() -> None:
    fp1 = make_send_fingerprint("hello", "abc")
    fp2 = make_send_fingerprint("hello", "abc")
    assert is_duplicate_send(fp2, fp1) is True
    assert is_duplicate_send(make_send_fingerprint("other", "abc"), fp1) is False


def test_conversation_display_title() -> None:
    assert conversation_display_title("New conversation", "First message preview") == "First message preview"
    assert conversation_display_title("My plan", "ignored") == "My plan"


def test_quick_action_chips() -> None:
    assert len(QUICK_ACTION_CHIPS) == 5
    assert QUICK_ACTION_CHIPS[0]["label"] == "بحث"
    assert QUICK_ACTION_CHIPS[0]["prompt"]


def test_sidebar_html() -> None:
    assert "ArabArena AI" in sidebar_brand_html()
    item = sidebar_chat_item_html("عنوان", "معاينة")
    assert "aa-sidebar-chat-item" in item
    assert "عنوان" in item
    footer = sidebar_footer_html("qwen3:8b")
    assert "qwen3:8b" in footer
    assert "Powered by ArabArena AI" in footer


def test_chat_copy() -> None:
    assert "عرب أرينا" in CHAT_INPUT_PLACEHOLDER
    assert "التفكير" in THINKING_MESSAGE


def test_format_model_display() -> None:
    assert format_model_display("qwen", "qwen3:8b") == "qwen3:8b"


def test_disclaimer_footer_html() -> None:
    footer = disclaimer_footer_html()
    assert AI_DISCLAIMER_TEXT.split()[0] in footer
    assert "aa-disclaimer-footer" in footer


def test_attachment_chip_html() -> None:
    assert "file.pdf" in attachment_chip_html("file.pdf", "document")


def test_is_local_provider() -> None:
    assert is_local_provider("qwen") is True
    assert is_local_provider("openai") is False


def test_dashboard_css_brand_tokens() -> None:
    css = dashboard_css()
    assert "direction: rtl" in css
    assert ARABARENA_COLORS["accent"] in css
    assert ARABARENA_GRADIENTS["shell_glow"] in css
    assert "aa-composer-shell" in css
    assert "aa-welcome-compact" in css


def test_onboarding_html() -> None:
    html = onboarding_html("Title", "Sub")
    assert "aa-canvas-empty" in html
    assert "Title" in html


def test_format_relative_time_ar_now() -> None:
    assert format_relative_time_ar(None) == "—"
