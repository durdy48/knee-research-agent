# ADR-0001 — Project Philosophy and Foundational Principles

**Status:** Accepted  
**Date:** 2026-07-10  
**Decision Makers:** Project Owner, AI Architecture Team

---

# Context

The Knee Research Agent (KRA) is intended to become a long-term evidence-based knowledge platform focused initially on knee osteoarthritis in young and active patients.

The project is expected to evolve over many years.

Technologies, AI models, automation tools and data sources will inevitably change.

Without a clear architectural philosophy, the project risks gradually drifting away from its original purpose.

This Architecture Decision Record establishes the principles that every future design and implementation decision must preserve.

---

# Decision

The project adopts the following foundational principles.

These principles have priority over implementation convenience.

---

# Principle 1 — The Domain Comes First

The medical domain defines the system.

Technology never defines the domain.

If a technology imposes constraints that conflict with the domain model, the technology should be adapted or replaced.

---

# Principle 2 — Knowledge Is the Product

The project does not exist to collect papers.

The project exists to build trustworthy knowledge.

Scientific publications are inputs.

Knowledge is the product.

---

# Principle 3 — Evidence Before Opinion

Every conclusion must be supported by scientific evidence.

The system must never generate unsupported medical conclusions.

When evidence is weak or contradictory, uncertainty must be explicitly preserved.

---

# Principle 4 — Personalisation Never Changes Scientific Truth

Scientific knowledge remains objective.

Personalisation only determines relevance.

Patient characteristics, goals and preferences influence what is highlighted, but never alter the underlying evidence.

---

# Principle 5 — Traceability Is Mandatory

Every conclusion, report and insight must be traceable back to its supporting evidence.

Users should always be able to understand why the system reached a particular conclusion.

---

# Principle 6 — Knowledge Evolves

Scientific understanding is never final.

Every Research Cycle may strengthen, weaken or replace previous conclusions.

Historical knowledge must remain accessible.

Nothing should disappear without history.

---

# Principle 7 — Components Are Replaceable

No implementation technology owns the knowledge.

AI models, automation frameworks, MCP servers, note-taking applications and databases are replaceable components.

The domain model remains stable.

---

# Principle 8 — Humans Make Decisions

The platform supports informed decision-making.

It does not diagnose.

It does not prescribe treatment.

It does not replace healthcare professionals.

Its role is to improve understanding.

---

# Principle 9 — Documentation Is Part of the Product

Architecture, terminology and design decisions are first-class assets.

Documentation evolves together with the software.

A feature is not considered complete if its documentation is outdated.

---

# Principle 10 — Long-Term Thinking

Every architectural decision should favour long-term maintainability over short-term convenience.

The project is expected to remain useful for many years.

Temporary implementation shortcuts should never compromise the long-term integrity of the knowledge base.

---

# Consequences

Following these principles means that:

- Documentation is maintained before implementation diverges.
- Knowledge remains independent of specific technologies.
- Every AI component can be replaced.
- Personalisation never compromises scientific integrity.
- The knowledge base continuously improves instead of accumulating isolated summaries.
- Future contributors can understand the project by reading the documentation before reading the code.

---

# Future ADRs

Future Architecture Decision Records should only be created when a decision:

- changes the architecture,
- introduces a new domain concept,
- modifies an architectural principle,
- affects long-term maintainability.

Implementation details should not be recorded as ADRs.

---

# References

- `PROBLEM_STATEMENT.md`
- `SPECIFICATION.md`
- `DOMAIN_MODEL.md`
- `ARCHITECTURE.md`
- `GLOSSARY.md`