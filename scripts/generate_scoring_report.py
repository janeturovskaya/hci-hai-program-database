#!/usr/bin/env python3
"""Generate a non-ranking pilot scoring review report."""
from __future__ import annotations

from pathlib import Path

from validate_manual_data import ROOT, SCORE_FIELDS, read_csv, validate_all

SCORES_FILE = ROOT / "data/manual/program_scores.csv"
PROGRAMS_FILE = ROOT / "data/manual/programs.csv"
UNIVERSITIES_FILE = ROOT / "data/manual/universities.csv"
REPORT_FILE = ROOT / "reports/program_scoring.md"


def generate_report() -> int:
    issues = validate_all()
    if issues:
        for issue in issues:
            location = f":{issue.row}" if issue.row else ""
            print(f"ERROR {issue.table}{location} - {issue.message}")
        return 1
    _, programs = read_csv(PROGRAMS_FILE)
    _, universities = read_csv(UNIVERSITIES_FILE)
    _, scores = read_csv(SCORES_FILE)
    univ_by_id = {u["university_id"]: u for u in universities}
    scores_by_program: dict[str, list[dict[str, str]]] = {}
    for score in scores:
        scores_by_program.setdefault(score.get("program_id", ""), []).append(score)

    lines = ["# Pilot program scoring report", "", "This report is a review aid, not a ranking.", ""]
    low_or_ie: list[str] = []
    for program in programs:
        university = univ_by_id.get(program.get("university_id", ""), {})
        title = f"{university.get('university_name', program.get('university_id', ''))} — {program.get('program_name', '')}"
        lines += [f"## {title}", ""]
        program_scores = scores_by_program.get(program["program_id"], [])
        if not program_scores:
            lines += ["No score has been recorded for this program.", ""]
            continue
        for score in program_scores:
            lines += [f"### Score `{score['score_id']}`", "", f"Scorer: {score.get('scorer','')}  ", f"Date: {score.get('scoring_date','')}", "", "| Dimension | Score | Confidence |", "| --- | --- | --- |"]
            for field in SCORE_FIELDS:
                val = score.get(field, "")
                conf = score.get(f"{field}_confidence", "")
                lines.append(f"| {field} | {val} | {conf} |")
                if val == "IE" or conf == "low":
                    low_or_ie.append(f"{title}: {field}={val} confidence={conf}")
            lines += ["", f"Missing evidence notes: {score.get('missing_evidence_notes','') or 'None recorded.'}", "", f"Source evidence IDs: {score.get('source_evidence_ids','') or 'None recorded.'}", "", f"Overall notes: {score.get('overall_notes','') or 'None recorded.'}", ""]
    unscored = [p for p in programs if p["program_id"] not in scores_by_program]
    lines += ["## Warnings: programs without scores", ""]
    lines += ([f"* {p['program_name']} (`{p['program_id']}`)" for p in unscored] or ["* None"])
    lines += ["", "## Warnings: IE scores or low confidence", ""]
    lines += ([f"* {item}" for item in low_or_ie] or ["* None"])
    lines.append("")
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {REPORT_FILE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(generate_report())
