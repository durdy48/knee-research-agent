<!--
WORKFLOW — coordinates roles only. Workflows contain NO intelligence; they sequence
roles and define hand-offs. Each role is defined in agents/roles/. Follows ADR-0001.
-->

# Workflow — Monthly Research

## Purpose

Run one complete monthly Research Cycle from literature to report and insight.

## Trigger

Once per month (or on demand).

## Steps

1. **Research Coordinator** — plan the cycle: which Clinical Topics to refresh.
2. For each Clinical Topic:
   1. **Literature Collector** — find new relevant Papers → list of Papers.
   2. **Paper Reviewer** — for each new Paper → one Paper Review.
   3. **Evidence Evaluator** — consolidate the Paper Reviews → Evidence.
   4. **Knowledge Consolidator** — apply an Evidence Update to the Living Clinical Topic
      (snapshot if consensus changes).
3. **Medical Writer** — produce the monthly Executive Report.
4. **Personal Insight Generator** — produce Personal Insights for the patient.

## Inputs

- The set of Clinical Topics to refresh.
- The Patient Profile / Persona / Personal Goals.

## Outputs

- Updated Living Clinical Topics.
- One immutable Executive Report (Monthly Review).
- Personal Insights.

## Transition rules

- A step starts only when the previous step's artifact exists.
- Evidence steps are never skipped.
- Personalisation happens only after knowledge is consolidated.
