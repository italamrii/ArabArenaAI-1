# Contributing to ArabArenaAI-1

Thank you for your interest in contributing to ArabArenaAI-1. This project follows a **Saudi-first, Arabic-first** mission. Contributions should strengthen regional AI capability — not generic chatbot features disconnected from Gulf context.

---

## Before You Start

1. Read [README.md](README.md) for vision and priorities
2. Read [ROADMAP.md](ROADMAP.md) to understand the current phase
3. Review relevant strategy docs in `docs/`
4. Check existing issues before opening a duplicate

**Current phase:** Phase 1 — Project Foundation. Training code and model weights are out of scope until later phases unless explicitly requested by maintainers.

---

## How to Contribute

### Documentation

- Fix typos, clarify strategy, improve Arabic terminology consistency
- Add citations and sources for Saudi/GCC factual claims
- Translate or bilingualize docs where it improves accessibility (keep English as primary for now unless agreed otherwise)

### Data (Phase 2+)

- Propose datasets with **license**, **provenance**, and **Saudi/GCC relevance** metadata
- Never commit raw datasets to git — use manifests and external storage
- Follow [docs/DATA_STRATEGY.md](docs/DATA_STRATEGY.md)

### Evaluation (Phase 4+)

- Propose benchmark items with gold answers and scoring rubrics
- Flag bias or cultural inaccuracy in existing benchmark drafts
- Follow [docs/BENCHMARKS.md](docs/BENCHMARKS.md)

### Code (when enabled in later phases)

- Match existing style; keep changes focused
- Add tests for non-trivial logic under `tests/`
- Do not commit secrets, API keys, or model weights

---

## Pull Request Process

1. Fork the repository (or branch from `main` if you have write access)
2. Create a descriptive branch: `docs/data-strategy-update`, `eval/saudi-knowledge-items`, etc.
3. Fill out the [pull request template](.github/PULL_REQUEST_TEMPLATE.md) completely
4. Ensure CI passes (when configured)
5. Request review from a code owner (when assigned)

Maintainers may ask for changes related to license compliance, factual accuracy, or alignment with project priorities.

---

## Issue Guidelines

Use the [issue template](.github/ISSUE_TEMPLATE.md) and include:

- **Phase** alignment (which roadmap phase does this support?)
- **Priority domain** (Saudi / GCC / Arabic / Business / Engineering / Global)
- **Repro steps** for bugs; **acceptance criteria** for features

---

## Code of Conduct

- Be respectful and professional
- No harassment, discrimination, or sharing of non-public partner data
- Disclose conflicts of interest when proposing datasets or vendor integrations

A formal Code of Conduct document will be added before public release (Phase 8).

---

## Security

Do **not** open public issues for security vulnerabilities. Contact maintainers through the security disclosure channel (to be published before Phase 7).

---

## Licensing

By contributing, you agree that your contributions will be licensed under the same terms as the project ([LICENSE](LICENSE)), unless otherwise agreed in writing for data or model artifacts with separate licenses.

---

## Questions

Open a GitHub issue with the `question` label, or contact project maintainers (contact details to be added before public release).
