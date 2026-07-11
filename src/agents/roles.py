"""Role registry.

The behaviour contract for each role lives in agents/roles/<name>.md. A role can be
executed by any model, a script or a human (ADR-0001, Principle 7). This registry maps
role names to the pipeline stage that currently realises them in the MVP; stages whose
intelligence is not yet automated are marked as "manual" / None.
"""
from __future__ import annotations

from core.pipeline import stages

ROLES = {
    "research-coordinator": {"spec": "agents/roles/research-coordinator.md", "stage": None},
    "literature-collector": {"spec": "agents/roles/literature-collector.md", "stage": "ingest (manual selection)"},
    "paper-reviewer": {"spec": "agents/roles/paper-reviewer.md", "stage": stages.review},
    "evidence-evaluator": {"spec": "agents/roles/evidence-evaluator.md", "stage": None},
    "knowledge-consolidator": {"spec": "agents/roles/knowledge-consolidator.md", "stage": stages.consolidate},
    "change-analyzer": {"spec": "agents/roles/change-analyzer.md", "stage": None},
    "knowledge-diff-generator": {"spec": "agents/roles/knowledge-diff-generator.md", "stage": None},
    "version-manager": {"spec": "agents/roles/version-manager.md", "stage": "topics.snapshot"},
    "medical-writer": {"spec": "agents/roles/medical-writer.md", "stage": stages.report},
    "personal-insight-generator": {"spec": "agents/roles/personal-insight-generator.md", "stage": stages.insight},
}
