"""In-memory knowledge index for local RAG prototype."""

from __future__ import annotations

from pydantic import BaseModel, Field

from knowledge.pack_loader import load_manifest
from rag.chunker import KnowledgeChunk, chunk_documents_from_manifest
from rag.config import KNOWLEDGE_ROOT
from rag.eligibility import is_rag_eligible


class KnowledgeIndex(BaseModel):
    pack_id: str
    chunks: list[KnowledgeChunk] = Field(default_factory=list)
    domains: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)

    @property
    def chunk_count(self) -> int:
        return len(self.chunks)


def build_knowledge_index(*, knowledge_root=None) -> KnowledgeIndex:
    """Build a local in-memory index from eligible seed documents."""
    root = knowledge_root or KNOWLEDGE_ROOT
    manifest = load_manifest(root / "manifests" / "saudi_knowledge_pack_v1.json")
    chunks = chunk_documents_from_manifest(knowledge_root=root)
    if not chunks:
        raise ValueError("No RAG-eligible chunks indexed. Check manifest allowed_use and documents.")

    return KnowledgeIndex(
        pack_id=manifest.pack_id,
        chunks=chunks,
        domains=sorted({chunk.domain for chunk in chunks}),
        source_ids=sorted({chunk.source_id for chunk in chunks}),
    )


def summarize_index(index: KnowledgeIndex) -> dict[str, int | list[str]]:
    return {
        "pack_id": index.pack_id,
        "chunk_count": index.chunk_count,
        "domains": index.domains,
        "source_count": len(index.source_ids),
    }
