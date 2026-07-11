"""Personal Insight Engine — connects consolidated knowledge to the person (pure domain).

It answers one concrete question: **"Given all the available scientific evidence, what has
actually changed for me?"** It never changes the science (Golden Rule 3) and never
prescribes (Golden Rule 5) — it highlights relevance and suggests prudent, non-directive
next steps, always deferring to a healthcare professional.

Relevance is a simple, transparent, adjustable score:

    Relevance = mean(Clinical Match, Goal Match, Evidence Strength, Novelty)

where Clinical Match covers the person's conditions *and* their current treatments, so a
change to a treatment you are on lifts relevance (and can turn the monthly state red).

Output includes the fixed "¿Ha cambiado algo para mí?" indicator with three states
(green / yellow / red). "Confidence for You" (a per-profile confidence) is left as a
prepared placeholder — distinct from the Topic's confidence.
"""
from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from typing import List, Optional

from core.models import ClinicalTopic, PersonalContext

DISCLAIMER = (
    "KRA mejora tu comprensión de la evidencia; no diagnostica, no prescribe y no sustituye "
    "el criterio de un profesional sanitario. Las decisiones son siempre tuyas y de tu médico."
)

# Bilingual (ES↔EN) keyword lexicon per topic. The patient writes their profile in Spanish
# but topic names are in English, so plain name matching never fires. This curated,
# transparent map is the source of the personal match — extend it as topics evolve.
# Keep entries accent-free and lowercase (profile text is normalised the same way).
TOPIC_KEYWORDS = {
    "TOPIC-PRP": {
        "prp", "plasma rico en plaquetas", "plaquetas", "factores de crecimiento",
        "platelet", "platelet-rich plasma", "growth factors",
    },
    "TOPIC-MESENCHYMAL-STEM-CELLS": {
        "celulas madre", "celulas madre mesenquimales", "madre mesenquimales", "mesenquimales",
        "mesenchymal", "stem cells", "mesenchymal stem cells",
    },
    "TOPIC-CARTILAGE-REGENERATION": {
        "cartilago", "regeneracion de cartilago", "condral", "lesion condral", "condrocitos",
        "condropatia", "condromalacia", "microfractura",
        "cartilage", "chondral", "chondrocyte", "microfracture", "osteochondral",
    },
    "TOPIC-MENISCUS-REPAIR-SCAFFOLD": {
        "menisco", "meniscal", "rotura de menisco", "sutura meniscal", "meniscectomia",
        "reparacion meniscal", "meniscus", "meniscus repair", "scaffold",
    },
    "TOPIC-EARLY-KNEE-OSTEOARTHRITIS": {
        "artrosis", "artrosis precoz", "artrosis temprana", "osteoartritis", "gonartrosis",
        "desgaste articular", "osteoarthritis", "early osteoarthritis", "knee osteoarthritis",
    },
    "TOPIC-EXERCISE-&-REHABILITATION": {
        "ejercicio", "rehabilitacion", "fisioterapia", "fortalecimiento", "cuadriceps",
        "propiocepcion", "exercise", "rehabilitation", "rehab", "physiotherapy", "strengthening",
    },
    "TOPIC-CLINICAL-GUIDELINES-&-SYSTEMATIC-REVIEWS": {
        "guia clinica", "guias clinicas", "recomendaciones", "revision sistematica",
        "guideline", "guidelines", "systematic review", "recommendations",
    },
}

# Goal keywords that signal an active lifestyle, and topic terms that serve such goals.
_ACTIVITY_HINTS = ("activ", "deporte", "sport", "padel", "correr", "running", "gimnasio",
                   "gym", "senderismo", "montana", "bici", "ciclismo", "caminar")
_ACTIVITY_TOPIC_HINTS = ("exercise", "ejercicio", "rehab", "cartilage", "cartilago",
                         "meniscus", "menisco", "early", "artrosis")


def _norm(s: str) -> str:
    """Lowercase and strip accents so 'Pádel'/'padel' and 'Menisco'/'menisco' compare equal."""
    s = unicodedata.normalize("NFKD", (s or "").lower())
    return "".join(c for c in s if not unicodedata.combining(c)).strip()


def _topic_terms(topic: ClinicalTopic) -> set:
    """The normalised terms that identify a topic: its name plus its bilingual aliases."""
    terms = {_norm(topic.name)}
    terms |= {_norm(k) for k in TOPIC_KEYWORDS.get(topic.topic_id, set())}
    return {t for t in terms if t}


def _matches(values: List[str], terms: set) -> bool:
    """True if any profile value overlaps any topic term (substring, accent-insensitive)."""
    for v in values:
        nv = _norm(v)
        if not nv:
            continue
        if any(t in nv or nv in t for t in terms):
            return True
    return False


def _is_active(values: List[str]) -> bool:
    blob = " ".join(_norm(v) for v in values)
    return any(h in blob for h in _ACTIVITY_HINTS)


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


def _clinical_match(terms: set, ctx: PersonalContext) -> float:
    # A topic is clinically relevant if it concerns one of the person's conditions
    # (diagnoses / injury history / surgeries) OR a treatment they are currently on — a
    # change to your own treatment matters to you, so it should lift relevance too.
    facts = (ctx.patient.diagnoses + ctx.patient.injury_history + ctx.patient.surgeries
             + ctx.variables.current_treatments)
    if not any(f.strip() for f in facts if f):
        return 0.5  # unknown profile -> neutral, honest
    return 1.0 if _matches(facts, terms) else 0.3


def _goal_match(terms: set, ctx: PersonalContext) -> float:
    goals = ctx.goals.goals
    if not any(g.strip() for g in goals if g):
        return 0.5
    if _matches(goals, terms):
        return 1.0
    blob = " ".join(terms)
    if _is_active(goals) and any(h in blob for h in _ACTIVITY_TOPIC_HINTS):
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

        for t in topics:
            ds = deltas_by_topic.get(t.topic_id, [])
            if not ds:
                continue
            impacts = {d.get("impact") for d in ds}
            terms = _topic_terms(t)
            relevance = round(sum([
                _clinical_match(terms, ctx), _goal_match(terms, ctx),
                float(t.confidence), _novelty(impacts),
            ]) / 4, 3)

            if "Contradiction" in impacts:
                msg = (f"Se mantiene o aparece una controversia en {t.name}; no hay evidencia "
                       "suficiente para cambiar la estrategia actual.")
                # Red only if it touches a treatment the person is currently on.
                if _matches(ctx.variables.current_treatments, terms):
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
