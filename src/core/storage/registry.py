"""Paper Registry — the entry point of the pipeline.

Reads and writes papers/registry.json. Tracks which papers exist and their state
(discovered -> pending_review -> reviewed -> consolidated). See papers/README.md.
"""
from __future__ import annotations

import json
from datetime import date
from typing import Optional

from . import paths
from ..models import ids

_DEFAULT = {
    "schema_version": "1.0",
    "description": "Paper Registry — the entry point of the pipeline.",
    "id_conventions": {
        "paper": "PAPER-YYYY-NNNN",
        "claim": "CLAIM-YYYY-NNNN",
        "topic": "TOPIC-<name>",
        "report": "REPORT-YYYY-MM",
        "run": "RUN-YYYY-MM-NNN",
    },
    "states": ["discovered", "pending_review", "reviewed", "consolidated"],
    "papers": [],
}


def load() -> dict:
    f = paths.registry_file()
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    return json.loads(json.dumps(_DEFAULT))  # deep copy


def save(reg: dict) -> None:
    paths.ensure(paths.papers_dir())
    paths.registry_file().write_text(
        json.dumps(reg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def get(reg: dict, paper_id: str) -> Optional[dict]:
    for p in reg["papers"]:
        if p["paper_id"] == paper_id:
            return p
    return None


def next_paper_id(reg: dict) -> str:
    year = date.today().year
    prefix = f"PAPER-{year}-"
    seqs = [
        int(p["paper_id"].rsplit("-", 1)[-1])
        for p in reg["papers"]
        if p["paper_id"].startswith(prefix)
    ]
    seq = (max(seqs) + 1) if seqs else 1
    return ids.paper_id(year, seq)


def add_paper(
    reg: dict,
    *,
    title: str,
    doi: Optional[str] = None,
    pmid: Optional[str] = None,
    year: Optional[int] = None,
    study_type: Optional[str] = None,
    topics: Optional[list] = None,
) -> dict:
    entry = {
        "paper_id": next_paper_id(reg),
        "doi": doi,
        "pmid": pmid,
        "title": title,
        "year": year,
        "study_type": study_type,
        "status": "pending_review",
        "review": None,
        "claims": None,
        "topics": topics or [],
        "discovered_at": ids.today(),
        "last_updated": ids.today(),
    }
    reg["papers"].append(entry)
    return entry


def set_status(reg: dict, paper_id: str, status: str) -> dict:
    p = get(reg, paper_id)
    if p is None:
        raise KeyError(paper_id)
    if status not in reg.get("states", _DEFAULT["states"]):
        raise ValueError(f"unknown status: {status}")
    p["status"] = status
    p["last_updated"] = ids.today()
    return p
