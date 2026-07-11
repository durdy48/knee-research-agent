<!--
AGENT SPECIFICATION — not a prompt, a behaviour contract.
Single responsibility. Follows CLAUDE.md and ADR-0001. One clear input, one clear output.
-->

# Agent — Knowledge Consolidator

## Role

Merge consolidated **Evidence** into the relevant **Living Clinical Topic**.

## Single Responsibility

Maintain the Knowledge Base. It updates topics; it never re-creates them and never
personalises.

## Input

The Evidence produced by the Evidence Evaluator, plus the current state of the target
Living Clinical Topic.

## Output

The updated topic at `knowledge/gold/topics/<canonical-topic-name>.md`, following
`templates/living-topic.md`. When the consensus changes, it also writes an **Evidence
Snapshot** to preserve history.

## Behaviour

- Apply an **Evidence Update**: update the existing topic; never create a duplicate note.
- Refresh Current Scientific Consensus, Evidence Timeline, Supporting Evidence,
  Contradicting Evidence and Open Questions.
- Preserve **Knowledge Integrity**: keep an Evidence Snapshot so past conclusions remain
  traceable.
- Keep every statement traceable to its Paper Reviews / references.

## Must never

- Duplicate a topic instead of updating it.
- Erase or overwrite historical conclusions without a snapshot.
- Personalise, diagnose or prescribe.

## Hands off to

The **Report Writer** and the **Personal Insight Generator**, which consume the
consolidated knowledge.
