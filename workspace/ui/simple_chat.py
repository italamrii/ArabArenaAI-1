"""ArabArena AI — premium chat-only interface."""

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
    CHAT_PLACEHOLDER,
    SHOW_UPLOADS,
    THINKING_LABEL,
    build_prompt_with_attachments,
    chunk_text_for_stream,
    generate_chat_response,
    process_upload_bytes,
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
        st.toast(f"تم رفع {attachment['filename']}")
    except ValueError as exc:
        st.markdown(f'<div class="aa-inline-notice">{html.escape(str(exc))}</div>', unsafe_allow_html=True)


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
        '<div class="aa-chat-shell"><div class="aa-thinking">'
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

        st.markdown('<div class="aa-chat-shell"><div class="aa-msg-assistant">', unsafe_allow_html=True)
        st.write_stream(chunk_text_for_stream(response))
        st.markdown("</div></div>", unsafe_allow_html=True)

        st.session_state.simple_messages.append({"role": "assistant", "content": response})
    except Exception as exc:
        st.session_state.last_error = str(exc)
        st.session_state.simple_messages.pop()
    finally:
        st.session_state.is_generating = False
        st.rerun()


def _render_brand(*, compact: bool) -> None:
    state = "compact" if compact else "hero"
    st.markdown(
        f'<div class="aa-brand aa-brand-{state}">'
        '<span class="aa-brand-mark" aria-hidden="true"></span>'
        '<span class="aa-brand-name">ArabArena AI</span>'
        '<span class="aa-brand-spark">✨</span>'
        "</div>",
        unsafe_allow_html=True,
    )


def _render_thread() -> None:
    messages = st.session_state.simple_messages
    if not messages:
        return

    st.markdown('<div class="aa-chat-shell"><div class="aa-thread">', unsafe_allow_html=True)
    for message in messages:
        role = message.get("role", "assistant")
        content = message.get("content", "")
        if role == "user":
            st.markdown(
                f'<div class="aa-msg-user">{html.escape(content)}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown('<div class="aa-msg-assistant">', unsafe_allow_html=True)
            st.markdown(content)
            st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)


def _render_composer(*, docked: bool, hero: bool) -> None:
    disabled = st.session_state.get("is_generating", False)
    mode_class = " aa-composer-hero" if hero else ""
    dock_class = " aa-composer-dock" if docked else ""

    if hero:
        st.markdown('<div class="aa-composer-spotlight"></div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="aa-composer-stage{mode_class}">'
        f'<div class="aa-composer{dock_class}">'
        f'<div class="aa-composer-inner">',
        unsafe_allow_html=True,
    )

    if SHOW_UPLOADS:
        uploaded = st.file_uploader(
            "upload",
            type=["png", "jpg", "jpeg", "webp", "pdf", "txt", "md", "csv", "json"],
            label_visibility="collapsed",
            key="simple_upload",
            disabled=disabled,
        )
        if uploaded is not None:
            _handle_upload(uploaded)

    with st.form("simple_chat_form", clear_on_submit=True):
        input_col, send_col = st.columns([11, 1], vertical_alignment="bottom")
        with input_col:
            prompt = st.text_area(
                "message",
                placeholder=CHAT_PLACEHOLDER,
                label_visibility="collapsed",
                height=88,
                disabled=disabled,
            )
        with send_col:
            send = st.form_submit_button("↑", type="primary", use_container_width=True, disabled=disabled)

    st.markdown("</div></div></div>", unsafe_allow_html=True)

    if send and prompt and prompt.strip():
        _queue_message(prompt.strip())


def main() -> None:
    _init_state()
    st.markdown(simple_chat_css(show_uploads=SHOW_UPLOADS), unsafe_allow_html=True)

    outbound = st.session_state.get("outbound_message")
    if outbound and not st.session_state.get("is_generating"):
        _process_outbound_message(outbound)
        return

    has_messages = bool(st.session_state.simple_messages)
    hero = not has_messages

    _render_brand(compact=has_messages)

    warning = st.session_state.pop("last_response_warning", None)
    if warning:
        st.markdown(f'<div class="aa-inline-notice">{html.escape(warning)}</div>', unsafe_allow_html=True)
    error = st.session_state.pop("last_error", None)
    if error:
        st.markdown(
            f'<div class="aa-inline-notice">{html.escape(f"تعذّر إرسال الرسالة: {error}")}</div>',
            unsafe_allow_html=True,
        )

    if has_messages:
        _render_thread()

    _render_composer(docked=has_messages, hero=hero)


if __name__ == "__main__":
    main()
