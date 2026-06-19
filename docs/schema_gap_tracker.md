# Schema gap tracker

Use this living document to track schema, validation, reporting, scoring, and workflow changes discovered during pilot runs. Do not add real university/program/faculty/lab facts here; this file is for gaps in the database design and workflow.

## How to use this tracker

1. Add one row per discovered gap.
2. Use a stable `gap_id`, such as `gap_001`.
3. Link or reference the pilot run summary in `source` when possible.
4. Keep examples short and generic if they are not already public data in canonical CSVs.
5. Update `status` as decisions are made.

## Allowed `issue_type` values

- `missing_field`
- `unclear_field`
- `field_too_broad`
- `field_too_narrow`
- `validation_gap`
- `evidence_gap`
- `workflow_gap`
- `reporting_gap`
- `scoring_gap`
- `other`

## Allowed `status` values

- `open`
- `needs_decision`
- `planned`
- `implemented`
- `rejected`

## Gaps

| gap_id | date_found | source | affected_table | affected_field | issue_type | description | example | proposed_change | priority | status | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| _Add rows after a pilot run._ |  |  |  |  |  |  |  |  |  |  |  |
| gap_010 | 2026-06-17 | pilot_006_cornell_berkeley_promotion_review | candidate_programs; programs | program_type | missing_field | Interdisciplinary information-school programs can be strong adjacent fits but are not dedicated HCI degrees, making promotion-readiness harder to compare with MHCI/HCDE/MS-HCI programs | MIMS or MPS Information Science may have HCI/UX/AI pathways without being a dedicated HCI degree | Consider a structured `program_type` or `fit_type` field distinguishing dedicated_hci, hcde, infosci_adjacent, data_ai_adjacent, and other pathways | medium | open | Observed while reviewing Cornell MPS Information Science and Berkeley MIMS |
| gap_011 | 2026-06-17 | pilot_006_cornell_berkeley_promotion_review | docs; candidate_programs | promotion_criteria | workflow_gap | Promotion criteria for adjacent InfoSci programs are not documented, so promoting Berkeley MIMS would set policy implicitly | Berkeley MIMS has strong HCI/AI/UX evidence but remains a broader information-management degree | Add documented promotion criteria for adjacent programs before promoting more non-dedicated-HCI degrees | high | open | This review deferred Berkeley promotion primarily to avoid implicit policy-setting |
| gap_012 | 2026-06-17 | pilot_006_cornell_berkeley_promotion_review | candidate_programs | promotion_recommendation | missing_field | Candidate review findings currently live in narrative reports, but candidate rows have no structured recommendation field | Cornell recommendation is keep_needs_review; Berkeley recommendation is defer | Consider adding a controlled recommendation or review_decision field separate from `review_status` | low | open | Useful if promotion-readiness reviews continue beyond pilot reports |
| gap_007 | 2026-06-17 | pilot_005_missing_scoring_evidence_enrichment | program_scores | career_relevance_for_ai_uxr | evidence_gap | AI-specific UX research career evidence remains difficult to separate from general UX/HCI career evidence in official program career pages | Official pages often list UX researcher, UX designer, product, or HCI roles without distinguishing AI-specific UX research | Keep AI-specific limitations in scoring notes; consider a separate structured career subdimension if future pilots repeatedly need it | medium | open | Observed across CMU, UW, and Georgia Tech official career evidence |
| gap_008 | 2026-06-17 | pilot_005_missing_scoring_evidence_enrichment | program_scores | research_access_for_masters | field_too_broad | Direct master’s research access varies by program and current scoring compresses directed research, thesis/lab access, capstone projects, and faculty-supervised projects into one field | One program may have directed research registration while another has a required faculty-supervised project or only capstone evidence | Consider later structured fields or subcategories for directed research, thesis/lab placement, capstone/project supervision, and research ecosystem access | medium | open | Do not change schema until more programs confirm the pattern |
| gap_009 | 2026-06-17 | pilot_005_missing_scoring_evidence_enrichment | scripts; reports | audit_program_scores.py | workflow_gap | The requested scoring audit workflow was absent in the checked-out repository even though generated reports referenced an audit need | Running `python scripts/audit_program_scores.py` initially failed because the file was missing | Add a deterministic audit script that validates score evidence IDs, claim-category coverage, IE dimensions, and used evidence rows missing categories | high | implemented | Implemented during pilot 005 and regenerated `reports/program_scoring_audit.md` |
| gap_001 | 2026-06-17 | pilot_001_hci_hai_programs | candidate_programs | relevant_area | field_too_narrow | Some programs fit multiple relevant areas but the schema allows one controlled value | Cornell MPS and Berkeley MIMS may span UX, HCI, social computing, and AI/product pathways | Added optional semicolon-separated `secondary_relevant_areas` while preserving primary `relevant_area` | medium | implemented | Implemented for all candidate entity CSVs; validation checks allowed values, duplicates, and primary repeats |
| gap_002 | 2026-06-17 | pilot_002_faculty_labs_program_enrichment | candidate_labs | lab_or_center_type | missing_field | Lab/center candidates can be labs, centers, institutes, department research areas, projects, or groups, but the table has no structured type field | A research-area page may be evidence-backed but is not the same entity type as a named lab | Add optional controlled `lab_or_center_type` values such as lab, center, institute, department_research_area, project, research_group | medium | open | Observed while adding one lab/center/group candidate per pilot university |
| gap_003 | 2026-06-17 | pilot_002_faculty_labs_program_enrichment | evidence; candidate_sources | claim_category | missing_field | Program-detail evidence often supports one specific field, but evidence rows do not classify the claim type | A source may support duration but not cost or deadline | Add optional controlled claim categories such as duration, deadline, cost, prerequisites, capstone, online_available, research_orientation, faculty_fit, lab_fit | medium | open | Would make candidate review and canonical enrichment easier to audit |
| gap_004 | 2026-06-17 | pilot_002_faculty_labs_program_enrichment | candidate_faculty | research_fit_dimensions | field_too_broad | Faculty research fit needs more structure than keywords plus primary/secondary relevant areas | Human-AI interaction, methods, domain, advising access, and responsible-AI angle may vary independently | Consider optional structured fields for HCI fit, HAI fit, methods, domain/population, and student research access | low | needs_decision | Avoid over-modeling until another faculty/lab pilot confirms scoring needs |
| gap_005 | 2026-06-17 | PR #11 workflow follow-up | programs; evidence | canonical program detail fields | workflow_gap | Existing promoted program details required manual CSV edits, creating risk of unsupported changes or missed evidence rows | Duration, capstone, deadline, cost, and notes updates after promotion | Add a safe canonical program enrichment CLI with supported-field allowlist, evidence creation, validation, rollback, and docs | high | implemented | Implemented by `scripts/enrich_program.py`; use the CLI instead of manual edits for program-detail enrichment |
| gap_006 | 2026-06-17 | pilot_003_scoring_workflow | program_scores; evidence | scoring claim granularity | workflow_gap | Scoring needs evidence tied to dimensions, but existing evidence rows often support broad program facts rather than individual scoring dimensions | HAI strength, faculty/lab fit, master's research access, and AI/data curriculum often need dimension-specific evidence before scoring | Add optional evidence claim categories or a score-to-evidence join table if scoring expands beyond pilot review | medium | partially implemented | This PR adds optional controlled `claim_category` support for evidence and candidate sources and uses it for the three promoted pilot programs; a future score-to-evidence join table may still be useful if scoring expands. |
