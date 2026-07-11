"""Stable identifier helpers.

See papers/README.md for the conventions. Identifiers are stable so that hundreds of
documents can be referenced reliably over the life of the project.
"""
from __future__ import annotations

import re
from datetime import date


def paper_id(year: int, seq: int) -> str:
    return f"PAPER-{year}-{seq:04d}"


def claim_id(year: int, seq: int) -> str:
    return f"CLAIM-{year}-{seq:04d}"


def topic_id(name: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-").upper()
    return f"TOPIC-{slug}"


def report_id(year: int, month: int) -> str:
    return f"REPORT-{year}-{month:02d}"


def run_id(year: int, month: int, seq: int) -> str:
    return f"RUN-{year}-{month:02d}-{seq:03d}"


def topic_name(topic_id_value: str) -> str:
    """`TOPIC-PRP` -> `PRP`."""
    return topic_id_value.split("-", 1)[1] if "-" in topic_id_value else topic_id_value


def today() -> str:
    return date.today().isoformat()
