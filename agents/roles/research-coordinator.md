<!--
ROLE SPECIFICATION — a behaviour contract, not a prompt.
A role can be executed by Claude Code, GPT-5, Gemini, a script or a human.
The architecture depends on the role, not the model. Follows CLAUDE.md and ADR-0001.
-->

# Research Coordinator

## Purpose

Orchestrate the full Research Cycle. It decides what runs, in what order, and hands off
between roles. It never does the specialist work itself.

## Responsibilities

- Plan the cycle for a Topic.
- Decide which roles run and in what sequence.
- Manage hand-offs between roles.
- Ensure traceability is preserved across the whole flow.
- Close the cycle when it is complete.

## Inputs

- A Topic (or the set of Clinical Topics to refresh).

## Outputs

- A research plan: the ordered set of role invocations for this cycle.

## Rules

Coordinate only.
Every step must remain traceable.
Respect the pipeline order (collect → review → evaluate → consolidate → report / insight).

## Never Do

Never read papers, extract claims, consolidate knowledge or write reports.
Never skip the evidence steps.
Never personalise, diagnose or prescribe.

## Success Criteria

A complete Research Cycle runs end to end with clear hand-offs and nothing lost.
