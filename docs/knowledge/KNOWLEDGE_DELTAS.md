# KNOWLEDGE_DELTAS — the record of change, and the Knowledge Ledger

**Version:** 0.1 (design, pre-implementation)
**Status:** Draft for human curation
**Last Updated:** 2026-07-11

> Every time the Consolidator changes a Topic, it emits a **Knowledge Delta**: an immutable,
> human-readable record of *what changed and why*. The ordered, append-only log of all
> Deltas across all Topics is the **Knowledge Ledger** — KRA's complete historical
> explainability.
>
> Companion: `KNOWLEDGE_CONSOLIDATION.md` (§5), `CONFIDENCE_MODEL.md`. Aligns with the
> `EvolutionEvent` already recorded by `src/core/knowledge_engine.py`.

---

## What a Knowledge Delta is

A Knowledge Delta answers, for one change to one Topic: *what changed, why, on what evidence,
with what effect on confidence, and who produced it.* It is the unit that makes knowledge
evolution auditable. It supersedes the looser "Knowledge Diff" wording in the GLOSSARY: a
Diff is the *difference* between two Topic Versions; a **Delta** is the difference **plus its
justification and provenance**.

### Fields

| Field | Meaning |
|-------|---------|
| `delta_id` | stable identifier |
| `topic_id` | the Clinical Topic affected |
| `date` | when the change was consolidated |
| `impact` | Impact Classification (New / Reinforcement / Contradiction / Irrelevant) |
| `what_changed` | plain-language summary of the change to the consensus/controversies |
| `why` | the reasoning (which evidence, how it compared with the prior consensus) |
| `evidence` | the Paper(s)/Claim(s) that caused it (DOIs/PMIDs — traceable) |
| `confidence_before` / `confidence_after` | the confidence move |
| `controversy_changes` | controversies opened / updated / resolved |
| `from_version` / `to_version` | Topic Version before and after |
| `produced_by` | the workflow or human actor (e.g. `manual`, `claude`, a curator) |

The first six of these already exist in embryo as `EvolutionEvent`
(`topic_id`, `date`, `impact`, `papers_added`, `confidence_before`, `confidence_after`,
`summary`). The Delta is the richer, publishable form: it adds explicit `why`, `evidence`,
`controversy_changes`, version links and provenance.

### Rules

- **Immutable.** A Delta is written once and never edited. Corrections are new Deltas.
- **One change, one Delta.** Each consolidation run emits exactly one Delta (or none, if the
  new evidence was `Irrelevant`).
- **Fully traceable.** `evidence` must reference real sources; `why` must be reconstructable
  from them (Golden Rule 4).

---

## The Knowledge Ledger

The **Knowledge Ledger** is the append-only, ordered log of every Knowledge Delta across all
Topics. It is *not* a blockchain and needs no cryptography — it is a faithful, auditable
record of how the knowledge base reached its current state.

Its promise: if, three years from now, you ask *"why did KRA move from advising caution on
PRP to calling it promising for a specific subgroup?"*, the Ledger lets you reconstruct the
entire chain of reasoning — every study, every confidence move, every controversy opening and
resolution, in order. This **complete historical explainability** is something very few AI
tools offer, and it is a candidate for KRA's most differentiating feature.

Properties:

- **Append-only.** Entries are never deleted or rewritten (Golden Rule 7).
- **Global order.** Deltas are timestamped and ordered, across topics.
- **Queryable by topic and by time.** "Show the evolution of PRP" = filter the Ledger by
  `topic_id`. "What changed this month" = filter by date range.
- **The source for Topic Versions and Evidence Snapshots.** A Topic's history is exactly the
  sequence of Deltas that produced its versions.

---

## Consequence: the Executive Report almost writes itself

Because every change is a Delta, the monthly Executive Report (`reports/YYYY-MM.md`, Spanish)
does not need to re-read the papers. It is a **view over the Ledger** for the period:

```
"What changed this month?"  →  the month's Knowledge Deltas
    ├─ new advances            → New / Reinforcement deltas
    ├─ evidence that shifted   → Contradiction deltas + confidence moves
    ├─ new/!changed controversies → controversy_changes
    └─ questions to raise      → open questions surfaced by the deltas
```

The report separates **fact** (the deltas: what the evidence did) from **personal
interpretation** (the Insight layer), per `CLAUDE.md` §11.

---

## Relationship to what already exists

- `EvolutionEvent` + `ClinicalTopic.events` (append-only) are the **seed** of the Ledger. The
  design here extends that record with justification, evidence links, controversy changes and
  provenance, and elevates the cross-topic log to a first-class artifact.
- `Topic Version` and `Evidence Snapshot` (GLOSSARY) are produced *from* Deltas.
- Nothing here requires new infrastructure yet; it specifies the **behaviour** the future
  Consolidator and renderers must honour.

---

## Open design questions (for human curation)

- Where does the Ledger live — inside each Topic's history, a single `knowledge/ledger.md`,
  or both (per-topic view rendered from a global store)?
- Is a Delta ever allowed to bundle multiple papers reviewed together, or strictly one paper
  per Delta?
- What is the minimum content of a Delta's `why` for it to be considered publishable?
