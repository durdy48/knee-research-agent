"""A single unit of work in a workflow."""
from __future__ import annotations

from abc import ABC, abstractmethod

from .context import WorkflowContext


class WorkflowStep(ABC):
    name: str = "step"

    @abstractmethod
    def run(self, ctx: WorkflowContext) -> None:
        """Read from and write to ctx.data; may emit events via ctx.emit(...)."""
