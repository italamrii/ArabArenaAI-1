"""Project attachment validation, storage, and text extraction for chat uploads."""

from __future__ import annotations

import csv
import io
import json
import os
import uuid
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.orm import Session

from workspace.db.models import ProjectFile
from workspace.services.authz import get_project_for_owner

ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".txt", ".md", ".csv", ".json"}
ALLOWED_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_DOCUMENT_EXTENSIONS

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_TEXT_SNIPPET_CHARS = 2000

IMAGE_UNSUPPORTED_MESSAGE = (
    "تم رفع الصورة، لكن النموذج الحالي لا يدعم تحليل الصور بعد."
)
PDF_LIMITED_MESSAGE = "تم رفع الملف، وسيتم دعمه بشكل أوسع لاحقاً."
LOCAL_MODEL_SLOW_HINT = "النموذج المحلي قد يستغرق وقتاً أطول حسب قوة الجهاز."

VISION_CAPABLE_PROVIDERS: set[str] = set()


@dataclass
class AttachmentResult:
    file_id: uuid.UUID
    filename: str
    mime_type: str | None
    kind: str
    size_bytes: int
    storage_key: str
    text_snippet: str | None = None
    user_notice: str | None = None
    supports_vision: bool = False


def _upload_root() -> Path:
    root = Path(os.getenv("WORKSPACE_UPLOAD_DIR", "workspace_uploads"))
    root.mkdir(parents=True, exist_ok=True)
    return root


def _extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def classify_attachment(filename: str) -> str:
    ext = _extension(filename)
    if ext in ALLOWED_IMAGE_EXTENSIONS:
        return "image"
    if ext in ALLOWED_DOCUMENT_EXTENSIONS:
        return "document"
    return "unsupported"


def validate_attachment(filename: str, data: bytes) -> None:
    """Raise ValueError when upload is not allowed."""
    if not filename or not filename.strip():
        raise ValueError("اسم الملف مطلوب")
    ext = _extension(filename)
    if ext not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise ValueError(f"نوع الملف غير مدعوم. الأنواع المسموحة: {allowed}")
    if not data:
        raise ValueError("الملف فارغ")
    if len(data) > MAX_UPLOAD_BYTES:
        raise ValueError("حجم الملف يتجاوز الحد المسموح (10MB)")


def provider_supports_vision(provider: str | None) -> bool:
    if not provider:
        return False
    return provider.strip().lower() in VISION_CAPABLE_PROVIDERS


def _guess_mime(filename: str) -> str | None:
    ext = _extension(filename)
    mapping = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".pdf": "application/pdf",
        ".txt": "text/plain",
        ".md": "text/markdown",
        ".csv": "text/csv",
        ".json": "application/json",
    }
    return mapping.get(ext)


def extract_text_content(data: bytes, filename: str) -> str | None:
    """Extract compact text from supported document types."""
    ext = _extension(filename)
    if ext in {".txt", ".md"}:
        text = data.decode("utf-8", errors="replace").strip()
        return text[:MAX_TEXT_SNIPPET_CHARS] if text else None
    if ext == ".json":
        try:
            payload = json.loads(data.decode("utf-8", errors="replace"))
            serialized = json.dumps(payload, ensure_ascii=False, indent=2)
            return serialized[:MAX_TEXT_SNIPPET_CHARS]
        except json.JSONDecodeError:
            return data.decode("utf-8", errors="replace")[:MAX_TEXT_SNIPPET_CHARS]
    if ext == ".csv":
        reader = csv.reader(io.StringIO(data.decode("utf-8", errors="replace")))
        rows = [" | ".join(row) for row in reader]
        joined = "\n".join(rows).strip()
        return joined[:MAX_TEXT_SNIPPET_CHARS] if joined else None
    if ext == ".pdf":
        return extract_pdf_text(data)
    return None


def extract_pdf_text(data: bytes) -> str | None:
    """Best-effort PDF text extraction when pypdf is available."""
    try:
        from pypdf import PdfReader
    except ImportError:
        return None
    try:
        reader = PdfReader(io.BytesIO(data))
        chunks: list[str] = []
        for page in reader.pages[:5]:
            text = page.extract_text() or ""
            if text.strip():
                chunks.append(text.strip())
        combined = "\n".join(chunks).strip()
        return combined[:MAX_TEXT_SNIPPET_CHARS] if combined else None
    except Exception:
        return None


def build_attachment_prompt_context(result: AttachmentResult) -> str:
    """Build compact attachment context to prepend to chat prompt."""
    lines = [f"[مرفق: {result.filename}]"]
    if result.text_snippet:
        lines.append(result.text_snippet)
    return "\n".join(lines)


def save_project_attachment(
    session: Session,
    owner_id: uuid.UUID,
    project_id: uuid.UUID,
    *,
    filename: str,
    data: bytes,
    provider: str | None = None,
) -> AttachmentResult:
    """Validate, store, and register an uploaded attachment for a project."""
    validate_attachment(filename, data)
    get_project_for_owner(session, project_id, owner_id)

    kind = classify_attachment(filename)
    file_id = uuid.uuid4()
    safe_name = Path(filename).name
    storage_dir = _upload_root() / str(project_id)
    storage_dir.mkdir(parents=True, exist_ok=True)
    storage_path = storage_dir / f"{file_id}_{safe_name}"
    storage_path.write_bytes(data)
    storage_key = str(storage_path)

    text_snippet: str | None = None
    user_notice: str | None = None
    supports_vision = provider_supports_vision(provider)

    if kind == "image":
        if not supports_vision:
            user_notice = IMAGE_UNSUPPORTED_MESSAGE
    elif kind == "document":
        if _extension(filename) == ".pdf":
            text_snippet = extract_pdf_text(data)
            if not text_snippet:
                user_notice = PDF_LIMITED_MESSAGE
        else:
            text_snippet = extract_text_content(data, filename)

    summary = text_snippet or user_notice
    record = ProjectFile(
        id=file_id,
        project_id=project_id,
        owner_id=owner_id,
        filename=safe_name,
        mime_type=_guess_mime(safe_name),
        storage_key=storage_key,
        size_bytes=len(data),
        summary=summary,
    )
    session.add(record)
    session.flush()

    return AttachmentResult(
        file_id=file_id,
        filename=safe_name,
        mime_type=record.mime_type,
        kind=kind,
        size_bytes=len(data),
        storage_key=storage_key,
        text_snippet=text_snippet,
        user_notice=user_notice,
        supports_vision=supports_vision,
    )


def list_project_attachments(
    session: Session,
    owner_id: uuid.UUID,
    project_id: uuid.UUID,
) -> list[ProjectFile]:
    """List stored attachments for an owned project."""
    get_project_for_owner(session, project_id, owner_id)
    from sqlalchemy import select

    stmt = (
        select(ProjectFile)
        .where(ProjectFile.project_id == project_id, ProjectFile.owner_id == owner_id)
        .order_by(ProjectFile.created_at.desc())
    )
    return list(session.scalars(stmt).all())
