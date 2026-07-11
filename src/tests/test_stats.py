#!/usr/bin/env python3
"""Stats tests — the observability dashboard reports consistent counts.

Integration-style: reads the real knowledge base (skips if none consolidated yet).
Run: python3 src/tests/test_stats.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.storage import paths  # noqa: E402


def main() -> int:
    from application.use_cases.stats import format_stats, gather_stats

    s = gather_stats()
    for key in ("living_topics", "evidence_items", "knowledge_deltas", "open_questions",
                "controversies", "research_runs", "runs_succeeded", "runs_failed",
                "average_confidence"):
        assert key in s, f"missing stat: {key}"
    assert s["runs_succeeded"] + s["runs_failed"] <= s["research_runs"]
    assert isinstance(format_stats(s), str) and "Knowledge Base" in format_stats(s)

    if paths.knowledge_en_dir().is_dir():
        assert s["living_topics"] >= 1
        assert 0.0 <= float(s["average_confidence"]) <= 1.0

    print("OK — stats test passed (keys + consistency)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
