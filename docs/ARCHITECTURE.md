# Architecture

**Version:** 1.0.0  
**Status:** Stable  
**Last Updated:** 2026-07-10

---

# Purpose

This document describes the high-level architecture of the Knee Research Agent (KRA).

The architecture is intentionally technology-agnostic.

Its purpose is to define responsibilities, boundaries and information flow independently of implementation details.

Technology choices may evolve over time without changing the architecture.

---

# Architectural Vision

The Knee Research Agent is a **Knowledge Platform** rather than a traditional software application.

Its primary goal is not to store documents, but to continuously transform scientific literature into trustworthy, traceable and personalised knowledge.

Knowledge is treated as a living asset that evolves as new evidence becomes available.

---

# Architectural Principles

## Domain First

The domain model drives the architecture.

Technology never defines the domain.

---

## Evidence First

Every conclusion must be supported by scientific evidence.

No unsupported knowledge may exist in the system.

---

## Knowledge Before Documents

Documents are representations of knowledge.

Knowledge is the primary asset.

---

## Traceability by Design

Every conclusion, recommendation and report must be traceable back to its supporting evidence.

Transparency is mandatory.

---

## Knowledge Integrity

Knowledge evolves continuously.

Previous conclusions must never disappear without preserving their history.

Version control and historical snapshots preserve the evolution of scientific understanding.

---

## Replaceable Components

No technology owns the knowledge.

Every implementation component should be replaceable with minimal impact on the rest of the system.

---

## Human in the Loop

The platform supports informed decision-making.

It never replaces healthcare professionals or clinical judgement.

---

# Layered Architecture

The system is organised into independent responsibility layers.

```
┌─────────────────────────────────────────────┐
│                User Layer                   │
│                                             │
│ Reports · Search · Obsidian · Questions     │
└─────────────────────────────────────────────┘
                     ▲
                     │
┌─────────────────────────────────────────────┐
│         Personal Intelligence Layer         │
│                                             │
│ Patient Context · Goals · Relevance         │
└─────────────────────────────────────────────┘
                     ▲
                     │
┌─────────────────────────────────────────────┐
│              Knowledge Layer                │
│                                             │
│ Clinical Topics · Evidence · Consensus      │
│ Knowledge Graph · History                   │
└─────────────────────────────────────────────┘
                     ▲
                     │
┌─────────────────────────────────────────────┐
│             Processing Layer                │
│                                             │
│ Extraction · Evaluation · Consolidation     │
└─────────────────────────────────────────────┘
                     ▲
                     │
┌─────────────────────────────────────────────┐
│            Acquisition Layer                │
│                                             │
│ Scientific Sources                          │
└─────────────────────────────────────────────┘
```

Each layer has a single responsibility.

Higher layers never bypass lower layers.

---

# Knowledge Flow

Knowledge continuously evolves through the following lifecycle.

```
Scientific Literature

↓

Paper

↓

Claim

↓

Evidence

↓

Living Clinical Topic

↓

Knowledge Base

↓

Personal Insight

↓

Executive Report
```

Every transformation increases the level of abstraction while preserving traceability.

---

# Component Responsibilities

## Acquisition Layer

Responsible for discovering new scientific information.

Examples include:

- biomedical literature
- clinical trial registries
- clinical guidelines
- scientific news
- citation networks

The architecture does not depend on any specific provider.

---

## Processing Layer

Responsible for transforming raw information into structured evidence.

Responsibilities include:

- document ingestion
- claim extraction
- evidence evaluation
- contradiction detection
- quality assessment
- evidence normalisation

This layer never performs personalisation.

---

## Knowledge Layer

The core of the platform.

Responsible for maintaining:

- Living Clinical Topics
- consolidated knowledge
- evidence history
- consensus evolution
- knowledge relationships

This layer contains the current state of scientific understanding.

---

## Personal Intelligence Layer

Responsible for applying Personal Context to consolidated knowledge.

Inputs:

- Patient Profile
- Personal Goals
- Persona

Outputs:

- personalised insights
- relevance scoring
- specialist discussion points
- executive summaries

Scientific knowledge is never modified.

Only relevance changes.

---

## User Layer

Responsible for presenting information.

Possible interfaces include:

- Obsidian
- Executive Reports
- Search
- Dashboards
- Future web interfaces

Presentation never owns knowledge.

---

# Source of Truth

The architecture distinguishes between knowledge ownership and knowledge presentation.

| Asset | Source of Truth |
|--------|-----------------|
| Scientific evidence | Original publications |
| Consolidated knowledge | Version-controlled Markdown repository |
| Documentation | Git repository |
| Personal visualisation | Obsidian |
| Historical evolution | Git history |
| Personal context | Patient Profile |

The source of truth is never duplicated.

Views are disposable.

Knowledge is not.

---

# Component Independence

The architecture deliberately avoids coupling the system to any specific technology.

Examples of replaceable components include:

- AI models
- MCP servers
- literature providers
- note-taking applications
- automation engines
- report generators

Replacing one component must not require redesigning the domain.

---

# Architectural Boundaries

The architecture separates objective knowledge from personal interpretation.

```
Scientific Evidence
        │
        ▼
Consolidated Knowledge
        │
──────── Boundary ────────
        │
        ▼
Personal Context
        │
        ▼
Insights
```

Scientific facts remain objective.

Personalisation begins only after knowledge has been consolidated.

---

# Evolution Strategy

The architecture is designed for long-term evolution.

Expected future capabilities include:

- multiple AI agents
- additional medical domains
- knowledge graph reasoning
- longitudinal evidence analysis
- automated literature surveillance
- predictive evidence monitoring
- collaborative knowledge curation

These capabilities extend the architecture without changing its principles.

---

# Relationship to Other Documents

The problem space is defined in `PROBLEM_STATEMENT.md`.

Project objectives are described in `SPECIFICATION.md`.

Domain entities are defined in `DOMAIN_MODEL.md`.

Official terminology is maintained in `GLOSSARY.md`.

Architectural decisions are documented as ADRs.

Implementation guidelines are described in `CLAUDE.md`.