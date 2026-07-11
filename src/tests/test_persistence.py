#!/usr/bin/env python3
"""Persistence tests — KnowledgeStore round-trip, ledger ids, history snapshots.

Isolated with a temporary KRA_ROOT so it never touches the real knowledge base.
Run: python3 src/tests/test_persistence.py
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main() -> int:
    prev_root = os.environ.get("KRA_ROOT")
    with tempfile.TemporaryDirectory() as d:
        os.environ["KRA_ROOT"] = d
        # Import AFTER setting KRA_ROOT so paths resolve to the temp dir.
        from core.models import ClinicalTopic, Controversy, KnowledgeDelta
        from core.models.enums import Impact, ResolutionLevel
        from infrastructure.repositories.knowledge_store import KnowledgeStore

        store = KnowledgeStore()
        topic = ClinicalTopic(
            topic_id="TOPIC-X", name="X", version=2, confidence=0.6,
            supporting_evidence=["10.1/a"],
            controversies=[Controversy(controversy_id="TOPIC-X-C1", question="disputed?",
                                       contradicting_studies=["10.2/b"],
                                       resolution_level=ResolutionLevel.open)],
        )
        store.save_topic(topic)

        # Round-trip: the object is the source of truth.
        loaded = store.load_topic("TOPIC-X")
        assert loaded is not None and loaded.version == 2 and loaded.confidence == 0.6
        assert loaded.controversies[0].question == "disputed?"

        # Views written (canonical English + Spanish Obsidian).
        assert (Path(d) / "knowledge/en/topics/TOPIC-X/current.md").is_file()
        assert (Path(d) / "obsidian/TOPIC-X.md").is_file()
        assert "disputed?" in (Path(d) / "obsidian/TOPIC-X.md").read_text(encoding="utf-8")

        # Ledger ids are sequential and immutable-append.
        id1 = store.append_delta(KnowledgeDelta(delta_id="a", topic_id="TOPIC-X", date="2026-01-01", impact=Impact.new))
        id2 = store.append_delta(KnowledgeDelta(delta_id="b", topic_id="TOPIC-X", date="2026-02-01", impact=Impact.contradiction))
        assert id1 == "KD-2026-00001" and id2 == "KD-2026-00002"
        assert sum(1 for _ in (Path(d) / "knowledge/ledger.jsonl").open()) == 2

        # Re-saving a new version snapshots the previous one (history is never lost).
        topic.version = 3
        store.save_topic(topic)
        hist = list((Path(d) / "knowledge/en/topics/TOPIC-X/history").glob("*.md"))
        assert len(hist) == 1, hist

    if prev_root is None:
        os.environ.pop("KRA_ROOT", None)
    else:
        os.environ["KRA_ROOT"] = prev_root

    print("OK — persistence test passed (round-trip + ledger ids + history snapshot)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
