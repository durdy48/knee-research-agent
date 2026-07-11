"""Per-run metrics — useful once hundreds of papers are processed.

Tokens/cost are filled by AI adapters (Sprint 3B); the engine tracks timing and counts.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class RunMetrics:
    duration_s: float = 0.0
    steps: Dict[str, float] = field(default_factory=dict)  # step name -> seconds
    claims: int = 0
    errors: int = 0
    tokens: int = 0
    cost_usd: float = 0.0
