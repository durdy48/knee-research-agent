# Definition of Done — Workflows

**Version:** 1.0.0
**Status:** Stable
**Last Updated:** 2026-07-11

A workflow is **Done** only when it meets every criterion below. Establishing this now
keeps a homogeneous quality bar as new workflows (`topic_update`, `monthly_research`, …)
are built on the same engine.

## Criteria (every workflow)

1. **Unique identifiers.** Every entity it creates has a stable id (`PAPER-…`,
   `CLAIM-…`, `TOPIC-…`, `REPORT-…`, `RUN-…`).
2. **Typed validation.** Every artifact it produces validates against its Pydantic model
   (objects are the source of truth; Markdown/JSON are views).
3. **Traceability.** Every Claim, conclusion and insight links back to its source
   (`GLOSSARY: Traceability`).
4. **Execution metrics.** It records run metrics (duration, per-step time, counts,
   errors; tokens/cost when AI is involved).
5. **Events.** It emits events on the `EventBus` (started / step.completed / completed /
   failed).
6. **Unit tests.** Its domain logic and steps are covered by unit tests.
7. **End-to-end test.** There is one integration test that runs it through all layers.
8. **Idempotent.** Re-running with the same input does not duplicate data.
9. **Artifacts saved.** It persists its artifacts to the correct locations.
10. **Final state recorded.** It ends in a recorded terminal state (`COMPLETED` or
    `FAILED`).

## Applied to `paper_ingestion`

- Paper gets a unique `PAPER-YYYY-NNNN` id. ✅
- `PaperReview` is a Pydantic model and validates on construction. ✅
- Claims are traceable via `…claims.json` (`paper_id` + `source_review`). ✅
- `RunMetrics` (duration, per-step time, claims, errors) are produced. ✅
- Events `paper.created` / `paper.reviewed` / `review.saved` / `workflow.completed`. ✅
- Unit tests (`test_framework`, `test_use_cases`, `test_domain_events`). ✅
- End-to-end test (`test_vertical_slice`). ✅
- Idempotent by DOI (re-running the same DOI reuses the paper). ✅
- Artifacts in `reviews/paper-reviews/` and linked in `papers/registry.json`. ✅
- Final state `COMPLETED` recorded in the run context. ✅

This checklist is verified automatically by `src/tests/test_definition_of_done.py`.
