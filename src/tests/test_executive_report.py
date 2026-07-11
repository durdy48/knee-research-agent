#!/usr/bin/env python3
"""Executive Report tests — the monthly report is a reproducible view over the Ledger.

Integration-style: reads the real knowledge/ledger.jsonl, topics and reviews (skips if the
knowledge base has not been consolidated yet). Run: python3 src/tests/test_executive_report.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.storage import paths  # noqa: E402


def main() -> int:
    if not paths.ledger_file().is_file():
        print("SKIP — no ledger yet (run `kra run research` first)")
        return 0

    import tempfile

    from application.use_cases.executive_report import generate_executive_report

    # Read the real knowledge base, but write to a temp dir so the test never mutates
    # the repo's reports/ (this is an integration test, not a fixture).
    with tempfile.TemporaryDirectory() as tmp:
        out = generate_executive_report("2026-07", out_dir=Path(tmp))
        text = out.read_text(encoding="utf-8")
        for header in ["## Resumen ejecutivo", "## Cambios por tema", "## Controversias abiertas",
                       "## Preguntas de investigación", "## Métricas de la ejecución"]:
            assert header in text, f"missing section: {header}"
        assert "PRP" in text
        assert "Knowledge Deltas" in text
        # Determinism: same inputs -> identical report.
        assert generate_executive_report("2026-07", out_dir=Path(tmp)).read_text(encoding="utf-8") == text

    print("OK — executive report test passed (5 sections + reproducible)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
