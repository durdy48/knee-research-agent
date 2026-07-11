<!--
WORKFLOW — coordinates roles only. Workflows contain NO intelligence; they sequence
roles and define hand-offs. Each role is defined in agents/roles/. Follows ADR-0001.
-->

# Workflow — Paper Ingestion

## Purpose

Ingest a single known Paper into the knowledge base (e.g. a paper the patient found).

## Trigger

A specific Paper (identifier or file) is provided.

## Steps

1. **Paper Reviewer** — produce one immutable Paper Review from the Paper.
2. **Evidence Evaluator** — re-evaluate the affected Evidence including this review.
3. **Knowledge Consolidator** — apply an Evidence Update to the related Living Clinical
   Topic(s) if the evidence changes (snapshot if consensus changes).

## Inputs

- One Paper (PDF / DOI / PMID / full text).

## Outputs

- One Paper Review stored in `reviews/paper-reviews/`.
- Updated Living Clinical Topic(s) if the evidence changed.

## Transition rules

- A step starts only when the previous step's artifact exists.
- If the paper does not change the evidence, the review is still kept (cumulative
  knowledge), and no topic is modified.
