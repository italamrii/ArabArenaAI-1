"""Tests for Saudi Knowledge Pack v1."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from knowledge.pack_loader import (
    DEFAULT_MANIFEST,
    KnowledgePackManifest,
    SCHEMA_PATH,
    load_manifest,
    load_schema,
    validate_knowledge_pack,
)

KNOWLEDGE_ROOT = Path(__file__).resolve().parent.parent / "knowledge"
REQUIRED_SOURCE_FIELDS = {
    "source_id",
    "title",
    "organization",
    "url",
    "domain",
    "license_status",
    "allowed_use",
    "collection_status",
    "collected_at",
    "notes",
    "document_file",
}


def test_manifest_json_loads() -> None:
    manifest = load_manifest()
    assert manifest.pack_id == "saudi_knowledge_pack_v1"
    assert len(manifest.sources) == 7


def test_manifest_required_fields() -> None:
    payload = json.loads(DEFAULT_MANIFEST.read_text(encoding="utf-8"))
    for source in payload["sources"]:
        missing = REQUIRED_SOURCE_FIELDS - set(source.keys())
        assert not missing, f"Missing fields on {source.get('source_id')}: {missing}"


def test_schema_json_loads() -> None:
    schema = load_schema()
    assert schema["title"]
    assert "source" in schema["$defs"]


def test_all_documents_have_manifest_entries() -> None:
    report = validate_knowledge_pack(knowledge_root=KNOWLEDGE_ROOT)
    orphan_issues = [issue for issue in report.issues if issue.code == "orphan_document"]
    missing_doc_issues = [issue for issue in report.issues if issue.code == "missing_document"]
    assert not orphan_issues
    assert not missing_doc_issues


def test_pack_validation_passes() -> None:
    report = validate_knowledge_pack(knowledge_root=KNOWLEDGE_ROOT)
    assert report.ok
    assert report.domains_registered == 7
    assert report.sources_count == 7


def test_collected_source_requires_approved_license() -> None:
    bad_payload = {
        "pack_id": "test_pack",
        "pack_version": "1.0.0",
        "status": "proposed",
        "sources": [
            {
                "source_id": "skp-test-001",
                "title": "Test",
                "organization": "Org",
                "url": "https://example.com",
                "domain": "qiwa",
                "license_status": "proposed",
                "allowed_use": "none",
                "collection_status": "collected",
                "collected_at": "2026-01-01T00:00:00+00:00",
                "notes": "invalid collected state",
                "document_file": "documents/qiwa.md",
            }
        ],
    }
    with pytest.raises(ValueError, match="approved license_status"):
        KnowledgePackManifest.model_validate(bad_payload)
