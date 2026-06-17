#!/usr/bin/env python3
"""Safely promote reviewed candidate rows into canonical manual CSV files."""
from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Iterable

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from add_candidate import slugify, unique_id
from validate_manual_data import ROOT, read_csv, validate_all

CANDIDATE_CONFIG = {
    "university": {
        "candidate_file": ROOT / "data/candidates/candidate_universities.csv",
        "manual_file": ROOT / "data/manual/universities.csv",
        "id_field": "university_id",
        "name_fields": ("university_name",),
        "id_parts": ("university_name",),
        "prefix": "univ_",
        "columns": ("university_id", "university_name", "city", "state", "public_private", "relevant_departments", "notes", "official_url", "last_checked"),
    },
    "program": {
        "candidate_file": ROOT / "data/candidates/candidate_programs.csv",
        "manual_file": ROOT / "data/manual/programs.csv",
        "id_field": "program_id",
        "name_fields": ("university_id", "program_name"),
        "id_parts": ("university_name", "program_name"),
        "prefix": "prog_",
        "columns": ("program_id", "university_id", "program_name", "degree_type", "department_or_school", "format", "duration", "research_orientation", "thesis_or_capstone", "online_available", "application_deadline", "prerequisites", "cost_notes", "official_url", "source_url", "last_checked", "notes"),
    },
    "faculty": {
        "candidate_file": ROOT / "data/candidates/candidate_faculty.csv",
        "manual_file": ROOT / "data/manual/faculty.csv",
        "id_field": "faculty_id",
        "name_fields": ("university_id", "name"),
        "id_parts": ("university_name", "faculty_name"),
        "prefix": "fac_",
        "columns": ("faculty_id", "university_id", "name", "title", "department", "lab", "research_keywords", "hci_relevance", "hai_relevance", "methods", "recent_publications", "faculty_url", "google_scholar_url", "source_url", "last_checked", "notes"),
    },
    "lab": {
        "candidate_file": ROOT / "data/candidates/candidate_labs.csv",
        "manual_file": ROOT / "data/manual/labs.csv",
        "id_field": "lab_id",
        "name_fields": ("university_id", "lab_name"),
        "id_parts": ("university_name", "lab_name"),
        "prefix": "lab_",
        "columns": ("lab_id", "university_id", "lab_name", "director", "themes", "student_opportunities", "projects", "publications_url", "lab_url", "source_url", "last_checked", "notes"),
    },
}

SOURCE_FILE = ROOT / "data/candidates/candidate_sources.csv"
EVIDENCE_FILE = ROOT / "data/manual/evidence.csv"
EVIDENCE_COLUMNS = ("evidence_id", "entity_type", "entity_id", "claim", "source_url", "source_type", "quote_or_snippet", "date_accessed", "confidence", "uncertainty_notes")


def write_rows(path: Path, columns: Iterable[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns))
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def append_row(path: Path, columns: Iterable[str], row: dict[str, str]) -> None:
    with path.open("a", encoding="utf-8", newline="") as handle:
        csv.DictWriter(handle, fieldnames=list(columns)).writerow({column: row.get(column, "") for column in columns})


def find_candidate(entity_type: str, candidate_id: str) -> tuple[list[str], list[dict[str, str]], dict[str, str]]:
    columns, rows = read_csv(CANDIDATE_CONFIG[entity_type]["candidate_file"])
    matches = [row for row in rows if row.get("candidate_id", "").strip() == candidate_id]
    if not matches:
        raise ValueError(f"No {entity_type} candidate found with candidate_id '{candidate_id}'.")
    if len(matches) > 1:
        raise ValueError(f"Multiple {entity_type} candidates found with candidate_id '{candidate_id}'.")
    return columns, rows, matches[0]


def resolve_university_id(candidate: dict[str, str], provided: str) -> str:
    if provided:
        return provided
    _, rows = read_csv(ROOT / "data/manual/universities.csv")
    name = candidate.get("university_name", "").strip().casefold()
    matches = [r for r in rows if r.get("university_name", "").strip().casefold() == name]
    if len(matches) == 1:
        return matches[0].get("university_id", "").strip()
    if not matches:
        raise ValueError("--university-id is required because no matching canonical university was found.")
    raise ValueError("--university-id is required because multiple matching canonical universities were found.")


def build_notes(candidate: dict[str, str]) -> str:
    parts = []
    if candidate.get("notes", "").strip():
        parts.append(candidate["notes"].strip())
    parts.append(f"Promoted from candidate_id {candidate.get('candidate_id', '').strip()}.")
    if candidate.get("university_name", "").strip():
        parts.append(f"Candidate university_name: {candidate['university_name'].strip()}.")
    return " ".join(parts)


def existing_ids(path: Path, id_field: str) -> set[str]:
    _, rows = read_csv(path)
    return {row.get(id_field, "").strip() for row in rows if row.get(id_field, "").strip()}


def canonical_id(entity_type: str, candidate: dict[str, str], provided: str) -> str:
    config = CANDIDATE_CONFIG[entity_type]
    if provided:
        return provided
    return unique_id(config["prefix"], (candidate.get(field, "") for field in config["id_parts"]), existing_ids(config["manual_file"], config["id_field"]))


def build_manual_row(entity_type: str, candidate: dict[str, str], entity_id: str, university_id: str, today: str) -> dict[str, str]:
    notes = build_notes(candidate)
    source_url = candidate.get("source_url", "").strip()
    if entity_type == "university":
        return {"university_id": entity_id, "university_name": candidate.get("university_name", ""), "city": candidate.get("city", ""), "state": candidate.get("state", ""), "public_private": "", "relevant_departments": "", "notes": notes, "official_url": source_url, "last_checked": today}
    if entity_type == "program":
        return {"program_id": entity_id, "university_id": university_id, "program_name": candidate.get("program_name", ""), "degree_type": candidate.get("degree_type", ""), "department_or_school": candidate.get("department_or_school", ""), "format": candidate.get("format", ""), "duration": "", "research_orientation": "", "thesis_or_capstone": "", "online_available": "", "application_deadline": "", "prerequisites": "", "cost_notes": "", "official_url": source_url, "source_url": source_url, "last_checked": today, "notes": notes}
    if entity_type == "faculty":
        return {"faculty_id": entity_id, "university_id": university_id, "name": candidate.get("faculty_name", ""), "title": candidate.get("title", ""), "department": candidate.get("department", ""), "lab": candidate.get("lab_or_group", ""), "research_keywords": candidate.get("research_keywords", ""), "hci_relevance": "", "hai_relevance": "", "methods": "", "recent_publications": "", "faculty_url": source_url, "google_scholar_url": "", "source_url": source_url, "last_checked": today, "notes": notes}
    return {"lab_id": entity_id, "university_id": university_id, "lab_name": candidate.get("lab_name", ""), "director": candidate.get("director", ""), "themes": candidate.get("themes", ""), "student_opportunities": "", "projects": "", "publications_url": "", "lab_url": source_url, "source_url": source_url, "last_checked": today, "notes": notes}


def likely_duplicate(entity_type: str, row: dict[str, str]) -> dict[str, str] | None:
    config = CANDIDATE_CONFIG[entity_type]
    _, rows = read_csv(config["manual_file"])
    wanted = tuple(row.get(field, "").strip().casefold() for field in config["name_fields"])
    if not all(wanted):
        return None
    for existing in rows:
        if tuple(existing.get(field, "").strip().casefold() for field in config["name_fields"]) == wanted:
            return existing
    return None


def linked_sources(entity_type: str, candidate_id: str) -> list[dict[str, str]]:
    _, rows = read_csv(SOURCE_FILE)
    sources = [r for r in rows if r.get("associated_entity_type", "").strip() == entity_type and r.get("associated_candidate_id", "").strip() == candidate_id]
    return sorted(sources, key=lambda r: r.get("source_id", ""))


def build_evidence_row(args: argparse.Namespace, candidate: dict[str, str], entity_id: str, today: str) -> dict[str, str]:
    sources = linked_sources(args.entity_type, candidate["candidate_id"])
    source = None
    if args.source_id:
        matches = [s for s in sources if s.get("source_id", "").strip() == args.source_id]
        if not matches:
            raise ValueError(f"source_id '{args.source_id}' is not linked to candidate_id '{candidate['candidate_id']}'.")
        source = matches[0]
    elif sources:
        source = sources[0]
    else:
        print("WARNING: No linked candidate source found; using the candidate source_url for evidence.", file=sys.stderr)
    source_url = (source or candidate).get("source_url", "").strip()
    existing = existing_ids(EVIDENCE_FILE, "evidence_id")
    evidence_id = args.evidence_id or unique_id("ev_", [args.entity_type, entity_id, slugify(args.evidence_claim)[:40]], existing)
    uncertainty = (source or {}).get("uncertainty_notes", "").strip()
    trace = f"Promoted from candidate_id {candidate['candidate_id']}."
    return {"evidence_id": evidence_id, "entity_type": args.entity_type, "entity_id": entity_id, "claim": args.evidence_claim, "source_url": source_url, "source_type": (source or {}).get("source_type", "") or "candidate_source", "quote_or_snippet": (source or {}).get("evidence_snippet", ""), "date_accessed": (source or {}).get("date_accessed", "") or today, "confidence": (source or {}).get("confidence", "") or "medium", "uncertainty_notes": (uncertainty + " " + trace).strip()}


def run_validation_or_rollback(backups: dict[Path, str]) -> bool:
    issues = validate_all()
    if not issues:
        print("Manual and candidate CSV validation passed.")
        return True
    for path, content in backups.items():
        path.write_text(content, encoding="utf-8")
    print("Validation failed after writing; promotion changes were rolled back.", file=sys.stderr)
    for issue in issues:
        loc = f":{issue.row}" if issue.row else ""
        print(f"{issue.severity.upper()} {issue.table}{loc} - {issue.message}", file=sys.stderr)
    return False


def promote_candidate(args: argparse.Namespace) -> int:
    try:
        candidate_columns, candidate_rows, candidate = find_candidate(args.entity_type, args.candidate_id)
        if candidate.get("review_status", "").strip() != "reviewed":
            if not args.allow_unreviewed:
                raise ValueError(f"Candidate review_status must be 'reviewed' before promotion; found '{candidate.get('review_status', '').strip()}'.")
            print("WARNING: Promoting a candidate that is not reviewed. Use this only for intentional exceptions.", file=sys.stderr)
        if args.create_evidence and not args.evidence_claim:
            raise ValueError("--evidence-claim is required when --create-evidence is provided.")
        university_id = "" if args.entity_type == "university" else resolve_university_id(candidate, args.university_id)
        entity_id = canonical_id(args.entity_type, candidate, args.canonical_id)
        config = CANDIDATE_CONFIG[args.entity_type]
        if entity_id in existing_ids(config["manual_file"], config["id_field"]):
            raise ValueError(f"Canonical ID '{entity_id}' already exists. Use a different --canonical-id.")
        manual_row = build_manual_row(args.entity_type, candidate, entity_id, university_id, date.today().isoformat())
        duplicate = likely_duplicate(args.entity_type, manual_row)
        if duplicate and not args.allow_duplicate:
            raise ValueError(f"Likely duplicate canonical record exists with {config['id_field']} '{duplicate.get(config['id_field'], '').strip()}'. Use --allow-duplicate to promote anyway.")
        evidence_row = build_evidence_row(args, candidate, entity_id, date.today().isoformat()) if args.create_evidence else None
    except ValueError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    paths = [config["manual_file"], config["candidate_file"]] + ([EVIDENCE_FILE] if evidence_row else [])
    backups = {path: path.read_text(encoding="utf-8") for path in paths}
    append_row(config["manual_file"], config["columns"], manual_row)
    for row in candidate_rows:
        if row.get("candidate_id", "").strip() == args.candidate_id:
            row["review_status"] = "promoted"
    write_rows(config["candidate_file"], candidate_columns, candidate_rows)
    if evidence_row:
        append_row(EVIDENCE_FILE, EVIDENCE_COLUMNS, evidence_row)
        print(f"Created evidence row {evidence_row['evidence_id']}.")
    print(f"Promoted {args.entity_type} candidate {args.candidate_id} to {entity_id}.")
    if not run_validation_or_rollback(backups):
        return 1
    if args.generate_report:
        return subprocess.run([sys.executable, str(ROOT / "scripts/generate_candidate_review.py")], check=False).returncode
    return 0


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entity_type", choices=sorted(CANDIDATE_CONFIG))
    parser.add_argument("candidate_id")
    parser.add_argument("--canonical-id", default="")
    parser.add_argument("--university-id", default="")
    parser.add_argument("--allow-unreviewed", action="store_true")
    parser.add_argument("--allow-duplicate", action="store_true")
    parser.add_argument("--create-evidence", action="store_true")
    parser.add_argument("--evidence-id", default="")
    parser.add_argument("--evidence-claim", default="")
    parser.add_argument("--source-id", default="")
    parser.add_argument("--generate-report", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    return promote_candidate(make_parser().parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
