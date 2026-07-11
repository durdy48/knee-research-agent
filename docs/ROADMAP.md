# ROADMAP — Knee Research Agent (KRA)

**Version:** 1.1.0
**Status:** Living
**Last Updated:** 2026-07-11

> How the project advances, sprint by sprint. The guiding rule of this phase: **the
> benchmark drives the evolution of the corpus, not the other way around.** We grow the
> Gold Standard only when the metrics reveal a gap.

---

## Guiding principle for the current phase

Until now the goal was an impeccable architecture. From here on, the goal is to
demonstrate that the architecture produces **reliable, traceable and useful knowledge**.
The open question that matters now is:

> *Can an LLM produce reviews that approach the Gold Standard?*

Until that is answered, expanding the corpus has decreasing returns. So we measure first,
then let the data decide what to build and which papers to add.

---

## Done (foundation)

- **Design & doctrine** — `PROBLEM_STATEMENT`, `SPECIFICATION`, `DOMAIN_MODEL`,
  `ARCHITECTURE`, `GLOSSARY`, and `ADR-0001` (ten golden principles). `CLAUDE.md` agent
  manual and `DEFINITION_OF_DONE`.
- **Roles & templates** — 10 agent role specs and 3 workflow coordinations; Living Topic,
  Executive Report, Paper Review (data contract) and Insight templates.
- **Domain core (Pydantic)** — models, ports, in-memory repositories, domain events, the
  knowledge-evolution engine (confidence moves, history preserved).
- **Workflow framework** — domain-agnostic steps/runner/events/metrics + Definition of
  Done, with the `paper_ingestion` vertical slice.
- **Benchmark + Gold Standard v1.0** — 3-part dataset (Gold Papers / Reviews / Topics),
  14 curated entries across all 7 clinical areas, controversy modelled on purpose
  (PRP/MSC/cartilage/early-OA). Runner + metrics + `kra benchmark`.

---

## Sprint 5A — First real measurement *(in progress)*

The single controlled integration point:

```
Paper -> ClaudeAIReviewer -> PaperReview -> Quality Gates -> Benchmark -> vs Gold Review
```

- [x] **AIProvider layer** — `stub` / `fake` / `claude` providers behind the `AIReviewer`
  port, so models are comparable without touching the rest of the system.
- [x] **ClaudeAIReviewer** — real adapter with a strict extraction prompt (never invent,
  every claim grounded, preserve controversy). Fails clearly without an API key.
- [x] **Quality Gates** — enforce traceability, study type and evidence level before a
  review counts.
- [x] **KPIs** — GRSS (headline), CDR (controversy detection) and UCR (unsupported
  claims), reported separately. Wired into `kra benchmark`.
- [x] **Green with stub/fake** — full harness tested without a key.
- [x] **Abstract enrichment** — the reviewer reads real source text when available:
  `Paper.abstract` + `LocalAbstractSource` (drop real abstracts in `sources/abstracts/`).
  Never fabricated; missing abstracts fall back to metadata with a caution flag.
- [x] **ManualAIProvider (no API key)** — human-in-the-loop / Claude Code as engine.
  `kra review-package` emits `prompt.md` + `schema.json` + `metadata.json` per paper; the
  engine fills `runs/manual/reviews/<gold_id>.json` (or a combined `reviews.json`); KRA
  ingests, gates and scores it. Same JSON contract as the API adapter, so `claude` can
  replace `manual` later with no other change.
- [x] **First real measurement (manual)** — `kra benchmark --model manual` over the 14
  curated papers. *Caveat: this first run is optimistic — the same intelligence curated
  the Gold Standard and produced the reviews, so it calibrates the loop rather than blindly
  testing a model. A blind eval needs a separate reviewer or held-out gold.*
- [x] **Evidence Classification fix** — separate Evidence Level (1–5) from Evidence
  Classification (stars / Consensus / Exploratory); Quality Gates now accept guidelines,
  consensus and scoping reviews. Gate pass-rate 78.6% → 100%.
- [x] **GRSS decomposed** — per-component sub-scores (claims, grounding, controversies,
  metadata, evidence, limitations, clinical relevance) to show *where* a reviewer fails.
- [x] **Baseline frozen** — `docs/BASELINE_v0.1.md` records dataset/gold/prompt/workflow/
  provider/metrics + the caveat (tag `baseline-v0.1` on the user's machine).
- [ ] **Blind Review experiment** — 3 papers outside the Gold Standard, reviewed by a
  reviewer that has not seen the gold; compare vs a manual review. First unbiased signal.
- [ ] **Blind / API run** — plug an Anthropic key (`kra benchmark --model claude`) or a
  local model (Ollama) to measure a reviewer that did not see the gold.
- [ ] **Iterative prompt tuning** — adjust the reviewer prompt against the metrics.

**Checkpoint:** once the first real benchmark runs (even with 10–15 papers), **freeze
development and analyse the results** before building more. Let the metrics point the way.

---

## Sprint 5B — Knowledge production (design first)

Design the "intellectual heart" before writing its code — same rigour as `SPECIFICATION.md`.

- [x] **Design docs** in `docs/knowledge/`: `KNOWLEDGE_CONSOLIDATION.md` (the rulebook),
  `CONFIDENCE_MODEL.md`, `CONTROVERSY_MODEL.md`, `KNOWLEDGE_DELTAS.md` (+ the Knowledge
  Ledger concept). Glossary updated with the new terms.
- [x] **Knowledge Consolidation Engine** (`src/core/consolidation/`): six deterministic
  components (Evidence Merger, Consensus Builder, Controversy Manager, Confidence
  Calculator, Delta Generator, Event Log) + orchestrating engine. New domain models:
  `Controversy`, `KnowledgeDelta`, Topic `version`. Behaviour tests + a generic run over
  TOPIC-PRP and TOPIC-MSC (same engine, different topics).
- [x] **Engine review passed** — determinism, idempotency (reprocessing a paper is a
  no-op; a new version only appears on real change), explainability (each Delta names the
  CONFIDENCE_MODEL rule + triggering evidence + before/after) and Living-Topic integrity
  (never duplicated, never overwritten without history, always emits a Delta). End-to-end
  test added: Paper → Review → Quality Gates → Consolidation → Delta → Topic.
- [x] **Persistence (review passed), in order:**
  1. `kra consolidate-topic <area>` command.
  2. Living Topic persisted to `knowledge/en/topics/<id>/` (canonical: `current.json` +
     `current.md`, with `history/` Evidence Snapshots).
  3. Append-only **Knowledge Ledger** at `knowledge/ledger.jsonl` (ids `KD-YYYY-NNNNN`,
     each entry naming the rule, evidence and confidence move).
  4. Spanish `obsidian/<id>.md` view (rendered from the canonical topic — not the source).
  Verified end to end: TOPIC-PRP (v5, 4 deltas, controversy preserved) and TOPIC-MSC (v3),
  idempotent on re-run.

## Sprint 6 — ResearchRun (one command, the whole pipeline)

Design first (`docs/RESEARCH_RUN.md`), then automate by phases.

- [x] **`docs/RESEARCH_RUN.md`** — what a run is, artifacts, states, failure handling, resume.
- [x] **Phase 1** — `kra run research`: drives Review → Quality Gates → Knowledge
  Consolidation across areas, recording `runs/YYYY-MM/RUN-NNNN/` (manifest, metrics, logs,
  outputs). Deterministic, idempotent, resumable. First real run consolidated all 7 areas.
- [x] **Phase 2** — **Executive Report**: `kra report-month` (and run Phase 2) generates a
  reproducible Spanish `reports/YYYY-MM.md` from the Ledger, with five sections (resumen,
  cambios por tema, controversias abiertas, preguntas de investigación, métricas). First
  report covers all 7 topics, 14 deltas and 4 open controversies.
- [x] **Phase 3** — **Personal Insight Engine** (`src/core/insight/`): connects consolidated
  knowledge to the `patient/` profile. Relevance = Clinical Match + Goal Match + Evidence
  Strength + Novelty; a fixed "¿Ha cambiado algo para mí?" indicator (🟢/🟡/🔴); prudent,
  non-prescriptive actions; a "Confidence for You" placeholder. `kra insights-month` and
  run Phase 3 write `reports/YYYY-MM-insights.md` (Spanish). Never changes the science
  (Rule 3), never prescribes (Rule 5).
- [ ] **Phase 4** — Obsidian sync as a discrete stage (today produced inline by consolidation).

## Sprint 7 — Proactivity

- Alerts on relevant change (new evidence → consensus change → High Priority for the user).

## Sprint 8 — Real sources & scheduling

- Real integration with TomeSphere / PubMed / ClinicalTrials.gov; automatic discovery of new
  evidence; periodic scheduling (cron / GitHub Actions).

## Sprint 9 — Scale & compare, only if the metrics ask for it

- Expand the Gold Standard to **30–40 papers** *if the benchmark shows a gap*.
- **Model comparison** across providers (Claude / GPT / Gemini / local); cost/time optimisation.

---

## Release Candidate (RC1) — Hardening & real use *(current phase)*

The system is functionally complete for a first version. The priority now is **not more
features** but answering: *would you trust it to run automatically every month for two
years?* Four blocks:

- [x] **1. Repository hygiene** — `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`,
  `.editorconfig`, `Makefile`, `.gitignore`. (Optional: `pre-commit` with black/ruff/mypy.)
- [x] **2. Observability** — `kra stats`: a one-glance dashboard of the knowledge base and runs.
- [x] **3. Architectural docs** — `docs/DECISIONS.md` (why KRA is different) and
  `docs/SECURITY_AND_PRIVACY.md`.
- [~] **4. Real validation** — *the most important step*. For 2–3 months, do **not** touch
  the architecture. Run KRA monthly as a user and note: did the report help? was there noise?
  did it catch anything genuinely interesting? were the priorities right? what did I ignore?
  Those observations are worth more than a dozen new features.
  - **Automated monthly run set up** (2026-07): a scheduled task `kra-monthly-run` runs
    `kra run research` on day 1 of each month (08:00) and delivers the Executive Report +
    Personal Insight as a monthly check-in. Each run counts toward the **6 monthly runs**
    that gate KRA v2. Caveat: until a real literature source or an API key is connected, the
    run is idempotent ("no changes") — a valid, honest signal; the habit and mechanism are
    the point for now.
- [x] **LICENSE** — MIT (permissive; the author, as sole copyright holder, can relicense
  later). A medical-disclaimer note is appended.

## Declaring v1.0 — a symbolic snapshot (when validation is done)

When KRA is declared **v1.0** (after the 2–3 month validation phase), freeze a full,
immutable copy of the project as a photograph of the knowledge and the system at that moment:

```
archive/KRA-v1.0/   ← docs, benchmark, Gold Standard, architecture, example reports, metrics
```

It will be fascinating to compare it with KRA v2/v3 years from now. Symbolic, not urgent —
do it the day you decide the validation phase is complete.

## Strategic direction — KRA v2 (later, after real use)

Kept as project memory; **do not build yet**:

- **Automatic evidence discovery** — robust integration with PubMed, ClinicalTrials.gov,
  Semantic Scholar (and TomeSphere if it adds value) + scheduled alerts, so `kra monthly`
  runs unattended and removes the manual step.
- **Evidence Timeline** — open a topic and see how its consensus evolved over years (e.g.
  PRP 2018→2026 with RESTORE marked), to answer *"how has the scientific consensus changed
  over the last ten years?"*. Needs real data over months.
- **A technical article** — *"Building a Deterministic Knowledge Evolution Engine for Living
  Medical Evidence"* — the architecture (Knowledge Deltas, Living Topics, evidence↔
  personalisation separation, auditable ledger) is interesting in its own right.

---

## How to run the current benchmark

```bash
# key-free baselines (no extraction / structural-only)
./kra benchmark --model stub
./kra benchmark --model fake

# manual mode — Claude Code (or web) as the engine, no API key
./kra review-package                 # emit prompt/schema packages per curated paper
#   fill runs/manual/reviews/<gold_id>.json (or a combined reviews.json)
./kra benchmark --model manual       # score the manual reviews vs the Gold Standard

# later: blind run with an API key (swap the provider, nothing else changes)
export KRA_ANTHROPIC_API_KEY=sk-ant-...
pip install anthropic
./kra benchmark --model claude
```
