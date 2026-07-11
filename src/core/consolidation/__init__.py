"""Knowledge Consolidation Engine — the intellectual heart of KRA (pure domain logic).

Turns validated PaperReviews into an updated Living Clinical Topic + a KnowledgeDelta,
deterministically and with history preserved. See docs/knowledge/.
"""
from __future__ import annotations

from .components import (
    ConfidenceCalculator,
    ConsensusBuilder,
    ControversyManager,
    DeltaGenerator,
    EventLog,
    EvidenceMerger,
    MergedEvidence,
)
from .engine import ConsolidationResult, KnowledgeConsolidationEngine

__all__ = [
    "KnowledgeConsolidationEngine",
    "ConsolidationResult",
    "EvidenceMerger",
    "ConsensusBuilder",
    "ControversyManager",
    "ConfidenceCalculator",
    "DeltaGenerator",
    "EventLog",
    "MergedEvidence",
]
