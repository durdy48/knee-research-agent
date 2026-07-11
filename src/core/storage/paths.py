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


def knowledge_en_dir() -> Path:
    """Canonical (English) Living Topics produced by the Consolidator."""
    return root() / "knowledge" / "en" / "topics"


def ledger_file() -> Path:
    """Append-only Knowledge Ledger (one KnowledgeDelta per line)."""
    return root() / "knowledge" / "ledger.jsonl"


def obsidian_dir() -> Path:
    """Spanish, human-facing view of the knowledge base (not the source of truth)."""
    return root() / "obsidian"


def templates_dir() -> Path:
    return root() / "templates"


def ensure(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p
