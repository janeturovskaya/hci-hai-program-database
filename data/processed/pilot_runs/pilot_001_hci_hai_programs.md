# Pilot 001: HCI/HAI programs

## Pilot date

- Date completed: 2026-06-17
- Date range covered, if different: 2026-06-17

## Researcher

- Name or initials: Codex
- Review partners, if any: None

## Universities tested

- [x] University 1: Carnegie Mellon University
- [x] University 2: University of Washington
- [x] University 3: Georgia Institute of Technology
- [x] University 4, optional: Cornell University
- [x] University 5, optional: University of California, Berkeley

## Candidate entities added

- Universities:
  - Count: 5
  - Notes: Added only the pilot universities provided in the task prompt.
- Programs:
  - Count: 5
  - Notes: Added only the graduate programs provided in the task prompt.
- Faculty:
  - Count: 0
  - Notes: No faculty candidates were added in this controlled pilot.
- Labs:
  - Count: 0
  - Notes: No lab candidates were added in this controlled pilot.
- Sources/evidence:
  - Count: 10 candidate source rows plus 6 canonical evidence rows from promotion.
  - Notes: All source URLs and evidence snippets came from the task prompt; no scraping or web search was performed.

## Candidates promoted

- Count: 6
- Entity types promoted: 3 universities and 3 programs.
- Were evidence rows created for promoted records? [x] yes [ ] no [ ] mixed
- Notes: Promoted Carnegie Mellon University, University of Washington, Georgia Institute of Technology, and their reviewed pilot programs. Cornell University and University of California, Berkeley were not promoted.

## Candidates rejected

- Count: 0
- Common rejection reasons: Not applicable.
- Notes: No pilot candidates were rejected.

## Candidates left in `needs_review` / `needs_source`

- `needs_review` count: 4
- `needs_source` count: 0
- Why were they left unresolved? Cornell University and University of California, Berkeley were intentionally left in review as edge cases because their programs are relevant information-school programs rather than dedicated HCI degrees.

## Evidence quality observations

- [x] Official source URLs were easy to find.
- [x] Snippets were short and claim-specific.
- [x] Evidence was direct enough for promotion.
- [x] Some evidence was indirect or split across pages.

Notes: The promoted candidates had direct program-page evidence. The Cornell and Berkeley cases are useful follow-up examples because a single program or school can span several relevant areas.

## Schema gaps discovered

- Gap summary: `relevant_area` currently allows only one value, but some information-school programs may fit multiple areas.
- Affected table/field: `candidate_programs.relevant_area` and related candidate/canonical relevant-area modeling.
- Proposed change: Consider allowing multi-value relevant areas or adding `secondary_relevant_areas`.

## CLI/workflow friction

- [x] Candidate intake commands were clear.
- [x] Candidate review report was useful.
- [x] Manual status updates were clear.
- [x] Promotion commands were clear.
- [x] Validation errors were actionable.

Notes: `scripts/add_candidate.py` supports `--review-status`, which allowed the reviewed candidates to be set during intake. The default status is `discovered`, so the two intentionally unresolved edge cases were manually updated to `needs_review` after intake.

## Validation or CI issues

- Did validation pass locally? [x] yes [ ] no
- Did placeholder-data guard pass? [x] yes [ ] no
- Did unit tests pass? [x] yes [ ] no
- Any CI-only issues? None observed locally.

Notes: Full checks passed after candidate intake, review-report regeneration, promotion, and pilot-summary documentation.

## Duplicate handling issues

- Were duplicate warnings clear? [ ] yes [ ] no [x] not applicable
- Were intentional duplicates needed? [ ] yes [x] no
- Notes: No duplicate candidates or canonical rows were encountered.

## Promotion issues

- Were canonical IDs clear? [x] yes [ ] no
- Were university links for programs/faculty/labs clear? [x] yes [ ] no
- Were evidence rows created as expected? [x] yes [ ] no
- Notes: Program promotions required the expected `--university-id` values, and canonical evidence rows were created from the linked candidate sources.

## Fields that need to be added, renamed, or clarified

- Field/table: `relevant_area`
- Issue: A single controlled value can be too narrow for programs spanning UX, HCI, social computing, and AI/product pathways.
- Suggested wording or schema change: Add multi-value support or a secondary relevant-area field while keeping a primary area for report grouping.

## Questions before scaling

- Question 1: Should candidate statuses default to `needs_review` rather than `discovered` for manually sourced pilot data?
- Question 2: Should canonical program rows include an explicit relevance taxonomy separate from candidate intake relevance?
- Question 3: How should non-dedicated HCI degrees be scored against dedicated HCI programs before broader promotion?

## Recommended next changes

1. Decide how to represent primary and secondary relevant areas.
2. Add guidance for when information-school programs should be promoted versus held for review.
3. Run a second pilot with faculty/lab candidates after the program-only workflow is reviewed.

## Decision

Choose one:

- [ ] Ready to scale
- [x] Needs another pilot
- [ ] Needs schema revision before another pilot

Decision rationale: The university/program workflow is usable and validation passed, but the single-value relevant-area field and edge-case program handling should be clarified before scaling.
