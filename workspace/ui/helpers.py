"""UI helpers, copy, and HTML fragments for ArabArena workspace dashboard."""

from __future__ import annotations

import html
import os
import uuid
from datetime import datetime, timezone

import httpx

DEFAULT_LOCAL_USER_ID = "550e8400-e29b-41d4-a716-446655440000"

AI_DISCLAIMER_TEXT = (
    "قد ينتج عن الذكاء الاصطناعي معلومات غير دقيقة، يرجى التحقق من المعلومات المهمة."
)

CHAT_INPUT_PLACEHOLDER = "اسأل عرب أرينا..."
DEFAULT_VIEW = "chat"

QUICK_ACTION_CHIPS = [
    {"label": "بحث", "prompt": "ساعدني في البحث داخل مشروعي واقترح أهم النقاط."},
    {"label": "استكشف أفكار", "prompt": "اقترح 5 أفكار جديدة قابلة للتنفيذ لمشروعي."},
    {"label": "نموذج ربحي", "prompt": "اقترح نموذجاً ربحياً مناسباً للسوق السعودي والخليج."},
    {"label": "خطة مشروع", "prompt": "أعد خطة مشروع مختصرة لمدة 90 يوماً."},
    {"label": "تحليل منافسين", "prompt": "حلّل المنافسين المحتملين واقترح تمييزاً واضحاً."},
]

PROVIDER_OPTIONS = [
    "qwen",
    "mock",
    "openai",
    "anthropic",
    "google",
    "deepseek",
    "llama",
    "arabarena",
]

MEMORY_TYPE_OPTIONS = [
    "note",
    "goal",
    "decision",
    "milestone",
    "output",
    "file_summary",
]

THINKING_MESSAGE = "جارٍ التفكير..."
LOCAL_MODEL_SLOW_HINT = "النموذج المحلي قد يستغرق وقتاً أطول حسب قوة الجهاز."

_GENERIC_CONVERSATION_TITLES = frozenset(
    {"new conversation", "محادثة جديدة", "new chat", "conversation", "محادثة"}
)


def resolve_user_id(explicit: str | None = None) -> uuid.UUID:
    raw = (explicit or os.getenv("WORKSPACE_DEV_USER_ID") or DEFAULT_LOCAL_USER_ID).strip()
    return uuid.UUID(raw)


def resolve_display_name() -> str | None:
    name = os.getenv("WORKSPACE_USER_NAME", "").strip()
    return name or None


def welcome_greeting() -> str:
    name = resolve_display_name()
    if name:
        return f"مرحباً، {name}"
    return "مرحباً، كيف أقدر أساعدك؟"


def format_model_display(provider: str | None, model_name: str | None) -> str:
    chosen = (provider or os.getenv("WORKSPACE_DEFAULT_PROVIDER", "qwen") or "qwen").strip()
    if model_name and model_name.strip():
        return model_name.strip()
    return chosen


def format_relative_time_ar(dt) -> str:
    if dt is None:
        return "—"
    try:
        now = datetime.now(timezone.utc)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        minutes = int((now - dt).total_seconds() // 60)
        if minutes < 1:
            return "الآن"
        if minutes < 60:
            return f"منذ {minutes} د"
        hours = minutes // 60
        if hours < 24:
            return f"منذ {hours} س"
        return f"منذ {hours // 24} ي"
    except Exception:
        return str(dt)[:16]


def sidebar_brand_html() -> str:
    return '<div class="aa-sidebar-brand">ArabArena AI <span style="color:#C9A227">✨</span></div>'


def sidebar_section_html(title: str) -> str:
    return f'<div class="aa-sidebar-section">{html.escape(title)}</div>'


def sidebar_chat_item_html(title: str, preview: str, updated_label: str | None = None) -> str:
    time_html = (
        f'<div class="aa-sidebar-chat-time">{html.escape(updated_label)}</div>'
        if updated_label
        else ""
    )
    return (
        '<div class="aa-sidebar-chat-item">'
        f'<div class="aa-sidebar-chat-title">{html.escape(title)}</div>'
        f'<div class="aa-sidebar-chat-preview">{html.escape(preview)}</div>'
        f"{time_html}"
        "</div>"
    )


def sidebar_footer_html(model_label: str) -> str:
    return (
        '<div class="aa-sidebar-footer">'
        '<span class="aa-powered-badge">Powered by ArabArena AI</span>'
        f'<div style="margin-top:0.45rem;font-size:0.7rem;">{html.escape(model_label)}</div>'
        "</div>"
    )


def welcome_html(greeting: str) -> str:
    return (
        f'<div class="aa-welcome-compact">{html.escape(greeting)}</div>'
    )


def conversation_display_title(title: str | None, preview: str) -> str:
    cleaned = (title or "").strip()
    if cleaned.lower() in _GENERIC_CONVERSATION_TITLES or not cleaned:
        snippet = preview.strip()
        return snippet[:40] if snippet else "محادثة"
    return cleaned[:48]


def make_send_fingerprint(prompt: str, conversation_id: str | None) -> str:
    return f"{conversation_id or 'new'}::{prompt.strip()}"


def is_duplicate_send(fingerprint: str, last_fingerprint: str | None) -> bool:
    return bool(last_fingerprint) and fingerprint == last_fingerprint


def format_message_metadata(metadata: dict | None) -> str:
    if not metadata:
        return "لا توجد تفاصيل."
    lines = []
    if "provider" in metadata:
        lines.append(f"المزود: {metadata['provider']}")
    if "model" in metadata:
        lines.append(f"النموذج: {metadata['model']}")
    if "context_used" in metadata:
        lines.append(f"استخدام السياق: {'نعم' if metadata['context_used'] else 'لا'}")
    if metadata.get("context_chars") is not None:
        lines.append(f"حجم السياق: {metadata['context_chars']}")
    if metadata.get("memories_used"):
        lines.append(f"ذاكرة مستخدمة: {len(metadata['memories_used'])}")
    if metadata.get("error"):
        lines.append(f"خطأ: {metadata['error']}")
    return "\n".join(lines) if lines else "لا توجد تفاصيل."


def disclaimer_footer_html(text: str | None = None) -> str:
    return f'<div class="aa-disclaimer-footer">{html.escape(text or AI_DISCLAIMER_TEXT)}</div>'


def attachment_chip_html(filename: str, kind: str | None = None) -> str:
    label = html.escape(kind or "file")
    return (
        f'<span class="aa-attachment-chip">'
        f'{html.escape(filename)} <span style="color:#10A37F">({label})</span>'
        "</span>"
    )


def onboarding_html(title: str, subtitle: str) -> str:
    return (
        '<div class="aa-canvas-empty">'
        f'<h1 class="aa-welcome">{html.escape(title)}</h1>'
        f'<p style="color:#9CA3AF;margin-top:0.5rem;">{html.escape(subtitle)}</p>'
        "</div>"
    )


def is_local_provider(provider: str | None) -> bool:
    return (provider or "").strip().lower() in {"qwen", "llama", "mock"}


def check_ollama_status(base_url: str | None = None, *, timeout: float = 2.0) -> tuple[bool, str]:
    url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")
    try:
        response = httpx.get(f"{url}/api/tags", timeout=timeout)
        if response.status_code == 200:
            return True, f"Ollama متصل"
        return False, f"Ollama غير متاح"
    except httpx.HTTPError:
        return False, "Ollama غير متصل"
