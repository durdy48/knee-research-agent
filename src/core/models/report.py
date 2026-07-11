"""Executive Report — the monthly, immutable patient-facing output."""
from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class ExecutiveReport(BaseModel):
    report_id: str
    month: str  # YYYY-MM
    generated: str = ""
    advances: List[str] = Field(default_factory=list)
    promising_treatments: List[str] = Field(default_factory=list)
    new_trials: List[str] = Field(default_factory=list)
    changes: List[str] = Field(default_factory=list)
    worth_monitoring: List[str] = Field(default_factory=list)
    questions_for_specialist: List[str] = Field(default_factory=list)
    topics_updated: List[str] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)
    immutable: bool = True
