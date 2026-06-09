# Phase Next — Workspace Layer

Architecture plan for transforming ArabArena AI from single-turn evaluation into a **project-aware AI workspace** with persistent memory and (later) domain experts.

This document tracks incremental delivery. **Steps 1–7 (Phase A)** are implemented; later phases are planned only.

---

## Vision

```
Project → Memory → Expert Understanding → AI Execution → Deliverables
```

The workspace layer is **additive**. Existing evaluation, RAG, and knowledge-pack tooling must keep working unchanged.

---

## Quick Start

```bash
pip install -r requirements-workspace.txt
```

Set environment variables:

```bash
WORKSPACE_ENABLED=true
WORKSPACE_DATABASE_URL=sqlite:///./workspace_dev.db
```

Optional local model defaults:

```bash
WORKSPACE_DEFAULT_PROVIDER=qwen
OLLAMA_BASE_URL=http://localhost:11434
QWEN_MODEL=qwen3:8b
```

Run migrations if using PostgreSQL (SQLite tables auto-create via `init_db` in dev):

```bash
alembic upgrade head
```

Run API:

```bash
uvicorn workspace.api.app:app --reload
```

Run Arabic workspace dashboard:

```bash
streamlit run workspace/ui/workspace_dashboard.py
```

Dev auth header for API:

```http
X-User-Id: 550e8400-e29b-41d4-a716-446655440000
```

`WORKSPACE_ENABLED=false` (default) → all workspace routes return **404** `Workspace is disabled`.

---

## Step 1 — Implemented (Database Foundation)

| Component | Location |
|-----------|----------|
| SQLAlchemy models | `workspace/db/models.py` |
| Alembic migration | `workspace/db/migrations/versions/001_initial_workspace.py` |
| Ownership helpers | `workspace/services/authz.py` |
| Feature flag | `WORKSPACE_ENABLED` (default **false**) |

Models: `User`, `Project`, `ProjectMemory`, `ProjectFile`, `ProjectMilestone`, `Conversation`, `ConversationMessage`, `ProjectSummary`, `ActivityLog`.

---

## Step 2 — Implemented (Project CRUD Service + API)

| Component | Location |
|-----------|----------|
| Project service | `workspace/services/project_service.py` |
| Schemas | `workspace/schemas/project.py` |
| API | `workspace/api/routes/projects.py` |

### Project endpoints

| Method | Path |
|--------|------|
| POST | `/api/v1/workspace/projects` |
| GET | `/api/v1/workspace/projects` |
| GET | `/api/v1/workspace/projects/{project_id}` |
| PATCH | `/api/v1/workspace/projects/{project_id}` |
| POST | `/api/v1/workspace/projects/{project_id}/archive` |
| DELETE | `/api/v1/workspace/projects/{project_id}` |

---

## Step 3 — Implemented (Memory CRUD Service + API)

| Component | Location |
|-----------|----------|
| Memory service | `workspace/services/memory_service.py` |
| Schemas | `workspace/schemas/memory.py` |
| API | `workspace/api/routes/memories.py` |

### Memory endpoints

| Method | Path |
|--------|------|
| POST | `/api/v1/workspace/projects/{project_id}/memories` |
| GET | `/api/v1/workspace/projects/{project_id}/memories` |
| GET | `/api/v1/workspace/projects/{project_id}/memories/{memory_id}` |
| PATCH | `/api/v1/workspace/projects/{project_id}/memories/{memory_id}` |
| POST | `/api/v1/workspace/projects/{project_id}/memories/{memory_id}/pin` |
| POST | `/api/v1/workspace/projects/{project_id}/memories/{memory_id}/unpin` |
| POST | `/api/v1/workspace/projects/{project_id}/memories/{memory_id}/archive` |
| PATCH | `/api/v1/workspace/projects/{project_id}/memories/{memory_id}/importance` |
| DELETE | `/api/v1/workspace/projects/{project_id}/memories/{memory_id}` |

---

## Step 4 — Implemented (Memory Search)

| Component | Location |
|-----------|----------|
| Text ranking helpers | `workspace/services/text_search.py` |
| Search service | `workspace/services/memory_search_service.py` |
| Schemas | `workspace/schemas/search.py` |
| API | `GET /api/v1/workspace/projects/{project_id}/memories/search?q=...` |

Local ranking only (no vector DB):

- Arabic/English normalization via shared `evaluation/scorers/text_utils.py`
- Token overlap, exact phrase boost, title boost, pinned boost, importance boost, light recency boost
- Owner-scoped, project-scoped, excludes archived by default
- Filters: `memory_type`, `memory_scope`, `include_archived`

Tests: `tests/test_workspace_memory_search.py`

---

## Step 5 — Implemented (Context Builder)

| Component | Location |
|-----------|----------|
| Context builder | `workspace/context/context_builder.py` |
| Context-aware runner | `workspace/context/context_aware_runner.py` |

Builds a compact Arabic-friendly context block (~1200 tokens / 4800 chars):

1. Project name and description
2. Pinned memories
3. High-importance memories
4. Recent decisions
5. Project summaries (if any)
6. Relevant search hits for the user query

`ContextAwareRunner` wraps existing `BaseRunner` without modifying it — prepends context to the system prompt.

Tests: `tests/test_workspace_context_builder.py`, `tests/test_workspace_context_runner.py`

---

## Step 6 — Implemented (Workspace Chat)

| Component | Location |
|-----------|----------|
| Conversation service | `workspace/services/conversation_service.py` |
| Schemas | `workspace/schemas/conversation.py` |
| API | `workspace/api/routes/conversations.py` |

### Conversation endpoints

| Method | Path |
|--------|------|
| POST | `/api/v1/workspace/projects/{project_id}/conversations` |
| GET | `/api/v1/workspace/projects/{project_id}/conversations` |
| GET | `/api/v1/workspace/projects/{project_id}/conversations/{conversation_id}` |
| POST | `/api/v1/workspace/projects/{project_id}/conversations/{conversation_id}/messages` |

`send_message` flow: verify ownership → store user message → build context → run model via `ContextAwareRunner` → store assistant reply with `metadata_json` (`model`, `provider`, `context_used`, `memories_used`, `context_chars`).

Default provider: `WORKSPACE_DEFAULT_PROVIDER=qwen` (Ollama). Configurable per message. Clean error on model failure.

Tests: `tests/test_workspace_conversation_service.py`, `tests/test_workspace_search_conversation_api.py`

---

## Step 7 — Implemented (Arabic Interactive Workspace Dashboard)

| Component | Location |
|-----------|----------|
| Dashboard | `workspace/ui/workspace_dashboard.py` |
| Helpers | `workspace/ui/helpers.py` |

Separate from `evaluation/dashboard.py`. Arabic-first with RTL styling.

Sections:

1. **المشاريع** — create/list/select projects
2. **الذاكرة** — create/list/search memories, pin/unpin, archive, importance
3. **المحادثة الذكية** — project chat with context metadata
4. **ملخص المشروع** — description, assembled context, activity placeholder
5. **إعدادات** — provider/model selection, workspace flag warning, Ollama status

Run:

```bash
streamlit run workspace/ui/workspace_dashboard.py
```

Tests: `tests/test_workspace_dashboard_helpers.py` (helpers only; no heavy Streamlit UI tests)

---

## Not Implemented Yet

- Expert Layer (`experts/`)
- Auto Summarization
- Deliverables Engine
- Agents / autonomous workflows
- Vector DB / external embeddings
- Full authentication (JWT/SSO)

---

## Unchanged Systems

- `evaluation/` — benchmark pipeline, scorers, Streamlit eval dashboard
- `rag/` — routing, retrieval, RAG evaluation
- `knowledge/` — Saudi Knowledge Pack
- Existing CLIs: `evaluation/evaluate.py`, `rag/evaluate_rag.py`

---

## Planned Steps (Summary)

| Step | Scope | Status |
|------|--------|--------|
| 1 | Database foundation | **Done** |
| 2 | Project CRUD service + API | **Done** |
| 3 | Memory CRUD + pin/archive/importance | **Done** |
| 4 | Memory search (local ranking) | **Done** |
| 5 | Context builder + ContextAwareRunner | **Done** |
| 6 | Workspace chat (conversations) | **Done** |
| 7 | Arabic workspace dashboard | **Done** |
| 8+ | Expert framework, auto summarization, deliverables | Planned |

---

## Next Recommended Phase

**Phase B — Expert Layer foundation**

- `experts/` registry and routing (read-only integration with workspace context)
- Domain expert prompts without autonomous agents
- Still no changes to `evaluation/`, `rag/`, or `knowledge/`
- Keep `WORKSPACE_ENABLED=false` by default until production-ready
