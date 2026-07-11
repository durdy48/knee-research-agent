"""Pipeline stages — reproduce the manual flow that was validated in RUN-2026-07-001.

Each stage manages state and artifacts (registry, review files, topic versioning, runs).
The *intelligence* of each stage (actually reading a paper, synthesising a topic) is the
job of the corresponding role in agents/roles/ and is left as a template scaffold here:
this MVP wires the pipeline; a role (AI or human) fills the content.
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Optional

from ..storage import paths, registry, runs
from ..knowledge import topics
from ..models import ids
from ..models import EvolutionEvent


def _slug(text: str, maxlen: int = 60) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "-", text.lower()).strip("-")
    return s[:maxlen] or "untitled"


def _scaffold_from_template(template_name: str, target: Path) -> Path:
    paths.ensure(target.parent)
    if not target.exists():
        tmpl = paths.templates_dir() / template_name
        target.write_text(
            tmpl.read_text(encoding="utf-8") if tmpl.exists() else "",
            encoding="utf-8",
        )
    return target


def ingest(
    *,
    title: str,
    doi: Optional[str] = None,
    pmid: Optional[str] = None,
    year: Optional[int] = None,
    study_type: Optional[str] = None,
    topics_list: Optional[list] = None,
) -> dict:
    """Register a paper (status: pending_review). Entry point of the pipeline."""
    reg = registry.load()
    entry = registry.add_paper(
        reg,
        title=title,
        doi=doi,
        pmid=pmid,
        year=year,
        study_type=study_type,
        topics=topics_list or [],
    )
    registry.save(reg)
    return entry


def review(paper_id: str) -> Path:
    """Scaffold a Paper Review for a paper and mark it reviewed."""
    reg = registry.load()
    p = registry.get(reg, paper_id)
    if p is None:
        raise KeyError(paper_id)
    year = p.get("year") or date.today().year
    name = _slug(p.get("title") or paper_id)
    review_path = paths.reviews_dir() / f"{year}-{name}.md"
    _scaffold_from_template("paper-review.md", review_path)
    claims_path = review_path.with_suffix(".claims.json")
    if not claims_path.exists():
        claims_path.write_text(
            '{\n  "schema_version": "1.0",\n'
            f'  "paper_id": "{paper_id}",\n'
            f'  "source_review": "{review_path.relative_to(paths.root())}",\n'
            '  "claims": []\n}\n',
            encoding="utf-8",
        )
    p["review"] = str(review_path.relative_to(paths.root()))
    p["claims"] = str(claims_path.relative_to(paths.root()))
    registry.set_status(reg, paper_id, "reviewed")
    registry.save(reg)
    return review_path


def consolidate(topic_id: str) -> dict:
    """Consolidate reviewed papers of a topic into its Living Clinical Topic.

    Snapshots the current version (Version Manager) and records an evolution event.
    """
    reg = registry.load()
    reviewed = [
        p for p in reg["papers"]
        if topic_id in p.get("topics", []) and p["status"] in ("reviewed", "consolidated")
    ]
    pending = [p for p in reviewed if p["status"] == "reviewed"]

    topics.snapshot(topic_id)  # preserve history before change
    current = topics.ensure_current(topic_id)

    event = EvolutionEvent(
        topic_id=topic_id,
        date=ids.today(),
        impact="New" if pending else "Irrelevant",
        papers_added=len(pending),
        summary=(
            f"Consolidated {len(pending)} newly reviewed paper(s) into {topic_id}."
            if pending else f"No new reviewed papers for {topic_id}."
        ),
    )
    topics.append_event(event)

    for p in pending:
        registry.set_status(reg, p["paper_id"], "consolidated")
    registry.save(reg)

    return {
        "topic_id": topic_id,
        "current": str(current.relative_to(paths.root())),
        "papers_consolidated": [p["paper_id"] for p in pending],
        "event": event.model_dump(mode="json"),
    }


def report(topic_id: str) -> Path:
    """Scaffold the monthly Executive Report (immutable)."""
    stamp = date.today().strftime("%Y-%m")
    target = paths.reports_dir() / f"{stamp}.md"
    return _scaffold_from_template("executive-report.md", target)


def insight(topic_id: str) -> Path:
    """Scaffold a Personal Insight for a topic."""
    target = paths.insights_dir() / f"{topic_id.lower()}-insight.md"
    return _scaffold_from_template("insight.md", target)
