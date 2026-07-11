"""AI provider adapters (the AIProvider layer).

Every provider implements the ``AIReviewer`` port from ``core.ports.services`` — the model
abstraction the chat asked for, so the benchmark can compare providers without touching the
rest of the system. Swap the provider, keep everything else.

  - StubAIReviewer   : extracts nothing (dry runs / honest zero baseline).
  - FakeAIReviewer   : deterministic, key-free, exercises the harness end to end.
  - ManualAIProvider : human-in-the-loop / Claude Code as engine (no API key).
  - ClaudeAIReviewer : the real reviewer (needs an Anthropic API key).
"""
from __future__ import annotations

from .claude import ClaudeAIReviewer
from .fake import FakeAIReviewer
from .manual import ManualAIProvider, ReviewPendingError, build_review_package
from .stub import StubAIReviewer

__all__ = [
    "StubAIReviewer",
    "FakeAIReviewer",
    "ManualAIProvider",
    "ReviewPendingError",
    "build_review_package",
    "ClaudeAIReviewer",
]
