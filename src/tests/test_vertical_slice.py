#!/usr/bin/env python3
"""Vertical-slice test — `kra run paper` end to end through all layers.

Runs on an isolated temp root (KRA_ROOT) with the real Json/File adapters and the stub
AI reviewer. Run: python3 src/tests/test_vertical_slice.py
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

SRC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SRC))


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="kra-slice-"))
    os.environ["KRA_ROOT"] = str(tmp)

    from application.workflows import PaperIngestionWorkflow
    from core.storage import paths
    from infrastructure.ai.stub import StubAIReviewer
    from infrastructure.repositories.file_review_store import FileReviewStore
    from infrastructure.repositories.json_registry import JsonPaperRepository

    wf = PaperIngestionWorkflow(JsonPaperRepository(), StubAIReviewer(), FileReviewStore())
    s = wf.run(doi="10.1000/demo", title="PRP vs HA demo", year=2025, topics=["TOPIC-PRP"])

    assert s["paper_id"].startswith("PAPER-"), s["paper_id"]
    assert s["state"] == "COMPLETED", s["state"]
    assert s["status"] == "reviewed"
    assert s["n_claims"] == 0  # stub reviewer fabricates nothing
    assert (tmp / s["review"]).exists()
    assert (tmp / s["claims"]).exists()

    reg = json.loads(paths.registry_file().read_text(encoding="utf-8"))
    entry = reg["papers"][0]
    assert entry["review"] == s["review"] and entry["claims"] == s["claims"]

    claims = json.loads((tmp / s["claims"]).read_text(encoding="utf-8"))
    assert claims["paper_id"] == s["paper_id"]

    # idempotent-ish: a second run gets a new id, registry keeps both
    s2 = wf.run(doi="10.1000/demo2", title="Second demo")
    assert s2["paper_id"] != s["paper_id"]
    reg = json.loads(paths.registry_file().read_text(encoding="utf-8"))
    assert len(reg["papers"]) == 2

    shutil.rmtree(tmp, ignore_errors=True)
    print("OK — vertical slice test passed (kra run paper end to end)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
