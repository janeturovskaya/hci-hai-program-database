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
