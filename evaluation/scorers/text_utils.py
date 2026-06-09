"""Text utilities for scoring."""

from __future__ import annotations

import re
import unicodedata


def normalize_text(text: str) -> str:
    """Normalize text for comparison (Unicode NFC, lowercase, whitespace)."""
    normalized = unicodedata.normalize("NFC", text.strip().lower())
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def tokenize(text: str) -> set[str]:
    """Simple whitespace/punctuation tokenization suitable for Arabic and Latin."""
    normalized = normalize_text(text)
    tokens = re.findall(r"[\w\u0600-\u06FF]+", normalized, flags=re.UNICODE)
    return set(tokens)


def overlap_ratio(reference: str, response: str) -> float:
    ref_tokens = tokenize(reference)
    resp_tokens = tokenize(response)
    if not ref_tokens:
        return 0.0
    if not resp_tokens:
        return 0.0
    intersection = ref_tokens & resp_tokens
    return len(intersection) / len(ref_tokens)
