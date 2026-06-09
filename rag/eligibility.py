"""Determine which knowledge-pack sources are eligible for prototype RAG."""

from __future__ import annotations

from knowledge.pack_loader import KnowledgeSourceEntry, LicenseStatus


def is_rag_eligible(source: KnowledgeSourceEntry) -> bool:
    """
    Allow manual seed documents only when license is not blocked/rejected and
    allowed_use explicitly permits registry-only or prototype RAG.
    """
    license_status = str(source.license_status).lower()
    if license_status in {LicenseStatus.BLOCKED.value, "rejected"}:
        return False

    allowed = source.allowed_use.lower()
    if "no rag" in allowed:
        return False
    if allowed.startswith("blocked") or allowed.startswith("rejected"):
        return False

    return "registry_only" in allowed or "prototype" in allowed
