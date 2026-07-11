# Glossary

**Version:** 1.0.0
**Status:** Stable
**Last Updated:** 2026-07-11

---

> This document defines the **official language** of the project (its *ubiquitous
> language*). Every other document, prompt and — eventually — piece of code must use
> these terms with exactly these meanings.
>
> **Rule:** we do not invent a term if a consolidated one already exists in software
> engineering, knowledge management or medicine. We reuse the standard term. We only
> coin a new term when it genuinely adds clarity. When a new term appears, it is added
> here **first**, and only then used elsewhere.

---

## 1. Core Knowledge Model

**Paper**
An individual scientific publication (article, preprint, review). A paper is an
*input* to the system and is never, by itself, consolidated knowledge.

**Claim**

An atomic factual statement extracted from a single Paper.

Claims are the smallest unit of scientific information handled by the system.

Multiple Claims are evaluated together to produce consolidated Evidence.

Example:

"PRP reduced WOMAC score by 18%."

**Traceability**

The ability to connect every conclusion, insight or recommendation back to its supporting evidence and original scientific publications.

Traceability is mandatory throughout the system.

**Knowledge Integrity**

The principle that scientific knowledge must never lose its history.

Knowledge may evolve as new evidence appears, but previous conclusions remain traceable through version control and historical snapshots.

**Evidence Snapshot**

An immutable representation of the state of evidence for a Clinical Topic at a specific point in time.

Snapshots allow the system to compare how scientific consensus evolves across Research Cycles.

**Evidence**
Information extracted from one or more papers. Evidence is the bridge between a raw
paper and consolidated knowledge.

**Clinical Topic**
The central unit of knowledge. A continuously evolving subject that papers enrich over
time. Examples: PRP, Meniscus Scaffold, Early Knee Osteoarthritis. Also called a
*Living Clinical Topic*.

**Living Clinical Topic**
A Clinical Topic treated as a living document: it is never re-created, only updated as
new evidence arrives. See also *Living Document*.

**Knowledge**
A consolidated conclusion derived from evidence across multiple papers. Distinct from
*Data* (a single fact) and *Insight* (a personalised interpretation).

**Knowledge Base**
The complete set of all consolidated Clinical Topics. The system's persistent,
evolving understanding of the domain.

**Knowledge Graph**
The network of relationships between Clinical Topics, papers, treatments, diseases and
concepts. Relationships are treated as first-class, enabling an explorable graph
rather than a flat set of documents.

**Data (Level 1)**
A raw fact taken directly from a study. Example: "the sample was 240 patients."

**Knowledge (Level 2)**
A conclusion consolidated across studies. Example: "most studies show a moderate
benefit in mild osteoarthritis."

**Insight (Level 3)**
A personalised interpretation of consolidated knowledge for a specific individual.
Example: "this is relevant for you because you have post-traumatic osteoarthritis."

**Finding**
A newly detected discovery surfaced during a Research Cycle (e.g. a new trial, a new
paper that changes a topic).

**Evidence Update**
A change to a Clinical Topic caused by new evidence. The topic is updated; no duplicate
note is created.

**Open Question**
An unresolved question the system is tracking. When enough evidence answers it, it is
promoted into consolidated knowledge.

**Consensus**
The prevailing position across the strongest available evidence for a topic, at a
given point in time. Consensus can change between Research Cycles.

---

## 2. Evidence & Quality

**Evidence Level**
A rating of how strong a graded study's design is, on the 1–5 star scale (see below).
Applies to study designs that fit the scale (meta-analysis … expert opinion).

**Evidence Classification**
The *kind* of evidence rating a document deserves. Graded designs get a star level;
documents that do not fit the 1–5 scale get a categorical label. This distinction stops
the Quality Gates from wrongly rejecting valid non-graded documents.

| Document | Classification |
|-------------------------------|----------------|
| Meta-analysis / Systematic Review | ★★★★★ |
| Randomized Controlled Trial | ★★★★ |
| Cohort Study | ★★★ |
| Case-Control / Case Series | ★★ |
| Clinical Guideline / Position Statement | Consensus |
| Scoping / Narrative Review | Exploratory |

**Evidence Quality Scale**
The star scale used to rank graded study types:

| Stars | Study type |
|-------|-----------------------------|
| ★★★★★ | Meta-analysis |
| ★★★★★ | Systematic Review |
| ★★★★ | Randomized Controlled Trial |
| ★★★ | Cohort Study |
| ★★ | Case Series |
| ★ | Expert Opinion |

**Confidence**
How confident a conclusion is **for the specific individual's case**. Distinct from
*Evidence Level*: evidence can be strong in general (high Evidence Level) while
confidence for this patient is only moderate.

**Meta-analysis**
A study that statistically combines results from multiple studies. Highest evidence
level.

**Systematic Review**
A structured review that appraises all relevant studies on a question.

**Randomized Controlled Trial (RCT)**
An experimental study where participants are randomly assigned to groups.

**Cohort Study**
An observational study following groups over time.

**Case Series**
A report describing outcomes for a small group of patients, without a control group.

**Expert Opinion**
A position stated by an expert without supporting study data. Lowest evidence level.

---

## 3. Personalisation

**Patient**
The set of relatively stable clinical facts about the person: age, sex, injury
history, surgeries, diagnoses.

**Patient Profile**
The document holding the *Patient* facts. Changes slowly over time.

**Persona**
The set of consumption preferences: language, report cadence, level of technical
detail, what to prioritise. Kept separate from clinical facts so the system can serve
other users without mixing clinical data with preferences.

**Personal Goals**
The individual's objectives that guide relevance. Examples: delay a prosthesis, keep
playing padel, reduce pain, maintain strength, slow the progression of osteoarthritis.

**Personal Context**
The combination of Patient, Persona and Personal Goals used to compute relevance.

**Personal Intelligence Layer (PIL)**
The final layer of the system. It applies Personal Context to consolidated knowledge
to produce Insights. It never alters the underlying scientific evidence — only what is
relevant, highlighted and asked.

**Personal Relevance**
A rating of how relevant a piece of consolidated knowledge is to the individual, given
their Personal Context.

---

## 4. Process & Lifecycle

**Research Cycle**
One complete execution of the system (for example, monthly). It runs the full pipeline
from literature to executive report.

**Evidence Extraction**
The step that reads papers and extracts structured evidence.

**Evidence Evaluation**
The step that rates the quality and relevance of extracted evidence.

**Knowledge Consolidation**
The step that merges new evidence into existing Clinical Topics, updating conclusions
rather than duplicating them.

**Personal Insight Generation**
The step that applies the Personal Intelligence Layer to produce personalised insights.

**Personal Insight Engine**
The component (`src/core/insight/`) that answers "given all the evidence, what changed for
*me*?" using a transparent relevance score (Clinical Match + Goal Match + Evidence Strength
+ Novelty). It highlights relevance and suggests prudent next steps; it never changes the
science (Golden Rule 3) nor prescribes (Golden Rule 5).

**Patient Profile**
The person's context, in two parts: *Estables* (age, surgeries, diagnoses) and *Variables*
(pain, weight, strength, activity, current treatments, last MRI, goals). Kept in `patient/`.
Used only to weight relevance — never to change a scientific conclusion.

**Confidence for You**
A per-profile confidence (distinct from a Topic's Confidence): how strongly a consolidated
conclusion applies to the specific person. Currently a prepared placeholder.

**Executive Report**
The human-readable monthly output summarising what changed, what is worth monitoring,
and which questions to raise with a healthcare professional.

**Monthly Review**
An immutable, dated snapshot of the Executive Report for a given month.

**Impact Classification**
The Change Analyzer's assessment of how new Evidence affects a Clinical Topic. Exactly
one of: *New* (adds knowledge that did not exist), *Reinforcement* (strengthens the
existing consensus), *Contradiction* (conflicts with the existing consensus) or
*Irrelevant* (no meaningful effect).

**Knowledge Consolidator**
The component (design in `docs/knowledge/`) that turns many validated Evidence items about
one Clinical Topic into a single, confidence-weighted consensus plus explicit controversies,
preserving history. The "intellectual heart" of KRA; it works with knowledge, not papers.

**Knowledge Diff**
The *difference* between two versions of a Living Clinical Topic — what was added,
strengthened, weakened, contradicted or resolved. (The justified, provenance-bearing form of
this is the **Knowledge Delta**.)

**Knowledge Delta**
The immutable, human-readable record of one change to a Topic: what changed, why, on what
evidence, the confidence before/after, the controversy changes, the version link and who
(which workflow) produced it. The unit that makes knowledge evolution auditable. Design in
`docs/knowledge/KNOWLEDGE_DELTAS.md`; seeded by `EvolutionEvent` in the knowledge engine.

**Knowledge Ledger**
The append-only, ordered log of every Knowledge Delta across all Topics — KRA's complete
historical explainability. Not a blockchain; a faithful audit trail of how the knowledge base
reached its current state.

**Controversy**
A first-class object tracking an active disagreement about a specific claim: its supporting
studies, contradicting studies, possible explanations and *resolution level*. Never deleted;
preserved explicitly (Golden Rule 2). Design in `docs/knowledge/CONTROVERSY_MODEL.md`.

**Resolution Level**
The state of a Controversy: *open → emerging → contested → resolving → resolved* (a resolved
controversy may reopen with new contradicting evidence). Its history is always kept.

**Topic Version**
A dated state of a Living Clinical Topic. The live state is kept in `current.md`; past
states are preserved as Evidence Snapshots under `history/`, so knowledge evolves
without losing its history (Knowledge Integrity).

---

## 5. Document Types

**Living Document**
A document that is continuously updated and never considered finished. Example: a
Clinical Topic.

**Immutable Document**
A document that is written once and never changed, kept for history. Example: a
Monthly Review or an archived paper record.

**Specification (`SPECIFICATION.md`)**
The project contract: what we build and why, independent of technology.

**Glossary (`GLOSSARY.md`)**
This document. The official language of the project.

**Architecture (`ARCHITECTURE.md`)**
How the system works, including technology-specific decisions.

**ADR — Architecture Decision Record**
A dated record capturing an important decision: its context, the alternatives
considered, the decision taken, and its consequences. Stored under `docs/adr/`.

**Roadmap (`ROADMAP.md`)**
The delivery plan, organised into sprints.

**`CLAUDE.md`**
The operating manual for the AI agent (Claude Code): project purpose, style rules,
document conventions, folder structure and what an agent must never do.

---

## 6. Sources & Tooling

**PubMed**
Primary biomedical literature database; maximum biomedical coverage.

**ClinicalTrials.gov**
Registry of clinical trials, used to track studies in progress and recruiting.

**Semantic Scholar**
Source used to discover related work and follow citations.

**TomeSphere**
A platform that exposes scientific literature as agent-usable tools via MCP (search,
summarise, follow citations, retrieve full text and figures).

**MCP (Model Context Protocol)**
The protocol that lets an AI agent call external tools and data sources in a
standardised way.

**Obsidian**
The knowledge management application hosting the consolidated Knowledge Base as
interlinked Markdown notes. Content in Obsidian is written in Spanish.

**Ubiquitous Language**
The shared vocabulary — defined in this glossary — used consistently across
documentation, prompts and code, so the same word always means the same thing.

---

## 7. Medical Domain

**Knee Osteoarthritis (OA)**
Progressive degeneration of the knee joint cartilage. The primary domain of the
project.

**Post-traumatic Osteoarthritis**
Osteoarthritis that develops after a joint injury (e.g. after ACL or meniscus damage).

**ACL (Anterior Cruciate Ligament)**
A major stabilising ligament of the knee; its injury and reconstruction are within
scope.

**Meniscus**
The knee's cartilage cushions; injuries, repair, scaffolds and transplants are within
scope.

**Cartilage**
The joint surface tissue whose degeneration and regeneration are central to the domain.

**PRP (Platelet-Rich Plasma)**
An injectable biological treatment derived from the patient's own blood platelets.

**MSC (Mesenchymal Stem Cells)**
Stem cells (e.g. bone-marrow or adipose-derived) studied for cartilage repair.

**Scaffold**
A biomaterial structure used to support tissue regeneration; e.g. a *meniscus
scaffold*.

**MACI (Matrix-induced Autologous Chondrocyte Implantation)**
A cartilage repair technique using the patient's own cultured chondrocytes on a matrix.

**ACI (Autologous Chondrocyte Implantation)**
An earlier cartilage repair technique using the patient's own cultured chondrocytes.

**Osteotomy (High Tibial Osteotomy)**
A surgical realignment of the leg to offload the damaged part of the knee.

**WOMAC**
A standardised questionnaire scoring pain, stiffness and function in osteoarthritis.

**KOOS**
The Knee injury and Osteoarthritis Outcome Score, a standardised outcome measure.

**Kellgren-Lawrence**
A radiographic grading scale for the severity of osteoarthritis.

---

## 8. Benchmark & Evaluation

**Gold Standard**
The curated reference dataset used to benchmark the system: real, verifiable Gold Papers,
their canonical Gold Reviews and the expected Gold Topics. Human-curated (Principle 8).

**AI Provider**
A swappable adapter that implements the `AIReviewer` port and turns a Paper into a
PaperReview (e.g. `ClaudeAIReviewer`, plus `stub` and `fake` for key-free runs). Lets the
benchmark compare models without changing the rest of the system.

**Quality Gate**
A checkpoint between a produced PaperReview and the Benchmark that enforces the golden
rules before a review counts: every claim carries its supporting data (traceability),
study type and evidence level are assigned, and the review is non-empty.

**GRSS (Gold Review Similarity Score)**
The headline KPI: a weighted composite (0–100%) of how close a produced review is to the
Gold Review. It is **decomposed** into sub-scores — claims, grounding, controversies,
metadata, evidence, limitations and clinical relevance — so you can see *where* a reviewer
succeeds or fails, not just the aggregate.

**CDR (Controversy Detection Rate)**
The share of gold claims expressing controversy or a null result that the model recovers.
KRA's differentiating KPI: it measures whether the model preserves uncertainty rather than
flattening it. Reported separately from GRSS.

**UCR (Unsupported Claim Rate)**
The share of produced claims not corroborated by the Gold Review (a proxy for statements
not supported by the source). Lower is better; ideally 0%. Reported separately from GRSS.

## Naming Rules

The following conventions apply across the project:

- Domain entities are written in PascalCase.
- File names use UPPER_CASE or snake_case according to repository conventions.
- Clinical Topics are singular.
- Documents use British English.
- Obsidian notes are written in Spanish.