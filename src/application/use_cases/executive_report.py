"""Executive Report generator — a reproducible monthly view over the Knowledge Ledger.

Reads the month's Knowledge Deltas (knowledge/ledger.jsonl), the current Living Topics
(knowledge/en/) and, if given, the ResearchRun metrics, and writes reports/YYYY-MM.md in
Spanish (patient-facing). Five fixed sections: resumen, cambios por tema, controversias,
preguntas de investigación, métricas. Deterministic — same inputs, same report.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from application.use_cases.consolidate_knowledge import area_to_topic_id
from benchmark import load_dataset
from core.models import Paper
from core.storage import paths
from infrastructure.ai import ManualAIProvider
from infrastructure.repositories.knowledge_store import KnowledgeStore


def _read_ledger(month: str) -> List[dict]:
    f = paths.ledger_file()
    if not f.is_file():
        return []
    out = []
    for line in f.read_text(encoding="utf-8").splitlines():
        if line.strip():
            d = json.loads(line)
            if (d.get("date") or "").startswith(month):
                out.append(d)
    return out


def _open_questions_for(area: str, provider: ManualAIProvider, gold) -> List[str]:
    qs: List[str] = []
    for e in gold.curated():
        if e.area != area:
            continue
        review = provider.review(Paper(paper_id=e.gold_id, title=e.title, doi=e.doi,
                                       pmid=e.pmid, study_type=e.study_type, topics=[e.area]))
        for q in review.open_questions:
            if q and q not in qs:
                qs.append(q)
    return qs


def generate_executive_report(month: str, *, run_dir: Optional[Path] = None,
                              out_dir: Optional[Path] = None) -> Path:
    gold = load_dataset(name="gold-standard")
    provider = ManualAIProvider(paths.runs_dir() / "manual" / "reviews")
    store = KnowledgeStore()
    id_to_area = {area_to_topic_id(a): a for a in {e.area for e in gold.curated()}}

    deltas = _read_ledger(month)
    by_topic: Dict[str, List[dict]] = {}
    for d in deltas:
        by_topic.setdefault(d["topic_id"], []).append(d)

    topics = {tid: store.load_topic(tid) for tid in by_topic}
    n_topics = len(by_topic)
    n_deltas = len(deltas)
    papers = sorted({e for d in deltas for e in d.get("evidence", [])})
    controversies = [(tid, c) for tid, t in topics.items() if t
                     for c in t.controversies]

    lines: List[str] = [f"# Informe ejecutivo — {month}", "",
                        "_Generado por KRA a partir del Knowledge Ledger (fuente de verdad: `knowledge/en/`)._", ""]

    # 1. Resumen ejecutivo
    lines += ["## Resumen ejecutivo", ""]
    resumen = [f"En {month} se actualizaron **{n_topics} temas** con **{n_deltas} cambios de "
               f"conocimiento** (Knowledge Deltas), sobre **{len(papers)} estudios**."]
    if controversies:
        resumen.append(f"Se mantienen **{len(controversies)} controversia(s) abierta(s)**, "
                       "que el sistema preserva en lugar de resolver prematuramente.")
    else:
        resumen.append("No hay controversias abiertas este mes.")
    resumen.append("Cada cambio es trazable a su evidencia y a la regla de confianza aplicada.")
    lines += [" ".join(resumen), ""]

    # 2. Cambios por tema
    lines += ["## Cambios por tema", ""]
    for tid, ds in by_topic.items():
        t = topics.get(tid)
        name = t.name if t else tid
        ver = f" (v{t.version})" if t else ""
        lines.append(f"### {name}{ver}")
        for d in ds:
            cb, ca = d.get("confidence_before"), d.get("confidence_after")
            lines.append(f"- **{d.get('impact')}** — {d.get('what_changed')} "
                         f"(confianza {cb} → {ca}); evidencia: {', '.join(d.get('evidence', [])) or '—'}")
        lines.append("")

    # 3. Controversias abiertas
    lines += ["## Controversias abiertas", ""]
    if controversies:
        for tid, c in controversies:
            name = topics[tid].name if topics.get(tid) else tid
            lines += [f"### {name}: {c.question}",
                      f"- Nivel de resolución: **{c.resolution_level}**",
                      f"- A favor: {len(c.supporting_studies)} · En contra: {len(c.contradicting_studies)}",
                      ""]
    else:
        lines += ["_Ninguna._", ""]

    # 4. Preguntas de investigación
    lines += ["## Preguntas de investigación", ""]
    open_qs: List[str] = []
    for tid in by_topic:
        area = id_to_area.get(tid)
        if area:
            open_qs += [q for q in _open_questions_for(area, provider, gold) if q not in open_qs]
    if open_qs:
        lines += [f"- {q}" for q in open_qs] + [""]
    else:
        lines += ["_Ninguna registrada._", ""]

    # 5. Métricas de la ejecución
    lines += ["## Métricas de la ejecución", ""]
    lines += [f"- Temas actualizados: {n_topics}",
              f"- Knowledge Deltas: {n_deltas}",
              f"- Estudios implicados: {len(papers)}"]
    if run_dir is not None:
        mf = run_dir / "manifest.json"
        if mf.is_file():
            m = json.loads(mf.read_text(encoding="utf-8"))
            lines.append(f"- Ejecución: {m.get('run_id')} ({m.get('started')} → {m.get('finished')})")
    lines += ["- Coste: $0.00 · Proveedor: manual", ""]

    dest = paths.ensure(out_dir if out_dir is not None else paths.root() / "reports")
    out = dest / f"{month}.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out
