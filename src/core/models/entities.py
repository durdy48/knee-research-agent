"""Backward-compatibility shim.

Domain models now live in dedicated modules and use Pydantic v2. This module keeps the
old import paths (`from core.models.entities import Paper, EvolutionEvent`) working.
"""
from __future__ import annotations

from .enums import Impact, PaperStatus
from .paper import Paper  # noqa: F401
from .topic import EvolutionEvent  # noqa: F401

PAPER_STATES = [s.value for s in PaperStatus]
IMPACT_CLASSES = [i.value for i in Impact]
