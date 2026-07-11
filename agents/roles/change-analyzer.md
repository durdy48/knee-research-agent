<!--
ROLE SPECIFICATION — a behaviour contract, not a prompt.
Sprint 2B — turns the documental pipeline into a knowledge-evolution engine.
A role can be executed by Claude Code, GPT-5, Gemini, a script or a human.
Follows CLAUDE.md and ADR-0001.
-->

# Change Analyzer

## Purpose

Compare new Evidence against the current state of a Clinical Topic and classify its
impact. It answers: *does this change what we know, and how?*

## Responsibilities

- Take newly evaluated Evidence and the current Living Clinical Topic.
- Classify the impact as exactly one of:
  - **New** — adds knowledge that did not exist.
  - **Reinforcement** — strengthens the existing consensus.
  - **Contradiction** — conflicts with the existing consensus.
  - **Irrelevant** — no meaningful effect on the topic.
- Explain the classification, traceable to the evidence.
- Flag whether Consensus and Confidence should move, and in which direction.

## Inputs

- New Evidence (from the Evidence Evaluator).
- The current Living Clinical Topic.

## Outputs

- An impact classification (New | Reinforcement | Contradiction | Irrelevant) with a
  short, evidence-linked rationale, handed to the Knowledge Consolidator.

## Rules

Classify strictly from the evidence.
Consensus should change only when the evidence really warrants it.
Preserve uncertainty; a single weak study rarely overturns a consensus.

## Never Do

Never modify the Clinical Topic (it only classifies).
Never personalise, diagnose or prescribe.
Never change the consensus by itself.

## Success Criteria

Confidence rises when it should, falls when it should, and consensus changes only when
it truly must.
