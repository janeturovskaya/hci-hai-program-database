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
