<!--
WORKFLOW — coordinates roles only. Workflows contain NO intelligence; they sequence
roles and define hand-offs. Each role is defined in agents/roles/. Follows ADR-0001.
-->

# Workflow — Topic Update

## Purpose

Update a single Living Clinical Topic when new evidence appears, without running a full
monthly cycle.

## Trigger

New relevant literature detected for one topic, or a manual request.

## Steps

1. **Literature Collector** — find new Papers for the topic → list of Papers.
2. **Paper Reviewer** — for each new Paper → one Paper Review.
3. **Evidence Evaluator** — consolidate the new Paper Reviews with existing evidence →
   Evidence.
4. **Knowledge Consolidator** — apply an Evidence Update to the Living Clinical Topic
   (snapshot if consensus changes).

## Inputs

- One Clinical Topic.

## Outputs

- The updated Living Clinical Topic (and an Evidence Snapshot when needed).

## Transition rules

- A step starts only when the previous step's artifact exists.
- No report or insight is produced here (that belongs to Monthly Research).
- The topic is updated, never duplicated.
