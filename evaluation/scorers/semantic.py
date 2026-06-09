"""Semantic similarity scoring for calibrated rubric evaluation."""

from __future__ import annotations

import re
from dataclasses import dataclass

from evaluation.scorers.text_utils import normalize_text, overlap_ratio, tokenize

ARABIC_STOPWORDS = {
    "في",
    "من",
    "على",
    "إلى",
    "عن",
    "ما",
    "هل",
    "هي",
    "هو",
    "ذلك",
    "التي",
    "الذي",
    "هذا",
    "these",
    "the",
    "and",
    "for",
    "with",
    "that",
    "before",
    "after",
}

# Synonym groups: any alias match counts as the same concept.
SYNONYM_GROUPS: list[frozenset[str]] = [
    frozenset({"burn", "rate", "burn rate", "burnrate", "معدل الحرق", "الحرق", "معدل حرق"}),
    frozenset({"cash", "نقد", "النقد", "صرف", "صرف النقد", "spending", "spend", "إنفاق", "الإنفاق النقدي", "انفاق"}),
    frozenset({"monthly", "month", "شهري", "شهرياً", "شهر", "شهريا"}),
    frozenset({"profitability", "profit", "profitable", "ربحية", "الربحية", "ربح"}),
    frozenset({"startup", "startups", "ناشئة", "الناشئة", "شركات ناشئة"}),
    frozenset({"nitaqat", "نطاقات", "نطاق", "saudization", "السعودization", "توطين"}),
    frozenset({"qiwa", "قوى", "منصة قوى"}),
    frozenset({"zatca", "هيئة الزكاة", "الزكاة", "الضريبة", "e-invoicing", "فوترة"}),
    frozenset({"etimad", "اعتماد", "منصة اعتماد"}),
    frozenset({"misa", "وزارة الاستثمار", "investment ministry"}),
    frozenset({"absher", "أبشر", "abshr"}),
    frozenset({"vision", "2030", "رؤية", "رؤية 2030", "vision2030"}),
    frozenset({"neom", "نيوم"}),
    frozenset({"commercial", "register", "سجل", "التجاري", "السجل التجاري"}),
    frozenset({"contract", "عقد", "عقود", "employment", "عمل"}),
    frozenset({"tax", "ضريبة", "ضرائب", "vat", "زكاة"}),
    frozenset({"invoice", "invoicing", "فاتورة", "فواتير", "فوترة"}),
    frozenset({"compliance", "امتثال", "الامتثال", "regulatory", "تنظيمي"}),
    frozenset({"runway", "مدة التشغيل", "تشغيل"}),
]

_ALIAS_TO_GROUP: dict[str, int] = {}
for group_idx, group in enumerate(SYNONYM_GROUPS):
    for alias in group:
        _ALIAS_TO_GROUP[normalize_text(alias)] = group_idx


@dataclass(frozen=True)
class SemanticMatchResult:
    similarity: float
    concept_recall: float
    matched_concepts: list[str]
    missing_concepts: list[str]
    lexical_overlap: float
    length_ratio: float


def _find_group_hits(text: str) -> set[int]:
    normalized = normalize_text(text)
    hits: set[int] = set()
    for alias, group_idx in _ALIAS_TO_GROUP.items():
        if len(alias) >= 3 and alias in normalized:
            hits.add(group_idx)
    return hits


def _important_tokens(text: str) -> set[str]:
    tokens = tokenize(text)
    return {token for token in tokens if len(token) >= 4 and token not in ARABIC_STOPWORDS}


def extract_reference_concepts(reference: str) -> list[str]:
    """Return human-readable concept labels expected from the reference."""
    labels: list[str] = []
    group_hits = _find_group_hits(reference)
    for group_idx in sorted(group_hits):
        canonical = sorted(SYNONYM_GROUPS[group_idx], key=len)[0]
        labels.append(canonical)

    for token in sorted(_important_tokens(reference), key=len, reverse=True):
        if len(labels) >= 8:
            break
        if not any(token in normalize_text(label) for label in labels):
            labels.append(token)
    return labels[:8]


def _concept_matched(reference: str, response: str, concept: str) -> bool:
    response_norm = normalize_text(response)
    concept_norm = normalize_text(concept)

    if concept_norm in response_norm:
        return True

    group_idx = _ALIAS_TO_GROUP.get(concept_norm)
    if group_idx is not None:
        return any(normalize_text(alias) in response_norm for alias in SYNONYM_GROUPS[group_idx])

    for alias, idx in _ALIAS_TO_GROUP.items():
        if alias in concept_norm or concept_norm in alias:
            if any(normalize_text(a) in response_norm for a in SYNONYM_GROUPS[idx]):
                return True
    return False


def analyze_semantic_match(reference: str, response: str) -> SemanticMatchResult:
    """Compute meaning-oriented similarity between reference and model answer."""
    if not reference.strip() or not response.strip():
        return SemanticMatchResult(0.0, 0.0, [], extract_reference_concepts(reference), 0.0, 0.0)

    concepts = extract_reference_concepts(reference)
    matched = [concept for concept in concepts if _concept_matched(reference, response, concept)]
    missing = [concept for concept in concepts if concept not in matched]

    ref_groups = _find_group_hits(reference)
    resp_groups = _find_group_hits(response)
    group_recall = len(ref_groups & resp_groups) / max(len(ref_groups), 1) if ref_groups else 0.0

    ref_tokens = _important_tokens(reference)
    resp_tokens = _important_tokens(response)
    token_recall = len(ref_tokens & resp_tokens) / max(len(ref_tokens), 1) if ref_tokens else 0.0

    concept_recall = len(matched) / max(len(concepts), 1) if concepts else group_recall
    if concepts:
        concept_recall = max(concept_recall, group_recall)

    lexical_overlap = overlap_ratio(reference, response)
    ref_len = max(len(normalize_text(reference)), 1)
    resp_len = len(normalize_text(response))
    length_ratio = resp_len / ref_len

    # Blend concept recall, synonym groups, and lexical overlap.
    similarity = min(
        1.0,
        (0.45 * concept_recall) + (0.25 * group_recall) + (0.20 * lexical_overlap) + (0.10 * min(token_recall, 1.0)),
    )

    # Reward longer answers that cover reference concepts (length penalty control).
    if length_ratio > 1.2 and concept_recall >= 0.5:
        similarity = min(1.0, similarity + 0.08)
    if length_ratio > 2.0 and concept_recall >= 0.6:
        similarity = min(1.0, similarity + 0.05)

    return SemanticMatchResult(
        similarity=round(similarity, 4),
        concept_recall=round(concept_recall, 4),
        matched_concepts=matched,
        missing_concepts=missing,
        lexical_overlap=round(lexical_overlap, 4),
        length_ratio=round(length_ratio, 4),
    )


def semantic_score_to_rubric(similarity: float, concept_recall: float) -> float:
    """Map semantic similarity to a 0-5 rubric score."""
    base = similarity * 5.0
    if concept_recall >= 0.75:
        base = max(base, 4.0)
    elif concept_recall >= 0.5:
        base = max(base, 3.2)
    return min(5.0, round(base, 2))
