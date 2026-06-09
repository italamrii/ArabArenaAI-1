"""Base model runner interface."""

from __future__ import annotations

from abc import ABC, abstractmethod


class RunnerError(RuntimeError):
    """Raised when a model runner fails to generate a response."""


class BaseRunner(ABC):
    """Unified interface for all model providers."""

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    @abstractmethod
    def generate(self, prompt: str, *, system_prompt: str | None = None) -> str:
        """Generate a model response for the given prompt."""
        raise NotImplementedError

    @property
    @abstractmethod
    def provider(self) -> str:
        """Provider identifier (e.g. openai, anthropic)."""
        raise NotImplementedError
