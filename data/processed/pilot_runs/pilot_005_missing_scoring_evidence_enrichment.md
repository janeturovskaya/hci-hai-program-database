# Pilot 005 — Missing scoring evidence enrichment

Date: 2026-06-17

## Scope

This pilot enriched the three promoted canonical pilot programs only:

1. Carnegie Mellon University — Master of Human-Computer Interaction
2. University of Washington — Master of Science in Human Centered Design & Engineering
3. Georgia Institute of Technology — MS Program in Human-Computer Interaction

No new universities or programs were added. Cornell and UC Berkeley were not promoted.

## Approved official evidence added

Added official evidence rows for the scoring categories that were weak or missing in the prior audit:

- CMU MHCI
  - methods fit from the official MHCI curriculum page
  - career relevance from the official MHCI page
  - quant/data/AI curriculum from the official MHCI curriculum page
  - partial/indirect research-access evidence from the official capstone page
- UW HCDE MS
  - methods fit from the official MS degree requirements page
  - quant/data/AI curriculum from the official MS degree requirements page
  - directed research access from the official HCDE directed research page
  - career relevance from the official MS page
- Georgia Tech MS-HCI
  - methods fit from the official catalog
  - quant/data/AI curriculum from the official catalog
  - faculty-supervised project access from the official MS-HCI requirements page
  - broader research ecosystem access from the official MS-HCI research centers page
  - career relevance from the official MS-HCI career outcomes page

## Score changes

- CMU MHCI
  - `methods_fit_for_uxr_psychology_background`: `2` → `3`, confidence `medium` → `high`
  - `career_relevance_for_ai_uxr`: `2` → `3`, confidence `medium` → `high`
  - `quant_data_ai_curriculum`: `IE` → `1`, confidence `medium`
  - `research_access_for_masters`: remains `IE`
- UW HCDE MS
  - `methods_fit_for_uxr_psychology_background`: `IE` → `3`, confidence `high`
  - `research_access_for_masters`: remains `2`, confidence `medium` → `high`
  - `quant_data_ai_curriculum`: remains `2`, confidence `medium`
  - `career_relevance_for_ai_uxr`: remains `3`, confidence `high`
- Georgia Tech MS-HCI
  - `methods_fit_for_uxr_psychology_background`: `IE` → `3`, confidence `high`
  - `research_access_for_masters`: remains `2`, confidence `medium` → `high`
  - `quant_data_ai_curriculum`: remains `2`, confidence `medium`
  - `career_relevance_for_ai_uxr`: `2` → `3`, confidence `medium` → `high`

## What stayed IE

- CMU MHCI `research_access_for_masters` remains `IE` because the approved capstone evidence supports applied user research and faculty/sponsor-guided project work, but does not establish direct MHCI-specific lab, thesis, or directed research access.

## Evidence that remains insufficient

- AI-specific UX research career evidence remains indirect for all three programs; official career pages support UX/HCI career relevance but generally do not separate AI-specific UX research roles.
- Direct master’s research access evidence varies by program. UW has directed research evidence, Georgia Tech has required faculty-supervised project evidence, and CMU has only partial capstone evidence in the approved source set.
- Georgia Tech still lacks a used `faculty_lab_fit` claim-category row in the score evidence set, even though the score row retains the existing exploratory faculty/lab fit score.

## Rubric usability assessment

The scoring rubric is becoming more usable. Adding claim-specific evidence rows made it clearer which official sources support methods fit, career relevance, quant/data/AI curriculum, and research access. The remaining CMU research-access IE also shows that the rubric can preserve uncertainty instead of forcing a score from partial evidence.

## Recommended next step

Recommended next task: expand to the next small batch of programs before promoting/reviewing Cornell and UC Berkeley. The scoring workflow is now more evidence-aware for the three canonical pilot programs, but one more small batch would test whether the claim-category and audit workflow generalize beyond the initial promoted set.
