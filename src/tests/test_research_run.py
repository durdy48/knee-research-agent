#!/usr/bin/env python3
"""ResearchRun tests — run recording, metrics, failure handling and resume.

Isolated with a temporary KRA_ROOT and an injected fake consolidator (no reviews needed).
Run: python3 src/tests/test_research_run.py
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

WHEN = datetime(2026, 7, 1, 10, 0, 0)


def _ok(area):
    from application.use_cases.consolidate_knowledge import ConsolidationRun
    return ConsolidationRun(
        topic_id="TOPIC-" + area.upper(), area=area, reviewed=2,
        confidence_before=0.5, confidence_after=0.62, version=2,
        ledger_ids=["KD-2026-00001"], changed=True,
    )


def _report(month, run_dir=None):
    from core.storage import paths
    p = paths.ensure(paths.root() / "reports") / f"{month}.md"
    p.write_text("dummy report", encoding="utf-8")
    return p


def _insight(month):
    from core.storage import paths
    p = paths.ensure(paths.root() / "reports") / f"{month}-insights.md"
    p.write_text("dummy insight", encoding="utf-8")
    return p


def main() -> int:
    prev = os.environ.get("KRA_ROOT")
    with tempfile.TemporaryDirectory() as d:
        os.environ["KRA_ROOT"] = d
        from application.research_run import ResearchRun

        # 1) A run records manifest + metrics + outputs and increments run ids.
        m = ResearchRun(_ok, report_fn=_report, insight_fn=_insight, now=WHEN).run(["PRP", "MSC"])
        assert m["status"] == "completed" and m["run_id"] == "RUN-0001"
        base = Path(d) / "runs" / "2026-07" / "RUN-0001"
        assert (base / "manifest.json").is_file()
        assert (base / "outputs" / "PRP.json").is_file()
        assert (base / "logs" / "run.log").is_file()
        metrics = json.loads((base / "metrics.json").read_text())
        assert metrics["total_deltas"] == 2 and metrics["topics_updated"] == 2

        m2 = ResearchRun(_ok, report_fn=_report, insight_fn=_insight, now=WHEN).run(["PRP"])
        assert m2["run_id"] == "RUN-0002"

        # 2) A failing stage is recorded; the run is 'failed' and completed stages persist.
        def flaky(area):
            if area == "MSC":
                raise RuntimeError("stage blew up")
            return _ok(area)

        mf = ResearchRun(flaky, report_fn=_report, insight_fn=_insight, now=WHEN).run(["PRP", "MSC"])
        assert mf["status"] == "failed"
        st = {s["area"]: s["status"] for s in mf["stages"]}
        assert st["PRP"] == "completed" and st["MSC"] == "pending"
        assert "FAILED" in (Path(d) / "runs" / "2026-07" / mf["run_id"] / "logs" / "run.log").read_text()

        # 3) Resume re-drives only the incomplete stage (PRP already done, MSC now succeeds).
        mr = ResearchRun(_ok, report_fn=_report, insight_fn=_insight, now=WHEN).run(resume=mf["run_id"])
        assert mr["status"] == "completed"
        st2 = {s["area"]: s["status"] for s in mr["stages"]}
        assert st2["PRP"] == "completed" and st2["MSC"] == "completed"

    if prev is None:
        os.environ.pop("KRA_ROOT", None)
    else:
        os.environ["KRA_ROOT"] = prev

    print("OK — ResearchRun test passed (record + metrics + failure + resume)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
