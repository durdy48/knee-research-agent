"""Personal Insight Engine — connects consolidated knowledge to the person (pure domain).

It answers one concrete question: **"Given all the available scientific evidence, what has
actually changed for me?"** It never changes the science (Golden Rule 3) and never
prescribes (Golden Rule 5) — it highlights relevance and suggests prudent, non-directive
next steps, always deferring to a healthcare professional.

Relevance is a simple, transparent, adjustable score:

    Relevance = mean(Clinical Match, Goal Match, Evidence Strength, Novelty)

Output includes the fixed "¿Ha cambiado algo para mí?" indicator with three states
(green / yellow / red). "Confidence for You" (a per-profile confidence) is left as a
prepared placeholder — distinct from the Topic's confidence.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from core.models import ClinicalTopic, PersonalContext

DISCLAIMER = (
    "KRA mejora tu comprensión de la evidencia; no diagnostica, no prescribe y no sustituye "
    "el criterio de un profesional sanitario. Las decisiones son siempre tuyas y de tu médico."
)

_ACTIVITY_HINTS = ("activ", "deporte", "sport", "padel", "pádel", "correr", "running")
_ACTIVITY_TOPICS = ("exercise", "rehab", "cartilage", "meniscus", "early")


@dataclass
class InsightItem:
    topic: str
    relevance: float
    message: str


@dataclass
class PersonalInsightReport:
    month: str
    state: str            # "green" | "yellow" | "red"
    state_message: str
    items: List[InsightItem] = field(default_factory=list)
    suggested_actions: List[str] = field(default_factory=list)
    per_profile_confidence: Optional[float] = None  # "Confidence for You" — placeholder
    disclaimer: str = DISCLAIMER


def _kw(values: List[str]) -> List[str]:
    return [v.lower() for v in values if v]


def _clinical_match(topic_text: str, ctx: PersonalContext) -> float:
    facts = _kw(ctx.patient.diagnoses + ctx.patient.injury_history + ctx.patient.surgeries)
    if not facts:
        return 0.5  # unknown profile -> neutral, honest
    return 1.0 if any(f in topic_text or topic_text in f for f in facts) else 0.3


def _goal_match(topic_text: str, ctx: PersonalContext) -> float:
    goals = _kw(ctx.goals.goals)
    active = any(h in g for g in goals for h in _ACTIVITY_HINTS)
    if not goals:
        return 0.5
    if any(g in topic_text for g in goals):
        return 1.0
    if active and any(t in topic_text for t in _ACTIVITY_TOPICS):
        return 0.8
    return 0.3


def _novelty(impacts: set) -> float:
    if "Contradiction" in impacts:
        return 1.0
    if "New" in impacts:
        return 0.8
    if "Reinforcement" in impacts:
        return 0.5
    return 0.0


class PersonalInsightEngine:
    def generate(self, month: str, topics: List[ClinicalTopic], deltas_by_topic: dict,
                 ctx: PersonalContext) -> PersonalInsightReport:
        items: List[InsightItem] = []
        red = False
        treatments = _kw(ctx.variables.current_treatments)

        for t in topics:
            ds = deltas_by_topic.get(t.topic_id, [])
            if not ds:
                continue
            impacts = {d.get("impact") for d in ds}
            text = f"{t.name}".lower()
            relevance = round(sum([
                _clinical_match(text, ctx), _goal_match(text, ctx),
                float(t.confidence), _novelty(impacts),
            ]) / 4, 3)

            if "Contradiction" in impacts:
                msg = (f"Se mantiene o aparece una controversia en {t.name}; no hay evidencia "
                       "suficiente para cambiar la estrategia actual.")
                # Red only if it touches a treatment the person is currently on.
                if any(tr in text for tr in treatments):
                    red = True
            else:
                msg = (f"Nueva evidencia en {t.name} que conviene seguir; todavía no modifica "
                       "el consenso.")
            items.append(InsightItem(t.name, relevance, msg))

        items.sort(key=lambda i: i.relevance, reverse=True)

        if not items:
            state, state_msg = "green", "🟢 No hay cambios relevantes para tu caso este mes."
        elif red:
            state, state_msg = "red", "🔴 Ha cambiado el consenso de forma potencialmente relevante para tu perfil."
        else:
            state, state_msg = "yellow", "🟡 Hay nueva evidencia que conviene seguir."

        actions: List[str] = []
        if items:
            watch = ", ".join(i.topic for i in items[:3])
            actions.append(f"Comenta con tu traumatólogo o especialista si estos avances aplican a tu caso.")
            actions.append(f"Merece la pena seguir monitorizando: {watch}.")
            actions.append("No hay evidencia suficiente para modificar tu estrategia actual por tu cuenta.")
        else:
            actions.append("Mantén tu estrategia actual; no hay novedades que lo justifiquen.")

        return PersonalInsightReport(
            month=month, state=state, state_message=state_msg,
            items=items, suggested_actions=actions,
        )
