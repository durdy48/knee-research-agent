"""Personal Insight generation — the monthly '¿Ha cambiado algo para mí?' view.

Application orchestration: load the Patient Profile (infrastructure/disk), the consolidated
topics and the month's Knowledge Deltas, run the pure Personal Insight Engine (core), and
render a Spanish, patient-facing Markdown to reports/YYYY-MM-insights.md.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from core.insight import PersonalInsightEngine, PersonalInsightReport
from core.models import PersonalContext
from core.storage import paths
from infrastructure.repositories.knowledge_store import KnowledgeStore


def load_context() -> PersonalContext:
    f = paths.root() / "patient" / "profile.json"
    if not f.is_file():
        return PersonalContext()
    return PersonalContext.model_validate(json.loads(f.read_text(encoding="utf-8")))


def _month_deltas_by_topic(month: str) -> Dict[str, List[dict]]:
    out: Dict[str, List[dict]] = {}
    f = paths.ledger_file()
    if not f.is_file():
        return out
    for line in f.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        d = json.loads(line)
        if (d.get("date") or "").startswith(month):
            out.setdefault(d["topic_id"], []).append(d)
    return out


def _render_es(rep: PersonalInsightReport) -> str:
    lines = [
        f"# ¿Ha cambiado algo para mí? — {rep.month}",
        "",
        f"**{rep.state_message}**",
        "",
        "## Lo más relevante para ti este mes",
        "",
    ]
    if rep.items:
        for it in rep.items:
            lines.append(f"- {it.message}  _(relevancia {it.relevance})_")
    else:
        lines.append("- No hay cambios en la evidencia que afecten a tu caso este mes.")
    lines += ["", "## Acciones sugeridas", ""]
    lines += [f"- {a}" for a in rep.suggested_actions]
    lines += [
        "",
        "## Confianza para ti",
        "",
        ("_Pendiente de cálculo (Confidence for You): una confianza específica para tu perfil, "
         "distinta de la del tema._" if rep.per_profile_confidence is None
         else f"{rep.per_profile_confidence:.2f}"),
        "",
        "---",
        "",
        f"> {rep.disclaimer}",
        "",
    ]
    return "\n".join(lines)


def generate_personal_insights(month: str) -> Path:
    store = KnowledgeStore()
    ctx = load_context()
    by_topic = _month_deltas_by_topic(month)
    topics = [t for t in (store.load_topic(tid) for tid in by_topic) if t is not None]

    report = PersonalInsightEngine().generate(month, topics, by_topic, ctx)

    out_dir = paths.ensure(paths.root() / "reports")
    out = out_dir / f"{month}-insights.md"
    out.write_text(_render_es(report), encoding="utf-8")
    return out
