"""Gold Standard dataset models and loader (Pydantic).

The Gold Standard has three parts (see benchmark/gold_standard/README.md):
  - Gold Papers   : the selected articles (entries).
  - Gold Reviews  : the canonical review of each article (entry.gold_claims + metadata).
  - Gold Topics   : how a Living Clinical Topic should look after integrating the papers.
This lets the benchmark validate the whole pipeline, not just an isolated paper.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from core.storage import paths


class GoldClaim(BaseModel):
    text: str
    evidence_level: Optional[int] = None


class GoldEntry(BaseModel):
    """A Gold Paper + its canonical Gold Review."""

    gold_id: str
    area: str
    title: str
    doi: Optional[str] = None
    pmid: Optional[str] = None
    year: Optional[int] = None
    abstract: str = ""  # real source text for the reviewer; never fabricated (see sources/abstracts/)
    study_type: Optional[str] = None
    evidence_level: Optional[int] = None
    status: str = "curated"  # or "pending_curation" / "proposed"
    rationale: str = ""       # why this article was selected (human decision + motive)
    selected_by: str = ""     # who approved it (Principle 8: humans make decisions)
    gold_claims: List[GoldClaim] = Field(default_factory=list)


class GoldTopic(BaseModel):
    """The expected Living Clinical Topic after integrating the relevant papers."""

    topic_id: str
    name: str
    expected_consensus: str = ""
    min_confidence: float = 0.0
    max_confidence: float = 1.0
    key_claims: List[str] = Field(default_factory=list)
    from_papers: List[str] = Field(default_factory=list)  # gold_ids


class GoldStandard(BaseModel):
    name: str = "gold-standard"
    gold_version: str = "1.0"
    description: str = ""
    areas: Dict[str, int] = Field(default_factory=dict)
    entries: List[GoldEntry] = Field(default_factory=list)
    gold_topics: List[GoldTopic] = Field(default_factory=list)

    def curated(self) -> List[GoldEntry]:
        return [e for e in self.entries if e.status == "curated" and e.gold_claims]


def default_path(name: str = "gold-standard") -> Path:
    return paths.root() / "benchmark" / name.replace("-", "_") / "dataset.json"


def load_dataset(path: Optional[Path] = None, name: str = "gold-standard") -> GoldStandard:
    p = path or default_path(name)
    return GoldStandard.model_validate(json.loads(Path(p).read_text(encoding="utf-8")))
