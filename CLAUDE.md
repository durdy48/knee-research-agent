# CLAUDE.md — Operating Manual for AI Agents

**Version:** 1.1.0
**Status:** Stable
**Last Updated:** 2026-07-11

> This file tells any AI agent (Claude Code and others) **how to work inside the Knee
> Research Agent (KRA) project**. It is not documentation for humans — it is the
> operating contract for agents. Read it fully before doing anything in this
> repository.

---

## 1. What this project is

KRA is a **Knowledge Platform**, not a traditional application and not a chatbot. Its
job is to continuously transform scientific literature about knee osteoarthritis into
**trustworthy, traceable and personalised knowledge** for a specific patient.

Before acting, read the foundational documents in this order:

1. `docs/PROBLEM_STATEMENT.md` — the problem.
2. `docs/SPECIFICATION.md` — what we build and why.
3. `docs/DOMAIN_MODEL.md` — the core entities and knowledge lifecycle.
4. `docs/ARCHITECTURE.md` — responsibilities, layers and boundaries.
5. `docs/GLOSSARY.md` — the official language of the project.
6. `docs/adr/ADR-0001-project-philosophy.md` — the ten principles that must never be
   broken.
7. `docs/DEFINITION_OF_DONE.md` — when a workflow is actually finished.
8. `docs/ROADMAP.md` — the current phase and what comes next.

For the codebase specifically, also read `src/README.md` and the current measured state
in `docs/BASELINE_v0.1.md`.

If anything in this manual conflicts with `ADR-0001`, **ADR-0001 wins**.

---

## 2. Golden rules — never break these

Derived directly from `ADR-0001`:

1. **Knowledge is the product.** Papers are inputs; consolidated knowledge is the
   output. Do not just collect or summarise papers.
2. **Evidence before opinion.** Every conclusion must be supported by evidence. Never
   state unsupported medical conclusions. When evidence is weak or contradictory,
   preserve the uncertainty explicitly.
3. **Personalisation never changes scientific truth.** Personal context changes only
   *relevance* (what is highlighted), never the scientific conclusion.
4. **Traceability is mandatory.** Every claim, insight and report must link back to its
   supporting evidence and original sources.
5. **Humans make decisions.** Never diagnose, never prescribe, never replace a
   healthcare professional. The role is to improve understanding.
6. **No component owns the knowledge.** Claude, Obsidian, GitHub, MCP servers and data
   sources are replaceable components. The domain model is authoritative.
7. **Knowledge evolves but never loses history.** Update conclusions; never erase past
   ones without preserving a historical snapshot.
8. **Documentation is part of the product.** Update the relevant docs in the same
   change. A task is not complete if its documentation is outdated.

---

## 3. Language conventions

| Layer | Language |
|-------|----------|
| Code | English |
| Prompts | English |
| Documentation (`docs/`) | English |
| Literature queries (PubMed, etc.) | English |
| Canonical consolidated knowledge (`knowledge/en/`) | English |
| Patient-facing view (`obsidian/`) and executive reports | Spanish |

Rule of thumb: everything technical or agent-facing is in **English** — including the
**canonical** knowledge base in `knowledge/en/` (the source of truth). The patient-facing
Spanish lives in the `obsidian/` view and the reports, which are *rendered from* the
canonical knowledge, never the source of truth.

---

## 4. Ubiquitous language

Always use terms exactly as defined in `docs/GLOSSARY.md` (Paper, Claim, Evidence,
Clinical Topic, Knowledge Base, Insight, Finding, Evidence Update, Research Cycle,
Personal Intelligence Layer, etc.). The glossary also defines the benchmark vocabulary
(Gold Standard, AI Provider, Quality Gate, Evidence Classification, GRSS, CDR, UCR) — use
those terms exactly too.

If you need a term that is not in the glossary:

1. Check whether a standard term already exists in software engineering, knowledge
   management or medicine — if so, reuse it.
2. Only coin a new term when it genuinely adds clarity.
3. Add it to `docs/GLOSSARY.md` **first**, then use it elsewhere.

Do not introduce vocabulary that is not in the glossary.

---

## 5. Repository structure

```
knee-research-agent/
├── CLAUDE.md              ← this file (agent manual)
├── README.md             ← human overview (project entry point)
├── requirements.txt
├── kra                   ← CLI entry point (./kra <command>)
├── docs/
│   ├── PROBLEM_STATEMENT.md  SPECIFICATION.md  DOMAIN_MODEL.md  ARCHITECTURE.md
│   ├── GLOSSARY.md  ROADMAP.md  DEFINITION_OF_DONE.md  BASELINE_v0.1.md
│   └── adr/ADR-0001-project-philosophy.md
├── src/                  ← the codebase (hexagonal architecture; see §6 and src/README.md)
│   ├── core/             domain models (Pydantic), ports, storage, knowledge engine
│   ├── application/      use cases, workflows, quality_gates
│   ├── infrastructure/   adapters: ai/ (providers), sources/, repositories/, renderers/
│   ├── framework/        domain-agnostic workflow engine (steps, runner, events)
│   ├── benchmark/        runner + metrics (GRSS/CDR/UCR) + Gold Standard loader
│   ├── config/           typed settings
│   ├── cli/              the `kra` command
│   └── tests/            test suites (run each directly)
├── benchmark/            ← Gold Standard dataset (gold_standard/dataset.json, human-curated)
├── papers/               ← Paper Registry (registry.json)
├── reviews/              ← produced Paper Reviews (+ claims)
├── runs/                 ← run records; runs/manual/ holds manual review packages & answers
├── knowledge/            ← consolidated knowledge: en/topics/<id>/ (canonical, English) + ledger.jsonl
├── obsidian/             ← Spanish, human-facing view of the knowledge base (a view, not the source)
├── templates/            ← Living Topic / Report / Review / Insight templates
├── agents/               ← agent role specs and workflow coordinations (English)
├── prompts/              ← agent prompts (English)
└── workflows/            ← research-cycle workflow descriptions
```

Folders created only when later sprints reach them: `patient/` (Patient Profile, Persona,
Personal Goals), `reports/` (monthly executive reports), `scripts/` (automation). Do not
assume a folder exists — check first.

---

## 6. Codebase & architecture

The code in `src/` follows a **hexagonal / clean architecture**. The boundaries are not
optional:

- **`core/`** — the domain: Pydantic models, ports (abstract interfaces), storage paths,
  the knowledge-evolution engine. **The core never imports `infrastructure`.**
- **`application/`** — use cases, workflow coordinations and the **Quality Gates**.
- **`infrastructure/`** — adapters that implement the core's ports: `ai/` (the AI
  providers), `sources/` (abstract/literature input), `repositories/`, `renderers/`.
- **`framework/`** — a domain-agnostic workflow engine (steps, runner, events, metrics).
- **`benchmark/`**, **`config/`**, **`cli/`** — measurement, typed settings, entry point.

Hard rules for the codebase:

- **Pydantic v2 models are the source of truth.** Markdown, JSON and Obsidian notes are
  *views* rendered from objects — never the other way round.
- **All LLM/model code lives only in `infrastructure/ai/`,** behind the `AIReviewer`
  (AI Provider) port. The core stays ignorant of any specific model or SDK. To add a
  model, add a provider — do not thread a vendor through the core.
- **No vendor coupling in the domain** (Golden Rule 6).

---

## 7. How to run and verify

- **Tests** — every suite is a standalone script: `python3 src/tests/<name>.py`. They must
  all stay green; a change that breaks a suite is not done. Set `KRA_ROOT` to point tests
  at a specific repo root when needed.
- **CLI** — `./kra <command>`: `ingest`, `review`, `consolidate`, `report`, `insight`,
  `list`, `run paper`, `benchmark`, `review-package`.
- **Definition of Done** — a workflow is only finished when it satisfies
  `docs/DEFINITION_OF_DONE.md`. Include a verification step (tests, a benchmark run, or a
  fact-check) in every non-trivial change.
- **Dependencies** — `requirements.txt`; in a sandbox use `pip install ... --break-system-packages`.
- Per Golden Rule 8, update the affected docs (and this file when structure or workflow
  changes) in the **same** change.

---

## 8. Benchmark discipline

The benchmark is the project's compass. It answers, objectively, whether a change makes the
knowledge **better or worse**.

- **Gold Standard** (`benchmark/gold_standard/dataset.json`) — real, verifiable papers with
  human-curated gold reviews and topics. **Never fabricate** a paper or a finding; curation
  is a human decision (Golden Rule 5). Entries are `proposed` until a human approves them to
  `curated`.
- **Providers** sit behind the AI Provider abstraction: `stub` (extracts nothing),
  `fake` (key-free harness), `manual` (human-in-the-loop / Claude Code as engine, no key),
  `claude` (real, needs an API key). Compare with `./kra benchmark --model <provider>`.
- **Quality Gates** run before scoring: a review must be traceable (every claim carries its
  supporting data) and classified (Evidence Level *or* Evidence Classification — guidelines
  and scoping reviews use a category, not the 1–5 scale).
- **KPIs**, reported separately: **GRSS** (Gold Review Similarity Score, decomposed into
  sub-scores so you see *where* it fails), **CDR** (Controversy Detection Rate — the
  differentiator: does the reviewer preserve uncertainty?), **UCR** (Unsupported Claim
  Rate — lower is better).

The operating discipline: **knowledge never enters the system directly** — it is reviewed →
validated (gates) → measured (benchmark) → consolidated. And **the benchmark drives the
corpus, not the other way round**: expand the Gold Standard only when the metrics reveal a
gap.

---

## 9. How to work with knowledge

- A **Clinical Topic** is a *Living Document*: never re-create it, only update it.
- When a new paper arrives: extract **Claims** → evaluate them into **Evidence** →
  apply an **Evidence Update** to the relevant Clinical Topic. Never create a duplicate
  note for the same topic.
- Keep the three levels distinct and never mix them:
  - **Data** — a raw fact from one study.
  - **Knowledge** — a conclusion consolidated across studies.
  - **Insight** — a personalised interpretation for the patient.
- Preserve history (**Knowledge Integrity**): when consensus changes, record the change
  and keep an **Evidence Snapshot**; do not silently overwrite the past.

---

## 10. Clinical Topic template

The canonical Living Topic lives in `knowledge/en/topics/<id>/` (English, source of truth);
the Spanish `obsidian/` view is rendered from it. The patient-facing view uses this
structure (Spanish):

- **Resumen** — one-paragraph current state.
- **Nivel de evidencia** — star rating per the Evidence Quality Scale.
- **Consenso** — the prevailing position today.
- **Controversias** — where evidence disagrees.
- **Ensayos** — relevant clinical trials.
- **Papers** — supporting publications (with links).
- **Preguntas abiertas** — unresolved questions being tracked.
- **Cambios recientes** — what changed since the last Research Cycle.
- **Relevancia personal** — why (and how much) this matters for the patient.

---

## 11. Executive Report / Monthly Review

Reports live in `reports/` as immutable, dated files (`reports/YYYY-MM.md`, Spanish).
Each report answers, for the patient:

- What meaningful advances appeared?
- Which treatments look most promising?
- Which new clinical trials are recruiting?
- Has the evidence changed since last month?
- What is worth monitoring?
- Which questions to raise with the specialist?

Always separate **fact** (Data/Knowledge) from **personal interpretation** (Insight).

---

## 12. What an agent must NEVER do

- Never invent citations, data or evidence.
- Never present opinion as if it were evidence.
- Never give medical advice, diagnoses or prescriptions.
- Never bend a scientific conclusion to fit personal preferences.
- Never delete or overwrite historical knowledge without a snapshot.
- Never use a term that is not defined in the glossary.
- Never couple the domain/knowledge layer to a specific tool or vendor (keep all model
  code in `infrastructure/ai/`).
- Never leave the test suites red or the documentation stale after a change.

---

## 13. Naming conventions

- Domain/design docs: `UPPER_SNAKE_CASE.md` in `docs/` (e.g. `SPECIFICATION.md`).
- ADRs: `docs/adr/ADR-NNNN-short-title.md`, four-digit sequential number.
- Clinical Topics: `knowledge/<canonical-topic-name>.md` (e.g. `PRP.md`).
- Reports: `reports/YYYY-MM.md`.
- Prompts: `prompts/<area>/<name>.md`.
- Gold entries: `GOLD-<AREA>-NNN`; test suites: `src/tests/test_<area>.py`.

---

## 14. Working rhythm

- **Origin principle (now satisfied):** we did not write code until an AI agent could
  understand the project by reading the documentation alone. The design justified the code,
  and `src/` implements it. We are now in an **implementation phase** — keep the discipline
  that got us here.
- Work **outside-in**: validate each piece manually before automating it.
- Prefer the **smallest change** that keeps the design coherent, and update the docs
  alongside it (Golden Rule 8).
- Keep every test suite **green** and respect the **Definition of Done**.
- Let the **benchmark — not intuition — drive** what to build and which papers to add.
- Follow the sprint plan in `docs/ROADMAP.md`.

---

## References

- `docs/PROBLEM_STATEMENT.md`, `docs/SPECIFICATION.md`, `docs/DOMAIN_MODEL.md`,
  `docs/ARCHITECTURE.md`, `docs/GLOSSARY.md`
- `docs/adr/ADR-0001-project-philosophy.md`, `docs/DEFINITION_OF_DONE.md`,
  `docs/ROADMAP.md`, `docs/BASELINE_v0.1.md`
- `src/README.md` (codebase layout and usage)
