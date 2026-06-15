#!/usr/bin/env python3
"""Validate manual CSV templates/data against the project schema."""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd
import yaml
from pydantic import BaseModel, Field, HttpUrl, ValidationError, field_validator

ROOT = Path(__file__).resolve().parents[1]


class RowModel(BaseModel):
    """Shared permissive row checks for source-tracked research data."""

    model_config = {"extra": "allow"}

    last_checked: date | None = None
    source_url: HttpUrl | None = None
    official_url: HttpUrl | None = None
    faculty_url: HttpUrl | None = None
    google_scholar_url: HttpUrl | None = None
    lab_url: HttpUrl | None = None
    publications_url: HttpUrl | None = None
    confidence: str | None = None
    entity_type: str | None = None

    @field_validator("confidence")
    @classmethod
    def confidence_is_known(cls, value: str | None) -> str | None:
        if value in (None, ""):
            return None
        allowed = {"low", "medium", "high"}
        if value not in allowed:
            raise ValueError(f"confidence must be one of {sorted(allowed)}")
        return value

    @field_validator("entity_type")
    @classmethod
    def entity_type_is_known(cls, value: str | None) -> str | None:
        if value in (None, ""):
            return None
        allowed = {"university", "program", "faculty", "lab"}
        if value not in allowed:
            raise ValueError(f"entity_type must be one of {sorted(allowed)}")
        return value


class ValidationIssue(BaseModel):
    table: str
    row: int | None = None
    message: str
    severity: str = Field(default="error")


def load_schema(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def validate_table(table: str, spec: dict[str, Any], root: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    path = root / spec["file"]
    if not path.exists():
        return [ValidationIssue(table=table, message=f"Missing file: {path}")]

    df = read_csv(path)
    expected = list(spec["columns"])
    actual = list(df.columns)
    if actual != expected:
        issues.append(
            ValidationIssue(
                table=table,
                message=f"Columns differ. Expected {expected}; found {actual}",
            )
        )
        return issues

    primary_key = spec["primary_key"]
    if primary_key in df.columns and df[primary_key].duplicated().any():
        issues.append(ValidationIssue(table=table, message=f"Duplicate {primary_key} values found"))

    required = list(spec.get("required", []))
    for index, row in df.iterrows():
        row_number = int(index) + 2
        for column in required:
            if not str(row.get(column, "")).strip():
                issues.append(ValidationIssue(table=table, row=row_number, message=f"Missing required {column}"))
        values = {key: (value or None) for key, value in row.to_dict().items()}
        try:
            RowModel.model_validate(values)
        except ValidationError as error:
            issues.append(ValidationIssue(table=table, row=row_number, message=str(error)))

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
