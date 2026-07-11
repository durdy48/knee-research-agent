"""Workflow execution state."""
from __future__ import annotations

from enum import Enum


class WorkflowState(str, Enum):
    pending = "PENDING"
    running = "RUNNING"
    completed = "COMPLETED"
    failed = "FAILED"
