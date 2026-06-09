"""Tests for workspace attachment service."""

from __future__ import annotations

import json
import uuid

import pytest

pytest.importorskip("sqlalchemy")

from sqlalchemy import create_engine

from workspace.db.session import get_session_factory, init_db
from workspace.schemas.project import ProjectCreate
from workspace.services import attachment_service, project_service
from workspace.services.attachment_service import (
    IMAGE_UNSUPPORTED_MESSAGE,
    PDF_LIMITED_MESSAGE,
    build_attachment_prompt_context,
    classify_attachment,
    extract_text_content,
    provider_supports_vision,
    validate_attachment,
)


@pytest.fixture
def session():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    init_db(engine)
    factory = get_session_factory(engine)
    db = factory()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def owner_project(session):
    owner_id = uuid.uuid4()
    project = project_service.create_project(
        session,
        owner_id,
        ProjectCreate(name="Upload Project"),
    )
    session.commit()
    return owner_id, project


def test_validate_rejects_unsupported_type() -> None:
    with pytest.raises(ValueError, match="غير مدعوم"):
        validate_attachment("virus.exe", b"data")


def test_validate_rejects_empty_file() -> None:
    with pytest.raises(ValueError, match="فارغ"):
        validate_attachment("notes.txt", b"")


def test_validate_accepts_allowed_types() -> None:
    validate_attachment("photo.png", b"\x89PNG")
    validate_attachment("notes.md", b"# hello")


def test_classify_attachment() -> None:
    assert classify_attachment("a.png") == "image"
    assert classify_attachment("b.pdf") == "document"
    assert classify_attachment("c.exe") == "unsupported"


def test_extract_text_md_and_json() -> None:
    assert "hello" in (extract_text_content(b"# Title\nhello", "x.md") or "")
    payload = extract_text_content(json.dumps({"a": 1}).encode(), "x.json")
    assert payload is not None
    assert "a" in payload


def test_extract_text_csv() -> None:
    text = extract_text_content(b"a,b\n1,2", "data.csv")
    assert text is not None
    assert "1" in text


def test_image_unsupported_notice(session, owner_project, tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("WORKSPACE_UPLOAD_DIR", str(tmp_path))
    owner_id, project = owner_project
    result = attachment_service.save_project_attachment(
        session,
        owner_id,
        project.id,
        filename="pic.png",
        data=b"\x89PNG",
        provider="qwen",
    )
    session.commit()
    assert result.user_notice == IMAGE_UNSUPPORTED_MESSAGE
    assert provider_supports_vision("qwen") is False


def test_pdf_limited_notice_without_pypdf(session, owner_project, tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("WORKSPACE_UPLOAD_DIR", str(tmp_path))
    owner_id, project = owner_project
    result = attachment_service.save_project_attachment(
        session,
        owner_id,
        project.id,
        filename="doc.pdf",
        data=b"%PDF-1.4 minimal",
        provider="qwen",
    )
    session.commit()
    assert result.user_notice == PDF_LIMITED_MESSAGE


def test_build_attachment_prompt_context() -> None:
    from workspace.services.attachment_service import AttachmentResult

    result = AttachmentResult(
        file_id=uuid.uuid4(),
        filename="notes.txt",
        mime_type="text/plain",
        kind="document",
        size_bytes=10,
        storage_key="/tmp/x",
        text_snippet="Important note",
    )
    context = build_attachment_prompt_context(result)
    assert "notes.txt" in context
    assert "Important note" in context
