"""Tests for RAG source eligibility rules."""

from knowledge.pack_loader import KnowledgeSourceEntry, LicenseStatus
from rag.eligibility import is_rag_eligible


def _source(**overrides):
    base = {
        "source_id": "skp-test-001",
        "title": "Test",
        "organization": "Org",
        "url": "https://example.com",
        "domain": "qiwa",
        "license_status": "proposed",
        "allowed_use": "registry_only — pending legal review",
        "collection_status": "proposed",
        "collected_at": None,
        "notes": "test",
        "document_file": "documents/qiwa.md",
    }
    base.update(overrides)
    return KnowledgeSourceEntry(**base)


def test_registry_only_with_collection_blocked_phrase_is_eligible() -> None:
    source = _source(
        allowed_use="registry_only — collection blocked pending docs/legal/licenses/vision2030-license-review.md"
    )
    assert is_rag_eligible(source)


def test_blocked_license_is_not_eligible() -> None:
    source = _source(license_status=LicenseStatus.BLOCKED.value)
    assert not is_rag_eligible(source)


def test_no_rag_marker_is_not_eligible() -> None:
    source = _source(allowed_use="no rag — do not index")
    assert not is_rag_eligible(source)
