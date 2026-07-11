"""Living Clinical Topic storage with versioning (Version Manager behaviour).

Layout (see agents/roles/version-manager.md):

    knowledge/gold/topics/TOPIC-<name>/
        current.md          <- the live Living Clinical Topic
        history/YYYY-MM.md   <- Evidence Snapshots
        events.jsonl         <- knowledge-evolution events

Knowledge Integrity: knowledge evolves, but history is never lost.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Optional

from ..storage import paths
from ..models import ids
from ..models import EvolutionEvent


def topic_dir(topic_id: str) -> Path:
    return paths.topics_dir() / topic_id


def current_path(topic_id: str) -> Path:
    return topic_dir(topic_id) / "current.md"


def ensure_current(topic_id: str, name: Optional[str] = None) -> Path:
    """Create current.md from the living-topic template if it does not exist."""
    paths.ensure(topic_dir(topic_id))
    cur = current_path(topic_id)
    if not cur.exists():
        name = name or ids.topic_name(topic_id)
        template = paths.templates_dir() / "living-topic.md"
        content = template.read_text(encoding="utf-8") if template.exists() else "# {{Topic Name}}\n"
        content = content.replace("{{Topic Name}}", name)
        cur.write_text(content, encoding="utf-8")
    return cur


def snapshot(topic_id: str) -> Optional[Path]:
    """Copy current.md into history/YYYY-MM.md (an Evidence Snapshot). Never overwrites."""
    cur = current_path(topic_id)
    if not cur.exists():
        return None
    hist = paths.ensure(topic_dir(topic_id) / "history")
    stamp = date.today().strftime("%Y-%m")
    snap = hist / f"{stamp}.md"
    if not snap.exists():
        snap.write_text(cur.read_text(encoding="utf-8"), encoding="utf-8")
    return snap


def append_event(event: EvolutionEvent) -> Path:
    """Append a knowledge-evolution event (JSON line) for the topic."""
    paths.ensure(topic_dir(event.topic_id))
    events = topic_dir(event.topic_id) / "events.jsonl"
    with events.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event.model_dump(mode="json"), ensure_ascii=False) + "\n")
    return events
