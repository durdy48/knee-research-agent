#!/usr/bin/env python3
"""Workflow framework tests — domain-agnostic (no models, no AI, no storage).

Run: python3 src/tests/test_framework.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from framework import WorkflowContext, WorkflowRunner, WorkflowState, WorkflowStep  # noqa: E402


class AddStep(WorkflowStep):
    name = "add"

    def __init__(self, n: int) -> None:
        self.n = n

    def run(self, ctx: WorkflowContext) -> None:
        ctx.data["total"] = ctx.data.get("total", 0) + self.n
        ctx.emit("added", n=self.n)


class BoomStep(WorkflowStep):
    name = "boom"

    def run(self, ctx: WorkflowContext) -> None:
        raise RuntimeError("kaboom")


def main() -> int:
    # Happy path: steps run in order, state COMPLETED, metrics + events recorded.
    seen = []
    ctx = WorkflowContext()
    ctx.events.subscribe("*", lambda e: seen.append(e.name))
    ctx = WorkflowRunner([AddStep(2), AddStep(3)], name="sum").run(ctx)

    assert ctx.state == WorkflowState.completed
    assert ctx.data["total"] == 5
    assert set(ctx.metrics.steps) == {"add"}  # both steps share the name
    assert "workflow.started" in seen and "workflow.completed" in seen
    assert seen.count("added") == 2

    # Failure path: state FAILED, error counted, exception re-raised.
    ctx2 = WorkflowContext()
    try:
        WorkflowRunner([AddStep(1), BoomStep()], name="broken").run(ctx2)
        raise AssertionError("expected RuntimeError")
    except RuntimeError:
        pass
    assert ctx2.state == WorkflowState.failed
    assert ctx2.metrics.errors == 1
    assert "workflow.failed" in [e.name for e in ctx2.events.log]

    print("OK — workflow framework test passed (COMPLETED/FAILED, events, metrics)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
