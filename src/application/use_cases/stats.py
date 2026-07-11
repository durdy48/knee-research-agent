"""Knowledge-base statistics — observability, not a new capability.

`kra stats` gives a one-glance view of the system state: how much consolidated knowledge
exists, how many changes and controversies, and how the Research Runs have gone.
"""
from __future__ import annotations

import json
from typing import Dict

from core.storage import paths
from infrastructure.repositories.knowledge_store import KnowledgeStore


def gather_stats() -> Dict[str, object]:
    store = KnowledgeStore()
    tdir = paths.knowledge_en_dir()
    topic_ids = [p.name for p in tdir.iterdir() if p.is_dir()] if tdir.is_dir() else []
    topics = [t for t in (store.load_topic(t) for t in topic_ids) if t is not None]

    deltas = 0
    if paths.ledger_file().is_file():
        deltas = sum(1 for line in paths.ledger_file().open(encoding="utf-8") if line.strip())

    runs = succeeded = failed = 0
    root = paths.runs_dir()
    if root.is_dir():
        for month in root.iterdir():
            if not month.is_dir():
                continue
            for rd in month.glob("RUN-*"):
                mf = rd / "manifest.json"
                if mf.is_file():
                    runs += 1
                    st = json.loads(mf.read_text(encoding="utf-8")).get("status")
                    succeeded += st == "completed"
                    failed += st == "failed"

    n = len(topics)
    return {
        "living_topics": n,
        "evidence_items": sum(len(t.supporting_evidence) + len(t.contradicting_evidence) for t in topics),
        "knowledge_deltas": deltas,
        "open_questions": sum(len(t.open_questions) for t in topics),
        "controversies": sum(len(t.controversies) for t in topics),
        "research_runs": runs,
        "runs_succeeded": succeeded,
        "runs_failed": failed,
        "average_confidence": round(sum(t.confidence for t in topics) / n, 2) if n else 0.0,
    }


def format_stats(s: Dict[str, object]) -> str:
    return "\n".join([
        "Knowledge Base",
        "",
        f"  Living Topics    : {s['living_topics']}",
        f"  Evidence Items   : {s['evidence_items']}",
        f"  Knowledge Deltas : {s['knowledge_deltas']}",
        f"  Open Questions   : {s['open_questions']}",
        f"  Controversies    : {s['controversies']}",
        "",
        f"  Research Runs    : {s['research_runs']}",
        f"  Succeeded        : {s['runs_succeeded']}",
        f"  Failed           : {s['runs_failed']}",
        "",
        f"  Average Confidence: {s['average_confidence']}",
    ])
