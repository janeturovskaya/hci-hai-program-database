#!/usr/bin/env python3
"""Report potential duplicate records in manual CSV files using fuzzy matching."""
from __future__ import annotations

import argparse
import csv
from difflib import SequenceMatcher
from itertools import combinations
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIELDS = {
    "universities": "university_name",
    "programs": "program_name",
    "faculty": "name",
    "labs": "lab_name",
}


def load_schema(path: Path) -> dict[str, Any]:
    schema: dict[str, Any] = {}
    current_table: str | None = None
    current_key: str | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        if indent == 0 and stripped.endswith(":"):
            current_table = stripped[:-1]
            schema[current_table] = {}
            current_key = None
        elif indent == 2 and current_table:
            key, _, value = stripped.partition(":")
            schema[current_table][key] = value.strip() if value.strip() else []
            current_key = None if value.strip() else key
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


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def token_set_ratio(left: str, right: str) -> float:
    """Return a rapidfuzz-like token set similarity score from 0 to 100."""
    left_tokens = set(left.lower().split())
    right_tokens = set(right.lower().split())
    if not left_tokens and not right_tokens:
        return 100.0
    intersection = " ".join(sorted(left_tokens & right_tokens))
    left_remainder = " ".join(sorted(left_tokens - right_tokens))
    right_remainder = " ".join(sorted(right_tokens - left_tokens))
    left_combined = " ".join(part for part in (intersection, left_remainder) if part)
    right_combined = " ".join(part for part in (intersection, right_remainder) if part)
    return SequenceMatcher(None, left_combined, right_combined).ratio() * 100


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=ROOT / "schema/manual_csv_schemas.yaml")
    parser.add_argument("--threshold", type=int, default=90)
    args = parser.parse_args()

    schema = load_schema(args.schema)
    found = False
    for table, field in DEFAULT_FIELDS.items():
        path = ROOT / schema[table]["file"]
        rows = read_csv(path)
        for (left_idx, left), (right_idx, right) in combinations(enumerate(rows), 2):
            score = token_set_ratio(left[field], right[field])
            if score >= args.threshold:
                found = True
                print(f"{table}: rows {left_idx + 2} and {right_idx + 2} score={score:.1f} field={field}")
    if not found:
        print("No potential duplicates found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
