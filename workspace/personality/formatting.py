"""Response formatting hooks for ArabArena AI personality layer."""

from __future__ import annotations

import re

from workspace.personality.modes import InteractionMode
from workspace.personality.prompts import get_response_section_headers

ROBOTIC_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bas an ai model\b", re.IGNORECASE), ""),
    (re.compile(r"\bas an ai\b", re.IGNORECASE), ""),
    (re.compile(r"\bas a language model\b", re.IGNORECASE), ""),
    (re.compile(r"\bi am an ai\b", re.IGNORECASE), ""),
    (re.compile(r"\bi'?m an ai\b", re.IGNORECASE), ""),
    (re.compile(r"بصفتي\s+نموذج(?:اً|ا)?\s+لغوي(?:اً|ا)?", re.IGNORECASE), ""),
    (re.compile(r"ك(?:ذكاء|ـذكاء)\s+اصطناعي", re.IGNORECASE), ""),
    (re.compile(r"كنموذج\s+لغوي", re.IGNORECASE), ""),
)


def sanitize_robotic_language(text: str) -> str:
    """Remove common robotic disclaimers and phrasing."""
    cleaned = text
    for pattern, replacement in ROBOTIC_PATTERNS:
        cleaned = pattern.sub(replacement, cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def has_expected_sections(text: str, mode: InteractionMode) -> bool:
    """Return True when all mode-specific section headers are present."""
    headers = get_response_section_headers(mode)
    return all(header in text for header in headers)


def apply_response_formatting(text: str, mode: InteractionMode) -> str:
    """Post-process model output: sanitize tone and normalize whitespace."""
    cleaned = sanitize_robotic_language(text)
    cleaned = re.sub(r"[ \t]+\n", "\n", cleaned)
    return cleaned.strip()
