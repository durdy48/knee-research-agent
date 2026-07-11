# src/ — Knee Research Agent MVP

The first executable of the project. It reproduces the manual pipeline validated in
`runs/RUN-2026-07-001` as a small, working CLI.

## Layout

```
src/
├── core/
│   ├── models/      domain models + stable id helpers
│   ├── storage/     paths, Paper Registry, run logging
│   ├── knowledge/   Living Clinical Topic versioning (current + history)
│   └── pipeline/    the pipeline stages
├── agents/          role registry (maps roles -> stages)
├── workflows/       workflow coordinations (e.g. paper ingestion)
├── cli/             the `kra` command line
└── tests/
```

## Usage

From the repo root:

```bash
./kra ingest --title "PRP vs HA RCT" --doi 10.xxxx/yyyy --year 2025 --study-type RCT --topic TOPIC-PRP
./kra review PAPER-2026-0002
./kra consolidate TOPIC-PRP
./kra report TOPIC-PRP
./kra insight TOPIC-PRP
./kra list
```

(Equivalent: `python3 src/cli/main.py <command> ...`.)

### Vertical slice: `kra run paper`

The first complete flow through every layer (models → use case → workflow → repositories
→ adapters → CLI):

```bash
./kra run paper --doi 10.xxxx/yyyy --title "PRP vs HA RCT" --year 2025 --topic TOPIC-PRP
```

It creates the `Paper`, runs the `Paper Reviewer` (via the `AIReviewer` port — currently
the `StubAIReviewer`, which fabricates nothing), generates the `PaperReview`, extracts
`Claims`, saves the artifacts (`reviews/paper-reviews/…md` + `…claims.json`), links them
in the registry and prints a step-by-step summary. Replacing the stub with a real
`ClaudeAIReviewer` (Sprint 3B) fills the review with real content — no other layer changes.

## Scope of the MVP

This wires the pipeline: registry, state transitions, stable ids, topic versioning
(with Evidence Snapshots and evolution events) and run logging. The **intelligence** of
each stage — actually reviewing a paper, extracting claims, synthesising a topic — is
the job of the corresponding role in `agents/roles/` and is left as a template scaffold
for a role (AI or human) to fill. Nothing invents medical data.

## Tests

```bash
python3 src/tests/test_pipeline.py
```

Tests run against an isolated temporary root via the `KRA_ROOT` environment variable, so
they never touch the real knowledge base.
