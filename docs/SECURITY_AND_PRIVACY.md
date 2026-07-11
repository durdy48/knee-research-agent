# SECURITY & PRIVACY

**Status:** Living
**Last Updated:** 2026-07-11

> KRA handles a personal medical profile, even as a personal project. This document states
> plainly what data it stores, where, how to remove it, how secrets are handled, and what is
> never shared. Keep it honest and up to date.

## What personal data KRA stores

- **Patient Profile** (`patient/profile.json`): the person's context — *Estables* (age, sex,
  injury history, surgeries, diagnoses) and *Variables* (pain, weight, strength, activity,
  current treatments, last MRI, goals). This is the only personal/medical data KRA stores.
- **Personal Insights** (`reports/YYYY-MM-insights.md`): monthly, patient-facing views that
  reference the profile's relevance (never the raw medical data verbatim beyond what you put
  in the profile).

Everything else — Gold Standard, Living Topics, Ledger, Executive Reports — is scientific
knowledge derived from public literature and contains no personal data.

## Where it lives

- **Locally, on your machine**, inside the repository working tree. KRA does not run a
  server and does not upload the profile anywhere.
- If you push the repository to a remote (e.g. GitHub), **decide deliberately** whether
  `patient/profile.json` should be committed. To keep it private, add it to `.gitignore`
  and keep only `patient/profile.json` locally (a template can be committed instead).

## How to remove it

- Delete or blank `patient/profile.json` (reset it to the empty template). With no profile,
  the Personal Insight Engine falls back to generic, non-personalised insights.
- Delete `reports/*-insights.md` to remove generated personal views. The scientific
  knowledge base is unaffected.

## API keys and secrets

- The only secret is an optional **Anthropic API key**, read from the environment
  (`KRA_ANTHROPIC_API_KEY` / `ANTHROPIC_API_KEY`) — never hard-coded, never committed.
- `.env` and `*.key` / `*.pem` are in `.gitignore`. Do not paste keys into code, docs or
  chat. KRA runs fully key-free with the `manual` provider.

## What is never sent to third parties

- KRA does not transmit the Patient Profile or any personal data to third parties.
- The only outbound call KRA can make is to the Anthropic API **when you explicitly run the
  `claude` provider** — and that sends *paper text for review*, never your personal profile.
- No analytics, telemetry or background network calls.

## Consent and scope

KRA is a personal research tool. It improves understanding of the evidence; it does not
diagnose, prescribe, or replace a healthcare professional. Any sharing of the knowledge base
or reports with others is a deliberate, manual action you take.
