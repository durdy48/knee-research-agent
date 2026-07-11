<!--
ROLE SPECIFICATION — a behaviour contract, not a prompt.
Sprint 2B — turns the documental pipeline into a knowledge-evolution engine.
A role can be executed by Claude Code, GPT-5, Gemini, a script or a human.
Follows CLAUDE.md and ADR-0001 (Knowledge Integrity).
-->

# Version Manager

## Purpose

Preserve the full history of every Clinical Topic and allow reverting to any prior
state. It guarantees Knowledge Integrity: knowledge evolves, but nothing is ever lost.

## Responsibilities

- On each Evidence Update, snapshot the topic before it changes.
- Maintain the current version and the dated history of every topic.
- Enable rollback to any previous state if needed.

## Inputs

- A Clinical Topic update (from the Knowledge Consolidator).

## Outputs

- Versioned topic storage:

```
knowledge/gold/topics/TOPIC-<name>/
    current.md          ← the live Living Clinical Topic
    history/
        2026-07.md      ← Evidence Snapshot
        2026-08.md
```

## Rules

Never lose history.
Snapshot the current version before it is overwritten.
Every version is dated and traceable.

## Never Do

Never delete history.
Never overwrite an existing snapshot.
Never personalise, diagnose or prescribe.

## Success Criteria

Any past state of any topic can be recovered, and the history reflects the true
evolution of the science.
