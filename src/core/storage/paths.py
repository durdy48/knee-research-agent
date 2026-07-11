"""Repository paths.

The root can be overridden with the KRA_ROOT environment variable (used by tests).
Otherwise it is inferred from this file's location: src/core/storage/paths.py -> repo root.
"""
from __future__ import annotations

import os
from pathlib import Path


def root() -> Path:
    override = os.environ.get("KRA_ROOT")
    if override:
        return Path(override)
    return Path(__file__).resolve().parents[3]


def papers_dir() -> Path:
    return root() / "papers"


def registry_file() -> Path:
    return papers_dir() / "registry.json"


def reviews_dir() -> Path:
    return root() / "reviews" / "paper-reviews"


def topics_dir() -> Path:
    return root() / "knowledge" / "gold" / "topics"


def reports_dir() -> Path:
    return root() / "knowledge" / "gold" / "reports"


def insights_dir() -> Path:
    return root() / "knowledge" / "gold" / "insights"


def runs_dir() -> Path:
    return root() / "runs"


def templates_dir() -> Path:
    return root() / "templates"


def ensure(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p
