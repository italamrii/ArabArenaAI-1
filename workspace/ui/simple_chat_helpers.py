"""Pure helpers for the minimal ArabArena simple chat UI."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from evaluation.runners.base_runner import BaseRunner, RunnerError
from evaluation.runners.runner_factory import create_runner
from workspace.personality import (
    InteractionMode,
    apply_response_formatting,
    build_system_prompt,
    detect_interaction_mode,
)
from workspace.services.attachment_service import (
    ALLOWED_EXTENSIONS,
    IMAGE_UNSUPPORTED_MESSAGE,
    PDF_LIMITED_MESSAGE,
    classify_attachment,
    extract_pdf_text,
    extract_text_content,
    validate_attachment,
)

DEFAULT_PROVIDER = os.getenv("WORKSPACE_DEFAULT_PROVIDER", "qwen").strip().lower() or "qwen"
DEFAULT_MODEL = os.getenv("QWEN_MODEL", "qwen3:8b").strip() or "qwen3:8b"
DEFAULT_SYSTEM_PROMPT = build_system_prompt(InteractionMode.GENERAL)
MOCK_FALLBACK_WARNING = (
    "تعذّر الاتصال بالنموذج المطلوب. تم استخدام وضع تجريبي مؤقت."
)
CHAT_PLACEHOLDER = "اكتب رسالتك..."
SEARCH_PLACEHOLDER = "ابحث في المحادثات أو المواضيع..."
SEND_BUTTON_LABEL = "اسأل عرب أرينا"
CHAT_SUBTITLE = "اسأل عرب أرينا — مساعدك الذكي للأعمال والأفكار"
HERO_TAGLINE = CHAT_SUBTITLE
THINKING_LABEL = "✨ أفكر..."
SHOW_UPLOADS = False
FOOTER_BRAND = "ArabArena AI Beta"
FOOTER_POWERED = "Powered by Local AI"
AI_DISCLAIMER = (
    "قد ينتج عن الذكاء الاصطناعي معلومات غير دقيقة، يرجى التحقق من المعلومات المهمة."
)

QUICK_ACTION_CHIPS = [
    {"label": "🚀 فكرة مشروع", "prompt": "اقترح فكرة مشروع مبتكرة مناسبة للسوق الخليجي مع خطوات البداية."},
    {"label": "💰 خطة ربح", "prompt": "اقترح نموذجاً ربحياً واضحاً لمشروع صغير مع مصادر الدخل."},
    {"label": "📊 تحليل منافسين", "prompt": "حلّل المنافسين المحتملين واقترح تمييزاً تنافسياً."},
    {"label": "✉️ رسالة احترافية", "prompt": "اكتب رسالة احترافية بالعربية لعرض خدمة على عميل محتمل."},
    {"label": "📝 كتابة محتوى", "prompt": "اكتب محتوى تسويقياً جذاباً بالعربية لمنصة التواصل."},
]

# Backward-compatible alias for tests referencing SUGGESTION_CHIPS
SUGGESTION_CHIPS = QUICK_ACTION_CHIPS


def empty_state_greeting() -> str:
    name = os.getenv("WORKSPACE_USER_NAME", "").strip()
    if name:
        return f"مرحباً، {name}"
    return "مرحباً، كيف أقدر أساعدك اليوم؟"


def _snippet_around_match(text: str, query: str, *, radius: int = 70) -> str:
    lowered = text.lower()
    index = lowered.find(query.lower())
    if index < 0:
        return text[: radius * 2].strip()
    start = max(0, index - radius)
    end = min(len(text), index + len(query) + radius)
    prefix = "…" if start > 0 else ""
    suffix = "…" if end < len(text) else ""
    return f"{prefix}{text[start:end].strip()}{suffix}"


def search_messages(messages: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
    """Search in-session chat history for a query string."""
    needle = query.strip().lower()
    if not needle:
        return []
    hits: list[dict[str, Any]] = []
    for index, message in enumerate(messages):
        content = message.get("content") or ""
        if needle in content.lower():
            hits.append(
                {
                    "index": index,
                    "role": message.get("role", "assistant"),
                    "snippet": _snippet_around_match(content, needle),
                    "content": content,
                }
            )
    return hits


def chunk_text_for_stream(text: str, *, chunk_size: int = 12):
    """Yield progressive slices for UI streaming simulation."""
    import time

    if not text:
        yield ""
        return
    step = max(4, chunk_size)
    for index in range(step, len(text) + step, step):
        yield text[:index]
        time.sleep(0.012)


def allowed_upload_extensions() -> set[str]:
    return set(ALLOWED_EXTENSIONS)


def is_allowed_upload(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def process_upload_bytes(filename: str, data: bytes) -> dict[str, Any]:
    """Validate and extract in-memory attachment context without persisting to DB."""
    validate_attachment(filename, data)
    kind = classify_attachment(filename)
    ext = Path(filename).suffix.lower()
    text_snippet: str | None = None
    user_notice: str | None = None

    if kind == "image":
        user_notice = IMAGE_UNSUPPORTED_MESSAGE
    elif kind == "document":
        if ext == ".pdf":
            text_snippet = extract_pdf_text(data)
            if not text_snippet:
                user_notice = PDF_LIMITED_MESSAGE
        else:
            text_snippet = extract_text_content(data, filename)

    return {
        "filename": Path(filename).name,
        "kind": kind,
        "text_snippet": text_snippet,
        "user_notice": user_notice,
    }


def build_prompt_with_attachments(text: str, attachments: list[dict[str, Any]]) -> str:
    parts = [text.strip()]
    for attachment in attachments:
        filename = attachment.get("filename", "file")
        snippet = attachment.get("text_snippet")
        notice = attachment.get("user_notice")
        if snippet:
            parts.append(f"[مرفق: {filename}]\n{snippet}")
        elif notice:
            parts.append(f"[مرفق: {filename}]\n{notice}")
    return "\n\n".join(part for part in parts if part)


def resolve_runner(
    provider: str | None = None,
    model_name: str | None = None,
) -> BaseRunner:
    chosen = (provider or DEFAULT_PROVIDER).strip().lower()
    model = (model_name or DEFAULT_MODEL).strip() or DEFAULT_MODEL
    return create_runner(chosen, model_name=model)


def resolve_runner_with_fallback(
    provider: str | None = None,
    model_name: str | None = None,
) -> tuple[BaseRunner, str | None]:
    """Return a runner and optional warning when falling back to mock."""
    chosen = (provider or DEFAULT_PROVIDER).strip().lower()
    model = (model_name or DEFAULT_MODEL).strip() or DEFAULT_MODEL
    try:
        return create_runner(chosen, model_name=model), None
    except RunnerError:
        return create_runner("mock", model_name="mock"), MOCK_FALLBACK_WARNING


def generate_chat_response(
    prompt: str,
    *,
    provider: str | None = None,
    model_name: str | None = None,
    system_prompt: str | None = None,
    mode: InteractionMode | None = None,
) -> tuple[str, str | None]:
    """Generate assistant text with personality layer, provider fallback, and formatting."""
    detected_mode = mode or detect_interaction_mode(prompt)
    active_system_prompt = system_prompt or build_system_prompt(detected_mode)

    runner, warning = resolve_runner_with_fallback(provider, model_name)
    try:
        raw = runner.generate(prompt, system_prompt=active_system_prompt)
        return apply_response_formatting(raw, detected_mode), warning
    except RunnerError:
        mock = create_runner("mock", model_name="mock")
        raw = mock.generate(prompt, system_prompt=active_system_prompt)
        combined_warning = MOCK_FALLBACK_WARNING if not warning else warning
        return apply_response_formatting(raw, detected_mode), combined_warning
