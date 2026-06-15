#!/usr/bin/env python3
"""Report potential duplicate records in manual CSV files using fuzzy matching."""
from __future__ import annotations

import argparse
from itertools import combinations
from pathlib import Path

import pandas as pd
import yaml
from rapidfuzz import fuzz

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIELDS = {
    "universities": "university_name",
    "programs": "program_name",
    "faculty": "name",
    "labs": "lab_name",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=ROOT / "schema/manual_csv_schemas.yaml")
    parser.add_argument("--threshold", type=int, default=90)
    args = parser.parse_args()

    schema = yaml.safe_load(args.schema.read_text(encoding="utf-8"))
    found = False
    for table, field in DEFAULT_FIELDS.items():
        path = ROOT / schema[table]["file"]
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
        for (left_idx, left), (right_idx, right) in combinations(df.iterrows(), 2):
            score = fuzz.token_set_ratio(left[field], right[field])
            if score >= args.threshold:
                found = True
                print(f"{table}: rows {left_idx + 2} and {right_idx + 2} score={score:.1f} field={field}")
    if not found:
        print("No potential duplicates found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
