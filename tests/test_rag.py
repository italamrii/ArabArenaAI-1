"""Tests for local RAG prototype."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from evaluation.registry.benchmark_schema import BenchmarkCategory, BenchmarkItem, Difficulty
from evaluation.results.storage import EvaluationRunResult
from evaluation.runners.mock_runner import MockRunner
from rag.chunker import chunk_documents_from_manifest
from rag.index import build_knowledge_index
from rag.pipeline import run_rag_evaluation
from rag.rag_runner import RAGRunner, build_rag_prompt
from rag.retriever import retrieve
from rag.router import route_query
from rag.storage import load_rag_run, save_rag_run


def test_chunker_includes_metadata() -> None:
    chunks = chunk_documents_from_manifest()
    assert chunks
    sample = chunks[0]
    assert sample.source_id.startswith("skp-")
    assert sample.domain
    assert sample.document_file.startswith("documents/")
    assert sample.title
    assert sample.text


def test_build_index_counts() -> None:
    index = build_knowledge_index()
    assert index.chunk_count >= 7
    assert len(index.domains) == 7


def test_retriever_finds_qiwa_chunk() -> None:
    index = build_knowledge_index()
    decision = route_query("ما هي منصة قوى في السعودية؟", category="government")
    result = retrieve("ما هي منصة قوى في السعودية؟", index, route=decision)
    assert result.rag_used
    assert any(hit.domain == "qiwa" for hit in result.hits)


def test_build_rag_prompt_includes_context_and_question() -> None:
    index = build_knowledge_index()
    question = "ما هي منصة «قوى» في السعودية؟"
    decision = route_query(question, category="government")
    hits = retrieve(question, index, route=decision).hits
    assert hits
    prompt = build_rag_prompt(question, hits)
    assert "Question:" in prompt
    assert question in prompt
    assert "source_id=" in prompt


def test_rag_runner_with_mock_model() -> None:
    index = build_knowledge_index()
    mock = MagicMock()
    mock.model_name = "mock-a"
    mock.provider = "mock"
    mock.generate.return_value = "إجابة تجريبية مع citation skp-qiwa-001"

    runner = RAGRunner(mock, index, top_k=2)
    question = "ما هي منصة «قوى» في السعودية؟"
    result = runner.generate_with_metadata(question, category="government")
    assert result.answer
    assert result.rag_used
    assert result.citations
    mock.generate.assert_called_once()


def test_rag_result_storage(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("rag.pipeline.save_rag_run", lambda result, directory=None: save_rag_run(result, tmp_path))
    monkeypatch.setattr("rag.storage.RESULTS_DIR", tmp_path, raising=False)
    from evaluation.config import RESULTS_DIR

    monkeypatch.setattr("evaluation.config.RESULTS_DIR", tmp_path)

    result = run_rag_evaluation(
        "mock",
        runner=MockRunner(),
        include_yaml=False,
        limit=3,
        scoring_mode="calibrated",
        top_k=2,
    )
    path = tmp_path / f"rag_{result.run_id}.json"
    assert path.exists()
    loaded = load_rag_run(result.run_id, tmp_path)
    assert loaded.metadata.get("rag") is True
    assert loaded.metadata.get("chunks_indexed", 0) > 0
    assert "route" in loaded.item_scores[0]
    assert "rag_used" in loaded.item_scores[0]


def test_rag_comparison_finds_delta(tmp_path, monkeypatch) -> None:
    from evaluation.reports.rag_comparison import compare_rag_run

    baseline = EvaluationRunResult(
        run_id="baseline",
        timestamp="2026-01-01T00:00:00+00:00",
        model="mock-a",
        provider="mock",
        category_scores={"business": 40.0},
        aas=74.09,
        benchmark_count=1,
        execution_time=1.0,
        item_scores=[
            {
                "accuracy": 1.0,
                "completeness": 5.0,
                "relevance": 1.5,
                "benchmark_id": "biz-001",
                "category": "business",
            }
        ],
        metadata={"scoring_mode": "calibrated", "benchmark_ids": ["biz-001"]},
    )
    rag_run = baseline.model_copy(
        update={
            "run_id": "rag-run",
            "aas": 78.0,
            "item_scores": [
                {
                    "accuracy": 3.0,
                    "completeness": 5.0,
                    "relevance": 3.0,
                    "benchmark_id": "biz-001",
                    "category": "business",
                    "citations": [{"chunk_id": "skp-zatca-001-c001", "source_id": "skp-zatca-001"}],
                    "retrieved_chunks": ["chunk text"],
                }
            ],
            "metadata": {"rag": True, "scoring_mode": "calibrated", "benchmark_ids": ["biz-001"]},
        }
    )
    report = compare_rag_run(rag_run, baseline)
    assert report.aas_delta > 0
    assert report.examples_helped or report.top_improvements
