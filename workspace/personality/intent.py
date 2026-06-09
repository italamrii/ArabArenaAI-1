"""Intent detection for ArabArena AI personality modes."""

from __future__ import annotations

import re

from workspace.personality.modes import InteractionMode

# Arabic + English keyword signals (lowercase Latin; Arabic matched as-is).
FOUNDER_KEYWORDS: tuple[str, ...] = (
    "مشروع",
    "ريادة",
    "ربح",
    "ربحي",
    "تسويق",
    "منافس",
    "منافسين",
    "فكرة",
    "خطة",
    "استراتيج",
    "نمو",
    "عملاء",
    "عميل",
    "مبيعات",
    "إيراد",
    "revenue",
    "startup",
    "business",
    "market",
    "product",
    "go-to-market",
    "gtm",
    "pricing",
    "monetization",
    "pitch",
    "investor",
    "مستثمر",
    "saas",
    "brand",
    "علامة",
)

ENGINEERING_KEYWORDS: tuple[str, ...] = (
    "bug",
    "error",
    "exception",
    "stack trace",
    "traceback",
    "database",
    "sqlite",
    "sql",
    "api",
    "backend",
    "frontend",
    "architecture",
    "deploy",
    "performance",
    "latency",
    "memory leak",
    "test",
    "pytest",
    "refactor",
    "code",
    "python",
    "streamlit",
    "ollama",
    "qwen",
    "خطأ",
    "كود",
    "برمج",
    "تقني",
    "هندس",
    "سيرفر",
    "قاعدة بيانات",
    "مقفل",
    "locked",
    "timeout",
    "root cause",
    "debug",
    "fix",
    "إصلاح",
    "تشخيص",
)


def _normalize_for_match(text: str) -> str:
    lowered = text.lower().strip()
    lowered = re.sub(r"\s+", " ", lowered)
    return lowered


def _score_keywords(text: str, keywords: tuple[str, ...]) -> int:
    score = 0
    for keyword in keywords:
        if keyword.isascii():
            if keyword in text:
                score += 1
        elif keyword in text or keyword in text.replace(" ", ""):
            score += 1
    return score


def detect_interaction_mode(prompt: str) -> InteractionMode:
    """Classify user intent into founder, engineering, or general assistant mode."""
    if not prompt or not prompt.strip():
        return InteractionMode.GENERAL

    normalized = _normalize_for_match(prompt)
    founder_score = _score_keywords(normalized, FOUNDER_KEYWORDS)
    engineering_score = _score_keywords(normalized, ENGINEERING_KEYWORDS)

    if engineering_score > founder_score and engineering_score > 0:
        return InteractionMode.ENGINEERING
    if founder_score > 0 and founder_score >= engineering_score:
        return InteractionMode.FOUNDER
    return InteractionMode.GENERAL
