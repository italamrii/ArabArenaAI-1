"""Factory for model runners."""

from __future__ import annotations

from evaluation.runners.anthropic_runner import AnthropicRunner
from evaluation.runners.arabarena_runner import ArabArenaRunner
from evaluation.runners.base_runner import BaseRunner, RunnerError
from evaluation.runners.deepseek_runner import DeepSeekRunner
from evaluation.runners.google_runner import GoogleRunner
from evaluation.runners.local_runners import LlamaRunner, QwenRunner
from evaluation.runners.mock_runner import MockRunner
from evaluation.runners.openai_runner import OpenAIRunner

SUPPORTED_MODELS: dict[str, type[BaseRunner]] = {
    "mock": MockRunner,
    "openai": OpenAIRunner,
    "anthropic": AnthropicRunner,
    "google": GoogleRunner,
    "deepseek": DeepSeekRunner,
    "qwen": QwenRunner,
    "llama": LlamaRunner,
    "arabarena": ArabArenaRunner,
}


def create_runner(model: str, *, model_name: str | None = None) -> BaseRunner:
    """Instantiate a runner by provider key."""
    key = model.strip().lower()
    if key not in SUPPORTED_MODELS:
        supported = ", ".join(sorted(SUPPORTED_MODELS))
        raise RunnerError(f"Unsupported model provider '{model}'. Supported: {supported}")
    runner_cls = SUPPORTED_MODELS[key]
    if runner_cls is MockRunner:
        return MockRunner(model_name or "mock")
    return runner_cls(model_name=model_name)
