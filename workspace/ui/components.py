"""UI-only components for ArabArena chat shell."""

from __future__ import annotations

import time
from collections.abc import Iterator
from typing import Any, Callable

import streamlit as st

from workspace.ui.helpers import (
    CHAT_INPUT_PLACEHOLDER,
    QUICK_ACTION_CHIPS,
    THINKING_MESSAGE,
    attachment_chip_html,
    format_message_metadata,
    format_model_display,
)


def chunk_text_for_stream(text: str, *, chunk_size: int = 14) -> Iterator[str]:
    if not text:
        yield ""
        return
    step = max(4, chunk_size)
    for index in range(step, len(text) + step, step):
        yield text[:index]
        time.sleep(0.01)


def render_quick_chips(on_select: Callable[[str], None], *, disabled: bool = False) -> None:
    st.markdown('<div class="aa-quick-chips-wrap">', unsafe_allow_html=True)
    cols = st.columns(len(QUICK_ACTION_CHIPS))
    for index, chip in enumerate(QUICK_ACTION_CHIPS):
        if cols[index].button(
            chip["label"],
            key=f"chip_{index}",
            disabled=disabled,
        ):
            on_select(chip["prompt"])
    st.markdown("</div>", unsafe_allow_html=True)


def _pop_attachment(index: int) -> None:
    items = st.session_state.get("pending_attachments", [])
    if 0 <= index < len(items):
        items.pop(index)
        st.session_state.pending_attachments = items


def render_composer(
    *,
    user_id,
    project_id,
    docked: bool,
    disabled: bool,
    on_upload,
    on_queue,
) -> None:
    model_label = format_model_display(st.session_state.provider, st.session_state.model_name)
    shell_class = "aa-composer-shell aa-composer-dock" if docked else "aa-composer-shell"
    outer = st.columns([1, 8, 1])[1] if not docked else st.container()

    with outer:
        st.markdown(f'<div class="{shell_class}"><div class="aa-composer-inner">', unsafe_allow_html=True)

        attachments = st.session_state.get("pending_attachments", [])
        if attachments:
            chips_html = "".join(
                attachment_chip_html(item["filename"], item.get("kind")) for item in attachments
            )
            st.markdown(f'<div class="aa-composer-chips">{chips_html}</div>', unsafe_allow_html=True)
            chip_cols = st.columns(len(attachments))
            for index, item in enumerate(attachments):
                if chip_cols[index].button("×", key=f"rm_{index}", disabled=disabled):
                    _pop_attachment(index)
                    st.rerun()

        notice = st.session_state.get("last_upload_notice")
        if notice:
            st.markdown(f'<div class="aa-inline-note">{notice}</div>', unsafe_allow_html=True)

        with st.form("aa_composer_form", clear_on_submit=True):
            prompt = st.text_area(
                "msg",
                value=st.session_state.pop("composer_prefill", ""),
                placeholder=CHAT_INPUT_PLACEHOLDER,
                label_visibility="collapsed",
                height=56,
                disabled=disabled,
            )
            toolbar = st.columns([1, 1, 5, 1])
            with toolbar[0]:
                st.form_submit_button("🎤", disabled=True, help="قريباً")
            with toolbar[1]:
                st.markdown('<span class="aa-composer-plus">＋</span>', unsafe_allow_html=True)
            with toolbar[2]:
                st.markdown(
                    f'<div class="aa-composer-meta">{model_label}</div>',
                    unsafe_allow_html=True,
                )
            with toolbar[3]:
                send = st.form_submit_button(
                    "↑",
                    type="primary",
                    use_container_width=True,
                    disabled=disabled,
                )

        st.markdown('<div class="aa-upload-overlay">', unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "upload",
            type=["png", "jpg", "jpeg", "webp", "pdf", "txt", "md", "csv", "json"],
            label_visibility="collapsed",
            key="aa_upload",
            disabled=disabled,
        )
        st.markdown("</div></div></div>", unsafe_allow_html=True)

        if uploaded is not None:
            on_upload(user_id, project_id, uploaded)

        pending = st.session_state.pop("pending_send_prompt", None)
        if pending and not disabled:
            on_queue(pending)
        elif send and prompt and prompt.strip() and not disabled:
            on_queue(prompt.strip())
        elif send and not disabled:
            st.warning("اكتب رسالتك أولاً")


def render_thinking() -> None:
    st.markdown(f'<div class="aa-thinking">✨ {THINKING_MESSAGE}</div>', unsafe_allow_html=True)


def render_chat_bubble(message: dict[str, Any], *, save_fn) -> None:
    role = message.get("role", "assistant")
    avatar = "👤" if role == "user" else "✨"
    bubble_class = "aa-msg-user" if role == "user" else "aa-msg-assistant"
    st.markdown(f'<div class="aa-msg-row {bubble_class}">', unsafe_allow_html=True)
    with st.chat_message(role, avatar=avatar):
        st.markdown(message.get("content", ""))
        if role == "assistant":
            metadata = message.get("metadata") or {}
            if metadata:
                with st.expander("عرض التفاصيل"):
                    st.code(format_message_metadata(metadata))
            if message.get("id"):
                if st.button("💾 حفظ في الذاكرة", key=f"save_{message['id']}"):
                    save_fn(message.get("content", ""))
    st.markdown("</div>", unsafe_allow_html=True)
