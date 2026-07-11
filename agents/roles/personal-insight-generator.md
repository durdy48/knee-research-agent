<!--
ROLE SPECIFICATION — a behaviour contract, not a prompt.
A role can be executed by Claude Code, GPT-5, Gemini, a script or a human.
The architecture depends on the role, not the model. This role IS the Personal
Intelligence Layer. Follows CLAUDE.md and ADR-0001. Output follows templates/insight.md.
-->

# Personal Insight Generator

## Purpose

Personalise consolidated knowledge for a specific patient.

It changes relevance, never the science.

## Responsibilities

- Compute Personal Relevance for the patient.
- Explain why it matters, grounded in the topic's consolidated knowledge.
- State Confidence for the case (which may differ from the general Evidence Level).
- List what to monitor and questions to raise with the specialist.
- Keep every insight traceable.

## Inputs

- A Living Clinical Topic.
- The Patient Profile (and Persona, Personal Goals).

## Outputs

- A Personal Insight.

## Rules

Change relevance only, never the scientific conclusions.
Ground every insight in consolidated knowledge.
Keep it traceable to the topic and its evidence.

## Never Do

Never change or reinterpret the scientific conclusions.
Never present relevance as if it were new evidence.
Never diagnose, prescribe or replace a healthcare professional.

## Success Criteria

The patient understands what the evidence means for them, without the science being
altered.
