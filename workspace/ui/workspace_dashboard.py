"""ArabArena AI chat workspace — beta-stable chat shell, UI only."""

from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path
from typing import Any

import streamlit as st
from sqlalchemy import desc, select

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from workspace.config import is_workspace_enabled
from workspace.db.models import ConversationMessage
from workspace.db.session import create_engine_from_config, get_session_factory, init_db
from workspace.schemas.conversation import ConversationCreate
from workspace.schemas.memory import MemoryCreate
from workspace.schemas.project import ProjectCreate
from workspace.services import (
    attachment_service,
    conversation_service,
    memory_search_service,
    memory_service,
    project_service,
)
from workspace.ui.components import (
    chunk_text_for_stream,
    render_chat_bubble,
    render_composer,
    render_quick_chips,
    render_thinking,
)
from workspace.ui.helpers import (
    DEFAULT_VIEW,
    LOCAL_MODEL_SLOW_HINT,
    MEMORY_TYPE_OPTIONS,
    PROVIDER_OPTIONS,
    check_ollama_status,
    conversation_display_title,
    disclaimer_footer_html,
    format_model_display,
    format_relative_time_ar,
    is_duplicate_send,
    is_local_provider,
    make_send_fingerprint,
    onboarding_html,
    resolve_user_id,
    sidebar_brand_html,
    sidebar_footer_html,
    sidebar_section_html,
    welcome_greeting,
    welcome_html,
)
from workspace.ui.theme import dashboard_css

st.set_page_config(
    page_title="ArabArena AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def _session_factory():
    engine = create_engine_from_config()
    init_db(engine)
    return get_session_factory(engine)


def _with_session(fn):
    factory = _session_factory()
    session = factory()
    try:
        result = fn(session)
        session.commit()
        return result
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _as_uuid(value: str | uuid.UUID) -> uuid.UUID:
    return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))


@st.cache_data(show_spinner=False)
def _cached_css() -> str:
    return dashboard_css()


def _init_session_state() -> None:
    defaults: dict[str, Any] = {
        "user_id": resolve_user_id(),
        "selected_project_id": None,
        "selected_conversation_id": None,
        "chat_messages": [],
        "view": DEFAULT_VIEW,
        "provider": os.getenv("WORKSPACE_DEFAULT_PROVIDER", "qwen"),
        "model_name": os.getenv("QWEN_MODEL", "qwen3:8b"),
        "pending_attachments": [],
        "processed_upload_keys": set(),
        "last_context_used": True,
        "show_context_details": False,
        "is_generating": False,
        "outbound_message": None,
        "last_send_fingerprint": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _list_projects(user_id: uuid.UUID):
    return _with_session(lambda session: project_service.list_projects(session, user_id))


def _list_conversations(user_id: uuid.UUID, project_id: uuid.UUID):
    return _with_session(
        lambda session: conversation_service.list_conversations(session, user_id, project_id)
    )


def _conversation_preview(conversation_id: uuid.UUID) -> str:
    def _load(session):
        stmt = (
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conversation_id)
            .order_by(desc(ConversationMessage.created_at))
            .limit(1)
        )
        row = session.scalars(stmt).first()
        if row is None:
            return ""
        return (row.content or "")[:120]

    return _with_session(_load)


def _load_conversation_messages(conversation_id: uuid.UUID) -> list[dict[str, Any]]:
    def _load(session):
        stmt = (
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conversation_id)
            .order_by(ConversationMessage.created_at.asc())
        )
        rows = list(session.scalars(stmt).all())
        messages: list[dict[str, Any]] = []
        for row in rows:
            entry: dict[str, Any] = {
                "id": str(row.id),
                "role": row.role,
                "content": row.content,
            }
            if row.role == "assistant":
                entry["metadata"] = row.metadata_json or {}
                entry["provider"] = row.provider
                entry["model"] = row.model
            messages.append(entry)
        return messages

    return _with_session(_load)


def _sync_chat_history(conversation_id: uuid.UUID) -> None:
    st.session_state.chat_messages = _load_conversation_messages(conversation_id)


def _ensure_conversation(user_id: uuid.UUID, project_id: uuid.UUID) -> uuid.UUID:
    if st.session_state.selected_conversation_id:
        return _as_uuid(st.session_state.selected_conversation_id)

    def _create(session):
        return conversation_service.create_conversation(
            session,
            user_id,
            project_id,
            ConversationCreate(title="محادثة جديدة"),
        )

    conversation = _with_session(_create)
    st.session_state.selected_conversation_id = str(conversation.id)
    return conversation.id


def _start_new_conversation() -> None:
    st.session_state.selected_conversation_id = None
    st.session_state.chat_messages = []
    st.session_state.pending_attachments = []
    st.session_state.outbound_message = None
    st.session_state.is_generating = False
    st.session_state.view = "chat"


def _ensure_project(user_id: uuid.UUID) -> uuid.UUID | None:
    projects = _list_projects(user_id)
    if not projects:
        return None
    labels = {str(p.id): p.name for p in projects}
    current = st.session_state.selected_project_id or str(projects[0].id)
    if current not in labels:
        current = str(projects[0].id)
        st.session_state.selected_project_id = current
    return _as_uuid(current)


def _project_has_conversations(user_id: uuid.UUID, project_id: uuid.UUID) -> bool:
    return bool(_list_conversations(user_id, project_id))


def _show_compact_welcome(user_id: uuid.UUID, project_id: uuid.UUID) -> bool:
    if _has_messages():
        return False
    if _project_has_conversations(user_id, project_id):
        return False
    return True


def _build_prompt_with_attachments(text: str) -> str:
    parts = [text.strip()]
    for attachment in st.session_state.pending_attachments:
        snippet = attachment.get("text_snippet")
        filename = attachment.get("filename", "file")
        if snippet:
            parts.append(f"[attachment: {filename}]\n{snippet}")
        elif attachment.get("user_notice"):
            parts.append(f"[attachment: {filename}]\n{attachment['user_notice']}")
    return "\n\n".join(part for part in parts if part)


def _has_messages() -> bool:
    return bool(st.session_state.chat_messages)


def _process_upload(user_id: uuid.UUID, project_id: uuid.UUID, uploaded) -> None:
    upload_key = f"{uploaded.name}:{len(uploaded.getvalue())}"
    processed = st.session_state.setdefault("processed_upload_keys", set())
    if upload_key in processed:
        return
    try:
        def _save(session):
            return attachment_service.save_project_attachment(
                session,
                user_id,
                project_id,
                filename=uploaded.name,
                data=uploaded.getvalue(),
                provider=st.session_state.provider,
            )

        result = _with_session(_save)
        st.session_state.pending_attachments.append(
            {
                "file_id": str(result.file_id),
                "filename": result.filename,
                "text_snippet": result.text_snippet,
                "user_notice": result.user_notice,
                "kind": result.kind,
            }
        )
        processed.add(upload_key)
        if result.user_notice:
            st.session_state.last_upload_notice = result.user_notice
        st.toast(f"تم رفع {result.filename}")
    except ValueError as exc:
        st.error(str(exc))


def _save_assistant_memory(user_id: uuid.UUID, project_id: uuid.UUID, content: str) -> None:
    if not content.strip():
        return

    def _save(session):
        return memory_service.create_memory(
            session,
            user_id,
            project_id,
            MemoryCreate(
                memory_type="note",
                title="Saved reply",
                content=content.strip(),
                importance_score=60,
            ),
        )

    _with_session(_save)
    st.toast("تم الحفظ في الذاكرة")


def _queue_outbound_message(prompt: str) -> None:
    if st.session_state.get("is_generating"):
        return
    fingerprint = make_send_fingerprint(prompt, st.session_state.selected_conversation_id)
    if is_duplicate_send(fingerprint, st.session_state.get("last_send_fingerprint")):
        return
    st.session_state.outbound_message = prompt.strip()
    st.session_state.last_send_fingerprint = fingerprint
    st.rerun()


def _process_outbound_message(user_id: uuid.UUID, project_id: uuid.UUID, prompt: str) -> None:
    st.session_state.is_generating = True
    st.session_state.outbound_message = None

    conv_id = _ensure_conversation(user_id, project_id)
    full_prompt = _build_prompt_with_attachments(prompt)
    st.session_state.pending_attachments = []
    st.session_state.pop("last_upload_notice", None)

    st.session_state.chat_messages.append({"role": "user", "content": prompt})

    try:
        with st.chat_message("assistant", avatar="✨"):
            render_thinking()
            if is_local_provider(st.session_state.provider):
                st.caption(LOCAL_MODEL_SLOW_HINT)

            def _send(session):
                return conversation_service.send_message(
                    session,
                    user_id,
                    project_id,
                    conv_id,
                    full_prompt,
                    provider=st.session_state.provider,
                    model_name=st.session_state.model_name or None,
                )

            result = _with_session(_send)
            content = result.assistant_message.content if result.assistant_message else ""
            if content:
                st.write_stream(chunk_text_for_stream(content))
            else:
                st.markdown(content)

        metadata = result.assistant_message.metadata_json if result.assistant_message else {}
        st.session_state.chat_messages.append(
            {
                "id": str(result.assistant_message.id) if result.assistant_message else None,
                "role": "assistant",
                "content": content,
                "metadata": metadata or {},
                "provider": result.assistant_message.provider if result.assistant_message else None,
                "model": result.assistant_message.model if result.assistant_message else None,
            }
        )
        st.session_state.last_context_used = result.context_used
    except Exception as exc:
        st.error(f"تعذّر إرسال الرسالة: {exc}")
        st.session_state.chat_messages.pop()
    finally:
        st.session_state.is_generating = False
        st.rerun()


def _open_conversation(conversation_id: uuid.UUID) -> None:
    st.session_state.selected_conversation_id = str(conversation_id)
    _sync_chat_history(conversation_id)
    st.session_state.view = "chat"
    st.session_state.outbound_message = None
    st.session_state.is_generating = False


def _sidebar_conversations(user_id: uuid.UUID, project_id: uuid.UUID):
    rows = []
    for conv in _list_conversations(user_id, project_id):
        preview = _conversation_preview(conv.id)
        if not preview:
            continue
        rows.append((conv, preview))
        if len(rows) >= 8:
            break
    return rows


def _render_sidebar(user_id: uuid.UUID) -> None:
    st.sidebar.markdown(sidebar_brand_html(), unsafe_allow_html=True)

    project_id = _ensure_project(user_id)

    if st.sidebar.button("محادثة جديدة", use_container_width=True, type="primary"):
        _start_new_conversation()
        st.rerun()

    if project_id:
        st.sidebar.markdown(sidebar_section_html("المحادثات الأخيرة"), unsafe_allow_html=True)
        conversations = _sidebar_conversations(user_id, project_id)
        if not conversations:
            st.sidebar.caption("لا توجد محادثات بعد")
        else:
            st.sidebar.markdown('<div class="aa-sidebar-list">', unsafe_allow_html=True)
            for conv, preview in conversations:
                title = conversation_display_title(conv.title, preview)
                updated = format_relative_time_ar(conv.updated_at)
                label = f"{title} · {updated}"
                if st.sidebar.button(
                    label,
                    key=f"sb_conv_{conv.id}",
                    use_container_width=True,
                    help=preview,
                ):
                    _open_conversation(conv.id)
                    st.rerun()
            st.sidebar.markdown("</div>", unsafe_allow_html=True)

    if st.sidebar.button("الإعدادات", use_container_width=True):
        st.session_state.view = "settings"
        st.rerun()

    model_label = format_model_display(st.session_state.provider, st.session_state.model_name)
    st.sidebar.markdown(sidebar_footer_html(model_label), unsafe_allow_html=True)


def _render_onboarding(user_id: uuid.UUID) -> None:
    st.markdown(
        onboarding_html(
            "أنشئ مشروعك الأول",
            "أضف اسم مشروع ووصفاً مختصراً لبدء المحادثة مع ArabArena AI.",
        ),
        unsafe_allow_html=True,
    )
    with st.form("onboarding_create"):
        name = st.text_input("اسم المشروع")
        description = st.text_area("وصف مختصر")
        if st.form_submit_button("إنشاء وبدء") and name.strip():
            def _create(session):
                return project_service.create_project(
                    session,
                    user_id,
                    ProjectCreate(name=name.strip(), description=description.strip() or None),
                )

            project = _with_session(_create)
            st.session_state.selected_project_id = str(project.id)
            st.rerun()


def _render_chat_canvas(user_id: uuid.UUID, project_id: uuid.UUID) -> None:
    outbound = st.session_state.get("outbound_message")
    if outbound and not st.session_state.get("is_generating"):
        _process_outbound_message(user_id, project_id, outbound)
        return

    conv_id = st.session_state.selected_conversation_id
    if conv_id and not _has_messages():
        _sync_chat_history(_as_uuid(conv_id))

    has_messages = _has_messages()
    generating = st.session_state.get("is_generating", False)

    if _show_compact_welcome(user_id, project_id):
        st.markdown(welcome_html(welcome_greeting()), unsafe_allow_html=True)
        render_quick_chips(_queue_outbound_message, disabled=generating)
    elif not has_messages:
        render_quick_chips(_queue_outbound_message, disabled=generating)

    if has_messages:
        st.markdown('<div class="aa-chat-thread">', unsafe_allow_html=True)
        for message in st.session_state.chat_messages:
            render_chat_bubble(
                message,
                save_fn=lambda content: _save_assistant_memory(user_id, project_id, content),
            )
        st.markdown("</div>", unsafe_allow_html=True)

    render_composer(
        user_id=user_id,
        project_id=project_id,
        docked=has_messages or generating,
        disabled=generating,
        on_upload=_process_upload,
        on_queue=_queue_outbound_message,
    )
    st.markdown(disclaimer_footer_html(), unsafe_allow_html=True)


def _view_history(user_id: uuid.UUID) -> None:
    st.markdown("### المحادثات")
    project_id = _ensure_project(user_id)
    if not project_id:
        st.info("أنشئ مشروعاً أولاً من الإعدادات.")
        return

    conversations = _sidebar_conversations(user_id, project_id)
    if not conversations:
        st.info("لا توجد محادثات بعد.")
        return

    for conv, preview in conversations:
        title = conversation_display_title(conv.title, preview)
        updated = format_relative_time_ar(conv.updated_at)
        st.markdown(f"**{title}** · {updated}")
        st.caption(preview)
        if st.button("فتح", key=f"hist_{conv.id}"):
            _open_conversation(conv.id)
            st.rerun()


def _view_files(user_id: uuid.UUID) -> None:
    st.markdown("### الملفات")
    project_id = _ensure_project(user_id)
    if not project_id:
        return
    files = _with_session(
        lambda session: attachment_service.list_project_attachments(session, user_id, project_id)
    )
    if not files:
        st.info("لم يتم رفع ملفات بعد.")
        return
    for file in files:
        st.markdown(f"**{file.filename}**")
        st.caption(f"{file.mime_type or '—'} · {file.size_bytes or 0} bytes")
        if file.summary:
            st.write(file.summary[:280])


def _view_memories(user_id: uuid.UUID) -> None:
    st.markdown("### الذاكرة")
    project_id = _ensure_project(user_id)
    if not project_id:
        return

    with st.expander("إضافة ذاكرة", expanded=False):
        with st.form("memory_form"):
            title = st.text_input("العنوان")
            content = st.text_area("المحتوى")
            memory_type = st.selectbox("النوع", MEMORY_TYPE_OPTIONS)
            importance = st.slider("الأهمية", 0, 100, 50)
            if st.form_submit_button("حفظ") and content.strip():
                def _create(session):
                    return memory_service.create_memory(
                        session,
                        user_id,
                        project_id,
                        MemoryCreate(
                            memory_type=memory_type,
                            title=title.strip() or None,
                            content=content.strip(),
                            importance_score=importance,
                        ),
                    )

                _with_session(_create)
                st.success("تم الحفظ")
                st.rerun()

    query = st.text_input("بحث في الذاكرة", placeholder="ابحث...")
    if query.strip():
        results = _with_session(
            lambda session: memory_search_service.search_memories(
                session, user_id, project_id, query.strip()
            )
        )
        for hit in results.items:
            st.markdown(f"**{hit.memory.title or hit.memory.memory_type}**")
            st.caption(f"Score: {hit.score:.3f}")
            st.write(hit.snippet or hit.memory.content[:220])

    memories = _with_session(
        lambda session: memory_service.list_memories(session, user_id, project_id)
    )
    for memory in memories:
        pin = "📌 " if memory.is_pinned else ""
        st.markdown(f"**{pin}{memory.title or memory.memory_type}**")
        st.write(memory.content[:420])


def _view_settings(user_id: uuid.UUID) -> None:
    st.markdown("### الإعدادات")

    if is_workspace_enabled():
        st.success("Workspace مفعّل")
    else:
        st.error("Workspace غير مفعّل")

    projects = _list_projects(user_id)
    if projects:
        labels = {str(p.id): p.name for p in projects}
        current = st.session_state.selected_project_id or str(projects[0].id)
        if current not in labels:
            current = str(projects[0].id)
        selected = st.selectbox(
            "المشروع",
            list(labels.keys()),
            index=list(labels.keys()).index(current),
            format_func=lambda pid: labels[pid],
        )
        if selected != st.session_state.selected_project_id:
            st.session_state.selected_project_id = selected
            st.session_state.selected_conversation_id = None
            st.session_state.chat_messages = []
            st.session_state.pending_attachments = []
            st.rerun()
    else:
        with st.form("settings_create_project"):
            name = st.text_input("اسم المشروع")
            description = st.text_area("وصف مختصر")
            if st.form_submit_button("إنشاء مشروع") and name.strip():
                def _create(session):
                    return project_service.create_project(
                        session,
                        user_id,
                        ProjectCreate(name=name.strip(), description=description.strip() or None),
                    )

                project = _with_session(_create)
                st.session_state.selected_project_id = str(project.id)
                st.rerun()

    st.session_state.provider = st.selectbox(
        "المزود",
        PROVIDER_OPTIONS,
        index=PROVIDER_OPTIONS.index(st.session_state.provider)
        if st.session_state.provider in PROVIDER_OPTIONS
        else 0,
    )
    st.session_state.model_name = st.text_input("النموذج", value=st.session_state.model_name or "")
    ok, msg = check_ollama_status()
    st.success(msg) if ok else st.warning(msg)
    st.session_state.show_context_details = st.toggle(
        "عرض تفاصيل السياق",
        value=st.session_state.show_context_details,
    )
    st.text_input("User ID", value=str(user_id), disabled=True)

    tab_files, tab_memory = st.tabs(["الملفات", "الذاكرة"])
    with tab_files:
        _view_files(user_id)
    with tab_memory:
        _view_memories(user_id)

    st.markdown(disclaimer_footer_html(), unsafe_allow_html=True)


def main() -> None:
    if not is_workspace_enabled():
        st.error("WORKSPACE_ENABLED=false")
        st.code("WORKSPACE_ENABLED=true\nWORKSPACE_DATABASE_URL=sqlite:///./workspace_dev.db")
        return

    _init_session_state()
    st.markdown(_cached_css(), unsafe_allow_html=True)

    user_id = st.session_state.user_id
    _render_sidebar(user_id)

    view = st.session_state.view
    if view == "history":
        _view_history(user_id)
        return
    if view == "settings":
        _view_settings(user_id)
        return

    project_id = _ensure_project(user_id)
    if not project_id:
        _render_onboarding(user_id)
        return

    _render_chat_canvas(user_id, project_id)


if __name__ == "__main__":
    main()
