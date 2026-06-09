"""ArabArena AI interaction modes for the beta personality layer."""

from __future__ import annotations

from enum import Enum


class InteractionMode(str, Enum):
    """High-level intent modes that drive system prompt and response shape."""

    FOUNDER = "founder"
    ENGINEERING = "engineering"
    GENERAL = "general"

    @property
    def label_ar(self) -> str:
        labels = {
            InteractionMode.FOUNDER: "وضع المؤسس",
            InteractionMode.ENGINEERING: "وضع الهندسة",
            InteractionMode.GENERAL: "وضع المساعد",
        }
        return labels[self]
