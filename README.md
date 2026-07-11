# Knee Research Agent (KRA)

**A knowledge platform that turns scientific literature on knee osteoarthritis into
trustworthy, traceable and personalised knowledge — not a chatbot, not a paper summariser.**

KRA continuously reviews the research, validates it, measures how good the validation is,
and only then consolidates it into knowledge you could take to a specialist. The guiding
principle: **knowledge never enters the system directly.** It is reviewed → validated →
measured → consolidated, and only then does it become part of the knowledge base.

> KRA improves *understanding*. It never diagnoses, prescribes or replaces a healthcare
> professional. Decisions are always the human's.

---

## Why it is built this way

Eight golden principles govern the project (see `docs/adr/ADR-0001-project-philosophy.md`).
The ones you feel in every feature:

- **Knowledge is the product.** Papers are inputs; consolidated knowledge is the output.
- **Evidence before opinion.** Every claim links to its support; when the evidence is weak
  or contradictory, the uncertainty is preserved, not flattened.
- **Traceability is mandatory.** Every claim, insight and report traces back to its source.
- **Humans make decisions.** The system curates and explains; the person decides.
- **Knowledge evolves but never loses history.** Conclusions update; the past is snapshotted.

---

## How it works

The pipeline is deliberately staged so nothing unverified reaches the knowledge base:

```
Paper → Review → Quality Gates → Benchmark (vs Gold Standard)
                                      │
                                      ▼   (next phase)
        Validated Review → Knowledge Consolidation → Living Topics / Reports / Insights
```

- **Review** — a provider turns a paper into a structured `PaperReview` (claims + support,
  study type, evidence classification, limitations, controversies).
- **Quality Gates** — enforce traceability and classification before a review can count.
- **Benchmark** — scores the review against a curated **Gold Standard** with three KPIs:
  **GRSS** (similarity to the gold review, decomposed into sub-scores), **CDR** (did it
  detect the controversy?) and **UCR** (unsupported-claim rate). The benchmark is the
  compass: it drives what we improve and which papers we add, not the other way round.

### Providers (swap the model, keep everything else)

The reviewer sits behind an `AIProvider` abstraction, so you can run it with or without an
API key:

| Provider | What it is |
|----------|------------|
| `stub`   | extracts nothing — honest zero baseline |
| `fake`   | deterministic, key-free — exercises the harness |
| `manual` | human-in-the-loop / Claude Code as engine — **no API key** |
| `claude` | the real Anthropic-backed reviewer (needs a key) |

---

## Current status

- **Gold Standard v1.0** — 14 human-curated entries across all 7 clinical areas (PRP, MSC,
  cartilage regeneration, meniscus, early OA, guidelines, exercise), with real controversy
  modelled on purpose (e.g. the RESTORE RCT contradicting the favourable PRP meta-analyses).
- **Sprint 5A complete** — provider layer, Quality Gates, GRSS/CDR/UCR, evidence
  classification.
- **First measured baseline** — see `docs/BASELINE_v0.1.md` (measured with the `manual`
  provider; an optimistic calibration, not a blind evaluation — the caveat is documented).

---

## Repository layout

```
knee-research-agent/
├── CLAUDE.md            operating manual for AI agents (read before working)
├── README.md           this file
├── docs/               design & doctrine (PROBLEM_STATEMENT, SPECIFICATION, DOMAIN_MODEL,
│   │                   ARCHITECTURE, GLOSSARY, ROADMAP, DEFINITION_OF_DONE, BASELINE_v0.1)
│   └── adr/            architectural decisions (ADR-0001 = the ten principles)
├── src/                the codebase (hexagonal architecture) — see src/README.md
│   ├── core/           domain models (Pydantic), ports, knowledge engine
│   ├── application/    use cases, workflows, quality gates
│   ├── infrastructure/ adapters: ai providers, sources, repositories, renderers
│   ├── benchmark/      runner + metrics (GRSS/CDR/UCR)
│   ├── framework/      domain-agnostic workflow engine
│   └── cli/            the `kra` command
├── benchmark/          the Gold Standard dataset (gold_standard/dataset.json)
├── papers/ reviews/    paper registry and produced reviews
├── runs/               run records + manual review packages/answers
├── templates/ agents/ prompts/ workflows/   specs and prompts (English)
└── kra                 CLI entry point
```

Folders like `knowledge/` (Spanish Living Topics), `patient/` (Patient Profile) and
`reports/` are created as later sprints reach them.

---

## Quickstart

```bash
pip install -r requirements.txt

# run the test suites
for t in src/tests/test_*.py; do python3 "$t"; done

# benchmark (key-free)
./kra benchmark --model manual          # score the curated manual reviews vs the gold
./kra review-package                    # emit prompt/schema packages for new papers

# later, with an Anthropic key
export KRA_ANTHROPIC_API_KEY=sk-ant-...
./kra benchmark --model claude
```

---

## Language conventions

Everything technical or agent-facing is **English** (code, prompts, `docs/`). Everything the
patient reads — the consolidated knowledge base and the executive reports — is **Spanish**.

## Documentation map

Start with `docs/PROBLEM_STATEMENT.md` → `SPECIFICATION.md` → `DOMAIN_MODEL.md` →
`ARCHITECTURE.md` → `GLOSSARY.md`, then `adr/ADR-0001-project-philosophy.md`. AI agents must
also read `CLAUDE.md` (the operating contract) before making changes.

## Disclaimer

KRA is a personal research tool. It does not provide medical advice, diagnosis or treatment.
Always consult a qualified healthcare professional.
