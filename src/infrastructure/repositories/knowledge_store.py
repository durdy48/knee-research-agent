"""KnowledgeStore — persists consolidated knowledge to disk.

Layout (canonical source of truth in English):

    knowledge/en/topics/<TOPIC-ID>/
        current.json          <- the ClinicalTopic object (source of truth, round-trippable)
        current.md            <- rendered English view
        history/<date>-v<n>.md <- Evidence Snapshots (never overwritten)
    knowledge/ledger.jsonl    <- append-only Knowledge Ledger (one delta per line)
    obsidian/Temas/<TOPIC-ID>.md <- Spanish human-facing view (not the source of truth)

Golden Rule 7 (Knowledge Integrity): knowledge evolves, history is never lost.
"""
from __future__ import annotations

import json
from datetime import date as _date
from pathlib import Path
from typing import Optional

from core.models import ClinicalTopic, KnowledgeDelta
from core.storage import paths
from infrastructure.renderers.topic_renderer import render_topic_en, render_topic_es


class KnowledgeStore:
    def __init__(self) -> None:
        self.en_dir = paths.knowledge_en_dir()
        self.ledger = paths.ledger_file()

    def _topic_dir(self, topic_id: str) -> Path:
        return self.en_dir / topic_id

    # -- topics ------------------------------------------------------------------
    def load_topic(self, topic_id: str) -> Optional[ClinicalTopic]:
        f = self._topic_dir(topic_id) / "current.json"
        if not f.is_file():
            return None
        return ClinicalTopic.model_validate_json(f.read_text(encoding="utf-8"))

    def save_topic(self, topic: ClinicalTopic) -> Path:
        tdir = self._topic_dir(topic.topic_id)
        tdir.mkdir(parents=True, exist_ok=True)
        cur_md = tdir / "current.md"

        # Snapshot the previous version before overwriting (never lose history).
        prev = self.load_topic(topic.topic_id)
        if prev is not None and cur_md.is_file():
            hist = tdir / "history"
            hist.mkdir(parents=True, exist_ok=True)
            stamp = _date.today().isoformat()
            snap = hist / f"{stamp}-v{prev.version}.md"
            if not snap.exists():
                snap.write_text(cur_md.read_text(encoding="utf-8"), encoding="utf-8")

        (tdir / "current.json").write_text(topic.model_dump_json(indent=2), encoding="utf-8")
        cur_md.write_text(render_topic_en(topic), encoding="utf-8")

        # Spanish Obsidian view (a view, not the source of truth), under Temas/.
        obsidian_topic = paths.obsidian_topic_file(topic.topic_id)
        obsidian_topic.parent.mkdir(parents=True, exist_ok=True)
        obsidian_topic.write_text(render_topic_es(topic), encoding="utf-8")
        return cur_md

    # -- ledger ------------------------------------------------------------------
    def _next_ledger_id(self, when: str) -> str:
        year = (when or _date.today().isoformat())[:4]
        n = 0
        if self.ledger.is_file():
            n = sum(1 for _ in self.ledger.open(encoding="utf-8"))
        return f"KD-{year}-{n + 1:05d}"

    def append_delta(self, delta: KnowledgeDelta) -> str:
        """Append one delta to the append-only ledger; returns its ledger id (KD-YYYY-NNNNN)."""
        self.ledger.parent.mkdir(parents=True, exist_ok=True)
        ledger_id = self._next_ledger_id(delta.date)
        record = {"ledger_id": ledger_id, **delta.model_dump()}
        with self.ledger.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        return ledger_id
