"""Keyword and semantic-lite retrieval for local RAG."""

from __future__ import annotations

from pydantic import BaseModel, Field

from evaluation.scorers.semantic import _find_group_hits
from evaluation.scorers.text_utils import normalize_text, overlap_ratio, tokenize
from rag.config import (
    DEFAULT_TOP_K,
    RAG_MAX_CHUNKS,
    RAG_MIN_CHUNK_RELATIVE_GAP,
    RAG_MIN_CONFIDENCE,
    RAG_OPTIONAL_MIN_OVERLAP,
    RAG_REQUIRED_MIN_CONFIDENCE,
)
from rag.index import KnowledgeIndex
from rag.router import DOMAIN_ALIASES, RouteDecision, RouteType, detect_target_domains


class RetrievalHit(BaseModel):
    chunk_id: str
    source_id: str
    domain: str
    document_file: str
    title: str
    section_heading: str
    text: str
    score: float
    overlap_score: float
    domain_boost: float
    entity_boost: float
    matched_terms: list[str] = Field(default_factory=list)
    reason: str = ""


class RetrievalResult(BaseModel):
    query: str
    route: RouteType
    routing_reason: str = ""
    detected_entities: list[str] = Field(default_factory=list)
    target_domains: list[str] = Field(default_factory=list)
    rag_used: bool = False
    retrieval_confidence: float = 0.0
    top_chunk_ids: list[str] = Field(default_factory=list)
    top_chunk_scores: list[float] = Field(default_factory=list)
    blocked_reason: str = ""
    hits: list[RetrievalHit] = Field(default_factory=list)


def _matched_terms(query: str, chunk_text: str) -> list[str]:
    query_tokens = tokenize(query)
    chunk_tokens = tokenize(chunk_text)
    matched = sorted(query_tokens & chunk_tokens, key=len, reverse=True)
    for domain, aliases in DOMAIN_ALIASES.items():
        normalized_chunk = normalize_text(chunk_text)
        for alias in aliases:
            if alias.lower() in normalize_text(query) and alias.lower() in normalized_chunk:
                if alias not in matched:
                    matched.append(alias)
    return matched[:8]


def _query_domain_alias_boost(query: str, domain: str) -> float:
    """Boost when a domain alias explicitly appears in the query text."""
    normalized_q = normalize_text(query)
    for alias in DOMAIN_ALIASES.get(domain, []):
        if alias.lower() in normalized_q:
            return 0.22
    return 0.0


def _score_chunk(
    query: str,
    chunk,
    *,
    query_domains: set[str],
    allow_alias_boost: bool = True,
) -> RetrievalHit:
    overlap_score = overlap_ratio(chunk.text, query)
    query_tokens = tokenize(query)
    chunk_tokens = tokenize(chunk.text)
    token_recall = len(query_tokens & chunk_tokens) / max(len(query_tokens), 1) if query_tokens else 0.0
    domain_boost = 0.25 if chunk.domain in query_domains else 0.0

    query_groups = _find_group_hits(query)
    chunk_groups = _find_group_hits(chunk.text)
    entity_boost = 0.0
    if query_groups:
        entity_boost = len(query_groups & chunk_groups) / max(len(query_groups), 1)

    title_boost = 0.1 if any(token in normalize_text(chunk.title) for token in query_tokens if len(token) >= 4) else 0.0
    alias_boost = (
        _query_domain_alias_boost(query, chunk.domain)
        if allow_alias_boost and chunk.domain in query_domains
        else 0.0
    )
    score = min(
        1.0,
        (0.40 * overlap_score)
        + (0.30 * token_recall)
        + domain_boost
        + (0.15 * entity_boost)
        + title_boost
        + alias_boost,
    )
    matched = _matched_terms(query, chunk.text)
    reason_parts = []
    if domain_boost:
        reason_parts.append(f"domain match ({chunk.domain})")
    if entity_boost:
        reason_parts.append("entity overlap")
    if token_recall:
        reason_parts.append("token overlap")
    if alias_boost:
        reason_parts.append("query-domain alias match")
    if not reason_parts:
        reason_parts.append("low lexical overlap")

    return RetrievalHit(
        chunk_id=chunk.chunk_id,
        source_id=chunk.source_id,
        domain=chunk.domain,
        document_file=chunk.document_file,
        title=chunk.title,
        section_heading=chunk.section_heading,
        text=chunk.text,
        score=round(score, 4),
        overlap_score=round(overlap_score, 4),
        domain_boost=round(domain_boost, 4),
        entity_boost=round(entity_boost, 4),
        matched_terms=matched,
        reason=", ".join(reason_parts),
    )


def _trim_weak_chunks(hits: list[RetrievalHit]) -> list[RetrievalHit]:
    """Keep only high-confidence chunks; drop weak trailing padding."""
    if not hits:
        return []
    top_score = hits[0].score
    kept: list[RetrievalHit] = [hits[0]]
    for hit in hits[1:]:
        if hit.score >= top_score - RAG_MIN_CHUNK_RELATIVE_GAP:
            kept.append(hit)
        else:
            break
    return kept[:RAG_MAX_CHUNKS]


def retrieve(
    query: str,
    index: KnowledgeIndex,
    *,
    route: RouteDecision,
    top_k: int | None = None,
    min_confidence: float = RAG_MIN_CONFIDENCE,
) -> RetrievalResult:
    """Return routed, confidence-filtered chunks for a benchmark question."""
    limit = top_k or RAG_MAX_CHUNKS or DEFAULT_TOP_K
    base_result = RetrievalResult(
        query=query,
        route=route.route,
        routing_reason=route.routing_reason,
        detected_entities=route.detected_entities,
        target_domains=route.target_domains,
        rag_used=False,
    )

    if route.route == RouteType.RAG_BLOCKED:
        base_result.blocked_reason = route.routing_reason
        return base_result

    _, detected_domains = detect_target_domains(query)
    query_domains = set(route.target_domains) | set(detected_domains)

    candidates = index.chunks
    if route.target_domains:
        allowed = set(route.target_domains)
        candidates = [chunk for chunk in candidates if chunk.domain in allowed]

    scored = [
        _score_chunk(
            query,
            chunk,
            query_domains=query_domains,
            allow_alias_boost=route.route == RouteType.RAG_REQUIRED,
        )
        for chunk in candidates
    ]
    scored.sort(key=lambda hit: hit.score, reverse=True)

    top_score = scored[0].score if scored else 0.0
    base_result.retrieval_confidence = round(top_score, 4)
    base_result.top_chunk_ids = [hit.chunk_id for hit in scored[:limit]]
    base_result.top_chunk_scores = [hit.score for hit in scored[:limit]]

    threshold = min_confidence
    if route.route == RouteType.RAG_REQUIRED and route.target_domains:
        threshold = RAG_REQUIRED_MIN_CONFIDENCE

    if top_score < threshold:
        base_result.blocked_reason = (
            f"top retrieval score {top_score:.4f} below threshold {threshold:.2f}"
        )
        return base_result

    filtered = [hit for hit in scored if hit.score >= threshold][:limit]
    filtered = _trim_weak_chunks(filtered)

    if route.route == RouteType.RAG_OPTIONAL:
        if not filtered:
            base_result.blocked_reason = "optional route — no chunk met confidence threshold"
            return base_result
        if filtered[0].overlap_score < RAG_OPTIONAL_MIN_OVERLAP:
            base_result.blocked_reason = (
                f"optional route — overlap {filtered[0].overlap_score:.4f} "
                f"below {RAG_OPTIONAL_MIN_OVERLAP:.2f}"
            )
            return base_result

    if route.route == RouteType.RAG_REQUIRED and not filtered:
        base_result.blocked_reason = "required route — no chunk met confidence threshold"
        return base_result

    base_result.hits = filtered
    base_result.rag_used = bool(filtered)
    base_result.top_chunk_ids = [hit.chunk_id for hit in filtered]
    base_result.top_chunk_scores = [hit.score for hit in filtered]
    return base_result
