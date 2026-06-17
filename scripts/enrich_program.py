#!/usr/bin/env python3
"""Safely enrich existing canonical program rows with evidence-backed details."""
from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from add_candidate import slugify, unique_id
from promote_candidate import write_rows
from validate_manual_data import ROOT, read_csv, validate_all, load_simple_yaml

PROGRAMS_FILE = ROOT / "data/manual/programs.csv"
EVIDENCE_FILE = ROOT / "data/manual/evidence.csv"
EVIDENCE_COLUMNS = ("evidence_id", "entity_type", "entity_id", "claim", "source_url", "source_type", "quote_or_snippet", "date_accessed", "confidence", "uncertainty_notes")
UPDATE_FIELDS = (
    "duration", "research_orientation", "thesis_or_capstone", "online_available",
    "application_deadline", "prerequisites", "cost_notes", "official_url",
    "source_url", "notes",
)
PROTECTED_FIELDS = {"program_id", "university_id", "program_name", "degree_type", "department_or_school", "format", "last_checked"}


def is_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def allowed_confidence() -> set[str]:
    config = load_simple_yaml(ROOT / "config/settings.yaml")
    return set(config.get("validation", {}).get("allowed_confidence", []))


def evidence_ids() -> set[str]:
    if not EVIDENCE_FILE.exists():
        return set()
    _, rows = read_csv(EVIDENCE_FILE)
    return {row.get("evidence_id", "").strip() for row in rows if row.get("evidence_id", "").strip()}


def build_evidence_id(program_id: str, claim: str) -> str:
    return unique_id("ev_", ["program", program_id, slugify(claim)[:40]], evidence_ids())


def append_evidence(row: dict[str, str]) -> None:
    with EVIDENCE_FILE.open("a", encoding="utf-8", newline="") as handle:
        csv.DictWriter(handle, fieldnames=list(EVIDENCE_COLUMNS)).writerow({column: row.get(column, "") for column in EVIDENCE_COLUMNS})


def run_validation_or_rollback(backups: dict[Path, str]) -> bool:
    issues = validate_all()
    if not issues:
        print("Manual and candidate CSV validation passed.")
        return True
    for path, content in backups.items():
        path.write_text(content, encoding="utf-8")
    print("Validation failed after writing; enrichment changes were rolled back.", file=sys.stderr)
    for issue in issues:
        loc = f":{issue.row}" if issue.row else ""
        print(f"{issue.severity.upper()} {issue.table}{loc} - {issue.message}", file=sys.stderr)
    return False


def supplied_updates(args: argparse.Namespace) -> dict[str, str]:
    updates: dict[str, str] = {}
    for field in UPDATE_FIELDS:
        value = getattr(args, field)
        if value is not None:
            updates[field] = value
    return updates


def validate_args(args: argparse.Namespace, updates: dict[str, str]) -> None:
    if not updates and not args.clear_field:
        raise ValueError("At least one supported update field or --clear-field value is required.")
    invalid_clears = sorted(set(args.clear_field) - set(UPDATE_FIELDS))
    if invalid_clears:
        raise ValueError(f"--clear-field only supports {sorted(UPDATE_FIELDS)}; invalid: {invalid_clears}")
    overlap = sorted(set(updates) & set(args.clear_field))
    if overlap:
        raise ValueError(f"Fields cannot be both updated and cleared in the same run: {overlap}")
    if args.no_evidence:
        return
    missing = [name for name in ("evidence_claim", "source_url", "quote_or_snippet", "confidence") if not getattr(args, name)]
    if missing:
        raise ValueError("Evidence is required unless --no-evidence is used; missing: " + ", ".join("--" + m.replace("_", "-") for m in missing))
    if not is_http_url(args.source_url):
        raise ValueError("--source-url must be an http(s) URL when evidence is provided.")
    if args.confidence not in allowed_confidence():
        raise ValueError(f"--confidence must be one of {sorted(allowed_confidence())}.")


def find_program(rows: list[dict[str, str]], program_id: str) -> dict[str, str]:
    matches = [row for row in rows if row.get("program_id", "").strip() == program_id]
    if not matches:
        raise ValueError(f"No canonical program found with program_id '{program_id}'.")
    if len(matches) > 1:
        raise ValueError(f"Multiple canonical programs found with program_id '{program_id}'.")
    return matches[0]


def make_evidence_row(args: argparse.Namespace, today: str) -> dict[str, str]:
    uncertainty = args.uncertainty_notes.strip()
    trace = f"Enriched canonical program via scripts/enrich_program.py on {today}."
    return {
        "evidence_id": build_evidence_id(args.program_id, args.evidence_claim),
        "entity_type": "program",
        "entity_id": args.program_id,
        "claim": args.evidence_claim,
        "source_url": args.source_url,
        "source_type": args.source_type,
        "quote_or_snippet": args.quote_or_snippet,
        "date_accessed": args.date_accessed or today,
        "confidence": args.confidence,
        "uncertainty_notes": (uncertainty + " " + trace).strip(),
    }


def enrich_program(args: argparse.Namespace) -> int:
    updates = supplied_updates(args)
    try:
        validate_args(args, updates)
        columns, rows = read_csv(PROGRAMS_FILE)
        program = find_program(rows, args.program_id)
    except ValueError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    today = date.today().isoformat()
    evidence_row = None if args.no_evidence else make_evidence_row(args, today)
    if args.no_evidence:
        print("WARNING: Updating canonical program details without evidence. Use --no-evidence only for rare, intentional maintenance exceptions.", file=sys.stderr)

    backups = {PROGRAMS_FILE: PROGRAMS_FILE.read_text(encoding="utf-8")}
    if evidence_row:
        backups[EVIDENCE_FILE] = EVIDENCE_FILE.read_text(encoding="utf-8")
    for field, value in updates.items():
        if field == "notes" and program.get("notes", "") and not args.replace_notes:
            program[field] = program["notes"].rstrip() + " | Enrichment note: " + value
        else:
            program[field] = value
    for field in args.clear_field:
        program[field] = ""
    program["last_checked"] = today

    write_rows(PROGRAMS_FILE, columns, rows)
    if evidence_row:
        append_evidence(evidence_row)
        print(f"Created evidence row {evidence_row['evidence_id']}.")
    print(f"Enriched program {args.program_id}.")
    if not run_validation_or_rollback(backups):
        return 1
    if args.generate_report:
        for script in ("generate_candidate_review.py", "pilot_status.py"):
            result = subprocess.run([sys.executable, str(ROOT / f"scripts/{script}")], check=False)
            if result.returncode:
                return result.returncode
    return 0


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("program_id")
    for field in UPDATE_FIELDS:
        parser.add_argument("--" + field.replace("_", "-"), dest=field, default=None)
    parser.add_argument("--clear-field", action="append", default=[])
    parser.add_argument("--replace-notes", action="store_true")
    parser.add_argument("--evidence-claim", default="")
    parser.add_argument("--quote-or-snippet", default="")
    parser.add_argument("--confidence", default="")
    parser.add_argument("--source-type", default="official_page")
    parser.add_argument("--date-accessed", default="")
    parser.add_argument("--uncertainty-notes", default="")
    parser.add_argument("--no-evidence", action="store_true")
    parser.add_argument("--generate-report", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    return enrich_program(make_parser().parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
