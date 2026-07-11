"""Shared context passed through a workflow's steps."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

from .events import Event, EventBus
from .metrics import RunMetrics
from .state import WorkflowState


@dataclass
class WorkflowContext:
    data: Dict[str, Any] = field(default_factory=dict)
    events: EventBus = field(default_factory=EventBus)
    metrics: RunMetrics = field(default_factory=RunMetrics)
    state: WorkflowState = WorkflowState.pending

    def emit(self, event_name: str, **payload: Any) -> None:
        self.events.publish(Event(event_name, payload))
