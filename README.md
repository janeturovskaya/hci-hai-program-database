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

### Promote a reviewed candidate

Use `docs/candidate_promotion_checklist.md` before moving anything into `data/manual/`. In short, promote only when the source is official or highly reliable, the evidence snippet supports the claim, names are normalized, duplicate concerns are resolved, `review_status` is `reviewed`, uncertainty is documented, a canonical ID has been assigned, and a related evidence record exists or is ready to add.
