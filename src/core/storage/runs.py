"""Run logging — every pipeline execution leaves a trace under runs/.

'Todo paso deja un rastro': runs make the process auditable and repeatable.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

from . import paths
from ..models import ids


def next_run_id() -> str:
    today = date.today()
    prefix = f"RUN-{today.year}-{today.month:02d}-"
    existing = []
    if paths.runs_dir().exists():
        existing = [d.name for d in paths.runs_dir().glob(prefix + "*") if d.is_dir()]
    seqs = [int(n.rsplit("-", 1)[-1]) for n in existing if n.rsplit("-", 1)[-1].isdigit()]
    seq = (max(seqs) + 1) if seqs else 1
    return ids.run_id(today.year, today.month, seq)


def create(run_id: str, run_type: str, goal: str = "") -> Path:
    d = paths.ensure(paths.runs_dir() / run_id)
    log = d / "run.md"
    log.write_text(
        f"# Run — {run_id}\n\n"
        f"**Type:** {run_type}\n"
        f"**Date:** {ids.today()}\n\n"
        f"## Goal\n\n{goal}\n\n"
        f"## Steps\n\n",
        encoding="utf-8",
    )
    return log


def step(log: Path, line: str) -> None:
    with log.open("a", encoding="utf-8") as f:
        f.write(f"- {line}\n")
