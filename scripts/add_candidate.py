#!/usr/bin/env python3
"""Safely append one candidate intake row and optional linked source evidence."""
from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_manual_data import ROOT, ALLOWED_CLAIM_CATEGORIES, is_valid_url, load_simple_yaml, read_csv, validate_all

CANDIDATE_CONFIG = {
    "university": {
        "file": ROOT / "data/candidates/candidate_universities.csv",
        "prefix": "cand_univ_",
        "name_fields": ("university_name",),
        "columns": ("candidate_id", "university_name", "city", "state", "seed_reason", "relevant_area", "secondary_relevant_areas", "source_url", "discovered_date", "review_status", "notes"),
    },
    "program": {
        "file": ROOT / "data/candidates/candidate_programs.csv",
        "prefix": "cand_prog_",
        "name_fields": ("university_name", "program_name"),
        "columns": ("candidate_id", "university_name", "program_name", "degree_type", "department_or_school", "format", "seed_reason", "relevant_area", "secondary_relevant_areas", "source_url", "discovered_date", "review_status", "notes"),
    },
    "faculty": {
        "file": ROOT / "data/candidates/candidate_faculty.csv",
        "prefix": "cand_fac_",
        "name_fields": ("university_name", "faculty_name"),
        "columns": ("candidate_id", "university_name", "faculty_name", "title", "department", "lab_or_group", "research_keywords", "relevant_area", "secondary_relevant_areas", "source_url", "discovered_date", "review_status", "notes"),
    },
    "lab": {
        "file": ROOT / "data/candidates/candidate_labs.csv",
        "prefix": "cand_lab_",
        "name_fields": ("university_name", "lab_name"),
        "columns": ("candidate_id", "university_name", "lab_name", "director", "themes", "relevant_area", "secondary_relevant_areas", "source_url", "discovered_date", "review_status", "notes"),
    },
}

SOURCE_FILE = ROOT / "data/candidates/candidate_sources.csv"
SOURCE_COLUMNS = ("source_id", "source_type", "source_title", "source_url", "associated_entity_type", "associated_candidate_id", "date_accessed", "evidence_snippet", "confidence", "uncertainty_notes", "claim_category")


def slugify(value: str) -> str:
    """Normalize human-readable text into a lowercase snake-case ID fragment."""
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return re.sub(r"_+", "_", slug) or "candidate"


def unique_id(prefix: str, parts: Iterable[str], existing_ids: set[str]) -> str:
    base = prefix + slugify(" ".join(part for part in parts if part).strip())
    candidate = base
    suffix = 2
    while candidate in existing_ids:
        candidate = f"{base}_{suffix}"
        suffix += 1
    return candidate


def load_validation_config() -> dict[str, set[str]]:
    config = load_simple_yaml(ROOT / "config/settings.yaml")
    validation = config.get("validation", {})
    return {
        "review_status": set(validation.get("allowed_review_statuses", [])),
        "relevant_area": set(validation.get("allowed_relevant_areas", [])),
        "confidence": set(validation.get("allowed_confidence", [])),
    }


def read_existing_ids(path: Path, id_field: str) -> set[str]:
    _, rows = read_csv(path)
    return {row.get(id_field, "").strip() for row in rows if row.get(id_field, "").strip()}


def likely_duplicate(entity_type: str, candidate_row: dict[str, str]) -> dict[str, str] | None:
    config = CANDIDATE_CONFIG[entity_type]
    _, rows = read_csv(config["file"])
    key_fields = config["name_fields"]
    wanted = tuple(candidate_row.get(field, "").strip().casefold() for field in key_fields)
    if not all(wanted):
        return None
    for row in rows:
        existing = tuple(row.get(field, "").strip().casefold() for field in key_fields)
        if existing == wanted:
            return row
    return None


def append_row(path: Path, columns: Iterable[str], row: dict[str, str]) -> None:
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns))
        writer.writerow({column: row.get(column, "") for column in columns})


def validate_controlled_values(args: argparse.Namespace) -> list[str]:
    allowed = load_validation_config()
    errors: list[str] = []
    if args.review_status not in allowed["review_status"]:
        errors.append(f"review_status must be one of {sorted(allowed['review_status'])}")
    if args.relevant_area and args.relevant_area not in allowed["relevant_area"]:
        errors.append(f"relevant_area must be one of {sorted(allowed['relevant_area'])}")
    if args.secondary_relevant_areas:
        secondary_values = [value.strip() for value in args.secondary_relevant_areas.split(";") if value.strip()]
        for secondary_area in secondary_values:
            if secondary_area not in allowed["relevant_area"]:
                errors.append(f"secondary_relevant_areas values must be one of {sorted(allowed['relevant_area'])}")
        duplicates = sorted({value for value in secondary_values if secondary_values.count(value) > 1})
        if duplicates:
            errors.append(f"secondary_relevant_areas contains duplicate values: {duplicates}")
        if args.relevant_area and args.relevant_area in secondary_values:
            errors.append("secondary_relevant_areas must not repeat primary relevant_area")
    if args.claim_category and args.claim_category not in ALLOWED_CLAIM_CATEGORIES:
        errors.append(f"claim_category must be one of {sorted(ALLOWED_CLAIM_CATEGORIES)}")
    if args.confidence and args.confidence not in allowed["confidence"]:
        errors.append(f"confidence must be one of {sorted(allowed['confidence'])}")
    if args.source_url and not is_valid_url(args.source_url):
        errors.append("source_url must be an HTTP/HTTPS URL")
    return errors


def build_candidate_row(args: argparse.Namespace, today: str) -> dict[str, str]:
    config = CANDIDATE_CONFIG[args.entity_type]
    values = vars(args)
    row = {column: str(values.get(column, "") or "") for column in config["columns"]}
    row["discovered_date"] = args.discovered_date or today
    row["review_status"] = args.review_status
    if not row["candidate_id"]:
        existing = read_existing_ids(config["file"], "candidate_id")
        row["candidate_id"] = unique_id(config["prefix"], (row[field] for field in config["name_fields"]), existing)
    return row


def build_source_row(args: argparse.Namespace, candidate_id: str, today: str) -> dict[str, str]:
    existing = read_existing_ids(SOURCE_FILE, "source_id")
    parsed_path = urlparse(args.source_url).path.rsplit("/", 1)[-1]
    id_parts = [args.university_name or "source", parsed_path or args.source_title or args.entity_type]
    source_id = args.source_id or unique_id("cand_src_", id_parts, existing)
    confidence = args.confidence or "medium"
    return {
        "source_id": source_id,
        "source_type": args.source_type,
        "source_title": args.source_title or "",
        "source_url": args.source_url,
        "associated_entity_type": args.entity_type,
        "associated_candidate_id": candidate_id,
        "date_accessed": args.date_accessed or today,
        "evidence_snippet": args.evidence_snippet,
        "confidence": confidence,
        "uncertainty_notes": args.uncertainty_notes or "",
        "claim_category": args.claim_category or "",
    }


def run_validation_or_rollback(backups: dict[Path, str]) -> bool:
    issues = validate_all()
    if not issues:
        print("Manual and candidate CSV validation passed.")
        return True
    for path, content in backups.items():
        path.write_text(content, encoding="utf-8")
    print("Validation failed after writing; appended rows were rolled back.", file=sys.stderr)
    for issue in issues:
        location = f":{issue.row}" if issue.row else ""
        print(f"{issue.severity.upper()} {issue.table}{location} - {issue.message}", file=sys.stderr)
    return False


def add_candidate(args: argparse.Namespace) -> int:
    today = date.today().isoformat()
    errors = validate_controlled_values(args)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2

    candidate_row = build_candidate_row(args, today)
    duplicate = likely_duplicate(args.entity_type, candidate_row)
    if duplicate and not args.allow_duplicate:
        print(f"Likely duplicate found; existing candidate_id: {duplicate.get('candidate_id', '').strip()}", file=sys.stderr)
        print("Use --allow-duplicate to append another row anyway.", file=sys.stderr)
        return 1

    source_row = build_source_row(args, candidate_row["candidate_id"], today) if args.evidence_snippet else None
    if args.evidence_snippet and not args.source_url:
        print("ERROR: --source-url is required when --evidence-snippet is provided.", file=sys.stderr)
        return 2

    paths = [CANDIDATE_CONFIG[args.entity_type]["file"]] + ([SOURCE_FILE] if source_row else [])
    backups = {path: path.read_text(encoding="utf-8") for path in paths}
    append_row(CANDIDATE_CONFIG[args.entity_type]["file"], CANDIDATE_CONFIG[args.entity_type]["columns"], candidate_row)
    print(f"Added {args.entity_type} candidate {candidate_row['candidate_id']}.")
    if source_row:
        append_row(SOURCE_FILE, SOURCE_COLUMNS, source_row)
        print(f"Added linked source {source_row['source_id']}.")
    else:
        print("WARNING: No source evidence was added because --evidence-snippet was not provided.", file=sys.stderr)

    if not run_validation_or_rollback(backups):
        return 1
    if args.generate_report:
        result = subprocess.run([sys.executable, str(ROOT / "scripts/generate_candidate_review.py")], check=False)
        return result.returncode
    return 0


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entity_type", choices=sorted(CANDIDATE_CONFIG))
    parser.add_argument("--candidate-id", default="")
    parser.add_argument("--source-url", default="")
    parser.add_argument("--discovered-date", default="")
    parser.add_argument("--review-status", default="discovered")
    parser.add_argument("--relevant-area", default="")
    parser.add_argument("--secondary-relevant-areas", default="")
    parser.add_argument("--notes", default="")
    parser.add_argument("--allow-duplicate", action="store_true")
    parser.add_argument("--generate-report", action="store_true")
    parser.add_argument("--source-id", default="")
    parser.add_argument("--source-type", default="official_page")
    parser.add_argument("--source-title", default="")
    parser.add_argument("--date-accessed", default="")
    parser.add_argument("--evidence-snippet", default="")
    parser.add_argument("--confidence", default="")
    parser.add_argument("--uncertainty-notes", default="")
    parser.add_argument("--claim-category", default="")
    for field in ["university-name", "city", "state", "seed-reason", "program-name", "degree-type", "department-or-school", "format", "faculty-name", "title", "department", "lab-or-group", "research-keywords", "lab-name", "director", "themes"]:
        parser.add_argument(f"--{field}", dest=field.replace("-", "_"), default="")
    return parser


def main(argv: list[str] | None = None) -> int:
    return add_candidate(make_parser().parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
