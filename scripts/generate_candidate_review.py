#!/usr/bin/env python3
"""Generate a Markdown review report from candidate intake CSV files."""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

from validate_manual_data import CANDIDATE_ENTITY_TABLES, ROOT, validate_all

CANDIDATE_DIR = ROOT / "data" / "candidates"
REPORT_PATH = ROOT / "reports" / "candidate_review.md"

FILES = {
    "university": CANDIDATE_DIR / "candidate_universities.csv",
    "program": CANDIDATE_DIR / "candidate_programs.csv",
    "faculty": CANDIDATE_DIR / "candidate_faculty.csv",
    "lab": CANDIDATE_DIR / "candidate_labs.csv",
}

NAME_FIELDS = {
    "university": "university_name",
    "program": "program_name",
    "faculty": "faculty_name",
    "lab": "lab_name",
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_sources() -> dict[tuple[str, str], list[dict[str, str]]]:
    by_candidate: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in read_rows(CANDIDATE_DIR / "candidate_sources.csv"):
        entity_type = row.get("associated_entity_type", "").strip()
        candidate_id = row.get("associated_candidate_id", "").strip()
        if entity_type and candidate_id:
            by_candidate[(entity_type, candidate_id)].append(row)
    return by_candidate


def validation_messages_by_table_and_row() -> dict[tuple[str, int | None], list[str]]:
    grouped: dict[tuple[str, int | None], list[str]] = defaultdict(list)
    for issue in validate_all():
        if issue.table.startswith("candidate_"):
            grouped[(issue.table, issue.row)].append(issue.message)
    return grouped


def main() -> int:
    sources = load_sources()
    messages = validation_messages_by_table_and_row()
    grouped: dict[str, dict[str, dict[str, list[tuple[str, dict[str, str], int]]]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for entity_type, path in FILES.items():
        table = CANDIDATE_ENTITY_TABLES[entity_type]
        for index, row in enumerate(read_rows(path), start=2):
            status = row.get("review_status", "").strip() or "(missing review_status)"
            area = row.get("relevant_area", "").strip() or "(missing relevant_area)"
            university = row.get("university_name", "").strip() or "(missing university_name)"
            grouped[status][area][university].append((entity_type, row, index))

    lines = ["# Candidate Review Report", "", "This report summarizes only manually provided candidate intake data. It does not infer, scrape, or verify claims.", ""]
    if not any(grouped.values()):
        lines.append("No candidate rows are currently present.")
    for status in sorted(grouped):
        lines.extend([f"## Review status: {status}", ""])
        for area in sorted(grouped[status]):
            lines.extend([f"### Relevant area: {area}", ""])
            for university in sorted(grouped[status][area]):
                lines.extend([f"#### University: {university}", ""])
                for entity_type, row, row_number in grouped[status][area][university]:
                    candidate_id = row.get("candidate_id", "").strip() or "(missing candidate_id)"
                    name = row.get(NAME_FIELDS[entity_type], "").strip() or "(missing name/title)"
                    source_url = row.get("source_url", "").strip() or "(missing source_url)"
                    notes = row.get("notes", "").strip()
                    lines.extend([f"- **{entity_type.title()} candidate `{candidate_id}`**: {name}", f"  - Source URL: {source_url}"])
                    for source in sources.get((entity_type, candidate_id), []):
                        snippet = source.get("evidence_snippet", "").strip()
                        if snippet:
                            lines.append(f"  - Evidence snippet: {snippet}")
                    if notes:
                        lines.append(f"  - Notes: {notes}")
                    row_messages = messages.get((CANDIDATE_ENTITY_TABLES[entity_type], row_number), [])
                    if row_messages:
                        lines.append(f"  - Validation warnings/errors: {'; '.join(row_messages)}")
                lines.append("")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"Wrote {REPORT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
