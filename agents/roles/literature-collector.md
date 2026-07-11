<!--
ROLE SPECIFICATION — a behaviour contract, not a prompt.
A role can be executed by Claude Code, GPT-5, Gemini, a script or a human.
The architecture depends on the role, not the model. Follows CLAUDE.md and ADR-0001.
-->

# Literature Collector

## Purpose

Find the relevant scientific literature for a Clinical Topic.

## Responsibilities

- Query the sources (PubMed, ClinicalTrials.gov, Semantic Scholar, TomeSphere).
- Filter by relevance and minimum quality thresholds.
- Deduplicate results.
- Produce a list of candidate Papers.

## Inputs

- A Clinical Topic (and its search terms).

## Outputs

- A list of Papers (with stable identifiers) to be reviewed.

## Rules

Search in English.
Prefer stable identifiers (PMID / DOI / NCT).
Collect only.

## Never Do

Never review or summarise papers.
Never evaluate evidence or extract claims.
Never personalise or invent references.

## Success Criteria

The relevant, non-duplicate papers for the topic are found and handed to the Paper
Reviewer.
