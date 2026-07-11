# Gold Standard

The reference dataset used to benchmark KRA (`kra benchmark`). It lets us measure whether
any change to the system — a new model, a new prompt, a refactor — makes the knowledge
**better or worse**, objectively.

It has **three parts** so it validates the *whole pipeline*, not just an isolated paper:

- **Gold Papers** — the selected articles (`entries`).
- **Gold Reviews** — the canonical review of each article (`entry.gold_claims` + metadata:
  study type, evidence level).
- **Gold Topics** — how a Living Clinical Topic should look after integrating its papers
  (`gold_topics`: expected consensus, confidence range, key claims).

## Rules

- Entries are **real, verifiable papers** (DOI / PMID). **Never fabricate** a paper or a
  finding.
- The gold data is **human-curated** — the correct, evidence-based statements the system
  should recover (Principle 8: humans make decisions). Each article should be one you
  would be willing to cite in a conversation with your specialist.
- Target: **30 articles** across the areas in `dataset.json`:
  PRP (6), Mesenchymal Stem Cells (5), Cartilage Regeneration (5),
  Meniscus Repair / Scaffold (4), Exercise & Rehabilitation (4),
  Early Knee Osteoarthritis (3), Clinical Guidelines & Systematic Reviews (3).

## Status

**`gold_version` 1.0 — 14 curated Gold Papers/Reviews and 6 curated Gold Topics,
covering all 7 areas.**

Curated via pair-work (agent proposes real, verifiable candidates; the human decides;
the system records the decision and its motive in `rationale` + `selected_by`):

- **PRP** (4) — Belk 2021 (`GOLD-PRP-001`, used in `RUN-2026-07-001`), Dai 2017
  (`GOLD-PRP-002`), the RESTORE RCT / Bennell 2021 (`GOLD-PRP-003`) and Nie 2021
  (`GOLD-PRP-004`) → `TOPIC-PRP`.
- **Mesenchymal Stem Cells** (2) — Maheshwer 2021 (`GOLD-MSC-001`) and the 2024 OAC
  RCT synthesis (`GOLD-MSC-002`) → `TOPIC-MSC`.
- **Cartilage Regeneration** (2) — ACI vs microfracture meta-analysis 2020
  (`GOLD-CART-001`) and the Knutsen 2004 RCT (`GOLD-CART-002`) → `TOPIC-CARTILAGE`.
- **Meniscus Repair / Scaffold** (2) — meniscal-scaffold meta-analysis 2025
  (`GOLD-MEN-001`) and the collagen-vs-polyurethane review 2018 (`GOLD-MEN-002`) →
  `TOPIC-MENISCUS`.
- **Early Knee Osteoarthritis** (2) — Luyten classification criteria 2018
  (`GOLD-EARLY-001`) and the 2024 scoping review on definitions (`GOLD-EARLY-002`) →
  `TOPIC-EARLY-OA`.
- **Clinical Guidelines & Systematic Reviews** (1) — OARSI 2019 (`GOLD-GUIDE-001`).
- **Exercise & Rehabilitation** (1) — Cochrane / Fransen 2015 (`GOLD-EXER-001`) →
  `TOPIC-EXERCISE`.

**Controversy is preserved on purpose** (Golden Rule 2): RESTORE contradicts the
favourable PRP meta-analyses; MSC evidence is mixed; a landmark RCT found microfracture
not inferior to ACI; and early-OA has no agreed definition. The corresponding Gold
Topics model these conflicts with widened confidence ranges instead of a false certainty.

DOIs/PMIDs added during curation are flagged "to be reconfirmed against the full text"
in each entry's `rationale` until verified.

Entries proposed but not yet approved carry `"status": "proposed"` and do **not** count
in the benchmark; only `"status": "curated"` entries do. Target is 30 articles; areas
PRP, MSC, Cartilage, Meniscus and Early-OA still have open slots, curated the same way.

## How the benchmark uses it

For each curated Gold Paper, the system reviews it and its produced claims are compared
against the Gold Review (coverage, traceability, hallucinations, time, cost). Once a real
reviewer is integrated, the consolidated topic is compared against the Gold Topic
(consensus, confidence range, key-claim coverage). See `src/benchmark/`.
