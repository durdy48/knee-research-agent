"""Provider registry — maps a model name to an AIReviewer (AIProvider) adapter.

The abstraction the chat asked for: the benchmark names a provider, gets an ``AIReviewer``,
and never depends on any specific SDK. Add ``gpt`` / ``gemini`` / ``local`` here later
without touching the runner or metrics.

  - stub   : extracts nothing (honest zero baseline).
  - fake   : deterministic, key-free (exercises the harness).
  - claude : the real reviewer (needs an Anthropic API key).
"""
from __future__ import annotations

from typing import Callable, Dict, List

from core.ports.services import AIReviewer
from infrastructure.ai import ClaudeAIReviewer, FakeAIReviewer, ManualAIProvider, StubAIReviewer

_REGISTRY: Dict[str, Callable[[], AIReviewer]] = {
    "stub": StubAIReviewer,
    "fake": FakeAIReviewer,
    "manual": ManualAIProvider,
    "claude": ClaudeAIReviewer,
}


def available() -> List[str]:
    return sorted(_REGISTRY.keys())


def get_reviewer(name: str) -> AIReviewer:
    if name in _REGISTRY:
        return _REGISTRY[name]()
    raise ValueError(
        f"model '{name}' is not available. Available: {available()}. "
        "New providers implement the AIReviewer port; 'claude' needs an Anthropic API key."
    )
