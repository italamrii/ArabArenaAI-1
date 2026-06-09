"""Query routing for precision-controlled RAG retrieval."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from evaluation.scorers.text_utils import normalize_text
from rag.config import (
    RAG_BLOCKED_CATEGORIES,
    RAG_NEVER_OVERRIDE_CATEGORIES,
    RAG_OPTIONAL_CATEGORIES,
    RAG_REQUIRED_CATEGORIES,
)

# Strict entity aliases — avoid generic tokens like "2030", "رؤية", "منشآt", "ضريبة".
DOMAIN_ALIASES: dict[str, list[str]] = {
    "qiwa": ["qiwa", "قوى", "منصة قوى", "platform qiwa"],
    "nitaqat": ["nitaqat", "نطاقات", "saudization program", "برنامج نطاقات"],
    "monshaat": ["monshaat", "monsha'at", "authority of smes"],
    "zatca": [
        "zatca",
        "هيئة الزكاة",
        "zakat and tax",
        "e-invoicing",
        "الفوترة الإلكترونية",
        "ضريبة القيمة المضافة",
        "value added tax",
    ],
    "misa": ["misa", "وزارة الاستثمار", "ministry of investment"],
    "etimad": ["etimad", "منصة اعتماد", "اعتماد", "government procurement platform"],
    "vision2030": [
        "vision 2030",
        "رؤية 2030",
        "vision2030",
        "رؤية المملكة 2030",
        "رؤية المملكة",
        "saudi vision 2030",
    ],
}

ENTITY_DISPLAY_NAMES: dict[str, str] = {
    "qiwa": "Qiwa",
    "nitaqat": "Nitaqat",
    "monshaat": "Monsha'at",
    "zatca": "ZATCA",
    "misa": "MISA",
    "etimad": "Etimad",
    "vision2030": "Vision 2030",
}

# Programming may only use RAG when the question explicitly references documentation.
PROGRAMMING_DOC_MARKERS = (
    "documentation",
    "official manual",
    "api reference",
    "official docs",
    "الوثائق الرسمية",
    "الدليل الرسمي",
    "مرجع api",
)


class RouteType(str, Enum):
    RAG_REQUIRED = "rag_required"
    RAG_OPTIONAL = "rag_optional"
    RAG_BLOCKED = "rag_blocked"


class RouteDecision(BaseModel):
    route: RouteType
    routing_reason: str
    category: str = ""
    detected_entities: list[str] = Field(default_factory=list)
    target_domains: list[str] = Field(default_factory=list)
    entity_override: bool = False


def detect_target_domains(question: str) -> tuple[list[str], list[str]]:
    """Return (display entity names, target domain keys) detected in the question."""
    normalized = normalize_text(question)
    domains: list[str] = []
    entities: list[str] = []
    # Match longer aliases first to reduce partial false positives.
    alias_pairs: list[tuple[str, str]] = []
    for domain, aliases in DOMAIN_ALIASES.items():
        for alias in aliases:
            alias_pairs.append((domain, alias.lower()))
    alias_pairs.sort(key=lambda pair: len(pair[1]), reverse=True)

    matched_domains: set[str] = set()
    for domain, alias in alias_pairs:
        if domain in matched_domains:
            continue
        if alias in normalized:
            matched_domains.add(domain)
            domains.append(domain)
            entities.append(ENTITY_DISPLAY_NAMES.get(domain, domain))
    return entities, domains


def _programming_requests_documentation(question: str) -> bool:
    normalized = normalize_text(question)
    return any(marker in normalized for marker in PROGRAMMING_DOC_MARKERS)


def route_query(question: str, *, category: str | None = None) -> RouteDecision:
    """
    Classify a benchmark question for RAG retrieval behavior.

    Blocked categories (programming, translation, summarization, arabic_reasoning)
    never receive entity overrides. Optional categories require a named official
    entity — generic Saudi keywords alone are insufficient.
    """
    cat = (category or "").strip().lower()
    entities, target_domains = detect_target_domains(question)

    if cat in RAG_NEVER_OVERRIDE_CATEGORIES:
        if cat == "programming" and target_domains and _programming_requests_documentation(question):
            return RouteDecision(
                route=RouteType.RAG_OPTIONAL,
                routing_reason="Programming with explicit documentation reference and entity",
                category=cat,
                detected_entities=entities,
                target_domains=target_domains,
            )
        return RouteDecision(
            route=RouteType.RAG_BLOCKED,
            routing_reason=f"Category '{cat}' blocks RAG — no entity override",
            category=cat,
            detected_entities=entities,
            target_domains=[],
        )

    if cat in RAG_REQUIRED_CATEGORIES:
        reason = "Government category requires RAG when retrieval confidence passes"
        if target_domains:
            reason = f"Government category with entities: {', '.join(entities)}"
        return RouteDecision(
            route=RouteType.RAG_REQUIRED,
            routing_reason=reason,
            category=cat,
            detected_entities=entities,
            target_domains=target_domains,
        )

    if cat in RAG_OPTIONAL_CATEGORIES:
        if target_domains:
            return RouteDecision(
                route=RouteType.RAG_OPTIONAL,
                routing_reason=f"Optional RAG — official entity: {', '.join(entities)}",
                category=cat,
                detected_entities=entities,
                target_domains=target_domains,
            )
        return RouteDecision(
            route=RouteType.RAG_BLOCKED,
            routing_reason="Optional category — no named official entity detected",
            category=cat,
            detected_entities=entities,
            target_domains=[],
        )

    if target_domains:
        return RouteDecision(
            route=RouteType.RAG_OPTIONAL,
            routing_reason="Uncategorized question with official entity match",
            category=cat,
            detected_entities=entities,
            target_domains=target_domains,
        )

    return RouteDecision(
        route=RouteType.RAG_BLOCKED,
        routing_reason="No routing signal — RAG blocked by default",
        category=cat,
        detected_entities=entities,
        target_domains=[],
    )
