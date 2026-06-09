"""Shared HTTP utilities for provider runners."""

from __future__ import annotations

import os
from typing import Any

import httpx

from evaluation.runners.base_runner import RunnerError


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RunnerError(f"Missing required environment variable: {name}")
    return value


def post_json(
    url: str,
    payload: dict[str, Any],
    headers: dict[str, str],
    *,
    timeout: float = 120.0,
) -> dict[str, Any]:
    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                raise RunnerError("Provider returned non-object JSON response")
            return data
    except httpx.HTTPError as exc:
        raise RunnerError(f"HTTP request failed: {exc}") from exc
