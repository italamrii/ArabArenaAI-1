"""RAG prototype configuration."""

from __future__ import annotations

from pathlib import Path

RAG_ROOT = Path(__file__).resolve().parent
REPO_ROOT = RAG_ROOT.parent
KNOWLEDGE_ROOT = REPO_ROOT / "knowledge"
DEFAULT_TOP_K = 3
DEFAULT_CHUNK_MAX_CHARS = 480
RAG_RESULTS_PREFIX = "rag_"
RAG_COMPARISON_PREFIX = "rag_comparison_"

# Retrieval precision controls (Phase 5.4 / 5.4.1)
# Top hit must meet this score or RAG is skipped entirely.
RAG_MIN_CONFIDENCE = 0.65
RAG_MAX_CHUNKS = 3
# Government entity questions may pass slightly below optional threshold when alias+domain align.
RAG_REQUIRED_MIN_CONFIDENCE = 0.55
RAG_OPTIONAL_MIN_OVERLAP = 0.12
# Drop trailing chunks that fall far below the top hit (avoids weak padding).
RAG_MIN_CHUNK_RELATIVE_GAP = 0.20

RAG_BLOCKED_CATEGORIES = frozenset(
    {
        "programming",
        "translation",
        "summarization",
        "arabic_reasoning",
    }
)
RAG_OPTIONAL_CATEGORIES = frozenset({"saudi_knowledge", "business"})
RAG_REQUIRED_CATEGORIES = frozenset({"government"})

# Categories where entity detection must never enable RAG.
RAG_NEVER_OVERRIDE_CATEGORIES = RAG_BLOCKED_CATEGORIES

# allowed_use values that permit prototype RAG over manual seed documents only.
RAG_ALLOWED_USE_MARKERS = ("registry_only", "prototype")
