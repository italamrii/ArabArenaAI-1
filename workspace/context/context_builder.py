"""Build compact Arabic-friendly project context for AI prompts."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from workspace.db.models import ProjectMemory, ProjectSummary
from workspace.schemas.search import ContextBuildResult
from workspace.services.authz import get_project_for_owner
from workspace.services.memory_search_service import search_memories

# ~1200 tokens ≈ 4800 characters (conservative for mixed Arabic/Latin).
DEFAULT_MAX_CONTEXT_CHARS = 4800
IMPORTANCE_THRESHOLD = 70
MAX_PINNED = 8
MAX_IMPORTANT = 6
MAX_DECISIONS = 5
MAX_SUMMARIES = 2
MAX_SEARCH_HITS = 5


def _format_memory_line(memory: ProjectMemory) -> str:
    title = memory.title.strip() if memory.title else ""
    prefix = f"[{memory.memory_type}]"
    if title:
        return f"{prefix} {title}: {memory.content.strip()}"
    return f"{prefix} {memory.content.strip()}"


def _append_section(
    parts: list[str],
    *,
    heading: str,
    lines: list[str],
    used_ids: list[uuid.UUID],
    memory_ids: list[uuid.UUID],
    budget: int,
) -> int:
    """Append a section if budget allows; return remaining budget."""
    if not lines:
        return budget
    block = heading + "\n" + "\n".join(lines)
    if len(block) + 2 > budget:
        return budget
    parts.append(block)
    used_ids.extend(memory_ids)
    return budget - len(block) - 2


def build_project_context(
    session: Session,
    owner_id: uuid.UUID,
    project_id: uuid.UUID,
    *,
    query: str | None = None,
    max_chars: int = DEFAULT_MAX_CONTEXT_CHARS,
) -> ContextBuildResult:
    """Assemble a short project context block within a character budget."""
    project = get_project_for_owner(session, project_id, owner_id)
    parts: list[str] = []
    used_ids: list[uuid.UUID] = []
    remaining = max(200, max_chars)

    header_lines = [f"المشروع: {project.name}"]
    if project.description and project.description.strip():
        header_lines.append(f"الوصف: {project.description.strip()}")
    header = "\n".join(header_lines)
    parts.append(header)
    remaining -= len(header) + 2

    stmt = (
        select(ProjectMemory)
        .where(
            ProjectMemory.project_id == project_id,
            ProjectMemory.owner_id == owner_id,
            ProjectMemory.is_archived.is_(False),
        )
        .order_by(
            ProjectMemory.is_pinned.desc(),
            ProjectMemory.importance_score.desc(),
            ProjectMemory.updated_at.desc(),
        )
    )
    memories = list(session.scalars(stmt).all())

    pinned = [m for m in memories if m.is_pinned][:MAX_PINNED]
    if pinned:
        lines = [_format_memory_line(m) for m in pinned]
        remaining = _append_section(
            parts,
            heading="ذاكرة مثبتة:",
            lines=lines,
            used_ids=used_ids,
            memory_ids=[m.id for m in pinned],
            budget=remaining,
        )

    important = [
        m
        for m in memories
        if not m.is_pinned and m.importance_score >= IMPORTANCE_THRESHOLD
    ][:MAX_IMPORTANT]
    if important:
        lines = [_format_memory_line(m) for m in important]
        remaining = _append_section(
            parts,
            heading="ذاكرة مهمة:",
            lines=lines,
            used_ids=used_ids,
            memory_ids=[m.id for m in important],
            budget=remaining,
        )

    decisions = [
        m for m in memories if m.memory_type == "decision" and m.id not in used_ids
    ][:MAX_DECISIONS]
    if decisions:
        lines = [_format_memory_line(m) for m in decisions]
        remaining = _append_section(
            parts,
            heading="قرارات حديثة:",
            lines=lines,
            used_ids=used_ids,
            memory_ids=[m.id for m in decisions],
            budget=remaining,
        )

    summaries = list(
        session.scalars(
            select(ProjectSummary)
            .where(
                ProjectSummary.project_id == project_id,
                ProjectSummary.owner_id == owner_id,
            )
            .order_by(ProjectSummary.generated_at.desc())
            .limit(MAX_SUMMARIES)
        ).all()
    )
    if summaries and remaining > 80:
        summary_lines = [s.content.strip() for s in summaries if s.content.strip()]
        remaining = _append_section(
            parts,
            heading="ملخصات المشروع:",
            lines=summary_lines,
            used_ids=used_ids,
            memory_ids=[],
            budget=remaining,
        )

    if query and query.strip() and remaining > 80:
        search = search_memories(
            session,
            owner_id,
            project_id,
            query.strip(),
            limit=MAX_SEARCH_HITS,
        )
        hits = [hit for hit in search.items if hit.memory.id not in used_ids]
        if hits:
            lines = []
            hit_ids: list[uuid.UUID] = []
            for hit in hits:
                mem = hit.memory
                title = mem.title.strip() if mem.title else ""
                prefix = f"[{mem.memory_type}]"
                if title:
                    line = f"{prefix} {title}: {mem.content.strip()}"
                else:
                    line = f"{prefix} {mem.content.strip()}"
                lines.append(line)
                hit_ids.append(mem.id)
            remaining = _append_section(
                parts,
                heading="ذاكرة ذات صلة بالسؤال:",
                lines=lines,
                used_ids=used_ids,
                memory_ids=hit_ids,
                budget=remaining,
            )

    context_text = "\n\n".join(parts).strip()
    unique_ids = list(dict.fromkeys(used_ids))
    return ContextBuildResult(
        context_text=context_text,
        context_chars=len(context_text),
        memories_used=unique_ids,
        context_used=bool(context_text),
    )
