#!/usr/bin/env python3
"""Audit exploratory program scores for completeness and evidence traceability."""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from validate_manual_data import ROOT, SCORE_FIELDS, read_csv, validate_all

SCORES_FILE = ROOT / "data/manual/program_scores.csv"
PROGRAMS_FILE = ROOT / "data/manual/programs.csv"
UNIVERSITIES_FILE = ROOT / "data/manual/universities.csv"
EVIDENCE_FILE = ROOT / "data/manual/evidence.csv"
REPORT_FILE = ROOT / "reports/program_scoring_audit.md"

KEY_CLAIM_CATEGORIES = (
    "hci_strength",
    "hai_strength",
    "faculty_lab_fit",
    "research_access_for_masters",
    "quant_data_ai_curriculum",
    "methods_fit",
    "career_relevance",
    "practical_fit",
)
CONFIDENCE_VALUES = ("high", "medium", "low")


def split_evidence_ids(value: str) -> list[str]:
    return [item.strip() for item in value.split(";") if item.strip()]


def summarize_notes(notes: list[str], limit: int = 3) -> list[tuple[str, int]]:
    counts = Counter(note.strip() for note in notes if note.strip())
    return counts.most_common(limit)


def program_title(program: dict[str, str], universities_by_id: dict[str, dict[str, str]]) -> str:
    university = universities_by_id.get(program.get("university_id", ""), {})
    return f"{university.get('university_name', program.get('university_id', ''))} — {program.get('program_name', '')}"


def build_audit_lines(programs: list[dict[str, str]], universities: list[dict[str, str]], scores: list[dict[str, str]], evidence_rows: list[dict[str, str]]) -> list[str]:
    universities_by_id = {row.get("university_id", ""): row for row in universities}
    evidence_by_id = {row.get("evidence_id", ""): row for row in evidence_rows if row.get("evidence_id", "")}
    scores_by_program: dict[str, list[dict[str, str]]] = defaultdict(list)
    for score in scores:
        scores_by_program[score.get("program_id", "")].append(score)

    used_evidence_ids: set[str] = set()
    warnings: list[str] = []
    ie_by_dimension = Counter()
    low_by_dimension = Counter()
    dimension_counts: dict[str, Counter[str]] = {field: Counter() for field in SCORE_FIELDS}
    dimension_confidence: dict[str, Counter[str]] = {field: Counter() for field in SCORE_FIELDS}
    missing_notes_by_dimension: dict[str, list[str]] = {field: [] for field in SCORE_FIELDS}

    for score in scores:
        evidence_ids = split_evidence_ids(score.get("source_evidence_ids", ""))
        used_evidence_ids.update(evidence_ids)
        has_any_evidence = bool(evidence_ids)
        for field in SCORE_FIELDS:
            value = score.get(field, "").strip()
            confidence = score.get(f"{field}_confidence", "").strip()
            if value in {"0", "1", "2", "3"}:
                dimension_counts[field]["numeric"] += 1
                if not has_any_evidence:
                    warnings.append(f"Score `{score.get('score_id', '')}` has numeric `{field}` but no source_evidence_ids.")
            elif value == "IE":
                dimension_counts[field]["IE"] += 1
                ie_by_dimension[field] += 1
                note = score.get("missing_evidence_notes", "").strip()
                if note:
                    missing_notes_by_dimension[field].append(note)
                else:
                    warnings.append(f"Score `{score.get('score_id', '')}` has IE for `{field}` but blank missing_evidence_notes.")
            elif value == "NA":
                dimension_counts[field]["NA"] += 1
            else:
                dimension_counts[field]["blank"] += 1
            if confidence in CONFIDENCE_VALUES:
                dimension_confidence[field][confidence] += 1
                if confidence == "low":
                    low_by_dimension[field] += 1
                    warnings.append(f"Score `{score.get('score_id', '')}` has low confidence for `{field}`.")

        for evidence_id in evidence_ids:
            evidence = evidence_by_id.get(evidence_id)
            if evidence is None:
                warnings.append(f"Score `{score.get('score_id', '')}` references missing evidence ID `{evidence_id}`.")
            elif not evidence.get("claim_category", "").strip():
                warnings.append(f"Score `{score.get('score_id', '')}` uses evidence `{evidence_id}` with blank claim_category.")

    used_existing_evidence = [evidence_by_id[eid] for eid in sorted(used_evidence_ids) if eid in evidence_by_id]
    used_with_category = sum(1 for row in used_existing_evidence if row.get("claim_category", "").strip())
    used_without_category = sum(1 for row in used_existing_evidence if not row.get("claim_category", "").strip())
    unscored_programs = [program for program in programs if program.get("program_id", "") not in scores_by_program]
    for program in unscored_programs:
        warnings.append(f"Canonical program has no score row: {program_title(program, universities_by_id)} (`{program.get('program_id', '')}`).")

    program_count = len(programs) or 1
    for field, count in ie_by_dimension.items():
        if count == len(programs) or count / program_count >= 0.5:
            warnings.append(f"Most programs have IE for `{field}` ({count}/{len(programs)} scored/program slots).")

    category_counts = Counter((row.get("claim_category", "").strip() or "(blank)") for row in evidence_rows)

    lines = [
        "# Program scoring audit",
        "",
        "This report audits exploratory score completeness and evidence traceability. It is a review aid, not a ranking.",
        "",
        "## Overall summary",
        "",
        f"* Canonical programs: {len(programs)}",
        f"* Scored programs: {len(scores_by_program)}",
        f"* Unscored canonical programs: {len(unscored_programs)}",
        f"* Score rows: {len(scores)}",
        f"* Evidence IDs used by scores: {len(used_evidence_ids)}",
        f"* Used evidence rows with claim_category: {used_with_category}",
        f"* Used evidence rows without claim_category: {used_without_category}",
        "",
        "### IE values by dimension",
        "",
    ]
    lines.extend(f"* `{field}`: {ie_by_dimension.get(field, 0)}" for field in SCORE_FIELDS)
    lines += ["", "### Low-confidence scores by dimension", ""]
    lines.extend(f"* `{field}`: {low_by_dimension.get(field, 0)}" for field in SCORE_FIELDS)

    lines += ["", "## Per-program audit", ""]
    for program in programs:
        title = program_title(program, universities_by_id)
        program_scores = scores_by_program.get(program.get("program_id", ""), [])
        lines += [f"### {title}", "", f"* Program ID: `{program.get('program_id', '')}`", f"* Has score row: {'yes' if program_scores else 'no'}"]
        if not program_scores:
            lines.append("")
            continue
        for score in program_scores:
            evidence_ids = split_evidence_ids(score.get("source_evidence_ids", ""))
            missing_ids = [eid for eid in evidence_ids if eid not in evidence_by_id]
            blank_category_ids = [eid for eid in evidence_ids if eid in evidence_by_id and not evidence_by_id[eid].get("claim_category", "").strip()]
            ie_dims = [field for field in SCORE_FIELDS if score.get(field, "").strip() == "IE"]
            low_dims = [field for field in SCORE_FIELDS if score.get(f"{field}_confidence", "").strip() == "low"]
            lines += [
                "",
                f"#### Score `{score.get('score_id', '')}`",
                "",
                "| Dimension | Score | Confidence |",
                "| --- | --- | --- |",
            ]
            for field in SCORE_FIELDS:
                lines.append(f"| {field} | {score.get(field, '')} | {score.get(f'{field}_confidence', '')} |")
            lines += [
                "",
                f"* Source evidence IDs: {score.get('source_evidence_ids', '') or 'None recorded.'}",
                f"* Evidence IDs exist: {'yes' if not missing_ids else 'no — missing ' + ', '.join(f'`{eid}`' for eid in missing_ids)}",
                f"* Listed evidence rows have claim_category: {'yes' if evidence_ids and not blank_category_ids and not missing_ids else 'no' if evidence_ids else 'no evidence IDs listed'}",
                f"* Blank claim_category evidence IDs: {', '.join(f'`{eid}`' for eid in blank_category_ids) if blank_category_ids else 'None'}",
                f"* IE dimensions: {', '.join(f'`{field}`' for field in ie_dims) if ie_dims else 'None'}",
                f"* Low-confidence dimensions: {', '.join(f'`{field}`' for field in low_dims) if low_dims else 'None'}",
                f"* Missing evidence notes: {score.get('missing_evidence_notes', '') or 'None recorded.'}",
                "",
            ]

    lines += ["## Dimension coverage", ""]
    for field in SCORE_FIELDS:
        counts = dimension_counts[field]
        conf = dimension_confidence[field]
        lines += [
            f"### `{field}`",
            "",
            f"* Numeric scores: {counts.get('numeric', 0)}",
            f"* IE: {counts.get('IE', 0)}",
            f"* NA: {counts.get('NA', 0)}",
            f"* Blank: {counts.get('blank', 0)}",
            f"* High confidence: {conf.get('high', 0)}",
            f"* Medium confidence: {conf.get('medium', 0)}",
            f"* Low confidence: {conf.get('low', 0)}",
        ]
        common_notes = summarize_notes(missing_notes_by_dimension[field])
        if common_notes:
            lines.append("* Common missing evidence notes:")
            lines.extend(f"  * ({count}) {note}" for note, count in common_notes)
        else:
            lines.append("* Common missing evidence notes: None recorded.")
        lines.append("")

    lines += ["## Evidence-category coverage", "", "### Key scoring categories", ""]
    lines.extend(f"* `{category}`: {category_counts.get(category, 0)}" for category in KEY_CLAIM_CATEGORIES)
    lines += ["", "### All claim categories", ""]
    for category, count in sorted(category_counts.items()):
        lines.append(f"* `{category}`: {count}")

    lines += ["", "## Audit warnings", ""]
    lines.extend([f"* {warning}" for warning in warnings] or ["* None"])
    lines.append("")
    return lines


def audit_program_scores() -> int:
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
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text("\n".join(build_audit_lines(programs, universities, scores, evidence_rows)), encoding="utf-8")
    print(f"Wrote {REPORT_FILE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(audit_program_scores())
