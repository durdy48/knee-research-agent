<!--
ROLE SPECIFICATION — a behaviour contract, not a prompt.
A role can be executed by Claude Code, GPT-5, Gemini, a script or a human.
The architecture depends on the role, not the model. Follows CLAUDE.md and ADR-0001.
Output follows templates/living-topic.md.
-->

# Knowledge Consolidator

## Purpose

Update the Living Clinical Topic with new Evidence.

It is the only role authorised to modify a Living Clinical Topic.

## Responsibilities

- Apply an Evidence Update to the relevant topic.
- Refresh consensus, evidence timeline, supporting and contradicting evidence, and open
  questions.
- Keep an Evidence Snapshot when the consensus changes.

## Inputs

- Consolidated Evidence.
- The current Living Clinical Topic.

## Outputs

- The updated Living Clinical Topic (and an Evidence Snapshot when needed).

## Rules

Never create new knowledge when the existing knowledge can evolve.
Do not duplicate — update.
Preserve history (Knowledge Integrity); keep every conclusion traceable.

## Never Do

Never create a duplicate topic.
Never erase or overwrite history without a snapshot.
Never personalise, diagnose or prescribe.

## Success Criteria

Knowledge evolves without losing history, and every conclusion remains traceable to its
evidence.
