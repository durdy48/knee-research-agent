"""KnowledgeDelta — the immutable record of one change to a Clinical Topic.

See docs/knowledge/KNOWLEDGE_DELTAS.md. A Delta is the difference between two Topic
Versions PLUS its justification and provenance. The ordered log of all Deltas is the
Knowledge Ledger.
"""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .enums import Impact


class KnowledgeDelta(BaseModel):
    """One auditable change to a Topic. Written once, never edited."""

    model_config = ConfigDict(use_enum_values=True)

    delta_id: str
    topic_id: str
    date: str = ""
    impact: Impact = Impact.new
    what_changed: str = ""
    why: str = ""
    evidence: List[str] = Field(default_factory=list)  # DOIs / PMIDs / paper ids
    confidence_before: Optional[float] = None
    confidence_after: Optional[float] = None
    controversy_changes: List[str] = Field(default_factory=list)
    from_version: Optional[int] = None
    to_version: Optional[int] = None
    produced_by: str = ""
    immutable: bool = True
