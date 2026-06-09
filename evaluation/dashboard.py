"""ArabArenaAI-1 — local baseline evaluation dashboard (Streamlit)."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# Ensure repo root is importable
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from evaluation.dashboard_data import (
    category_filter_options,
    dashboard_summary,
    filter_runs,
    get_run_traces,
    load_all_runs,
    load_failure_audit,
    load_leaderboard,
    load_rag_comparison,
    load_rag_runs,
    load_regression_reports,
    load_run_json,
    load_scoring_comparison,
    lowest_scoring_traces,
    model_filter_options,
    run_filter_options,
    run_has_text_traces,
    run_label,
)
from evaluation.results.storage import EvaluationRunResult

st.set_page_config(
    page_title="ArabArenaAI-1 Baseline Dashboard",
    page_icon="📊",
    layout="wide",
)

SECTIONS = [
    "Overview",
    "Leaderboard",
    "Model Details",
    "Category Scores",
    "Failure Analysis",
    "Knowledge Gap Audit",
    "Scoring Calibration",
    "RAG Experiments",
    "Regression Reports",
    "Raw Run JSON Viewer",
]


@st.cache_data(ttl=30)
def _cached_rag_runs():
    return load_rag_runs()


@st.cache_data(ttl=30)
def _cached_runs() -> list[EvaluationRunResult]:
    return load_all_runs()


@st.cache_data(ttl=30)
def _cached_leaderboard():
    return load_leaderboard()


@st.cache_data(ttl=30)
def _cached_regressions():
    return load_regression_reports()


def _apply_category_filter(
    runs: list[EvaluationRunResult], category: str
) -> list[EvaluationRunResult]:
    if category == "All":
        return runs
    return [r for r in runs if category in r.category_scores]


def main() -> None:
    st.title("ArabArenaAI-1 Baseline Dashboard")
    st.caption("Local-first view of evaluation runs, leaderboards, and regression reports.")

    all_runs = _cached_runs()
    leaderboard = _cached_leaderboard()
    regressions = _cached_regressions()

    with st.sidebar:
        st.header("Filters")
        model_options = model_filter_options(all_runs)
        run_options = run_filter_options(all_runs)
        category_options = category_filter_options(all_runs)

        selected_model = st.selectbox("Model", model_options, index=0)
        selected_run = st.selectbox("Date / Run", run_options, index=0)
        selected_category = st.selectbox("Category", category_options, index=0)

        section = st.radio("Section", SECTIONS, index=0)

        st.divider()
        st.markdown("**Data paths**")
        st.text(f"Results: evaluation/results/")
        st.text(f"Reports: evaluation/reports/")

    filtered = filter_runs(all_runs, model_label=selected_model, run_label=selected_run)
    filtered = _apply_category_filter(filtered, selected_category)

    if section == "Overview":
        _render_overview(all_runs, leaderboard, filtered, selected_category)
    elif section == "Leaderboard":
        _render_leaderboard(leaderboard)
    elif section == "Model Details":
        _render_model_details(filtered if filtered else all_runs)
    elif section == "Category Scores":
        _render_category_scores(filtered if filtered else all_runs, selected_category)
    elif section == "Failure Analysis":
        _render_failure_analysis(filtered if filtered else all_runs, selected_category)
    elif section == "Knowledge Gap Audit":
        _render_knowledge_gap_audit(filtered if filtered else all_runs)
    elif section == "Scoring Calibration":
        _render_scoring_calibration(filtered if filtered else all_runs)
    elif section == "RAG Experiments":
        _render_rag_experiments(_cached_rag_runs())
    elif section == "Regression Reports":
        _render_regressions(regressions)
    elif section == "Raw Run JSON Viewer":
        _render_raw_json(all_runs if selected_run == "All" else filtered)


def _render_overview(
    all_runs: list[EvaluationRunResult],
    leaderboard,
    filtered: list[EvaluationRunResult],
    category: str,
) -> None:
    summary = dashboard_summary(all_runs, leaderboard)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Runs", summary["total_runs"])
    c2.metric("Models", summary["models_count"])
    c3.metric("Best AAS", f"{summary['best_aas']:.2f}" if summary["best_aas"] is not None else "—")
    c4.metric("Latest AAS", f"{summary['latest_aas']:.2f}" if summary["latest_aas"] is not None else "—")

    if not all_runs:
        st.warning("No evaluation runs found. Run: `python evaluation/evaluate.py --model mock`")
        return

    st.subheader("Latest Run")
    latest = all_runs[0]
    _run_metrics_row(latest)

    if category != "All" and filtered:
        st.subheader(f"Filtered — {category}")
        st.dataframe(
            [
                {
                    "Run": run_label(r),
                    "Model": f"{r.provider}:{r.model}",
                    "AAS": r.aas,
                    category: r.category_scores.get(category, 0.0),
                }
                for r in filtered[:10]
            ],
            use_container_width=True,
        )


def _render_leaderboard(leaderboard) -> None:
    st.subheader("Leaderboard")
    if leaderboard is None:
        st.info("No leaderboard.json found. Run an evaluation first.")
        return

    st.caption(f"Generated: {leaderboard.generated_at} · Total runs: {leaderboard.total_runs}")

    rows = [
        {
            "Rank": idx + 1,
            "Provider": e.provider,
            "Model": e.model,
            "Best AAS": e.best_aas,
            "Runs": e.run_count,
            "Benchmarks": e.benchmark_count,
            "Best Run ID": e.best_run_id[:8] + "…",
        }
        for idx, e in enumerate(leaderboard.entries)
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)

    if leaderboard.entries:
        top = leaderboard.entries[0]
        st.success(f"Leading model: **{top.provider}:{top.model}** — AAS **{top.best_aas:.2f}**")


def _render_model_details(runs: list[EvaluationRunResult]) -> None:
    st.subheader("Model Details")
    if not runs:
        st.warning("No runs match the current filters.")
        return

    for run in runs[:20]:
        with st.expander(f"{run.provider}:{run.model} — {run_label(run)} — AAS {run.aas:.2f}"):
            _run_metrics_row(run)
            st.json(
                {
                    "run_id": run.run_id,
                    "provider": run.provider,
                    "model": run.model,
                    "metadata": run.metadata,
                }
            )


def _render_category_scores(runs: list[EvaluationRunResult], category: str) -> None:
    st.subheader("Category Scores")
    if not runs:
        st.warning("No runs match the current filters.")
        return

    table = []
    for run in runs[:50]:
        row = {
            "Run": run_label(run),
            "Model": f"{run.provider}:{run.model}",
            "AAS": run.aas,
            "Benchmarks": run.benchmark_count,
            "Execution (s)": run.execution_time,
        }
        row.update(run.category_scores)
        table.append(row)

    st.dataframe(table, use_container_width=True, hide_index=True)

    if category != "All" and runs:
        chart = {run_label(r): r.category_scores.get(category, 0.0) for r in reversed(runs[:20])}
        st.bar_chart(chart)


def _render_failure_analysis(runs: list[EvaluationRunResult], sidebar_category: str) -> None:
    st.subheader("Failure Analysis")
    if not runs:
        st.warning("No runs match the current filters.")
        return

    run = runs[0]
    traces = get_run_traces(run)
    if not traces:
        st.info("No per-benchmark traces found for this run.")
        return

    if not run_has_text_traces(run):
        st.warning(
            "This run only has legacy score data (no question/answer text). "
            "Re-run evaluation to capture full traces."
        )

    categories = ["All"] + sorted({trace.category for trace in traces if trace.category})
    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox("Trace category", categories, index=0)
    with col2:
        limit = st.number_input("Show lowest N", min_value=1, max_value=50, value=10)

    effective_category = sidebar_category if sidebar_category != "All" else category
    if sidebar_category != "All":
        st.caption(f"Sidebar category filter applied: **{sidebar_category}**")

    worst = lowest_scoring_traces(traces, limit=int(limit), category=effective_category)
    st.caption(
        f"Run: {run_label(run)} · Model: {run.provider}:{run.model} · "
        f"Showing {len(worst)} lowest-scoring benchmarks"
    )

    for idx, trace in enumerate(worst, start=1):
        title = (
            f"#{idx} — {trace.benchmark_id} ({trace.category}) · "
            f"avg {trace.average_score:.2f} / 5.00"
        )
        with st.expander(title):
            score_cols = st.columns(3)
            score_cols[0].metric("Accuracy", f"{trace.accuracy:.2f}")
            score_cols[1].metric("Completeness", f"{trace.completeness:.2f}")
            score_cols[2].metric("Relevance", f"{trace.relevance:.2f}")

            st.markdown("**Question**")
            st.write(trace.question or "— (not stored in legacy runs)")

            st.markdown("**Reference Answer**")
            st.write(trace.reference_answer or "— (not stored in legacy runs)")

            st.markdown("**Model Answer**")
            st.write(trace.model_answer or "— (empty or not stored in legacy runs)")


def _render_knowledge_gap_audit(runs: list[EvaluationRunResult]) -> None:
    st.subheader("Knowledge Gap Audit")
    if not runs:
        st.warning("No runs match the current filters.")
        return

    run = runs[0]
    audit = load_failure_audit(run.run_id)
    if audit is None:
        st.info(
            "No failure audit found for this run. Generate one with:\n\n"
            f"`python evaluation/audit_failure.py --run-id {run.run_id}`"
        )
        return

    st.caption(
        f"Run: {run_label(run)} · Analyzed: {audit.total_failures_analyzed} failures · "
        f"Trace source: `{audit.trace_source}`"
    )

    counts = audit.classification_counts
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Knowledge Gap", counts.get("knowledge_gap", 0))
    c2.metric("Evaluation Gap", counts.get("evaluation_gap", 0))
    c3.metric("Benchmark Gap", counts.get("benchmark_gap", 0))
    c4.metric("AAS", f"{audit.aas:.2f}")

    st.markdown("### Priority Knowledge Sources")
    for source in audit.priority_knowledge_sources[:5]:
        st.markdown(
            f"**{source.rank}. {source.domain}** — "
            f"{source.knowledge_gap_count} knowledge-gap failures "
            f"(weighted score {source.failure_count})"
        )
        st.caption(", ".join(source.recommended_sources))

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### Top Repeated Entities")
        st.dataframe(audit.top_repeated_entities[:10], use_container_width=True, hide_index=True)
    with col_b:
        st.markdown("### Top Missing Concepts")
        st.dataframe(audit.top_missing_concepts[:10], use_container_width=True, hide_index=True)

    st.markdown("### Candidate Saudi Entities")
    st.write(", ".join(audit.candidate_saudi_entities) or "—")

    st.markdown("### Classified Failures")
    category_filter = st.selectbox(
        "Failure category",
        ["All", "Knowledge Gap", "Evaluation Gap", "Benchmark Gap"],
        key="audit_category_filter",
    )
    shown = audit.failures
    if category_filter != "All":
        shown = [item for item in audit.failures if item.failure_label == category_filter]

    for idx, failure in enumerate(shown[:20], start=1):
        with st.expander(
            f"#{idx} {failure.benchmark_id} — {failure.failure_label} · {failure.average_score:.2f}/5"
        ):
            st.write("**Reasons:**", "; ".join(failure.reasons) or "—")
            if failure.missing_entities:
                st.write("**Missing entities:**", ", ".join(failure.missing_entities))
            st.markdown("**Question**")
            st.write(failure.question)
            st.markdown("**Reference Answer**")
            st.write(failure.reference_answer)
            st.markdown("**Model Answer**")
            st.write(failure.model_answer or "— (not captured)")


def _render_scoring_calibration(runs: list[EvaluationRunResult]) -> None:
    st.subheader("Scoring Calibration")
    if not runs:
        st.warning("No runs match the current filters.")
        return

    run = runs[0]
    comparison = load_scoring_comparison(run.run_id)
    if comparison is None:
        st.info(
            "No scoring comparison found. Run an evaluation to generate one:\n\n"
            f"`python evaluation/evaluate.py --model qwen --limit 10 --scoring calibrated`"
        )
        return

    st.caption(
        f"Run: {run_label(run)} · Items compared: {comparison.items_compared} · "
        f"Over-penalized: {comparison.likely_over_penalized_count}"
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Legacy AAS", f"{comparison.old_aas:.2f}")
    c2.metric("Calibrated AAS", f"{comparison.calibrated_aas:.2f}")
    c3.metric("AAS Δ", f"{comparison.aas_delta:+.2f}")

    rows = []
    for category in sorted(comparison.old_category_scores.keys()):
        rows.append(
            {
                "Category": category,
                "Legacy": comparison.old_category_scores.get(category, 0.0),
                "Calibrated": comparison.calibrated_category_scores.get(category, 0.0),
                "Delta": comparison.category_deltas.get(category, 0.0),
            }
        )
    st.markdown("### Category Scores")
    st.dataframe(rows, use_container_width=True, hide_index=True)

    st.markdown("### Top Items With Biggest Positive Delta")
    for idx, item in enumerate(comparison.top_positive_deltas[:10], start=1):
        title = (
            f"#{idx} {item.benchmark_id} ({item.category}) — "
            f"{item.old_average:.2f} → {item.calibrated_average:.2f} (Δ {item.delta:+.2f})"
        )
        with st.expander(title):
            if item.potential_over_penalty:
                st.warning("Likely over-penalized under legacy overlap scoring")
            st.write(item.score_reason or "—")
            if item.matched_concepts:
                st.write("**Matched concepts:**", ", ".join(item.matched_concepts))
            st.markdown("**Question**")
            st.write(item.question)
            st.markdown("**Reference Answer**")
            st.write(item.reference_answer)
            st.markdown("**Model Answer**")
            st.write(item.model_answer[:1200] + ("…" if len(item.model_answer) > 1200 else ""))


def _render_rag_experiments(rag_runs: list[EvaluationRunResult]) -> None:
    st.subheader("RAG Experiments")
    if not rag_runs:
        st.info("No RAG runs found. Run: `python rag/evaluate_rag.py --model qwen --limit 10 --scoring calibrated`")
        return

    run = rag_runs[0]
    comparison = load_rag_comparison(run.run_id)
    st.caption(
        f"Latest RAG run: {run.run_id[:8]}… · Model: {run.provider}:{run.model} · "
        f"Chunks indexed: {run.metadata.get('chunks_indexed', '—')}"
    )

    if comparison:
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("Baseline AAS", f"{comparison.baseline_aas:.2f}")
        c2.metric("RAG AAS", f"{comparison.rag_aas:.2f}")
        c3.metric("AAS Δ", f"{comparison.aas_delta:+.2f}")
        c4.metric("Helped / Hurt", f"{comparison.helped_count} / {comparison.hurt_count}")
        c5.metric("RAG Used / Skipped", f"{comparison.rag_used_count} / {comparison.rag_skipped_count}")
        c6.metric("Avg Δ Used", f"{comparison.average_delta_rag_used:+.2f}")

        rows = []
        for category in sorted(comparison.rag_category_scores.keys()):
            rows.append(
                {
                    "Category": category,
                    "Baseline": comparison.baseline_category_scores.get(category, 0.0),
                    "RAG": comparison.rag_category_scores.get(category, 0.0),
                    "Delta": comparison.category_deltas.get(category, 0.0),
                }
            )
        st.markdown("### Category Comparison")
        st.dataframe(rows, use_container_width=True, hide_index=True)

    st.markdown("### Top Improvements")
    improvements = comparison.top_improvements[:5] if comparison else []
    for item in improvements:
        with st.expander(
            f"{item.benchmark_id} ({item.category}) "
            f"{item.baseline_average:.2f} → {item.rag_average:.2f} (Δ {item.delta:+.2f})"
        ):
            st.write(item.question)
            if item.retrieved_chunks:
                st.markdown("**Retrieved chunks**")
                for idx, chunk in enumerate(item.retrieved_chunks[:3], start=1):
                    st.markdown(f"**Chunk {idx}**")
                    st.write(chunk[:800] + ("…" if len(chunk) > 800 else ""))
            if item.citations:
                st.markdown("**Citations**")
                st.json(item.citations)

    st.markdown("### RAG Run Item Details")
    comparison_map = {item.benchmark_id: item for item in comparison.items} if comparison else {}
    for entry in run.item_scores[:10]:
        comp = comparison_map.get(entry["benchmark_id"])
        delta_label = f" · Δ {comp.delta:+.2f}" if comp else ""
        helped = " · helped" if comp and comp.rag_helped else ""
        hurt = " · hurt" if comp and comp.rag_hurt else ""
        with st.expander(
            f"{entry['benchmark_id']} — avg {_average_item(entry):.2f}{delta_label}{helped}{hurt}"
        ):
            st.write(
                f"**Route:** {entry.get('route', '—')} · "
                f"**RAG used:** {entry.get('rag_used', False)} · "
                f"**Reason:** {entry.get('routing_reason', '—')}"
            )
            if entry.get("detected_entities"):
                st.write("**Entities:**", ", ".join(entry["detected_entities"]))
            if entry.get("target_domains"):
                st.write("**Target domains:**", ", ".join(entry["target_domains"]))
            trace = next((t for t in get_run_traces(run) if t.benchmark_id == entry["benchmark_id"]), None)
            if trace:
                st.write(trace.model_answer[:1200] + ("…" if len(trace.model_answer) > 1200 else ""))
            if entry.get("retrieved_chunks"):
                st.markdown("**Retrieved chunks**")
                for idx, chunk in enumerate(entry["retrieved_chunks"][:3], start=1):
                    st.write(f"Chunk {idx}: {chunk[:600]}…" if len(chunk) > 600 else f"Chunk {idx}: {chunk}")


def _average_item(entry: dict) -> float:
    return (entry["accuracy"] + entry["completeness"] + entry["relevance"]) / 3.0


def _render_regressions(regressions: list) -> None:
    st.subheader("Regression Reports")
    if not regressions:
        st.info("No regression reports found. Run evaluations twice to generate comparisons.")
        return

    for report in regressions:
        with st.expander(f"Regression — run `{report['run_id'][:8]}…`"):
            st.markdown(str(report["content"]))


def _render_raw_json(runs: list[EvaluationRunResult]) -> None:
    st.subheader("Raw Run JSON Viewer")
    if not runs:
        st.warning("No runs available.")
        return

    run_map = {run_label(r): r.run_id for r in runs}
    choice = st.selectbox("Select run", list(run_map.keys()))
    run_id = run_map[choice]
    try:
        payload = load_run_json(run_id)
        st.json(payload)
    except FileNotFoundError as exc:
        st.error(str(exc))


def _run_metrics_row(run: EvaluationRunResult) -> None:
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Model", f"{run.provider}:{run.model}")
    c2.metric("AAS", f"{run.aas:.2f}")
    c3.metric("Benchmarks", run.benchmark_count)
    c4.metric("Time (s)", f"{run.execution_time:.2f}")
    c5.metric("Timestamp", run.timestamp[:19])


if __name__ == "__main__":
    main()
