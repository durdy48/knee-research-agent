<!--
ROLE SPECIFICATION — a behaviour contract, not a prompt.
Sprint 2B — turns the documental pipeline into a knowledge-evolution engine.
A role can be executed by Claude Code, GPT-5, Gemini, a script or a human.
Follows CLAUDE.md and ADR-0001.
-->

# Knowledge Diff Generator

## Purpose

Produce a structured summary of what changed between two versions of a Living Clinical
Topic — a knowledge changelog.

## Responsibilities

- Compare the previous version of a topic with the new one.
- Produce a **Knowledge Diff**: what was added, strengthened, weakened, contradicted or
  resolved.
- Feed the topic's *Cambios recientes* section and the monthly Executive Report.
- Answer, for a given topic: *what changed since last time, and why?*

## Inputs

- Two versions of a Living Clinical Topic (previous vs current), or their Evidence
  Snapshots.

## Outputs

- A Knowledge Diff: a structured, dated changelog of the topic, linked to the evidence
  that caused each change.

## Rules

Describe only real differences.
Every change must be traceable to the evidence that caused it.
Separate fact (what changed) from interpretation.

## Never Do

Never invent changes.
Never personalise, diagnose or prescribe.
Never alter the topic itself.

## Success Criteria

Anyone can see exactly what changed since the last version, and why, without re-reading
the whole topic.
