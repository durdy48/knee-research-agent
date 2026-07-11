#!/usr/bin/env python3
"""Personal Insight Engine tests — relevance, the 3-state indicator, and safety.

Pure-domain tests (no disk) plus an integration render if the knowledge base exists.
Run: python3 src/tests/test_personal_insights.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.insight import PersonalInsightEngine  # noqa: E402
from core.models import ClinicalTopic, PersonalContext  # noqa: E402
from core.models.patient import PatientProfile, PatientVariables, PersonalGoals  # noqa: E402
from core.storage import paths  # noqa: E402


def _topic(tid, name, conf=0.6):
    return ClinicalTopic(topic_id=tid, name=name, confidence=conf)


def test_states_and_safety() -> None:
    eng = PersonalInsightEngine()
    topics = [_topic("TOPIC-PRP", "PRP"), _topic("TOPIC-EXERCISE", "Exercise & Rehabilitation")]

    # Green: no deltas this month.
    g = eng.generate("2026-07", topics, {}, PersonalContext())
    assert g.state == "green" and not g.items

    # Yellow: new evidence, no profile match to a treatment.
    deltas = {"TOPIC-PRP": [{"impact": "Contradiction"}], "TOPIC-EXERCISE": [{"impact": "New"}]}
    y = eng.generate("2026-07", topics, deltas, PersonalContext())
    assert y.state == "yellow" and len(y.items) == 2
    # Never prescriptive; always defers to a professional; disclaimer present.
    joined = " ".join(y.suggested_actions) + " " + y.disclaimer
    assert "traumatólogo" in joined or "profesional" in joined
    assert "no sustituye" in y.disclaimer
    assert y.per_profile_confidence is None  # 'Confidence for You' is a prepared placeholder

    # Red: a contradiction that touches a treatment the person is currently on.
    ctx = PersonalContext(variables=PatientVariables(current_treatments=["PRP"]))
    r = eng.generate("2026-07", topics, {"TOPIC-PRP": [{"impact": "Contradiction"}]}, ctx)
    assert r.state == "red"


def test_relevance_prefers_matching_profile() -> None:
    eng = PersonalInsightEngine()
    topics = [_topic("TOPIC-PRP", "PRP", 0.6), _topic("TOPIC-EXERCISE", "Exercise & Rehabilitation", 0.6)]
    deltas = {"TOPIC-PRP": [{"impact": "New"}], "TOPIC-EXERCISE": [{"impact": "New"}]}
    ctx = PersonalContext(goals=PersonalGoals(goals=["seguir activo y jugando al pádel"]))
    rep = eng.generate("2026-07", topics, deltas, ctx)
    # Exercise should rank at least as relevant as PRP for an activity goal.
    top = rep.items[0].topic
    assert top in ("Exercise & Rehabilitation", "PRP")
    ex = next(i for i in rep.items if i.topic.startswith("Exercise"))
    prp = next(i for i in rep.items if i.topic == "PRP")
    assert ex.relevance >= prp.relevance


def test_render_if_knowledge_exists() -> None:
    if not paths.ledger_file().is_file():
        return
    from application.use_cases.personal_insights import generate_personal_insights
    out = generate_personal_insights("2026-07")
    text = out.read_text(encoding="utf-8")
    assert "¿Ha cambiado algo para mí?" in text
    assert "Acciones sugeridas" in text
    assert "no sustituye" in text


def main() -> int:
    test_states_and_safety()
    test_relevance_prefers_matching_profile()
    test_render_if_knowledge_exists()
    print("OK — personal insight test passed (states + relevance + safety + render)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
