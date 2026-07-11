"""Obsidian sync (ResearchRun Phase 4) — put the human-facing knowledge in one vault folder.

Writes the Spanish topic views AND the month's Executive Report + Personal Insight into the
Obsidian directory (`paths.obsidian_dir()`, configurable via `KRA_OBSIDIAN_DIR`). Obsidian is
a *view*, never the source of truth (that stays in `knowledge/en/`).
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from core.storage import paths
from infrastructure.renderers.topic_renderer import render_topic_es
from infrastructure.repositories.knowledge_store import KnowledgeStore


def sync_obsidian(month: Optional[str] = None) -> Path:
    store = KnowledgeStore()
    out = paths.obsidian_dir()
    out.mkdir(parents=True, exist_ok=True)

    # Vault layout mirrors the domain: Living Topics are persistent (updated in place),
    # monthly reports are immutable snapshots grouped by month.
    #   <vault>/Temas/<TOPIC>.md          (persistent, re-rendered each run)
    #   <vault>/Informes/<YYYY-MM>/...    (one folder per month, never overwritten across months)
    #   <vault>/README.md                 (navigable index at the root)
    paths.obsidian_temas_dir().mkdir(parents=True, exist_ok=True)

    # 1) Topic views (Spanish).
    tdir = paths.knowledge_en_dir()
    topic_ids: List[str] = [p.name for p in tdir.iterdir() if p.is_dir()] if tdir.is_dir() else []
    topics = [t for t in (store.load_topic(t) for t in topic_ids) if t is not None]
    for t in topics:
        paths.obsidian_topic_file(t.topic_id).write_text(render_topic_es(t), encoding="utf-8")

    # 2) The month's reports (Executive Report + Personal Insight), if they exist.
    reports = paths.root() / "reports"
    copied = []
    if month:
        month_dir = paths.obsidian_informes_dir(month)
        month_dir.mkdir(parents=True, exist_ok=True)
        for src_name, dst_name in [(f"{month}.md", f"Informe-{month}.md"),
                                   (f"{month}-insights.md", f"Insight-{month}.md")]:
            src = reports / src_name
            if src.is_file():
                (month_dir / dst_name).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
                copied.append(dst_name)

    # 3) An index so the vault folder is navigable.
    index = [
        "# Knee Research Agent — Base de conocimiento",
        "",
        "> Vista en Obsidian (español). La fuente de verdad es `knowledge/en/`.",
        "",
        "## Temas (Living Topics)",
        "",
        *[f"- [[{t.topic_id}]] — {t.name} (v{t.version}, confianza {t.confidence:.2f})" for t in topics],
        "",
        "## Informes del mes",
        "",
        *([f"- [[{c[:-3]}]]" for c in copied] or ["_Aún no hay informes de este mes._"]),
        "",
    ]
    (out / "README.md").write_text("\n".join(index), encoding="utf-8")
    return out
