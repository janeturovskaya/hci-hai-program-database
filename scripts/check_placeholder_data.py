#!/usr/bin/env python3
"""Fail if obvious placeholder values appear in real candidate or manual CSV data."""
from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIRS = (ROOT / "data/candidates", ROOT / "data/manual")
PLACEHOLDER_PATTERNS = (
    "Example University",
    "Example HCI Program",
    "Example Faculty Member",
    "example.edu",
)


@dataclass(frozen=True)
class PlaceholderFinding:
    path: Path
    row_number: int
    field: str
    pattern: str


def iter_csv_files(paths: tuple[Path, ...] = DATA_DIRS) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.exists():
            files.extend(sorted(path.glob("*.csv")))
    return files


def scan_csv(path: Path, patterns: tuple[str, ...] = PLACEHOLDER_PATTERNS) -> list[PlaceholderFinding]:
    findings: list[PlaceholderFinding] = []
    lowered_patterns = [(pattern, pattern.casefold()) for pattern in patterns]
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for index, row in enumerate(reader, start=2):
            for field, value in row.items():
                cell = (value or "").casefold()
                for pattern, lowered in lowered_patterns:
                    if lowered in cell:
                        findings.append(PlaceholderFinding(path=path, row_number=index, field=field or "", pattern=pattern))
    return findings


def scan(paths: tuple[Path, ...] = DATA_DIRS) -> list[PlaceholderFinding]:
    findings: list[PlaceholderFinding] = []
    for csv_file in iter_csv_files(paths):
        findings.extend(scan_csv(csv_file))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="Optional CSV directories to scan; defaults to data/candidates and data/manual.")
    args = parser.parse_args(argv)
    paths = tuple(args.paths) if args.paths else DATA_DIRS
    findings = scan(paths)
    if findings:
        for finding in findings:
            relative = finding.path.relative_to(ROOT) if finding.path.is_relative_to(ROOT) else finding.path
            print(f"PLACEHOLDER {relative}:{finding.row_number} field '{finding.field}' contains '{finding.pattern}'", file=sys.stderr)
        return 1
    print("No placeholder data found in candidate or manual CSV files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
