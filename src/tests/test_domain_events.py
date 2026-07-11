#!/usr/bin/env python3
"""Domain knowledge-evolution tests — pure domain, no AI, no storage.

Validates the milestone from the chat:
  create a ClinicalTopic -> apply a knowledge event -> confidence increases ->
  history is preserved.

Run: python3 src/tests/test_domain_events.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.knowledge_engine import apply_event  # noqa: E402
from core.models.enums import Impact  # noqa: E402
from core.models.topic import ClinicalTopic  # noqa: E402


def main() -> int:
    topic = ClinicalTopic(topic_id="TOPIC-PRP", name="PRP", confidence=0.50)

    # Reinforcement raises confidence and records an event.
    e1 = apply_event(topic, impact=Impact.reinforcement, papers_added=2, summary="Two RCTs reinforce PRP.")
    assert topic.confidence > 0.50, topic.confidence
    assert e1.confidence_before == 0.50 and e1.confidence_after == topic.confidence
    assert len(topic.events) == 1

    peak = topic.confidence

    # Contradiction lowers confidence but never erases history.
    e2 = apply_event(topic, impact=Impact.contradiction, papers_added=1, summary="A contradicting trial.")
    assert topic.confidence < peak, topic.confidence
    assert len(topic.events) == 2  # history preserved (append-only)

    # Irrelevant evidence does not move confidence.
    before = topic.confidence
    apply_event(topic, impact=Impact.irrelevant, papers_added=1, summary="Off-topic paper.")
    assert topic.confidence == before
    assert len(topic.events) == 3

    # Confidence stays within [0, 1].
    for _ in range(20):
        apply_event(topic, impact=Impact.new, papers_added=5)
    assert 0.0 <= topic.confidence <= 1.0

    # Full history is retained and ordered.
    assert [ev.impact for ev in topic.events[:3]] == [Impact.reinforcement, Impact.contradiction, Impact.irrelevant]

    print("OK — domain knowledge-evolution test passed (confidence moves, history preserved)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
