"""LocalAbstractSource — read real, human-provided abstracts from disk.

Abstracts are NOT fabricated by the system. A human pastes the real abstract text into
``sources/abstracts/<key>.txt`` (or ``.md``), where ``<key>`` is the paper's gold_id, PMID
or DOI (slashes replaced by underscores). This adapter looks the file up; if none exists it
returns None and the reviewer proceeds on metadata alone, flagging needs_full_text_confirmation.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

from core.storage import paths


def _slug(value: str) -> str:
    return value.replace("/", "_").replace("\\", "_").strip()


class LocalAbstractSource:
    def __init__(self, directory: Optional[Path] = None) -> None:
        self.directory = directory or (paths.root() / "sources" / "abstracts")

    def _candidates(self, keys: Iterable[Optional[str]]) -> Iterable[Path]:
        for key in keys:
            if not key:
                continue
            slug = _slug(str(key))
            for ext in (".txt", ".md"):
                yield self.directory / f"{slug}{ext}"

    def get(self, *keys: Optional[str]) -> Optional[str]:
        """Return the first abstract found for any of the given keys, else None."""
        for path in self._candidates(keys):
            if path.is_file():
                text = path.read_text(encoding="utf-8").strip()
                if text:
                    return text
        return None
