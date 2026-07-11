"""Workflow framework — a small, domain-agnostic execution engine.

Nothing here knows about knees, papers or AI. It runs ordered `WorkflowStep`s over a
shared `WorkflowContext`, tracks state and metrics, and publishes events on an
`EventBus`. The same engine powers paper_ingestion, topic_update and monthly_research,
and could power any other domain.
"""
from __future__ import annotations

from .context import WorkflowContext
from .events import Event, EventBus
from .metrics import RunMetrics
from .runner import WorkflowRunner
from .state import WorkflowState
from .step import WorkflowStep

__all__ = [
    "WorkflowContext",
    "Event",
    "EventBus",
    "RunMetrics",
    "WorkflowRunner",
    "WorkflowState",
    "WorkflowStep",
]
