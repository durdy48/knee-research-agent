#!/usr/bin/env python3
"""End-to-end MVP test — runs on an isolated temp root (KRA_ROOT).

Run: python3 src/tests/test_pipeline.py
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

SRC = Path(__file__).resolve().parents[1]
REPO = SRC.parent
sys.path.insert(0, str(SRC))


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="kra-test-"))
    os.environ["KRA_ROOT"] = str(tmp)
    # Copy the real templates so scaffolding works in the temp root.
    shutil.copytree(REPO / "templates", tmp / "templates")

    from core.models import ids
    from core.storage import registry
    from core.pipeline import stages
    from core.knowledge import topics

    # ID formats
    assert ids.paper_id(2026, 2) == "PAPER-2026-0002"
    assert ids.topic_id("PRP") == "TOPIC-PRP"
    assert ids.topic_name("TOPIC-PRP") == "PRP"

    # ingest
    entry = stages.ingest(
        title="Test PRP RCT", doi="10.9999/test", year=2025,
        study_type="RCT", topics_list=["TOPIC-PRP"],
    )
    assert entry["paper_id"] == "PAPER-2026-0001", entry["paper_id"]
    assert entry["status"] == "pending_review"

    # review
    review_path = stages.review(entry["paper_id"])
    assert review_path.exists()
    reg = registry.load()
    p = registry.get(reg, entry["paper_id"])
    assert p["status"] == "reviewed"
    assert p["review"] and p["claims"]

    # consolidate
    result = stages.consolidate("TOPIC-PRP")
    assert result["papers_consolidated"] == ["PAPER-2026-0001"]
    assert topics.current_path("TOPIC-PRP").exists()
    reg = registry.load()
    assert registry.get(reg, entry["paper_id"])["status"] == "consolidated"

    # a second consolidate snapshots history and records no new papers
    result2 = stages.consolidate("TOPIC-PRP")
    assert result2["papers_consolidated"] == []
    hist = list((topics.topic_dir("TOPIC-PRP") / "history").glob("*.md"))
    assert hist, "expected a history snapshot"
    events = (topics.topic_dir("TOPIC-PRP") / "events.jsonl").read_text().strip().splitlines()
    assert len(events) == 2

    # report + insight scaffolds
    assert stages.report("TOPIC-PRP").exists()
    assert stages.insight("TOPIC-PRP").exists()

    shutil.rmtree(tmp, ignore_errors=True)
    print("OK — MVP pipeline test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
