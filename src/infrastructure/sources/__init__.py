"""Source adapters — where the reviewer's input text comes from.

The core never fetches literature itself; it depends on the ``LiteratureSearcher`` port and
on source adapters like these. ``LocalAbstractSource`` reads human-provided abstracts from
disk so the ClaudeAIReviewer can review real text (never fabricated). A real PubMed /
TomeSphere adapter will slot in here later behind the same idea.
"""
from __future__ import annotations

from .local_abstracts import LocalAbstractSource

__all__ = ["LocalAbstractSource"]
