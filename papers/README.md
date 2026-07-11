# Paper Registry

**Version:** 1.0.0
**Status:** Stable
**Last Updated:** 2026-07-11

The Paper Registry (`papers/registry.json`) is the **entry point of the pipeline**. It
tracks which papers exist, which have been processed and which are pending, so the same
study is never reprocessed twice.

## State machine

```
discovered → pending_review → reviewed → consolidated
```

- **discovered** — the paper is known (found by the Literature Collector) but not yet
  reviewed.
- **pending_review** — queued for the Paper Reviewer.
- **reviewed** — a Paper Review (and its Claims) exists.
- **consolidated** — its evidence has been merged into a Living Clinical Topic.

## Entry schema

| Field | Meaning |
|-------|---------|
| `paper_id` | Stable identifier, `PAPER-YYYY-NNNN` |
| `doi` / `pmid` | Source identifiers |
| `title` | Paper title |
| `year` | Publication year |
| `study_type` | Study design |
| `status` | One of the states above |
| `review` | Path to the Paper Review (or `null`) |
| `claims` | Path to the extracted `claims.json` (or `null`) |
| `topics` | Related Clinical Topics (`TOPIC-<name>`) |
| `discovered_at` / `last_updated` | Dates |

## Unique identifiers

Stable identifiers are used from the start so hundreds of documents can be referenced
reliably:

- `PAPER-YYYY-NNNN` — a paper (e.g. `PAPER-2026-0001`)
- `CLAIM-YYYY-NNNN` — an extracted claim (e.g. `CLAIM-2026-0048`)
- `TOPIC-<name>` — a Clinical Topic (e.g. `TOPIC-PRP`)
- `REPORT-YYYY-MM` — a monthly Executive Report
- `RUN-YYYY-MM-NNN` — one pipeline execution (logged under `runs/`)
