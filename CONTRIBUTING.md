# Contributing to KRA

KRA is a knowledge platform, not a typical app. Before changing anything, read
`CLAUDE.md` (the operating contract) and `docs/adr/ADR-0001-project-philosophy.md`
(the ten principles). If a change conflicts with ADR-0001, ADR-0001 wins.

## Golden rules (non-negotiable)

- **Never fabricate** citations, data or evidence.
- **Evidence before opinion**; preserve uncertainty explicitly.
- **Personalisation never changes the science** (relevance only).
- **Traceability is mandatory**; every change is a justified, immutable Knowledge Delta.
- **Humans make decisions**; KRA never diagnoses or prescribes.
- **No vendor coupling in the domain**: all model code stays in `infrastructure/ai/`.
- **Documentation is part of the product**: update the relevant docs in the same change.

## Architecture boundaries

- `core/` is pure domain (Pydantic models, ports, the consolidation/insight engines). **It
  never imports `infrastructure`.**
- `application/` holds use cases, the Quality Gates and the ResearchRun orchestration.
- `infrastructure/` holds adapters (AI providers, sources, repositories, renderers).
- Pydantic objects are the source of truth; Markdown/JSON/Obsidian are views rendered from them.

## Adding things

- **A new model provider** → add a class in `infrastructure/ai/` implementing the
  `AIReviewer` port and register it in `src/benchmark/models.py`. Do not thread a vendor
  through the core.
- **A new gold entry** → it must be a real, verifiable paper (DOI/PMID). Add it as
  `proposed`; a human promotes it to `curated` (curation is a human decision).
- **A new workflow / phase** → orchestrate in `application/`; keep the domain logic pure and
  deterministic in `core/`.
- **A new term** → add it to `docs/GLOSSARY.md` first, then use it.

## Running and verifying

```bash
pip install -r requirements.txt
make test          # or: for t in src/tests/test_*.py; do python3 "$t"; done
make benchmark     # ./kra benchmark --model manual
```

- Every test suite is a standalone script under `src/tests/`; they must all stay green.
- A change is not done until its tests pass and its documentation is updated
  (see `docs/DEFINITION_OF_DONE.md`).
- Style: keep functions small and named after intent; prefer the smallest change that keeps
  the design coherent. If you use `black` / `ruff` / `mypy`, run them before committing.
