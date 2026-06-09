"""RAG prompt building and runner wrapper."""

from __future__ import annotations

from pydantic import BaseModel, Field

from evaluation.pipeline import load_system_prompt
from evaluation.runners.base_runner import BaseRunner, RunnerError
from rag.config import RAG_MAX_CHUNKS
from rag.index import KnowledgeIndex, build_knowledge_index
from rag.retriever import RetrievalHit, RetrievalResult, retrieve
from rag.router import route_query


class RAGCitation(BaseModel):
    chunk_id: str
    source_id: str
    domain: str
    document_file: str
    title: str
    section_heading: str
    score: float
    matched_terms: list[str] = Field(default_factory=list)
    reason: str = ""


class RAGGenerationResult(BaseModel):
    answer: str
    question: str
    rag_used: bool = False
    route: str = ""
    routing_reason: str = ""
    detected_entities: list[str] = Field(default_factory=list)
    target_domains: list[str] = Field(default_factory=list)
    retrieval_confidence: float = 0.0
    top_chunk_ids: list[str] = Field(default_factory=list)
    top_chunk_scores: list[float] = Field(default_factory=list)
    blocked_reason: str = ""
    citations: list[RAGCitation] = Field(default_factory=list)
    retrieved_chunks: list[str] = Field(default_factory=list)
    retrieval_hits: list[RetrievalHit] = Field(default_factory=list)
    prompt: str = ""


RAG_SYSTEM_PROMPT = (
    "You are a Saudi-first assistant. Answer benchmark questions using the provided "
    "retrieved context when it is relevant. Prefer facts from the context. If the context "
    "does not contain enough information, answer from general knowledge but say so briefly."
)


def build_rag_prompt(question: str, hits: list[RetrievalHit]) -> str:
    """Build a prompt with retrieved context and citation instructions."""
    if not hits:
        raise ValueError("build_rag_prompt requires at least one retrieval hit")

    context_blocks: list[str] = []
    for idx, hit in enumerate(hits, start=1):
        context_blocks.append(
            "\n".join(
                [
                    f"[Context {idx}] source_id={hit.source_id} chunk_id={hit.chunk_id} "
                    f"domain={hit.domain} title={hit.title}",
                    hit.text.strip(),
                ]
            )
        )

    context = "\n\n".join(context_blocks)
    return (
        "Use the retrieved context below when answering. "
        "Cite source_id and chunk_id when relying on a context block.\n\n"
        f"{context}\n\n"
        f"Question:\n{question.strip()}\n\n"
        "Answer:"
    )


def hits_to_citations(hits: list[RetrievalHit]) -> list[RAGCitation]:
    return [
        RAGCitation(
            chunk_id=hit.chunk_id,
            source_id=hit.source_id,
            domain=hit.domain,
            document_file=hit.document_file,
            title=hit.title,
            section_heading=hit.section_heading,
            score=hit.score,
            matched_terms=hit.matched_terms,
            reason=hit.reason,
        )
        for hit in hits
    ]


class RAGRunner:
    """Wrap an existing model runner with routed retrieval-augmented prompting."""

    def __init__(
        self,
        runner: BaseRunner,
        index: KnowledgeIndex,
        *,
        top_k: int = RAG_MAX_CHUNKS,
    ) -> None:
        self._runner = runner
        self._index = index
        self._top_k = top_k
        self._plain_system_prompt = load_system_prompt()

    @property
    def model_name(self) -> str:
        return self._runner.model_name

    @property
    def provider(self) -> str:
        return self._runner.provider

    def retrieve_routed(self, question: str, *, category: str | None = None) -> RetrievalResult:
        decision = route_query(question, category=category)
        return retrieve(question, self._index, route=decision, top_k=self._top_k)

    def generate_with_metadata(
        self,
        question: str,
        *,
        category: str | None = None,
        system_prompt: str | None = None,
    ) -> RAGGenerationResult:
        retrieval = self.retrieve_routed(question, category=category)
        decision = route_query(question, category=category)

        if not retrieval.rag_used or not retrieval.hits:
            try:
                answer = self._runner.generate(
                    question,
                    system_prompt=system_prompt or self._plain_system_prompt,
                )
            except RunnerError:
                raise
            blocked_reason = retrieval.blocked_reason or decision.routing_reason
            return RAGGenerationResult(
                answer=answer,
                question=question,
                rag_used=False,
                route=decision.route.value,
                routing_reason=decision.routing_reason,
                detected_entities=decision.detected_entities,
                target_domains=decision.target_domains,
                retrieval_confidence=retrieval.retrieval_confidence,
                top_chunk_ids=retrieval.top_chunk_ids,
                top_chunk_scores=retrieval.top_chunk_scores,
                blocked_reason=blocked_reason,
                prompt=question,
            )

        prompt = build_rag_prompt(question, retrieval.hits)
        try:
            answer = self._runner.generate(prompt, system_prompt=system_prompt or RAG_SYSTEM_PROMPT)
        except RunnerError:
            raise

        citations = hits_to_citations(retrieval.hits)
        return RAGGenerationResult(
            answer=answer,
            question=question,
            rag_used=True,
            route=decision.route.value,
            routing_reason=decision.routing_reason,
            detected_entities=decision.detected_entities,
            target_domains=decision.target_domains,
            retrieval_confidence=retrieval.retrieval_confidence,
            top_chunk_ids=retrieval.top_chunk_ids,
            top_chunk_scores=retrieval.top_chunk_scores,
            blocked_reason="",
            citations=citations,
            retrieved_chunks=[hit.text for hit in retrieval.hits],
            retrieval_hits=retrieval.hits,
            prompt=prompt,
        )

    def generate(self, prompt: str, *, system_prompt: str | None = None) -> str:
        return self.generate_with_metadata(prompt, system_prompt=system_prompt).answer


def create_rag_runner(model: str, *, runner: BaseRunner | None = None, top_k: int = RAG_MAX_CHUNKS) -> RAGRunner:
    from evaluation.runners.runner_factory import create_runner

    active = runner or create_runner(model)
    index = build_knowledge_index()
    return RAGRunner(active, index, top_k=top_k)
