"""Load and validate Saudi Knowledge Pack manifests."""

from __future__ import annotations

import json
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field, field_validator, model_validator

KNOWLEDGE_ROOT = Path(__file__).resolve().parent
MANIFESTS_DIR = KNOWLEDGE_ROOT / "manifests"
DOCUMENTS_DIR = KNOWLEDGE_ROOT / "documents"
DEFAULT_MANIFEST = MANIFESTS_DIR / "saudi_knowledge_pack_v1.json"
SCHEMA_PATH = MANIFESTS_DIR / "knowledge_manifest_schema.json"


class CollectionStatus(str, Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    COLLECTED = "collected"
    BLOCKED = "blocked"


class LicenseStatus(str, Enum):
    PROPOSED = "proposed"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    BLOCKED = "blocked"
    UNKNOWN = "unknown"


class KnowledgeSourceEntry(BaseModel):
    source_id: str
    title: str
    organization: str
    url: str
    domain: str
    license_status: LicenseStatus | str
    allowed_use: str
    collection_status: CollectionStatus | str
    collected_at: str | None = None
    notes: str
    document_file: str

    @field_validator("source_id")
    @classmethod
    def validate_source_id(cls, value: str) -> str:
        if not value.startswith("skp-"):
            raise ValueError("source_id must start with 'skp-'")
        return value

    @model_validator(mode="after")
    def validate_collection_state(self) -> KnowledgeSourceEntry:
        if self.collection_status == CollectionStatus.COLLECTED.value:
            if not self.collected_at:
                raise ValueError(f"{self.source_id}: collected_at required when collection_status is collected")
            if self.license_status in {
                LicenseStatus.PROPOSED.value,
                LicenseStatus.UNKNOWN.value,
                "",
            }:
                raise ValueError(
                    f"{self.source_id}: collected sources require explicit approved license_status"
                )
        return self


class KnowledgePackManifest(BaseModel):
    pack_id: str
    pack_version: str
    status: str
    description: str = ""
    sources: list[KnowledgeSourceEntry]

    @model_validator(mode="after")
    def unique_source_ids(self) -> KnowledgePackManifest:
        ids = [source.source_id for source in self.sources]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate source_id values in manifest")
        return self


class ValidationIssue(BaseModel):
    code: str
    message: str
    source_id: str | None = None


class ValidationReport(BaseModel):
    ok: bool
    manifest_path: str
    domains_registered: int
    sources_count: int
    documents_checked: int
    issues: list[ValidationIssue] = Field(default_factory=list)


def load_manifest(path: Path | None = None) -> KnowledgePackManifest:
    manifest_path = path or DEFAULT_MANIFEST
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    return KnowledgePackManifest.model_validate(payload)


def load_schema(path: Path | None = None) -> dict:
    schema_path = path or SCHEMA_PATH
    return json.loads(schema_path.read_text(encoding="utf-8"))


def validate_knowledge_pack(
    *,
    knowledge_root: Path | None = None,
    manifest_path: Path | None = None,
) -> ValidationReport:
    """Validate manifest structure, document coverage, and licensing rules."""
    root = knowledge_root or KNOWLEDGE_ROOT
    manifest_file = manifest_path or (root / "manifests" / "saudi_knowledge_pack_v1.json")
    issues: list[ValidationIssue] = []

    try:
        manifest = load_manifest(manifest_file)
    except (json.JSONDecodeError, ValueError) as exc:
        return ValidationReport(
            ok=False,
            manifest_path=str(manifest_file),
            domains_registered=0,
            sources_count=0,
            documents_checked=0,
            issues=[ValidationIssue(code="manifest_load", message=str(exc))],
        )

    domains = {source.domain for source in manifest.sources}
    documents_dir = root / "documents"

    for source in manifest.sources:
        if source.collection_status == CollectionStatus.COLLECTED.value:
            if not str(source.license_status).strip():
                issues.append(
                    ValidationIssue(
                        code="missing_license_status",
                        message="Collected source must have license_status",
                        source_id=source.source_id,
                    )
                )
            if source.collected_at is None:
                issues.append(
                    ValidationIssue(
                        code="missing_collected_at",
                        message="Collected source must have collected_at timestamp",
                        source_id=source.source_id,
                    )
                )

        doc_path = root / source.document_file
        if not doc_path.exists():
            issues.append(
                ValidationIssue(
                    code="missing_document",
                    message=f"Document not found: {source.document_file}",
                    source_id=source.source_id,
                )
            )

    manifest_docs = {source.document_file for source in manifest.sources}
    if documents_dir.exists():
        for doc_path in sorted(documents_dir.glob("*.md")):
            relative = f"documents/{doc_path.name}"
            if relative not in manifest_docs:
                issues.append(
                    ValidationIssue(
                        code="orphan_document",
                        message=f"Document has no manifest entry: {relative}",
                    )
                )

    return ValidationReport(
        ok=not issues,
        manifest_path=str(manifest_file),
        domains_registered=len(domains),
        sources_count=len(manifest.sources),
        documents_checked=len(manifest.sources),
        issues=issues,
    )
