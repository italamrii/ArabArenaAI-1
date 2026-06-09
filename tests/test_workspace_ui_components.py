"""Tests for UI streaming helper."""

from __future__ import annotations

from workspace.ui.components import chunk_text_for_stream


def test_chunk_text_for_stream_yields_progressive_text() -> None:
    text = "Hello ArabArena world"
    chunks = list(chunk_text_for_stream(text, chunk_size=5))
    assert chunks
    assert chunks[-1] == text
    assert len(chunks[0]) <= len(chunks[-1])
