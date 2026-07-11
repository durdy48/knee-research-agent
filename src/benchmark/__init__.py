"""Benchmark harness — measures whether the system produces reliable knowledge.

Domain-agnostic runner + metrics that compare the system's output against a curated Gold
Standard. Swap the reviewer (model) to compare models objectively.
"""
from __future__ import annotations

from .dataset import GoldEntry, GoldStandard, GoldTopic, load_dataset
from .metrics import (
    BenchmarkResult,
    EntryResult,
    evaluate_entry,
    evaluate_entry_full,
    evaluate_topic,
)
from .runner import BenchmarkRunner

__all__ = [
    "GoldEntry",
    "GoldStandard",
    "GoldTopic",
    "load_dataset",
    "BenchmarkResult",
    "EntryResult",
    "evaluate_entry",
    "evaluate_entry_full",
    "evaluate_topic",
    "BenchmarkRunner",
]
