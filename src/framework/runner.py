"""Runs an ordered list of steps over a context, tracking state and metrics."""
from __future__ import annotations

import time
from typing import List, Optional

from .context import WorkflowContext
from .state import WorkflowState
from .step import WorkflowStep


class WorkflowRunner:
    def __init__(self, steps: List[WorkflowStep], name: str = "workflow") -> None:
        self.steps = steps
        self.name = name

    def run(self, ctx: Optional[WorkflowContext] = None) -> WorkflowContext:
        ctx = ctx or WorkflowContext()
        ctx.state = WorkflowState.running
        ctx.emit("workflow.started", name=self.name)
        t0 = time.perf_counter()
        try:
            for step in self.steps:
                s0 = time.perf_counter()
                ctx.emit("step.started", step=step.name)
                step.run(ctx)
                ctx.metrics.steps[step.name] = round(time.perf_counter() - s0, 6)
                ctx.emit("step.completed", step=step.name)
            ctx.state = WorkflowState.completed
            ctx.emit("workflow.completed", name=self.name)
        except Exception as exc:  # noqa: BLE001 — record and re-raise
            ctx.metrics.errors += 1
            ctx.state = WorkflowState.failed
            ctx.emit("workflow.failed", name=self.name, error=str(exc))
            raise
        finally:
            ctx.metrics.duration_s = round(time.perf_counter() - t0, 6)
        return ctx
