# Pilot 002: faculty, labs, and program enrichment

## Pilot date

- Date completed: 2026-06-17
- Date range covered, if different: same day

## Researcher

- Name or initials: Codex
- Review partners, if any: none

## Universities tested

- [x] Carnegie Mellon University
- [x] University of Washington
- [x] Georgia Institute of Technology
- [x] Cornell University
- [x] University of California, Berkeley

## Candidate entities added

- Universities:
  - Count: 0
  - Notes: No new universities were added; pilot stayed within the existing five-university batch.
- Programs:
  - Count: 0
  - Notes: No unrelated programs were added.
- Faculty:
  - Count: 10
  - Notes: Added two official-source-backed faculty candidates per university where possible: Haiyi Zhu and John Zimmerman at CMU; Leah Findlater and Julie Kientz at UW; Diyi Yang and Duen Horng Chau at Georgia Tech; Qian Yang and Thorsten Joachims at Cornell; Niloufar Salehi and Marti Hearst at UC Berkeley.
- Labs:
  - Count: 5
  - Notes: Added one lab, center, institute, or research-area candidate per university: CMU HCII, UW HCDE Research, Georgia Tech Institute for People and Technology, Cornell Human-AI Interaction research area, and Berkeley Center for Technology, Society & Policy.
- Sources/evidence:
  - Count: 19 new candidate source rows and 6 new canonical evidence rows.
  - Notes: Candidate source rows include faculty/lab evidence plus program-detail evidence for Cornell and Berkeley. Canonical evidence rows support program-detail updates for the three promoted programs.

## Candidates promoted

- Count: 0
- Entity types promoted: none
- Were evidence rows created for promoted records? [x] yes [ ] no [ ] mixed
- Notes: Existing promoted university/program records for CMU, UW, and Georgia Tech were not re-promoted; only their canonical program detail fields and evidence rows were enriched.

## Candidates rejected

- Count: 0
- Common rejection reasons: not applicable
- Notes: No rejection decisions were made in this controlled enrichment step.

## Candidates left in `needs_review` / `needs_source`

- `needs_review` count: 4 existing candidate rows remain under review: Cornell university, Cornell program, UC Berkeley university, and UC Berkeley program.
- `needs_source` count: 0
- Why were they left unresolved? Cornell and UC Berkeley now have stronger faculty/lab and research-area evidence, but the pilot instruction was not to automatically promote them. Their program-detail evidence is still incomplete relative to canonical promotion needs.

## Evidence quality observations

- [x] Official source URLs were easy to find.
- [x] Snippets were short and claim-specific.
- [x] Evidence was direct enough for faculty/lab candidate intake.
- [x] Some evidence was indirect or split across pages.

Notes: Faculty profiles and departmental research pages were generally adequate for candidate intake. Program-detail fields were harder to normalize because pages mix stable requirements, annual deadlines, tuition-year notes, and general program descriptions.

## Program fields enriched

- CMU MHCI: duration, research orientation, capstone, application timing note, and cost note.
- UW HCDE MS: duration/credits, research orientation, capstone note, online availability, and application timing.
- Georgia Tech MS-HCI: duration/credits, research orientation, capstone/internship requirement, and selected prerequisites/admissions requirements.
- Cornell MPS and Berkeley MIMS: candidate source evidence and uncertainty notes were added, but no canonical program updates were made because they remain `needs_review`.

## What remained unclear

- Current exact CMU MHCI deadline and current-year total cost should be rechecked during a future admissions-cycle pass.
- UW HCDE cost notes were not captured in this pilot step.
- Georgia Tech official deadline, online availability, and cost notes were not captured clearly enough for canonical fields.
- Cornell and Berkeley program-detail fields remain incomplete and should not be promoted automatically.

## Schema gaps discovered

- Gap summary: lab candidates mix institutes, centers, labs, department research pages, and research-area pages.
- Affected table/field: `candidate_labs` / missing lab-center type field.
- Proposed change: add a controlled `lab_or_center_type` field later.

- Gap summary: program-detail evidence often supports only one field or claim, but evidence rows do not have a structured claim category.
- Affected table/field: `evidence` and `candidate_sources` / missing claim category.
- Proposed change: add optional claim category/type values such as duration, deadline, cost, prerequisites, capstone, online availability, and research orientation.

- Gap summary: faculty research fit requires more nuance than a single primary area plus secondary areas.
- Affected table/field: `candidate_faculty` / research fit dimensions.
- Proposed change: consider structured dimensions for HCI fit, HAI fit, methods, population/domain, and advising/research-access signals before scoring.

## CLI/workflow friction

- [x] Candidate intake commands were clear.
- [x] Candidate review report was useful.
- [x] Manual status updates were clear.
- [ ] Promotion commands were clear.
- [x] Validation errors were actionable.

Notes: `scripts/add_candidate.py` worked well for new faculty and lab candidates. Program-detail evidence for existing candidates/canonical programs required manual CSV updates because the candidate CLI only adds candidate rows and linked source snippets, not additional source rows for existing candidates or canonical program field updates.

## Validation or CI issues

- Did validation pass locally? [x] yes [ ] no
- Did placeholder-data guard pass? [x] yes [ ] no
- Did unit tests pass? [x] yes [ ] no
- Any CI-only issues? none observed locally.

Notes: All requested local checks passed after data updates.

## Duplicate handling issues

- Were duplicate warnings clear? [x] yes [ ] no [ ] not applicable
- Were intentional duplicates needed? [ ] yes [x] no
- Notes: No intentional duplicate candidate rows were needed.

## Promotion issues

- Were canonical IDs clear? [x] yes [ ] no
- Were university links for programs/faculty/labs clear? [x] yes [ ] no
- Were evidence rows created as expected? [x] yes [ ] no
- Notes: No new promotion was performed. Canonical program enrichment was straightforward for already promoted programs.

## Fields that need to be added, renamed, or clarified

- Field/table: `candidate_labs.lab_or_center_type`
  - Issue: Different official pages represent labs, institutes, centers, department groups, and research areas differently.
  - Suggested wording or schema change: controlled optional values such as `lab`, `center`, `institute`, `department_research_area`, `project`, `research_group`.
- Field/table: `evidence.claim_category` and `candidate_sources.claim_category`
  - Issue: Reviewers cannot easily filter evidence supporting program duration, deadline, cost, capstone, online availability, or research orientation.
  - Suggested wording or schema change: optional controlled claim-category field.
- Field/table: `candidate_faculty` research fit fields
  - Issue: Faculty fit cannot be expressed cleanly with keywords alone.
  - Suggested wording or schema change: add optional structured fit dimensions in a later schema iteration.

## Questions before scaling

- Should lab/center/research-area candidates be stored in one table with a type field, or split into separate canonical entity types?
- Should program deadlines and costs be normalized into cycle-specific tables before broader collection?
- Should faculty/lab candidates be promoted independently before university/program promotion, or only after a canonical university exists?

## Recommended next changes

1. Add a small workflow for attaching additional source evidence to an existing candidate without creating a duplicate candidate row.
2. Decide whether to add `claim_category` to evidence/source tables before collecting many program detail claims.
3. Run a targeted promotion review for Cornell and UC Berkeley using the new faculty/lab evidence, but keep promotion as a separate decision task.

## Decision

- [ ] Ready to scale
- [x] Needs another pilot
- [ ] Needs schema revision before another pilot

Decision rationale: The current schema can represent a small HCI/HAI ecosystem pilot, but lab/center types, claim categories, and faculty-fit dimensions should be clarified before scaling to many universities.
