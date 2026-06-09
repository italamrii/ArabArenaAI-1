"""Markdown chunking for Saudi Knowledge Pack seed documents."""

from __future__ import annotations

import re
from pathlib import Path

from pydantic import BaseModel, Field

from knowledge.pack_loader import KNOWLEDGE_ROOT, KnowledgeSourceEntry, load_manifest
from rag.config import DEFAULT_CHUNK_MAX_CHARS
from rag.eligibility import is_rag_eligible


class KnowledgeChunk(BaseModel):
    chunk_id: str
    text: str
    domain: str
    source_id: str
    document_file: str
    title: str
    section_heading: str = ""


def _split_paragraphs(text: str, max_chars: int) -> list[str]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            chunks.append(current)
        if len(paragraph) <= max_chars:
            current = paragraph
        else:
            sentences = re.split(r"(?<=[.!?؟])\s+", paragraph)
            current = ""
            for sentence in sentences:
                piece = f"{current} {sentence}".strip() if current else sentence
                if len(piece) <= max_chars:
                    current = piece
                else:
                    if current:
                        chunks.append(current)
                    current = sentence
    if current:
        chunks.append(current)
    return chunks


def chunk_markdown_text(
    text: str,
    *,
    source: KnowledgeSourceEntry,
    max_chars: int = DEFAULT_CHUNK_MAX_CHARS,
) -> list[KnowledgeChunk]:
    """Split a markdown document into section-aware chunks with metadata."""
    normalized = text.strip()
    if not normalized:
        return []

    sections = re.split(r"(?=\n## )", normalized)
    chunks: list[KnowledgeChunk] = []
    chunk_index = 0

    for section in sections:
        section = section.strip()
        if not section:
            continue
        heading_match = re.match(r"^##\s+(.+)$", section.splitlines()[0]) if section.startswith("##") else None
        section_heading = heading_match.group(1).strip() if heading_match else "Overview"
        body = section if not heading_match else "\n".join(section.splitlines()[1:]).strip()
        if heading_match and not body:
            body = section_heading
        for piece in _split_paragraphs(body or section, max_chars):
            chunk_index += 1
            chunks.append(
                KnowledgeChunk(
                    chunk_id=f"{source.source_id}-c{chunk_index:03d}",
                    text=piece.strip(),
                    domain=source.domain,
                    source_id=source.source_id,
                    document_file=source.document_file,
                    title=source.title,
                    section_heading=section_heading,
                )
            )
    return chunks


def chunk_documents_from_manifest(
    *,
    knowledge_root: Path | None = None,
    max_chars: int = DEFAULT_CHUNK_MAX_CHARS,
) -> list[KnowledgeChunk]:
    """Chunk all RAG-eligible seed documents listed in the knowledge manifest."""
    root = knowledge_root or KNOWLEDGE_ROOT
    manifest = load_manifest(root / "manifests" / "saudi_knowledge_pack_v1.json")
    all_chunks: list[KnowledgeChunk] = []

    for source in manifest.sources:
        if not is_rag_eligible(source):
            continue
        doc_path = root / source.document_file
        if not doc_path.exists():
            continue
        text = doc_path.read_text(encoding="utf-8")
        all_chunks.extend(chunk_markdown_text(text, source=source, max_chars=max_chars))

    return all_chunks
