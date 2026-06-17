#!/usr/bin/env python3
"""Validate manual and candidate CSV templates/data against the project schema."""
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
CANDIDATE_ENTITY_TABLES = {
    "university": "candidate_universities",
    "program": "candidate_programs",
    "faculty": "candidate_faculty",
    "lab": "candidate_labs",
}


@dataclass
class ValidationIssue:
    table: str
    message: str
    row: int | None = None
    severity: str = "error"


def load_simple_yaml(path: Path) -> dict[str, Any]:
    """Load this repository's limited YAML structures without third-party packages."""
    data: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = [(-1, data)]

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if stripped.startswith("- "):
            if not isinstance(parent, list):
                raise ValueError(f"Unsupported YAML list placement: {raw_line}")
            parent.append(stripped[2:].strip().strip("'\""))
            continue
        key, _, value = stripped.partition(":")
        if value.strip():
            if isinstance(parent, dict):
                parent[key] = value.strip().strip("'\"")
            continue
        container: Any = [] if key in {"required", "columns", "allowed_entity_types", "allowed_confidence", "allowed_review_statuses", "allowed_relevant_areas"} else {}
        if isinstance(parent, dict):
            parent[key] = container
        stack.append((indent, container))
    return data


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def is_valid_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate_row_values(
    table: str,
    row_number: int,
    values: dict[str, str],
    allowed_confidence: set[str],
    allowed_entity_types: set[str],
    allowed_review_statuses: set[str],
    allowed_relevant_areas: set[str],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for field in ("last_checked", "date_accessed", "discovered_date"):
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
    if confidence and confidence not in allowed_confidence:
        issues.append(ValidationIssue(table=table, row=row_number, message=f"confidence must be one of {sorted(allowed_confidence)}"))

    entity_type = values.get("entity_type", "").strip() or values.get("associated_entity_type", "").strip()
    if entity_type and entity_type not in allowed_entity_types:
        issues.append(ValidationIssue(table=table, row=row_number, message=f"entity type must be one of {sorted(allowed_entity_types)}"))

    review_status = values.get("review_status", "").strip()
    if review_status and review_status not in allowed_review_statuses:
        issues.append(ValidationIssue(table=table, row=row_number, message=f"review_status must be one of {sorted(allowed_review_statuses)}"))

    relevant_area = values.get("relevant_area", "").strip()
    if relevant_area and relevant_area not in allowed_relevant_areas:
        issues.append(ValidationIssue(table=table, row=row_number, message=f"relevant_area must be one of {sorted(allowed_relevant_areas)}"))

    secondary_relevant_areas = values.get("secondary_relevant_areas", "").strip()
    if secondary_relevant_areas:
        secondary_values = [value.strip() for value in secondary_relevant_areas.split(";") if value.strip()]
        for secondary_area in secondary_values:
            if secondary_area not in allowed_relevant_areas:
                issues.append(ValidationIssue(table=table, row=row_number, message=f"secondary_relevant_areas values must be one of {sorted(allowed_relevant_areas)}"))
        duplicates = sorted({value for value in secondary_values if secondary_values.count(value) > 1})
        if duplicates:
            issues.append(ValidationIssue(table=table, row=row_number, message=f"secondary_relevant_areas contains duplicate values: {duplicates}"))
        if relevant_area and relevant_area in secondary_values:
            issues.append(ValidationIssue(table=table, row=row_number, message="secondary_relevant_areas must not repeat primary relevant_area"))

    return issues


def validate_table(table: str, spec: dict[str, Any], root: Path, config: dict[str, Any]) -> list[ValidationIssue]:
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
    populated_primary_values = [row.get(primary_key, "").strip() for row in rows if row.get(primary_key, "").strip()]
    if len(populated_primary_values) != len(set(populated_primary_values)):
        issues.append(ValidationIssue(table=table, message=f"Duplicate {primary_key} values found"))

    validation = config.get("validation", {})
    allowed_confidence = set(validation.get("allowed_confidence", []))
    allowed_entity_types = set(validation.get("allowed_entity_types", []))
    allowed_review_statuses = set(validation.get("allowed_review_statuses", []))
    allowed_relevant_areas = set(validation.get("allowed_relevant_areas", []))

    for index, row in enumerate(rows):
        row_number = index + 2
        for column in spec.get("required", []):
            if not row.get(column, "").strip():
                issues.append(ValidationIssue(table=table, row=row_number, message=f"Missing required {column}"))
        issues.extend(validate_row_values(table, row_number, row, allowed_confidence, allowed_entity_types, allowed_review_statuses, allowed_relevant_areas))

    return issues


def validate_candidate_source_associations(schema: dict[str, Any], root: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    candidate_ids: dict[str, set[str]] = {}
    for entity_type, table in CANDIDATE_ENTITY_TABLES.items():
        spec = schema.get(table)
        if not spec:
            continue
        _, rows = read_csv(root / spec["file"])
        candidate_ids[entity_type] = {row.get("candidate_id", "").strip() for row in rows if row.get("candidate_id", "").strip()}

    spec = schema.get("candidate_sources")
    if not spec:
        return issues
    _, rows = read_csv(root / spec["file"])
    for index, row in enumerate(rows):
        row_number = index + 2
        entity_type = row.get("associated_entity_type", "").strip()
        candidate_id = row.get("associated_candidate_id", "").strip()
        if entity_type and not candidate_id:
            issues.append(ValidationIssue(table="candidate_sources", row=row_number, message="associated_candidate_id is required when associated_entity_type is provided"))
        if candidate_id and not entity_type:
            issues.append(ValidationIssue(table="candidate_sources", row=row_number, message="associated_entity_type is required when associated_candidate_id is provided"))
        if entity_type in candidate_ids and candidate_id and candidate_id not in candidate_ids[entity_type]:
            issues.append(ValidationIssue(table="candidate_sources", row=row_number, message=f"associated_candidate_id '{candidate_id}' was not found in {CANDIDATE_ENTITY_TABLES[entity_type]}"))
    return issues


def validate_all(schema_path: Path = ROOT / "schema/manual_csv_schemas.yaml", config_path: Path = ROOT / "config/settings.yaml") -> list[ValidationIssue]:
    schema = load_simple_yaml(schema_path)
    config = load_simple_yaml(config_path)
    issues: list[ValidationIssue] = []
    for table, spec in schema.items():
        issues.extend(validate_table(table, spec, ROOT, config))
    issues.extend(validate_candidate_source_associations(schema, ROOT))
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=ROOT / "schema/manual_csv_schemas.yaml")
    parser.add_argument("--config", type=Path, default=ROOT / "config/settings.yaml")
    args = parser.parse_args()

    issues = validate_all(args.schema, args.config)
    if issues:
        for issue in issues:
            location = f":{issue.row}" if issue.row else ""
            print(f"{issue.severity.upper()} {issue.table}{location} - {issue.message}", file=sys.stderr)
        return 1

    print("Manual and candidate CSV validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
