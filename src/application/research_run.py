"""ResearchRun — one command that drives the whole pipeline and records the execution.

Phase 1: for each area, Review -> Quality Gates -> Knowledge Consolidation (persisted). The
run is recorded under runs/YYYY-MM/RUN-NNNN/ (manifest, metrics, logs, outputs). Deterministic
and idempotent (a run over unchanged evidence produces no new Deltas). See docs/RESEARCH_RUN.md.

Orchestration only — the knowledge logic lives in core.consolidation via the
consolidate_topic_knowledge use case (injected, so this is testable in isolation).
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional

from application.use_cases.consolidate_knowledge import (
    ConsolidationRun,
    consolidate_topic_knowledge,
)
from benchmark import load_dataset
from core.storage import paths

Consolidator = Callable[[str], ConsolidationRun]
Reporter = Callable[..., Path]


def default_areas() -> List[str]:
    gold = load_dataset(name="gold-standard")
    return sorted({e.area for e in gold.curated()})


def _next_run_id(month_dir: Path) -> str:
    n = 0
    if month_dir.is_dir():
        n = sum(1 for p in month_dir.iterdir() if p.is_dir() and p.name.startswith("RUN-"))
    return f"RUN-{n + 1:04d}"


class ResearchRun:
    def __init__(
        self,
        consolidate: Optional[Consolidator] = None,
        *,
        report_fn: Optional[Reporter] = None,
        insight_fn: Optional[Callable[[str], Path]] = None,
        now: Optional[datetime] = None,
    ) -> None:
        self._consolidate = consolidate or consolidate_topic_knowledge
        self._report_fn = report_fn    # Phase 2; default resolved lazily
        self._insight_fn = insight_fn  # Phase 3; default resolved lazily
        self._now = now or datetime.now()

    def run(self, areas: Optional[List[str]] = None, *, resume: Optional[str] = None) -> dict:
        month = self._now.strftime("%Y-%m")
        month_dir = paths.ensure(paths.runs_dir() / month)

        if resume:
            run_id = resume
            run_dir = month_dir / run_id
            manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
            manifest["status"] = "running"  # re-open for the resumed pass
        else:
            areas = areas or default_areas()
            run_id = _next_run_id(month_dir)
            run_dir = paths.ensure(month_dir / run_id)
            manifest = {
                "run_id": run_id, "month": month, "phase": 1, "status": "running",
                "started": self._now.isoformat(timespec="seconds"), "finished": None,
                "areas": areas,
                "stages": [{"area": a, "status": "pending"} for a in areas],
            }
        paths.ensure(run_dir / "logs")
        paths.ensure(run_dir / "outputs")
        self._write(run_dir / "manifest.json", manifest)

        log = run_dir / "logs" / "run.log"
        done = {s["area"] for s in manifest["stages"] if s.get("status") == "completed"}
        try:
            for stage in manifest["stages"]:
                area = stage["area"]
                if area in done:
                    continue
                self._append(log, f"[{area}] consolidating...")
                result = self._consolidate(area)
                stage.update(
                    status="completed",
                    deltas=len(result.ledger_ids),
                    version=result.version,
                    reviewed=result.reviewed,
                    changed=result.changed,
                )
                self._write(run_dir / "outputs" / f"{_slug(area)}.json", {
                    "area": area, "topic_id": result.topic_id,
                    "confidence_before": result.confidence_before,
                    "confidence_after": result.confidence_after,
                    "version": result.version, "ledger_ids": result.ledger_ids,
                    "skipped_gate": result.skipped_gate,
                })
                self._append(log, f"[{area}] {result.confidence_before}->{result.confidence_after}, "
                                  f"{len(result.ledger_ids)} delta(s), v{result.version}")
                self._write(run_dir / "manifest.json", manifest)  # checkpoint after each stage
            # Phase 2: the monthly Executive Report (a view over the Ledger).
            report_fn = self._report_fn
            if report_fn is None:
                from application.use_cases.executive_report import generate_executive_report
                report_fn = generate_executive_report
            report = report_fn(month, run_dir=run_dir)
            manifest["report"] = str(Path(report).relative_to(paths.root()))
            manifest["phase"] = 2
            self._append(log, f"Executive report: {manifest['report']}")
            # Phase 3: the Personal Insight ("¿Ha cambiado algo para mí?").
            insight_fn = self._insight_fn
            if insight_fn is None:
                from application.use_cases.personal_insights import generate_personal_insights
                insight_fn = generate_personal_insights
            insight = insight_fn(month)
            manifest["insight"] = str(Path(insight).relative_to(paths.root()))
            manifest["phase"] = 3
            self._append(log, f"Personal insight: {manifest['insight']}")
            # Phase 4: Obsidian sync (topic views + this month's report & insight).
            try:
                from application.use_cases.obsidian_sync import sync_obsidian
                vault = sync_obsidian(month)
                manifest["obsidian"] = str(vault)
                manifest["phase"] = 4
                self._append(log, f"Obsidian sync: {vault}")
            except Exception as e:  # syncing to an external vault must not fail the run
                self._append(log, f"Obsidian sync skipped: {e!r}")
            manifest["status"] = "completed"
        except Exception as e:  # a stage failed: record, preserve completed stages
            manifest["status"] = "failed"
            self._append(log, f"FAILED: {e!r}")

        manifest["finished"] = datetime.now().isoformat(timespec="seconds")
        self._write(run_dir / "manifest.json", manifest)
        self._write(run_dir / "metrics.json", _metrics(manifest))
        return manifest

    @staticmethod
    def _write(path: Path, data: dict) -> None:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    @staticmethod
    def _append(path: Path, line: str) -> None:
        with path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")


def _slug(area: str) -> str:
    return area.replace(" / ", "-").replace("/", "-").replace(" ", "-")


def _metrics(manifest: dict) -> dict:
    stages = manifest["stages"]
    return {
        "run_id": manifest["run_id"],
        "status": manifest["status"],
        "areas": len(stages),
        "topics_updated": sum(1 for s in stages if s.get("changed")),
        "total_deltas": sum(s.get("deltas", 0) for s in stages),
    }
