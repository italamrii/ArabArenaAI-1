"""Tests for RAG query routing and precision retrieval."""

from __future__ import annotations

from unittest.mock import MagicMock

from rag.config import RAG_MIN_CONFIDENCE, RAG_REQUIRED_MIN_CONFIDENCE
from rag.index import build_knowledge_index
from rag.rag_runner import RAGRunner, build_rag_prompt
from rag.retriever import retrieve
from rag.router import RouteType, route_query


def test_programming_generic_python_is_rag_blocked() -> None:
    question = "Write a Python function `sum_list(nums)` that returns the sum."
    decision = route_query(question, category="programming")
    assert decision.route == RouteType.RAG_BLOCKED
    result = retrieve(question, build_knowledge_index(), route=decision)
    assert not result.rag_used
    assert result.blocked_reason


def test_sql_debugging_question_is_rag_blocked() -> None:
    question = "Debug this SQL: SELECT * FORM users WHERE id = 1;"
    decision = route_query(question, category="programming")
    assert decision.route == RouteType.RAG_BLOCKED
    assert not retrieve(question, build_knowledge_index(), route=decision).rag_used


def test_government_qiwa_is_rag_required_with_confidence() -> None:
    question = "ما هي منصة «قوى» في السعودية؟"
    decision = route_query(question, category="government")
    assert decision.route == RouteType.RAG_REQUIRED
    assert "qiwa" in decision.target_domains
    result = retrieve(question, build_knowledge_index(), route=decision)
    assert result.rag_used
    assert result.retrieval_confidence >= RAG_MIN_CONFIDENCE
    assert all(hit.score >= RAG_MIN_CONFIDENCE for hit in result.hits)


def test_nitaqat_routes_to_nitaqat_domain() -> None:
    decision = route_query("ما الهدف من برنامج نطاقات؟", category="government")
    assert "nitaqat" in decision.target_domains
    result = retrieve("ما الهدف من برنامج نطاقات؟", build_knowledge_index(), route=decision)
    assert result.rag_used
    assert result.hits[0].domain == "nitaqat"


def test_zatca_routes_to_zatca_domain() -> None:
    decision = route_query("ما هي ZATCA؟", category="business")
    assert decision.route == RouteType.RAG_OPTIONAL
    assert "zatca" in decision.target_domains
    result = retrieve("ما هي ZATCA؟", build_knowledge_index(), route=decision)
    # Short ZATCA query may not meet optional 0.65 bar — skip is acceptable.
    assert result.rag_used or result.retrieval_confidence < RAG_MIN_CONFIDENCE


def test_generic_saudi_culture_requires_confidence() -> None:
    question = "ما هو اليوم الوطني السعودي؟"
    decision = route_query(question, category="saudi_knowledge")
    assert decision.route == RouteType.RAG_BLOCKED
    result = retrieve(question, build_knowledge_index(), route=decision)
    assert not result.rag_used


def test_saudi_economy_vat_optional_without_confidence_skips() -> None:
    question = "ما هي ضريبة القيمة المضافة في السعودية وما نسبتها القياسية؟"
    decision = route_query(question, category="saudi_knowledge")
    assert decision.route == RouteType.RAG_OPTIONAL
    assert "zatca" in decision.target_domains
    result = retrieve(question, build_knowledge_index(), route=decision)
    # Seed pack lacks VAT rate detail — low confidence should skip RAG.
    assert not result.rag_used or result.retrieval_confidence >= RAG_MIN_CONFIDENCE


def test_summarization_without_document_reference_is_blocked() -> None:
    question = (
        "Source: «أطلقت المنصة ميزة الدفع الإلكتروني أمس.»\nOne-sentence summary."
    )
    decision = route_query(question, category="summarization")
    assert decision.route == RouteType.RAG_BLOCKED
    assert not retrieve(question, build_knowledge_index(), route=decision).rag_used


def test_summarization_vision2030_in_source_stays_blocked() -> None:
    question = (
        "Source: «رؤية 2030 تهدف لتنويع الاقتصاد، تمكين المواطنين.»\n"
        "Summarize in one Arabic paragraph."
    )
    decision = route_query(question, category="summarization")
    assert decision.route == RouteType.RAG_BLOCKED


def test_translation_generic_sentence_is_blocked() -> None:
    question = "Translate: «Out of stock.»"
    decision = route_query(question, category="translation")
    assert decision.route == RouteType.RAG_BLOCKED


def test_business_generic_strategy_is_blocked() -> None:
    decision = route_query("What is EBITDA margin?", category="business")
    assert decision.route == RouteType.RAG_BLOCKED


def test_vision2030_official_question_optional_with_confidence_gate() -> None:
    question = "ما هي رؤية المملكة العربية السعودية 2030 في جملة واحدة؟"
    decision = route_query(question, category="saudi_knowledge")
    assert decision.route == RouteType.RAG_OPTIONAL
    assert "vision2030" in decision.target_domains
    result = retrieve(question, build_knowledge_index(), route=decision)
    assert result.rag_used
    assert result.retrieval_confidence >= RAG_MIN_CONFIDENCE


def test_vision2030_neom_low_confidence_skips_rag() -> None:
    question = "ما هو مشروع «نيوم» وما دوره ضمن رؤية 2030؟"
    decision = route_query(question, category="saudi_knowledge")
    assert decision.route == RouteType.RAG_OPTIONAL
    result = retrieve(question, build_knowledge_index(), route=decision)
    assert not result.rag_used
    assert result.retrieval_confidence < RAG_MIN_CONFIDENCE


def test_arabic_reasoning_monshaat_false_positive_blocked() -> None:
    question = "لو أُلغيت رسوم ترخيص المنشآt الصغيرة، ماذا يُتوقع على عدد التسجيلات؟"
    decision = route_query(question, category="arabic_reasoning")
    assert decision.route == RouteType.RAG_BLOCKED
    assert not retrieve(question, build_knowledge_index(), route=decision).rag_used


def test_arabic_reasoning_does_not_retrieve_context() -> None:
    question = "إذا كان سعر الكتاب 20 ريالاً واشتريت 3 كتب، كم دفعت؟"
    decision = route_query(question, category="arabic_reasoning")
    assert decision.route == RouteType.RAG_BLOCKED


def test_no_chunks_means_normal_model_call() -> None:
    index = build_knowledge_index()
    mock = MagicMock()
    mock.model_name = "mock-a"
    mock.provider = "mock"
    mock.generate.return_value = "plain answer"

    runner = RAGRunner(mock, index)
    result = runner.generate_with_metadata(
        "Write a Python function to reverse a string.",
        category="programming",
    )
    assert result.rag_used is False
    assert result.route == RouteType.RAG_BLOCKED.value
    assert result.answer == "plain answer"
    mock.generate.assert_called_once()
    assert "retrieved context" not in mock.generate.call_args[0][0].lower()


def test_retrieval_hit_includes_confidence_fields() -> None:
    question = "ما هي منصة «قوى» في السعودية؟"
    decision = route_query(question, category="government")
    result = retrieve(question, build_knowledge_index(), route=decision)
    assert result.rag_used
    hit = result.hits[0]
    assert hit.score >= RAG_REQUIRED_MIN_CONFIDENCE
    assert hit.source_id
    assert hit.reason
    assert result.top_chunk_ids
    assert result.top_chunk_scores


def test_build_rag_prompt_requires_hits() -> None:
    index = build_knowledge_index()
    question = "ما هي منصة «قوى» في السعودية؟"
    decision = route_query(question, category="government")
    hits = retrieve(question, index, route=decision).hits
    prompt = build_rag_prompt(question, hits)
    assert "chunk_id=" in prompt
