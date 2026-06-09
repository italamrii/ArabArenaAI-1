"""Tests for Ollama-backed Qwen runner."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest

from evaluation.runners.base_runner import RunnerError
from evaluation.runners.local_runners import OllamaRunner, QwenRunner
from evaluation.runners.runner_factory import create_runner


def test_qwen_runner_default_model(monkeypatch) -> None:
    monkeypatch.delenv("QWEN_MODEL", raising=False)
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)
    runner = QwenRunner()
    assert runner.model_name == "qwen3:8b"
    assert runner.provider == "qwen"


def test_qwen_runner_custom_model(monkeypatch) -> None:
    monkeypatch.setenv("QWEN_MODEL", "qwen3:14b")
    runner = QwenRunner()
    assert runner.model_name == "qwen3:14b"


def test_factory_qwen_returns_ollama_runner() -> None:
    runner = create_runner("qwen")
    assert isinstance(runner, QwenRunner)
    assert runner.model_name == "qwen3:8b"


def test_factory_qwen_model_name_override() -> None:
    runner = create_runner("qwen", model_name="qwen3:14b")
    assert runner.model_name == "qwen3:14b"


@patch("evaluation.runners.local_runners.httpx.Client")
def test_ollama_generate_success(mock_client_cls: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "مرحباً", "done": True}
    mock_response.raise_for_status = MagicMock()

    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=None)
    mock_client.post.return_value = mock_response
    mock_client_cls.return_value = mock_client

    runner = OllamaRunner(model_name="qwen3:8b", base_url="http://localhost:11434", timeout=30.0)
    result = runner.generate("ما هي رؤية 2030؟", system_prompt="Answer in Arabic.")

    assert result == "مرحباً"
    mock_client.post.assert_called_once()
    call_kwargs = mock_client.post.call_args
    assert call_kwargs[0][0] == "http://localhost:11434/api/generate"
    payload = call_kwargs[1]["json"]
    assert payload["model"] == "qwen3:8b"
    assert payload["stream"] is False
    assert "ما هي رؤية 2030؟" in payload["prompt"]
    assert "Answer in Arabic." in payload["prompt"]


@patch("evaluation.runners.local_runners.httpx.Client")
def test_ollama_generate_timeout(mock_client_cls: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=None)
    mock_client.post.side_effect = httpx.TimeoutException("timed out")
    mock_client_cls.return_value = mock_client

    runner = OllamaRunner(model_name="qwen3:8b", timeout=1.0)
    with pytest.raises(RunnerError, match="timed out"):
        runner.generate("test prompt")


@patch("evaluation.runners.local_runners.httpx.Client")
def test_ollama_generate_empty_response(mock_client_cls: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "", "done": True}
    mock_response.raise_for_status = MagicMock()

    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=None)
    mock_client.post.return_value = mock_response
    mock_client_cls.return_value = mock_client

    runner = OllamaRunner(model_name="qwen3:8b")
    with pytest.raises(RunnerError, match="empty response"):
        runner.generate("test prompt")
