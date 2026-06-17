# HCI/HAI Program Database

A reproducible project foundation for building a structured research database of U.S. universities, graduate programs, faculty, and labs related to Human-Computer Interaction (HCI), Human-AI Interaction (HAI), Human-Centered AI, Social Computing, Responsible AI, and adjacent research areas.

This repository is intentionally scaffolded before data collection begins. It does **not** currently include real university records, scraped content, or generated institutional facts.

## Goals

- Collect university, program, faculty, lab, and evidence records with auditable source tracking.
- Validate hand-entered CSV files against explicit schemas.
- Deduplicate candidate records before review or export.
- Preserve raw, manual, processed, and exported data separately for reproducibility.
- Support future scoring and review workflows without locking into a scraping approach.

## Project structure

```text
hci-hai-program-database/
├── README.md
├── requirements.txt
├── config/
├── data/
│   ├── raw/
│   ├── manual/
│   ├── processed/
│   └── exports/
├── notebooks/
├── prompts/
├── reports/
├── schema/
└── scripts/
```

## Data directories

- `data/raw/`: unmodified source downloads or scrape outputs, when collection begins.
- `data/manual/`: manually curated CSV files that follow the canonical schemas.
- `data/processed/`: normalized, joined, deduplicated, or scored datasets.
- `data/exports/`: review-ready exports for downstream use.

## Manual CSV templates

The initial manual templates are empty and contain headers only:

- `data/manual/universities.csv`
- `data/manual/programs.csv`
- `data/manual/faculty.csv`
- `data/manual/labs.csv`
- `data/manual/evidence.csv`

Schemas are defined in `schema/manual_csv_schemas.yaml`. Evidence rows should be used to support specific claims with a source URL, source type, snippet, access date, confidence level, and uncertainty notes.

## Setup

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Validation

Validate the manual CSV files against the schema:

```bash
python scripts/validate_manual_data.py
```

Find likely duplicate manual records with fuzzy matching:

```bash
python scripts/find_potential_duplicates.py
```

## Data collection policy

Do not invent or infer real university data. Future additions should rely on official university, program, faculty, or lab pages wherever possible. Every non-obvious claim should be backed by an evidence record, and uncertain claims should include explicit uncertainty notes.

## Pilot batch workflow

The next recommended human step is to test the workflow with a pilot batch of 3–5 real universities using official source URLs. The pilot is for exercising candidate intake, review, promotion, validation, and schema feedback before any larger data collection effort. Do not scrape the web, bulk import records, or add unreviewed facts.

Pilot resources:

- [`docs/pilot_batch_workflow.md`](docs/pilot_batch_workflow.md) explains the staged pilot process.
- [`docs/source_evidence_rules.md`](docs/source_evidence_rules.md) defines acceptable source evidence and confidence levels.
- [`docs/pilot_batch_checklist.md`](docs/pilot_batch_checklist.md) provides a short practical checklist.
- [`examples/add_candidate_commands.sh`](examples/add_candidate_commands.sh) contains placeholder CLI examples that must be edited before use.

Use `scripts/check_placeholder_data.py` before committing data changes to ensure placeholder example values were not accidentally added to real candidate or manual CSV files.

## After the pilot: findings and schema gaps

After the first 3–5 university pilot, pause before scaling to a larger database. Review what worked, what was confusing, and what schema or workflow gaps should be fixed first.

Post-pilot resources:

- [`docs/pilot_findings_template.md`](docs/pilot_findings_template.md) provides a reusable findings template.
- [`docs/schema_gap_tracker.md`](docs/schema_gap_tracker.md) tracks schema and workflow gaps discovered during pilot runs.
- [`docs/pilot_readiness_checklist.md`](docs/pilot_readiness_checklist.md) helps confirm the project is ready before adding real pilot data.
- [`data/processed/pilot_runs/README.md`](data/processed/pilot_runs/README.md) explains where to store human-written pilot summaries.

Use `python scripts/pilot_status.py` for a lightweight status summary of candidate statuses, candidate sources, canonical row counts, promoted/rejected totals, and source-linkage warnings. The script summarizes workflow state only; it does not infer facts or verify source quality.

## Candidate intake workflow

Candidate data is intentionally separate from canonical manual data. Use `data/candidates/` for rough leads that still need review, source checking, deduplication, and promotion decisions. Nothing in candidate CSV files should be treated as canonical until it is manually promoted into `data/manual/` with supporting evidence.

### Candidate intake files

Header-only templates are provided for:

- `data/candidates/candidate_universities.csv`
- `data/candidates/candidate_programs.csv`
- `data/candidates/candidate_faculty.csv`
- `data/candidates/candidate_labs.csv`
- `data/candidates/candidate_sources.csv`

Do not scrape the web or invent institutional facts. Add only manually discovered candidate rows and source details you can review later.

### Add a rough candidate

1. Choose the matching candidate CSV.
2. Add a stable `candidate_id`.
3. Add the candidate name fields you know, a `source_url`, `discovered_date` in `YYYY-MM-DD` format, a controlled `review_status`, and a controlled `relevant_area` where applicable.
4. Use `notes` for uncertainty, duplicate concerns, or follow-up questions.

Allowed `review_status` values are `discovered`, `needs_source`, `needs_review`, `reviewed`, `promoted`, and `rejected`.

Allowed `relevant_area` values are `core_hci`, `human_ai_interaction`, `human_centered_ai`, `social_computing`, `responsible_ai`, `computational_social_science`, `accessibility`, `human_robot_interaction`, `mixed_methods_uxr`, `ai_product_evaluation`, and `other`.

### Add source evidence

Add source rows to `data/candidates/candidate_sources.csv` with a `source_id`, `source_url`, `date_accessed`, `evidence_snippet`, and `confidence`. When the source supports a specific candidate, set `associated_entity_type` to `university`, `program`, `faculty`, or `lab`, and set `associated_candidate_id` to an existing candidate ID in the matching candidate CSV.

### Validate candidates

Run the validator before review or promotion:

```bash
python scripts/validate_manual_data.py
```

The validator checks candidate headers, required fields, duplicate candidate/source IDs, ISO dates, HTTP/HTTPS URLs, controlled statuses, controlled relevant areas, confidence values, and candidate source associations.

### Generate the candidate review report

Run:

```bash
python scripts/generate_candidate_review.py
```

The script writes `reports/candidate_review.md`, grouping candidate rows by review status, relevant area, and university name. The report summarizes only provided candidate data and does not verify or infer unsupported claims.


### Add candidates with the CLI helper

Use `scripts/add_candidate.py` to append one candidate row at a time and, when you have an evidence snippet, append a linked row in `data/candidates/candidate_sources.csv`. The helper checks controlled values, blocks likely duplicates by default, generates readable IDs, writes the row, and then runs the existing CSV validation. If validation fails after writing, the script restores the edited CSV files to their previous contents before exiting non-zero.

Generated candidate IDs use normalized names plus entity prefixes such as `cand_univ_`, `cand_prog_`, `cand_fac_`, and `cand_lab_`; linked source IDs use `cand_src_`. If the readable ID already exists, the helper appends `_2`, `_3`, and so on.

When `--evidence-snippet` is provided, the source row is associated to the new candidate with `associated_entity_type` and `associated_candidate_id`. If no evidence snippet is provided, the candidate row is still added, but the script prints a warning and does not create a source row. This workflow remains candidate intake only; it does **not** promote records into canonical `data/manual/` files.

Examples:

```bash
python scripts/add_candidate.py university \
  --university-name "Example University" \
  --city "Example City" \
  --state "CA" \
  --seed-reason "Known HCI lab" \
  --relevant-area "human_ai_interaction" \
  --source-url "https://example.edu/hci" \
  --evidence-snippet "Example evidence snippet" \
  --confidence "medium" \
  --notes "Needs manual review"
```

```bash
python scripts/add_candidate.py program \
  --university-name "Example University" \
  --program-name "MS in Example HCI" \
  --degree-type "MS" \
  --department-or-school "School of Information" \
  --format "in-person" \
  --seed-reason "Relevant Human-AI curriculum" \
  --relevant-area "human_ai_interaction" \
  --source-url "https://example.edu/program" \
  --evidence-snippet "Example evidence snippet" \
  --confidence "medium" \
  --notes "Needs admissions review"
```

```bash
python scripts/add_candidate.py faculty \
  --university-name "Example University" \
  --faculty-name "Jane Example" \
  --title "Associate Professor" \
  --department "Computer Science" \
  --lab-or-group "Example HAI Lab" \
  --research-keywords "human-AI interaction; explainable AI; user studies" \
  --relevant-area "human_ai_interaction" \
  --source-url "https://example.edu/faculty/jane-example" \
  --evidence-snippet "Example evidence snippet" \
  --confidence "medium" \
  --notes "Check whether they advise master's students"
```

```bash
python scripts/add_candidate.py lab \
  --university-name "Example University" \
  --lab-name "Example Human-AI Lab" \
  --director "Jane Example" \
  --themes "human-AI collaboration; AI evaluation" \
  --relevant-area "human_ai_interaction" \
  --source-url "https://example.edu/lab" \
  --evidence-snippet "Example evidence snippet" \
  --confidence "medium" \
  --notes "Needs publication review"
```

Add `--generate-report` to regenerate `reports/candidate_review.md` after a successful append and validation. Use `--allow-duplicate` only when you intentionally want a second candidate with the same duplicate-check key.

### Promote reviewed candidates

Use `scripts/promote_candidate.py` to move one reviewed row from `data/candidates/` into the matching canonical CSV in `data/manual/`. Promotion is intentionally a controlled manual step: it preserves traceability in notes, can create a canonical evidence row, updates the candidate `review_status` to `promoted`, and validates the CSV files before keeping the changes.

Promotion expects the candidate row to have `review_status` set to `reviewed`. If you intentionally need to promote another status, pass `--allow-unreviewed`; the script will print a strong warning. This override should be rare and documented in candidate notes.

Promotion does **not** verify facts, scrape the web, or infer missing institutional details. It only moves reviewed, sourced data that a human has already checked into canonical CSV files.

Canonical IDs may be supplied with `--canonical-id`. If omitted, the script generates readable deterministic IDs from normalized name fields using these prefixes: `univ_`, `prog_`, `fac_`, and `lab_`. If an ID already exists, generated IDs receive `_2`, `_3`, and so on. For programs, faculty, and labs, pass `--university-id` unless the candidate university name matches exactly one canonical university in `data/manual/universities.csv`.

Use `--create-evidence` with `--evidence-claim` to create a row in `data/manual/evidence.csv` for the promoted canonical entity. By default, the first linked candidate source row by `source_id` is used; pass `--source-id cand_src_...` to choose a specific linked source. If there is no linked candidate source, the script uses the candidate row's `source_url` and prints a warning.

If validation fails after writing, `scripts/promote_candidate.py` restores every modified CSV file to its previous contents, prints the validation errors, and exits non-zero. Add `--generate-report` to regenerate `reports/candidate_review.md` after a successful promotion.

Examples:

```bash
python scripts/promote_candidate.py university cand_univ_example_university \
  --canonical-id univ_example_university \
  --create-evidence \
  --evidence-claim "Example University has a relevant HCI/HAI candidate source under review."
```

```bash
python scripts/promote_candidate.py program cand_prog_example_university_ms_example_hci \
  --canonical-id prog_example_university_ms_example_hci \
  --university-id univ_example_university \
  --create-evidence \
  --evidence-claim "The program page describes graduate-level HCI/HAI-relevant curriculum."
```

```bash
python scripts/promote_candidate.py faculty cand_fac_example_university_jane_example \
  --canonical-id fac_example_university_jane_example \
  --university-id univ_example_university \
  --create-evidence \
  --evidence-claim "The faculty profile describes HCI/HAI-relevant research."
```

```bash
python scripts/promote_candidate.py lab cand_lab_example_university_example_human_ai_lab \
  --canonical-id lab_example_university_example_human_ai_lab \
  --university-id univ_example_university \
  --create-evidence \
  --evidence-claim "The lab page describes HCI/HAI-relevant research themes."
```
