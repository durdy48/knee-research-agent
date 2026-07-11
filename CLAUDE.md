# CLAUDE.md — Operating Manual for AI Agents

**Version:** 1.0.0
**Status:** Stable
**Last Updated:** 2026-07-10

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
| Consolidated knowledge (Obsidian / `knowledge/`) | Spanish |
| Executive reports and monthly summaries | Spanish |

Rule of thumb: everything technical or agent-facing is in **English**; everything the
patient reads (knowledge base and reports) is in **Spanish**.

---

## 4. Ubiquitous language

Always use terms exactly as defined in `docs/GLOSSARY.md` (Paper, Claim, Evidence,
Clinical Topic, Knowledge Base, Insight, Finding, Evidence Update, Research Cycle,
Personal Intelligence Layer, etc.).

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
├── docs/
│   ├── PROBLEM_STATEMENT.md
│   ├── SPECIFICATION.md
│   ├── DOMAIN_MODEL.md
│   ├── ARCHITECTURE.md
│   ├── GLOSSARY.md
│   ├── ROADMAP.md
│   └── adr/
│       └── ADR-0001-project-philosophy.md
├── knowledge/            ← consolidated knowledge (Clinical Topics, Spanish)
├── sources/              ← raw source records (papers, trials)
├── reports/              ← monthly executive reports (immutable)
├── patient/              ← Patient Profile, Persona, Personal Goals
├── prompts/              ← agent prompts (English)
├── workflows/            ← research-cycle workflows
└── scripts/              ← automation (added in later sprints)
```

Some of these folders are created progressively across sprints. Do not assume a folder
exists — check first.

---

## 6. How to work with knowledge

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

## 7. Clinical Topic template

When creating or updating a Clinical Topic in `knowledge/`, use this structure
(content in Spanish):

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

## 8. Executive Report / Monthly Review

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

## 9. What an agent must NEVER do

- Never invent citations, data or evidence.
- Never present opinion as if it were evidence.
- Never give medical advice, diagnoses or prescriptions.
- Never bend a scientific conclusion to fit personal preferences.
- Never delete or overwrite historical knowledge without a snapshot.
- Never use a term that is not defined in the glossary.
- Never couple the domain/knowledge layer to a specific tool or vendor.
- Never write code before the design and documentation justify it (respect the sprint
  discipline in `docs/ROADMAP.md`).

---

## 10. Naming conventions

- Domain/design docs: `UPPER_SNAKE_CASE.md` in `docs/` (e.g. `SPECIFICATION.md`).
- ADRs: `docs/adr/ADR-NNNN-short-title.md`, four-digit sequential number.
- Clinical Topics: `knowledge/<canonical-topic-name>.md` (e.g. `PRP.md`).
- Reports: `reports/YYYY-MM.md`.
- Prompts: `prompts/<area>/<name>.md`.

---

## 11. Working rhythm

- **Rule of gold:** we do not write code until an AI agent can understand the project
  by reading the documentation alone.
- Work **outside-in**: validate each piece manually before automating it.
- Follow the sprint plan in `docs/ROADMAP.md`. When in doubt about scope, prefer the
  smallest change that keeps the design coherent, and update the docs alongside it.

---

## References

- `docs/PROBLEM_STATEMENT.md`, `docs/SPECIFICATION.md`, `docs/DOMAIN_MODEL.md`,
  `docs/ARCHITECTURE.md`, `docs/GLOSSARY.md`
- `docs/adr/ADR-0001-project-philosophy.md`
