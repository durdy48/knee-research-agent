"""Living Topic renderers — the canonical English view and the Spanish Obsidian view.

The ClinicalTopic object is the source of truth. ``render_topic_en`` is the canonical
knowledge/en/ view; ``render_topic_es`` is the human-facing Obsidian view (Spanish section
structure). Obsidian is a view, never the source of truth (per the design conversation).
"""
from __future__ import annotations

from core.models import ClinicalTopic


def _confidence_band(c: float) -> str:
    if c >= 0.75:
        return "high"
    if c >= 0.4:
        return "moderate"
    return "low"


def render_topic_en(topic: ClinicalTopic) -> str:
    lines = [
        f"# {topic.name}",
        "",
        f"**Topic:** {topic.topic_id}  ",
        f"**Version:** v{topic.version}  ",
        f"**Confidence:** {topic.confidence:.2f} ({_confidence_band(topic.confidence)})  ",
        f"**Last updated:** {topic.last_updated or ''}",
        "",
        "## Consensus",
        "",
        topic.current_scientific_consensus or topic.consensus or "_Not yet established._",
        "",
        "## Controversies",
        "",
    ]
    if topic.controversies:
        for c in topic.controversies:
            lines += [
                f"### {c.question}",
                f"- Resolution level: **{c.resolution_level}**",
                f"- Supporting: {', '.join(c.supporting_studies) or '—'}",
                f"- Contradicting: {', '.join(c.contradicting_studies) or '—'}",
                (f"- Possible explanations: {', '.join(c.possible_explanations)}"
                 if c.possible_explanations else ""),
                "",
            ]
    else:
        lines += ["_No open controversies._", ""]
    lines += [
        "## Supporting evidence",
        "",
        *([f"- {s}" for s in topic.supporting_evidence] or ["_None yet._"]),
        "",
        "## Contradicting evidence",
        "",
        *([f"- {s}" for s in topic.contradicting_evidence] or ["_None yet._"]),
        "",
        "## Open questions",
        "",
        *([f"- {q}" for q in topic.open_questions] or ["_None tracked._"]),
        "",
        "## Recent changes",
        "",
        *([f"- {e.date}: {e.impact} (confidence {e.confidence_before} -> {e.confidence_after})"
           for e in topic.events] or ["_No changes yet._"]),
        "",
    ]
    return "\n".join(x for x in lines if x is not None)


def render_topic_es(topic: ClinicalTopic) -> str:
    """Spanish Obsidian view. Section structure per the Clinical Topic template (Spanish);
    data is carried over from the canonical topic. Full translation/enrichment of the prose
    is a later step (it must never change the scientific conclusion)."""
    band = {"high": "alta", "moderate": "moderada", "low": "baja"}[_confidence_band(topic.confidence)]
    lines = [
        f"# {topic.name}",
        "",
        f"> Vista en español (Obsidian). La fuente de verdad es `knowledge/en/`.",
        "",
        f"**Tema:** {topic.topic_id} · **Versión:** v{topic.version} · "
        f"**Confianza:** {topic.confidence:.2f} ({band})",
        "",
        "## Consenso",
        "",
        topic.current_scientific_consensus or topic.consensus or "_Aún no establecido._",
        "",
        "## Controversias",
        "",
    ]
    if topic.controversies:
        for c in topic.controversies:
            lines += [
                f"### {c.question}",
                f"- Nivel de resolución: **{c.resolution_level}**",
                f"- A favor: {', '.join(c.supporting_studies) or '—'}",
                f"- En contra: {', '.join(c.contradicting_studies) or '—'}",
                "",
            ]
    else:
        lines += ["_Sin controversias abiertas._", ""]
    lines += [
        "## Preguntas abiertas",
        "",
        *([f"- {q}" for q in topic.open_questions] or ["_Ninguna en seguimiento._"]),
        "",
        "## Cambios recientes",
        "",
        *([f"- {e.date}: {e.impact} (confianza {e.confidence_before} -> {e.confidence_after})"
           for e in topic.events] or ["_Sin cambios todavía._"]),
        "",
    ]
    return "\n".join(lines)
