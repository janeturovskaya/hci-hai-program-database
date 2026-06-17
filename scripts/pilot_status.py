#!/usr/bin/env python3
"""Print a lightweight pilot status summary from candidate and manual CSV files."""
from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CANDIDATE_FILES = {
    "universities": ROOT / "data/candidates/candidate_universities.csv",
    "programs": ROOT / "data/candidates/candidate_programs.csv",
    "faculty": ROOT / "data/candidates/candidate_faculty.csv",
    "labs": ROOT / "data/candidates/candidate_labs.csv",
}

MANUAL_FILES = {
    "universities": ROOT / "data/manual/universities.csv",
    "programs": ROOT / "data/manual/programs.csv",
    "faculty": ROOT / "data/manual/faculty.csv",
    "labs": ROOT / "data/manual/labs.csv",
    "evidence": ROOT / "data/manual/evidence.csv",
}

SOURCE_FILE = ROOT / "data/candidates/candidate_sources.csv"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def count_by_status(rows: list[dict[str, str]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in rows:
        status = row.get("review_status", "").strip() or "(blank)"
        counts[status] += 1
    return counts


def count_rows(path: Path) -> int:
    return len(read_rows(path))


def candidate_ids_by_entity(candidate_files: dict[str, Path] = CANDIDATE_FILES) -> dict[str, set[str]]:
    entity_map = {"universities": "university", "programs": "program", "faculty": "faculty", "labs": "lab"}
    return {
        entity_map[name]: {row.get("candidate_id", "").strip() for row in read_rows(path) if row.get("candidate_id", "").strip()}
        for name, path in candidate_files.items()
    }


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def missing_source_warnings(candidate_files: dict[str, Path] = CANDIDATE_FILES) -> list[str]:
    warnings: list[str] = []
    for name, path in candidate_files.items():
        for index, row in enumerate(read_rows(path), start=2):
            if not row.get("source_url", "").strip():
                candidate_id = row.get("candidate_id", "").strip() or "(missing candidate_id)"
                warnings.append(f"WARNING: {display_path(path)}:{index} candidate {candidate_id} is missing source_url.")
    return warnings


def unlinked_source_warnings(source_file: Path = SOURCE_FILE, candidate_files: dict[str, Path] = CANDIDATE_FILES) -> list[str]:
    warnings: list[str] = []
    known_ids = candidate_ids_by_entity(candidate_files)
    for index, row in enumerate(read_rows(source_file), start=2):
        entity_type = row.get("associated_entity_type", "").strip()
        candidate_id = row.get("associated_candidate_id", "").strip()
        source_id = row.get("source_id", "").strip() or "(missing source_id)"
        if not entity_type or not candidate_id:
            warnings.append(f"WARNING: {display_path(source_file)}:{index} source {source_id} is not linked to a candidate.")
        elif candidate_id not in known_ids.get(entity_type, set()):
            warnings.append(f"WARNING: {display_path(source_file)}:{index} source {source_id} links to missing {entity_type} candidate {candidate_id}.")
    return warnings


def build_summary(candidate_files: dict[str, Path] = CANDIDATE_FILES, manual_files: dict[str, Path] = MANUAL_FILES, source_file: Path = SOURCE_FILE) -> dict[str, object]:
    candidate_rows = {name: read_rows(path) for name, path in candidate_files.items()}
    manual_counts = {name: count_rows(path) for name, path in manual_files.items()}
    status_counts = {name: count_by_status(rows) for name, rows in candidate_rows.items()}
    promoted = sum(counts.get("promoted", 0) for counts in status_counts.values())
    rejected = sum(counts.get("rejected", 0) for counts in status_counts.values())
    return {
        "status_counts": status_counts,
        "candidate_sources": count_rows(source_file),
        "manual_counts": manual_counts,
        "promoted_candidates": promoted,
        "rejected_candidates": rejected,
        "warnings": missing_source_warnings(candidate_files) + unlinked_source_warnings(source_file, candidate_files),
    }


def print_summary(summary: dict[str, object]) -> None:
    print("Pilot status summary")
    print("====================")
    print("Candidate rows by review_status:")
    status_counts = summary["status_counts"]
    assert isinstance(status_counts, dict)
    for entity_name in ("universities", "programs", "faculty", "labs"):
        counts = status_counts.get(entity_name, Counter())
        assert isinstance(counts, Counter)
        if counts:
            rendered = ", ".join(f"{status}: {count}" for status, count in sorted(counts.items()))
        else:
            rendered = "none"
        print(f"- candidate {entity_name}: {rendered}")
    print(f"Candidate sources: {summary['candidate_sources']}")
    print("Canonical manual rows:")
    manual_counts = summary["manual_counts"]
    assert isinstance(manual_counts, dict)
    for entity_name in ("universities", "programs", "faculty", "labs", "evidence"):
        print(f"- {entity_name}: {manual_counts.get(entity_name, 0)}")
    print(f"Promoted candidates: {summary['promoted_candidates']}")
    print(f"Rejected candidates: {summary['rejected_candidates']}")
    warnings = summary["warnings"]
    assert isinstance(warnings, list)
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")
    else:
        print("Warnings: none")


def main() -> int:
    print_summary(build_summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
