#!/usr/bin/env python3
"""Validate manual CSV templates/data against the project schema."""
from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
URL_FIELDS = {
    "source_url",
    "official_url",
    "faculty_url",
    "google_scholar_url",
    "lab_url",
    "publications_url",
}
ALLOWED_CONFIDENCE = {"low", "medium", "high"}
ALLOWED_ENTITY_TYPES = {"university", "program", "faculty", "lab"}


@dataclass
class ValidationIssue:
    table: str
    message: str
    row: int | None = None
    severity: str = "error"


def load_schema(path: Path) -> dict[str, Any]:
    """Load the repository's simple YAML schema without third-party packages."""
    schema: dict[str, Any] = {}
    current_table: str | None = None
    current_key: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line_without_comment = raw_line.split("#", 1)[0].rstrip()
        if not line_without_comment.strip():
            continue

        indent = len(line_without_comment) - len(line_without_comment.lstrip(" "))
        stripped = line_without_comment.strip()

        if indent == 0 and stripped.endswith(":"):
            current_table = stripped[:-1]
            schema[current_table] = {}
            current_key = None
        elif indent == 2 and current_table:
            key, _, value = stripped.partition(":")
            if value.strip():
                schema[current_table][key] = value.strip()
                current_key = None
            else:
                schema[current_table][key] = []
                current_key = key
        elif indent == 4 and stripped.startswith("- ") and current_table and current_key:
            schema[current_table][current_key].append(stripped[2:].strip())
        elif indent == 4 and current_table:
            key, _, value = stripped.partition(":")
            parent = schema[current_table].setdefault(current_key or "", {})
            if isinstance(parent, dict):
                parent[key] = value.strip()
        else:
            raise ValueError(f"Unsupported schema syntax: {raw_line}")

    return schema


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def is_valid_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate_row_values(table: str, row_number: int, values: dict[str, str]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for field in ("last_checked", "date_accessed"):
        value = values.get(field, "").strip()
        if value:
            try:
                date.fromisoformat(value)
            except ValueError:
                issues.append(ValidationIssue(table=table, row=row_number, message=f"{field} must be an ISO date (YYYY-MM-DD)"))

    for field in URL_FIELDS:
        value = values.get(field, "").strip()
        if value and not is_valid_url(value):
            issues.append(ValidationIssue(table=table, row=row_number, message=f"{field} must be an http(s) URL"))

    confidence = values.get("confidence", "").strip()
    if confidence and confidence not in ALLOWED_CONFIDENCE:
        issues.append(ValidationIssue(table=table, row=row_number, message=f"confidence must be one of {sorted(ALLOWED_CONFIDENCE)}"))

    entity_type = values.get("entity_type", "").strip()
    if entity_type and entity_type not in ALLOWED_ENTITY_TYPES:
        issues.append(ValidationIssue(table=table, row=row_number, message=f"entity_type must be one of {sorted(ALLOWED_ENTITY_TYPES)}"))

    return issues


def validate_table(table: str, spec: dict[str, Any], root: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    path = root / spec["file"]
    if not path.exists():
        return [ValidationIssue(table=table, message=f"Missing file: {path}")]

    columns, rows = read_csv(path)
    expected = list(spec["columns"])
    if columns != expected:
        issues.append(ValidationIssue(table=table, message=f"Columns differ. Expected {expected}; found {columns}"))
        return issues

    primary_key = spec["primary_key"]
    primary_values = [row.get(primary_key, "") for row in rows]
    populated_primary_values = [value for value in primary_values if value]
    if len(populated_primary_values) != len(set(populated_primary_values)):
        issues.append(ValidationIssue(table=table, message=f"Duplicate {primary_key} values found"))

    required = list(spec.get("required", []))
    for index, row in enumerate(rows):
        row_number = index + 2
        for column in required:
            if not row.get(column, "").strip():
                issues.append(ValidationIssue(table=table, row=row_number, message=f"Missing required {column}"))
        issues.extend(validate_row_values(table, row_number, row))

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=ROOT / "schema/manual_csv_schemas.yaml")
    args = parser.parse_args()

    schema = load_schema(args.schema)
    issues: list[ValidationIssue] = []
    for table, spec in schema.items():
        issues.extend(validate_table(table, spec, ROOT))

    if issues:
        for issue in issues:
            location = f":{issue.row}" if issue.row else ""
            print(f"{issue.severity.upper()} {issue.table}{location} - {issue.message}", file=sys.stderr)
        return 1

    print("Manual CSV validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
