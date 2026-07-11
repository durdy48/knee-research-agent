"""JsonPaperRepository — a PaperRepository backed by papers/registry.json.

The registry file is the Markdown/JSON view; the Paper objects are the source of truth.
Preserves the top-level registry keys (schema_version, id_conventions, states).
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import List, Optional

from core.models import Paper
from core.models.enums import PaperStatus
from core.ports.repositories import PaperRepository
from core.storage import paths


class JsonPaperRepository(PaperRepository):
    def __init__(self, registry_path: Optional[Path] = None) -> None:
        self._path = registry_path

    @property
    def path(self) -> Path:
        return self._path or paths.registry_file()

    def _load(self) -> dict:
        if self.path.exists():
            return json.loads(self.path.read_text(encoding="utf-8"))
        return {
            "schema_version": "1.0",
            "states": [s.value for s in PaperStatus],
            "papers": [],
        }

    def _write(self, data: dict) -> None:
        paths.ensure(self.path.parent)
        self.path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )

    def get(self, paper_id: str) -> Optional[Paper]:
        for p in self._load()["papers"]:
            if p["paper_id"] == paper_id:
                return Paper.model_validate(p)
        return None

    def save(self, paper: Paper) -> None:
        data = self._load()
        arr = data.setdefault("papers", [])
        entry = paper.model_dump(mode="json")
        for i, p in enumerate(arr):
            if p["paper_id"] == paper.paper_id:
                arr[i] = entry
                break
        else:
            arr.append(entry)
        self._write(data)

    def list_all(self) -> List[Paper]:
        return [Paper.model_validate(p) for p in self._load()["papers"]]

    def find_by_status(self, status: str) -> List[Paper]:
        return [Paper.model_validate(p) for p in self._load()["papers"] if p.get("status") == status]

    def next_id(self) -> str:
        year = date.today().year
        prefix = f"PAPER-{year}-"
        seqs = [
            int(p["paper_id"].rsplit("-", 1)[-1])
            for p in self._load()["papers"]
            if p["paper_id"].startswith(prefix)
        ]
        seq = (max(seqs) + 1) if seqs else 1
        return f"{prefix}{seq:04d}"
