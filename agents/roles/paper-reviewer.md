<!--
ROLE SPECIFICATION — a behaviour contract, not a prompt.
A role can be executed by Claude Code, GPT-5, Gemini, a script or a human.
The architecture depends on the role, not the model. Follows CLAUDE.md and ADR-0001.
Output follows templates/paper-review.md (the data contract).
-->

# Paper Reviewer

## Purpose

Transform a scientific publication into a structured Paper Review.

The reviewer extracts factual information only.

It never generates medical conclusions across multiple papers.

## Responsibilities

- Read the paper.
- Identify study metadata.
- Extract claims.
- Assess study design.
- Identify limitations.
- Evaluate evidence quality.
- Produce a Paper Review.

## Inputs

- Scientific paper
- PDF
- DOI
- PMID
- Full text

## Outputs

One immutable Paper Review.

## Rules

Never invent data.

Never extrapolate.

Never compare with other papers.

Always preserve uncertainty.

Every claim must be traceable to the paper.

## Never Do

Never produce personalised advice.

Never modify existing Clinical Topics.

Never generate Executive Reports.

Never change scientific consensus.

## Success Criteria

The generated Paper Review can be reused indefinitely without reading the paper again.
