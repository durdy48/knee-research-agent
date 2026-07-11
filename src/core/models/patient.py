"""Patient, Persona and Personal Goals — the personal context (never changes the science)."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class PatientProfile(BaseModel):
    """Relatively stable clinical facts about the person (the 'Estables')."""

    age: Optional[int] = None
    sex: Optional[str] = None
    injury_history: List[str] = Field(default_factory=list)
    surgeries: List[str] = Field(default_factory=list)
    diagnoses: List[str] = Field(default_factory=list)


class PatientVariables(BaseModel):
    """Things that change over time (the 'Variables'), so KRA evolves with the person."""

    pain: Optional[str] = None
    weight_kg: Optional[float] = None
    strength: Optional[str] = None
    activity_frequency: Optional[str] = None  # e.g. padel twice a week
    current_treatments: List[str] = Field(default_factory=list)
    last_mri: Optional[str] = None
    updated: str = ""


class Persona(BaseModel):
    """Consumption preferences (kept separate from clinical facts)."""

    language: str = "es"
    report_cadence: str = "monthly"
    technical_level: str = "high"
    priorities: List[str] = Field(default_factory=list)


class PersonalGoals(BaseModel):
    goals: List[str] = Field(default_factory=list)


class PersonalContext(BaseModel):
    patient: PatientProfile = Field(default_factory=PatientProfile)
    variables: PatientVariables = Field(default_factory=PatientVariables)
    persona: Persona = Field(default_factory=Persona)
    goals: PersonalGoals = Field(default_factory=PersonalGoals)
