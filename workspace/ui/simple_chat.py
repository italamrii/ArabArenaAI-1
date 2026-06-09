"""ArabArena AI — production-grade minimal chat."""

from __future__ import annotations

import html
import sys
from pathlib import Path
from typing import Any

import streamlit as st

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from workspace.ui.simple_chat_helpers import (
    AI_DISCLAIMER,
    CHAT_PLACEHOLDER,
    FOOTER_BRAND,
    FOOTER_POWERED,
    HERO_TAGLINE,
    QUICK_ACTION_CHIPS,
    SEARCH_PLACEHOLDER,
    SEND_BUTTON_LABEL,
    SHOW_UPLOADS,
    THINKING_LABEL,
    build_prompt_with_attachments,
    chunk_text_for_stream,
    empty_state_greeting,
    generate_chat_response,
    process_upload_bytes,
    search_messages,
)
from workspace.ui.simple_chat_theme import simple_chat_css

st.set_page_config(
    page_title="ArabArena AI",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed",
)


def _init_state() -> None:
    defaults: dict[str, Any] = {
        "simple_messages": [],
        "pending_attachments": [],
        "processed_upload_keys": set(),
        "is_generating": False,
        "outbound_message": None,
        "last_upload_notice": None,
        "last_response_warning": None,
        "search_query": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _handle_upload(uploaded) -> None:
    upload_key = f"{uploaded.name}:{len(uploaded.getvalue())}"
    processed = st.session_state.setdefault("processed_upload_keys", set())
    if upload_key in processed:
        return
    try:
        attachment = process_upload_bytes(uploaded.name, uploaded.getvalue())
        st.session_state.pending_attachments.append(attachment)
        processed.add(upload_key)
        notice = attachment.get("user_notice")
        if notice:
            st.session_state.last_upload_notice = notice
        st.toast(f"تم رفع {attachment['filename']}")
    except ValueError as exc:
        st.error(str(exc))


def _queue_message(prompt: str) -> None:
    if st.session_state.get("is_generating"):
        return
    text = prompt.strip()
    if not text:
        return
    st.session_state.outbound_message = text
    st.rerun()


def _render_thinking() -> None:
    st.markdown(
        '<div class="aa-chat-shell">'
        '<div class="aa-thinking-card">'
        f"{html.escape(THINKING_LABEL)}"
        '<span class="aa-thinking-dot"></span>'
        '<span class="aa-thinking-dot"></span>'
        '<span class="aa-thinking-dot"></span>'
        "</div></div>",
        unsafe_allow_html=True,
    )


def _process_outbound_message(prompt: str) -> None:
    st.session_state.is_generating = True
    st.session_state.outbound_message = None

    attachments = list(st.session_state.pending_attachments)
    full_prompt = build_prompt_with_attachments(prompt, attachments)
    st.session_state.pending_attachments = []
    st.session_state.pop("last_upload_notice", None)

    st.session_state.simple_messages.append({"role": "user", "content": prompt})

    try:
        _render_thinking()
        response, warning = generate_chat_response(full_prompt)
        if warning:
            st.session_state.last_response_warning = warning

        st.markdown('<div class="aa-chat-shell"><div class="aa-msg-assistant-card">', unsafe_allow_html=True)
        st.write_stream(chunk_text_for_stream(response))
        st.markdown("</div></div>", unsafe_allow_html=True)

        st.session_state.simple_messages.append({"role": "assistant", "content": response})
    except Exception as exc:
        st.session_state.last_error = str(exc)
        st.session_state.simple_messages.pop()
    finally:
        st.session_state.is_generating = False
        st.rerun()


def _render_hero(*, compact: bool) -> None:
    compact_class = " aa-hero-compact" if compact else ""
    st.markdown(
        f'<div class="aa-hero{compact_class}">'
        '<div class="aa-hero-glow"></div>'
        '<div class="aa-hero-brand-row">'
        '<div class="aa-brand-avatar" aria-hidden="true">✨</div>'
        '<div class="aa-hero-brand-text">'
        '<h1 class="aa-hero-title">ArabArena AI</h1>'
        f'<p class="aa-hero-tagline">{html.escape(HERO_TAGLINE)}</p>'
        '<span class="aa-hero-badge">Beta</span>'
        "</div></div></div>",
        unsafe_allow_html=True,
    )


def _render_empty_greeting() -> None:
    if st.session_state.simple_messages:
        return
    greeting = empty_state_greeting()
    st.markdown(
        '<div class="aa-empty-state">'
        f'<h2 class="aa-empty-greeting">{html.escape(greeting)}</h2>'
        "</div>",
        unsafe_allow_html=True,
    )


def _render_search() -> None:
    st.markdown('<div class="aa-search-shell">', unsafe_allow_html=True)
    st.markdown('<div class="aa-search-bar">', unsafe_allow_html=True)
    query = st.text_input(
        "search",
        value=st.session_state.get("search_query", ""),
        placeholder=SEARCH_PLACEHOLDER,
        label_visibility="collapsed",
        key="aa_search_input",
    )
    st.session_state.search_query = query
    st.markdown("</div>", unsafe_allow_html=True)

    if query.strip():
        results = search_messages(st.session_state.simple_messages, query)
        st.markdown('<div class="aa-search-results">', unsafe_allow_html=True)
        if not results:
            st.markdown(
                '<div class="aa-search-empty">لا توجد نتائج في هذه المحادثة</div>',
                unsafe_allow_html=True,
            )
        else:
            for hit in results[:8]:
                role_label = "أنت" if hit["role"] == "user" else "ArabArena AI"
                st.markdown(
                    '<div class="aa-search-result-card">'
                    f'<div class="aa-search-result-meta">{html.escape(role_label)}</div>'
                    f'<div class="aa-search-result-snippet">{html.escape(hit["snippet"])}</div>'
                    "</div>",
                    unsafe_allow_html=True,
                )
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def _render_thread() -> None:
    messages = st.session_state.simple_messages
    if not messages:
        return
    st.markdown('<div class="aa-chat-shell"><div class="aa-simple-thread">', unsafe_allow_html=True)
    for message in messages:
        role = message.get("role", "assistant")
        content = message.get("content", "")
        if role == "user":
            st.markdown(
                f'<div class="aa-msg-user">{html.escape(content)}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown('<div class="aa-msg-assistant-card">', unsafe_allow_html=True)
            st.markdown(content)
            st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)


def _render_composer(*, docked: bool) -> None:
    disabled = st.session_state.get("is_generating", False)
    dock_class = " aa-glow-composer-dock" if docked else ""
    form_key = "simple_chat_form"

    st.markdown('<div class="aa-composer-wrap">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="aa-glow-composer{dock_class}"><div class="aa-glow-composer-body">',
        unsafe_allow_html=True,
    )

    if SHOW_UPLOADS:
        attachments = st.session_state.get("pending_attachments", [])
        if attachments:
            chips = " ".join(
                f'<span class="aa-simple-chip">{item["filename"]}</span>' for item in attachments
            )
            st.markdown(chips, unsafe_allow_html=True)
        notice = st.session_state.get("last_upload_notice")
        if notice:
            st.markdown(f'<div class="aa-simple-note">{notice}</div>', unsafe_allow_html=True)

    with st.form(form_key, clear_on_submit=True):
        prompt = st.text_area(
            "message",
            placeholder=CHAT_PLACEHOLDER,
            label_visibility="collapsed",
            height=100,
            disabled=disabled,
        )
        st.markdown('<div class="aa-send-row">', unsafe_allow_html=True)
        send = st.form_submit_button(SEND_BUTTON_LABEL, type="primary", disabled=disabled)
        st.markdown("</div>", unsafe_allow_html=True)

    if SHOW_UPLOADS:
        st.markdown('<div class="aa-simple-upload-overlay aa-upload-hidden">', unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "upload",
            type=["png", "jpg", "jpeg", "webp", "pdf", "txt", "md", "csv", "json"],
            label_visibility="collapsed",
            key="simple_upload",
            disabled=disabled,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        if uploaded is not None:
            _handle_upload(uploaded)

    st.markdown("</div></div></div>", unsafe_allow_html=True)

    if send and prompt and prompt.strip():
        _queue_message(prompt.strip())


def _render_quick_chips() -> None:
    disabled = st.session_state.get("is_generating", False)
    st.markdown('<div class="aa-quick-chips">', unsafe_allow_html=True)
    cols = st.columns(len(QUICK_ACTION_CHIPS))
    for index, chip in enumerate(QUICK_ACTION_CHIPS):
        if cols[index].button(chip["label"], key=f"quick_{index}", disabled=disabled):
            _queue_message(chip["prompt"])
    st.markdown("</div>", unsafe_allow_html=True)


def _render_footer() -> None:
    st.markdown(
        f'<div class="aa-footer">'
        f'<div class="aa-footer-brand">{html.escape(FOOTER_BRAND)}</div>'
        f'<div class="aa-footer-powered">{html.escape(FOOTER_POWERED)}</div>'
        f'<div class="aa-footer-disclaimer">{html.escape(AI_DISCLAIMER)}</div>'
        "</div>",
        unsafe_allow_html=True,
    )


def main() -> None:
    _init_state()
    st.markdown(simple_chat_css(show_uploads=SHOW_UPLOADS), unsafe_allow_html=True)

    outbound = st.session_state.get("outbound_message")
    if outbound and not st.session_state.get("is_generating"):
        _process_outbound_message(outbound)
        return

    has_messages = bool(st.session_state.simple_messages)
    _render_hero(compact=has_messages)
    _render_search()

    warning = st.session_state.pop("last_response_warning", None)
    if warning:
        st.markdown(f'<div class="aa-inline-warning">{html.escape(warning)}</div>', unsafe_allow_html=True)
    error = st.session_state.pop("last_error", None)
    if error:
        st.error(f"تعذّر إرسال الرسالة: {error}")

    _render_empty_greeting()
    _render_thread()
    _render_composer(docked=has_messages)
    _render_quick_chips()
    _render_footer()


if __name__ == "__main__":
    main()
