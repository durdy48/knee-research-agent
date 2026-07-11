# RESEARCH_RUN — one command, the whole pipeline

**Version:** 0.1 (design; Phase 1 implemented)
**Status:** Living
**Last Updated:** 2026-07-11

> A **Research Run** is one complete, recorded execution of the KRA pipeline over a set of
> clinical areas. It turns KRA from a set of well-designed components into a system that
> works end to end with a single order (`kra run research`). This document defines what a
> run is, what it produces, what states it can be in, what happens when a stage fails, and
> how to resume one — designed before the automation is fixed in code.

---

## What a Research Run is

A run takes a set of **areas** (e.g. PRP, MSC, …), and for each one drives the pipeline:

```
Paper Discovery → Review (Package) → Quality Gates → Knowledge Consolidation
                                                    → Executive Report        (Phase 2)
                                                    → Personal Insights       (Phase 3)
                                                    → Obsidian Sync           (Phase 4)
```

It is **deterministic and idempotent**: a run over evidence that has not changed produces no
new Knowledge Deltas (a no-op), so re-running is always safe and comparable. Every run is
**recorded**, so a year from now you can re-run the same set and compare results.

Phases are automated one at a time (do not do it all at once):

- **Phase 1 (implemented):** Review → Quality Gates → Knowledge Consolidation, persisting the
  Living Topic (`knowledge/en/`), the Knowledge Ledger and the Spanish Obsidian view.
- **Phase 2:** append the run's changes to the monthly Executive Report (a view over the
  Ledger for the period).
- **Phase 3:** generate Personal Insights ("what changed this month that is relevant to my
  case?") — never modifying the evidence (Golden Rule 3).
- **Phase 4:** Obsidian sync as a discrete stage (currently produced inline by consolidation).

---

## Artifacts a run produces

```
runs/YYYY-MM/RUN-NNNN/
    manifest.json     <- run identity, phase, stages and their status
    metrics.json      <- summary metrics (topics updated, deltas, ledger ids)
    logs/             <- per-stage logs (human-readable trace)
    outputs/          <- per-area result summaries
```

Consolidated knowledge itself is written to the canonical store (`knowledge/en/`,
`knowledge/ledger.jsonl`, `obsidian/`), not inside the run folder — the run folder records
*that a run happened and what it did*, not the knowledge (which is the product).

### `manifest.json` (shape)

```json
{
  "run_id": "RUN-0001",
  "month": "2026-07",
  "phase": 1,
  "status": "completed",
  "started": "2026-07-11T20:40:00",
  "finished": "2026-07-11T20:40:03",
  "areas": ["PRP", "Mesenchymal Stem Cells"],
  "stages": [
    {"area": "PRP", "status": "completed", "deltas": 4, "version": 5},
    {"area": "Mesenchymal Stem Cells", "status": "completed", "deltas": 2, "version": 3}
  ]
}
```

---

## States

A run and each of its stages move through:

```
pending → running → completed
                 ↘ failed
```

- **pending** — declared but not started.
- **running** — in progress; the manifest is written with this status first, so a crash is
  detectable.
- **completed** — all stages finished successfully.
- **failed** — a stage raised; the run stops, the error is written to `logs/`, and every
  already-completed stage is preserved in the manifest.

---

## What happens if a stage fails

- The failing stage is marked `failed` with its error recorded in `logs/`.
- Stages already `completed` are left intact (their knowledge is already persisted).
- The run's overall `status` becomes `failed`. No partial or invented output is produced for
  the failing stage (Golden Rule: never fabricate).

## How to resume a run

`kra run research --resume RUN-NNNN` reloads the run's manifest and re-drives only the stages
that are not yet `completed`. Because consolidation is **idempotent**, re-driving a stage that
had partially run is safe: already-incorporated evidence is skipped and produces no duplicate
Delta or version bump. A fresh `kra run research` (no `--resume`) always starts a new run.

---

## Relationship to the rest of the system

- Uses the pure **Knowledge Consolidation Engine** (`src/core/consolidation/`) via the
  `consolidate_topic_knowledge` use case — the run is orchestration, not new domain logic.
- `metrics.json` is the natural place to later attach **benchmark** KPIs (GRSS/CDR/UCR) so a
  run also records how good its reviews were.
- Fits the workflow **framework** (`src/framework/`) — each phase is a step with a state and a
  timing, emitting events for logs and metrics.

## Open design questions (for human curation)

- Should Paper Discovery (Phase 1's first box) pull from a real source (PubMed/TomeSphere) or,
  until then, from the curated Gold Standard as the available validated reviews?
- Per-month vs global run numbering (currently per-month `RUN-NNNN`).
- Should a run write its own immutable copy of the Deltas it produced into `outputs/`, in
  addition to the shared Ledger?
