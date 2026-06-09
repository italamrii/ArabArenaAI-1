"""Local text search helpers for workspace memory ranking (no vector DB)."""

from __future__ import annotations

import re
import unicodedata
from datetime import datetime, timezone

from evaluation.scorers.text_utils import normalize_text, tokenize

# Ranking weights (local only; tuned for Arabic/English keyword overlap).
TOKEN_OVERLAP_WEIGHT = 1.0
EXACT_PHRASE_BOOST = 0.35
TITLE_BOOST = 0.25
PINNED_BOOST = 0.20
IMPORTANCE_WEIGHT = 0.003  # per importance point (0–100)
RECENCY_MAX_BOOST = 0.10
RECENCY_HALF_LIFE_DAYS = 30.0


def normalize_query(text: str) -> str:
    """Normalize a search query for Arabic/English matching."""
    return normalize_text(text)


def token_overlap_score(query: str, document: str) -> float:
    """Return Jaccard-like overlap: |Q ∩ D| / |Q|."""
    query_tokens = tokenize(query)
    doc_tokens = tokenize(document)
    if not query_tokens:
        return 0.0
    if not doc_tokens:
        return 0.0
    intersection = query_tokens & doc_tokens
    return len(intersection) / len(query_tokens)


def exact_phrase_boost(query: str, document: str) -> float:
    """Boost when the full normalized query appears in the document."""
    normalized_query = normalize_query(query)
    normalized_doc = normalize_query(document)
    if not normalized_query or len(normalized_query) < 2:
        return 0.0
    if normalized_query in normalized_doc:
        return EXACT_PHRASE_BOOST
    return 0.0


def title_match_boost(query: str, title: str | None) -> float:
    """Boost when query tokens appear in the memory title."""
    if not title or not title.strip():
        return 0.0
    overlap = token_overlap_score(query, title)
    if overlap <= 0:
        return 0.0
    return TITLE_BOOST * overlap


def pinned_boost(is_pinned: bool) -> float:
    return PINNED_BOOST if is_pinned else 0.0


def importance_boost(importance_score: int) -> float:
    clamped = max(0, min(100, importance_score))
    return clamped * IMPORTANCE_WEIGHT


def recency_boost(updated_at: datetime | None, *, now: datetime | None = None) -> float:
    """Light recency boost; decays over ~30 days."""
    if updated_at is None:
        return 0.0
    reference = now or datetime.now(timezone.utc)
    if updated_at.tzinfo is None:
        updated_at = updated_at.replace(tzinfo=timezone.utc)
    age_days = max(0.0, (reference - updated_at).total_seconds() / 86400.0)
    decay = 0.5 ** (age_days / RECENCY_HALF_LIFE_DAYS)
    return RECENCY_MAX_BOOST * decay


def rank_memory(
    query: str,
    *,
    title: str | None,
    search_text: str,
    is_pinned: bool,
    importance_score: int,
    updated_at: datetime | None,
) -> float:
    """Compute a composite local relevance score for one memory."""
    document = search_text or title or ""
    base = token_overlap_score(query, document) * TOKEN_OVERLAP_WEIGHT
    score = (
        base
        + exact_phrase_boost(query, document)
        + title_match_boost(query, title)
        + pinned_boost(is_pinned)
        + importance_boost(importance_score)
        + recency_boost(updated_at)
    )
    return round(score, 6)


def extract_highlight_snippet(text: str, query: str, *, max_len: int = 160) -> str:
    """Return a short snippet around the first query token match."""
    if not text:
        return ""
    normalized = normalize_text(text)
    tokens = [t for t in tokenize(query) if len(t) > 1]
    if not tokens:
        return text[:max_len].strip()
    for token in tokens:
        match = re.search(re.escape(token), normalized, flags=re.UNICODE)
        if match:
            start = max(0, match.start() - 40)
            end = min(len(text), match.end() + 80)
            snippet = text[start:end].strip()
            if start > 0:
                snippet = "…" + snippet
            if end < len(text):
                snippet = snippet + "…"
            return snippet[:max_len]
    return text[:max_len].strip()
