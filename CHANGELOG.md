# Changelog

All notable changes to KRA are recorded here. Format based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); the project aims to follow
semantic versioning once it leaves the Release Candidate phase.

## [Unreleased] — Release Candidate (RC1), hardening

### Added
- Repository hygiene: `README.md` (users + developers), `CHANGELOG.md`, `CONTRIBUTING.md`,
  `LICENSE` (MIT), `.editorconfig`, `Makefile`.
- Architectural docs: `docs/DECISIONS.md` (why KRA is different) and
  `docs/SECURITY_AND_PRIVACY.md`.
- Observability: `kra stats` — a one-glance dashboard of the knowledge base and runs.

## [0.2.0] — Knowledge that lives and reaches the person

### Added
- **Knowledge Consolidation Engine** (`src/core/consolidation/`): six deterministic
  components + orchestrating engine; models `Controversy`, `KnowledgeDelta`, Topic `version`.
  Design in `docs/knowledge/`.
- **Persistence**: canonical Living Topics in `knowledge/en/`, append-only **Knowledge
  Ledger** (`knowledge/ledger.jsonl`, ids `KD-YYYY-NNNNN`), Spanish `obsidian/` view.
  `kra consolidate-topic`.
- **ResearchRun** (`kra run research`): one command drives the whole pipeline, phased
  (Consolidation → Executive Report → Personal Insight), recorded under `runs/YYYY-MM/`.
- **Executive Report** (`kra report-month`) and **Personal Insight Engine**
  (`kra insights-month`, `src/core/insight/`), with the Patient Profile in `patient/`.
- `docs/RESEARCH_RUN.md`.

## [0.1.0] — Baseline: measured, key-free

### Added
- **Gold Standard v1.0**: 14 human-curated entries across 7 areas (controversy modelled on
  purpose); 3-part dataset (Papers / Reviews / Topics).
- **Benchmark**: providers behind an AI Provider port (`stub`, `fake`, `manual`, `claude`),
  Quality Gates, KPIs **GRSS / CDR / UCR** (decomposed), `kra benchmark`, `kra review-package`.
- **Evidence Classification** (stars / Consensus / Exploratory) so guidelines and scoping
  reviews are not wrongly rejected.
- First measured baseline (`docs/BASELINE_v0.1.md`) with the `manual` provider.

## [0.0.x] — Foundations

### Added
- Design & doctrine: problem statement, specification, domain model, architecture, glossary,
  `ADR-0001` (ten principles), Definition of Done, roadmap.
- Hexagonal `src/` codebase (Pydantic domain, ports, workflow framework), the `kra` CLI, and
  the manual MVP pipeline.
