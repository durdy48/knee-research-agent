# Knee Research Agent

**Version:** 1.0.0  
**Status:** Draft  
**Last Updated:** 2026-07-10

---

# 1. Vision

## Purpose

The purpose of this project is to build a long-term, evidence-based medical research system focused on knee osteoarthritis in young and active patients.

Rather than collecting papers or generating isolated summaries, the system continuously transforms scientific literature into structured knowledge that evolves as new evidence becomes available.

The final product is not software.

The final product is a living knowledge system that generates personalised, evidence-based insights for a specific patient profile.

---

## Mission

Transform scientific evidence into trustworthy understanding and evidence-based decision support.

The system helps users understand how medical knowledge evolves over time, identify relevant changes in scientific consensus, and prepare better-informed conversations with healthcare professionals.

The system never replaces medical advice or clinical judgement.

---

# 2. Guiding Principles

## Evidence First

Every conclusion must be supported by scientific evidence.

---

## Knowledge Over Documents

Knowledge is more valuable than storing documents.

Scientific publications are inputs.

Knowledge is the output.

---

## Topics Over Papers

Clinical Topics are the central knowledge entities.

Scientific papers continuously enrich those topics.

---

## Continuous Evolution

Knowledge is never finished.

Every research cycle may improve previous conclusions.

---

## Transparency

Every statement must be traceable back to its supporting evidence.

---

## Knowledge Integrity

The system must preserve the integrity of knowledge over time.

Conclusions may evolve, but previous states must remain traceable through version history and evidence references.

---

## Human-Centred

The project supports human decision making.

It never replaces healthcare professionals.

---

# 3. Foundational Concepts

## Living Clinical Topics

Clinical knowledge is organised around continuously evolving topics.

Examples include:

- PRP
- Stem Cells
- Meniscus Scaffold
- Cartilage Regeneration
- Early Knee Osteoarthritis

Scientific papers update topics.

Topics generate knowledge.

---

## Knowledge Graph

Knowledge should be interconnected.

Relationships between treatments, diseases, concepts, and evidence are considered first-class citizens.

---

## Personal Intelligence Layer

Scientific evidence remains objective.

Personalisation occurs only after evidence has been consolidated into knowledge.

Personal context influences relevance, never scientific conclusions.

The system separates three distinct levels of output:

- **Data** — a raw fact from a single study (e.g. "the sample was 240 patients").
- **Knowledge** — a consolidated conclusion across studies (e.g. "most studies show a moderate benefit in mild osteoarthritis").
- **Insight** — a personalised interpretation (e.g. "this is relevant for you because…").

Keeping these levels explicit prevents mixing facts with interpretations.

---

## Research Cycle

Each execution of the system performs the following lifecycle:

Scientific Literature

↓

Evidence Extraction

↓

Evidence Evaluation

↓

Knowledge Consolidation

↓

Personal Insight Generation

↓

Executive Report

---

## Knowledge Engine Layers

Acquire — Collect scientific literature, clinical trials and guidelines.

Understand — Extract claims, evaluate evidence quality and identify consensus or contradictions.

Knowledge — Maintain Living Clinical Topics and the interconnected knowledge graph.

Deliver — Generate executive reports, personal insights and specialist discussion points.

---

# 4. Scope

The initial version focuses on:

- Knee osteoarthritis
- Young patients (<50 years)
- Active lifestyle
- ACL injuries
- Meniscus injuries
- Cartilage regeneration
- Biological therapies
- Clinical trials
- Emerging treatments

Explicitly out of the current focus (to keep results specific):

- Prostheses in patients over 70
- Fractures
- General rheumatology
- Other joints (hip, ankle, hand, spine)

The more specific the focus, the better the results.

---

# 5. Expected Outcomes

The system continuously maintains:

- a trustworthy knowledge base
- living clinical topics
- monthly executive reports
- historical evidence
- personalised insights
- traceable conclusions

---

# 6. Non Goals

The system does not:

- diagnose diseases
- prescribe treatments
- replace medical professionals
- generate unsupported conclusions
- personalise scientific evidence
- hide uncertainty

---

# 7. Success Criteria

The project is successful if:

- knowledge continuously improves
- evidence remains traceable
- conclusions become increasingly reliable
- new research updates existing knowledge instead of creating duplication
- users gain better understanding of their condition
- users can have more informed conversations with healthcare professionals

---

# 8. Long-Term Vision

The long-term objective is to create a modular Personal Evidence Intelligence Platform capable of integrating multiple scientific databases, AI models, MCP servers, automation workflows and knowledge management systems while preserving a single trustworthy knowledge base.

---

## Relationship to Other Documents

The problem being solved is described in `PROBLEM_STATEMENT.md`.

The domain entities and relationships are defined in `DOMAIN_MODEL.md`.

Architectural decisions are documented in `docs/adr/`.
