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

## Sprint 5B — Knowledge production

- Automatic **Topic Update** (apply an Evidence Update to a Living Clinical Topic).
- **Knowledge consolidation** across papers into Living Clinical Topics (`knowledge/`).
- **Controversy detection** feeding the topic's consensus/uncertainty.
- **Knowledge Diff** generation between topic versions.

## Sprint 5C — Delivery & persistence

- **Executive Report** generation (`reports/YYYY-MM.md`, Spanish).
- **Personal Insight** generation (needs the Patient Profile in `patient/`).
- **Obsidian** renderer for the knowledge vault.
- **Git** persistence of the knowledge base.

## Sprint 6 — Scale, only if the metrics ask for it

- Expand the Gold Standard to **30–40 papers** *if the benchmark shows a gap*.
- **Model comparison** across providers (Claude / GPT / Gemini / local).
- **Cost and time** optimisation.

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
