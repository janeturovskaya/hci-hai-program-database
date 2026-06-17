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
| gap_001 | 2026-06-17 | pilot_001_hci_hai_programs | candidate_programs | relevant_area | field_too_narrow | Some programs fit multiple relevant areas but the schema allows one controlled value | Cornell MPS and Berkeley MIMS may span UX, HCI, social computing, and AI/product pathways | Added optional semicolon-separated `secondary_relevant_areas` while preserving primary `relevant_area` | medium | implemented | Implemented for all candidate entity CSVs; validation checks allowed values, duplicates, and primary repeats |
| gap_002 | 2026-06-17 | pilot_002_faculty_labs_program_enrichment | candidate_labs | lab_or_center_type | missing_field | Lab/center candidates can be labs, centers, institutes, department research areas, projects, or groups, but the table has no structured type field | A research-area page may be evidence-backed but is not the same entity type as a named lab | Add optional controlled `lab_or_center_type` values such as lab, center, institute, department_research_area, project, research_group | medium | open | Observed while adding one lab/center/group candidate per pilot university |
| gap_003 | 2026-06-17 | pilot_002_faculty_labs_program_enrichment | evidence; candidate_sources | claim_category | missing_field | Program-detail evidence often supports one specific field, but evidence rows do not classify the claim type | A source may support duration but not cost or deadline | Add optional controlled claim categories such as duration, deadline, cost, prerequisites, capstone, online_available, research_orientation, faculty_fit, lab_fit | medium | open | Would make candidate review and canonical enrichment easier to audit |
| gap_004 | 2026-06-17 | pilot_002_faculty_labs_program_enrichment | candidate_faculty | research_fit_dimensions | field_too_broad | Faculty research fit needs more structure than keywords plus primary/secondary relevant areas | Human-AI interaction, methods, domain, advising access, and responsible-AI angle may vary independently | Consider optional structured fields for HCI fit, HAI fit, methods, domain/population, and student research access | low | needs_decision | Avoid over-modeling until another faculty/lab pilot confirms scoring needs |
| gap_005 | 2026-06-17 | PR #11 workflow follow-up | programs; evidence | canonical program detail fields | workflow_gap | Existing promoted program details required manual CSV edits, creating risk of unsupported changes or missed evidence rows | Duration, capstone, deadline, cost, and notes updates after promotion | Add a safe canonical program enrichment CLI with supported-field allowlist, evidence creation, validation, rollback, and docs | high | implemented | Implemented by `scripts/enrich_program.py`; use the CLI instead of manual edits for program-detail enrichment |
