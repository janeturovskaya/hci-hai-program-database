#!/usr/bin/env python3
"""Audit pilot program scores for evidence coverage and scoring gaps."""
from __future__ import annotations

from pathlib import Path

from validate_manual_data import ROOT, SCORE_FIELDS, read_csv, validate_all

SCORES_FILE = ROOT / "data/manual/program_scores.csv"
PROGRAMS_FILE = ROOT / "data/manual/programs.csv"
UNIVERSITIES_FILE = ROOT / "data/manual/universities.csv"
EVIDENCE_FILE = ROOT / "data/manual/evidence.csv"
REPORT_FILE = ROOT / "reports/program_scoring_audit.md"

DIMENSION_TO_CATEGORIES = {
    "hci_strength": {"hci_strength", "program_existence"},
    "hai_strength": {"hai_strength"},
    "faculty_lab_fit": {"faculty_lab_fit"},
    "research_access_for_masters": {"research_access_for_masters"},
    "quant_data_ai_curriculum": {"quant_data_ai_curriculum"},
    "methods_fit_for_uxr_psychology_background": {"methods_fit"},
    "career_relevance_for_ai_uxr": {"career_relevance"},
    "practical_fit": {"practical_fit", "cost", "deadline", "duration", "capstone", "online_available", "prerequisites"},
    "evidence_quality": {"hci_strength", "hai_strength", "faculty_lab_fit", "research_access_for_masters", "quant_data_ai_curriculum", "methods_fit", "career_relevance", "practical_fit"},
}


def _title(program: dict[str, str], universities: dict[str, dict[str, str]]) -> str:
    university = universities.get(program.get("university_id", ""), {})
    return f"{university.get('university_name', program.get('university_id', ''))} — {program.get('program_name', '')}"


def generate_audit() -> int:
    issues = validate_all()
    if issues:
        for issue in issues:
            location = f":{issue.row}" if issue.row else ""
            print(f"ERROR {issue.table}{location} - {issue.message}")
        return 1

    _, programs = read_csv(PROGRAMS_FILE)
    _, universities = read_csv(UNIVERSITIES_FILE)
    _, scores = read_csv(SCORES_FILE)
    _, evidence_rows = read_csv(EVIDENCE_FILE)

    programs_by_id = {row["program_id"]: row for row in programs}
    universities_by_id = {row["university_id"]: row for row in universities}
    evidence_by_id = {row["evidence_id"]: row for row in evidence_rows}

    missing_or_invalid_ids: list[str] = []
    used_without_category: list[str] = []
    ie_dimensions: list[str] = []
    category_counts: dict[str, int] = {}
    dimensions_without_category_support: list[str] = []

    lines = [
        "# Program scoring audit",
        "",
        "This audit checks exploratory score rows for IE dimensions, evidence ID validity, and claim-category coverage.",
        "",
        "## Score evidence coverage",
        "",
    ]

    for score in scores:
        program = programs_by_id.get(score.get("program_id", ""), {})
        title = _title(program, universities_by_id) if program else score.get("program_id", "")
        evidence_ids = [value.strip() for value in score.get("source_evidence_ids", "").split(";") if value.strip()]
        used_rows = []
        for evidence_id in evidence_ids:
            evidence = evidence_by_id.get(evidence_id)
            if not evidence:
                missing_or_invalid_ids.append(f"{title}: {evidence_id}")
                continue
            used_rows.append(evidence)
            category = evidence.get("claim_category", "").strip()
            if category:
                category_counts[category] = category_counts.get(category, 0) + 1
            else:
                used_without_category.append(f"{title}: {evidence_id}")

        used_categories = {row.get("claim_category", "").strip() for row in used_rows if row.get("claim_category", "").strip()}
        lines += [f"### {title}", "", f"Source evidence rows used: {len(used_rows)}", "", "| Dimension | Score | Confidence | Matching evidence category present? |", "| --- | --- | --- | --- |"]
        for field in SCORE_FIELDS:
            score_value = score.get(field, "")
            confidence = score.get(f"{field}_confidence", "")
            expected_categories = DIMENSION_TO_CATEGORIES.get(field, set())
            has_category = bool(used_categories & expected_categories)
            if score_value == "IE":
                ie_dimensions.append(f"{title}: {field}")
            if score_value and score_value != "IE" and not has_category:
                dimensions_without_category_support.append(f"{title}: {field}")
            lines.append(f"| {field} | {score_value} | {confidence} | {'yes' if has_category else 'no'} |")
        lines.append("")

    lines += [
        "## Summary",
        "",
        f"* IE dimensions: {len(ie_dimensions)}",
        f"* Invalid source evidence IDs: {len(missing_or_invalid_ids)}",
        f"* Used evidence rows missing claim_category: {len(used_without_category)}",
        f"* Scored dimensions without matching claim-category support: {len(dimensions_without_category_support)}",
        "",
        "## Evidence claim-category coverage among used score evidence",
        "",
    ]
    if category_counts:
        for category in sorted(category_counts):
            lines.append(f"* {category}: {category_counts[category]}")
    else:
        lines.append("* None")
    lines += ["", "## Remaining IE dimensions", ""]
    lines += [f"* {item}" for item in ie_dimensions] or ["* None"]
    lines += ["", "## Invalid source evidence IDs", ""]
    lines += [f"* {item}" for item in missing_or_invalid_ids] or ["* None"]
    lines += ["", "## Used evidence rows missing claim_category", ""]
    lines += [f"* {item}" for item in used_without_category] or ["* None"]
    lines += ["", "## Scored dimensions without matching claim-category support", ""]
    lines += [f"* {item}" for item in dimensions_without_category_support] or ["* None"]
    lines.append("")

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {REPORT_FILE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(generate_audit())
