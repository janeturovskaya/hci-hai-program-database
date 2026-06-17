#!/usr/bin/env python3
"""Add or update an evidence-aware score row for one canonical program."""
from __future__ import annotations

import argparse
import csv
import sys
from datetime import date
from pathlib import Path

from validate_manual_data import ROOT, SCORE_FIELDS, ALLOWED_SCORES, ALLOWED_SCORE_CONFIDENCE, read_csv, validate_all

SCORES_FILE = ROOT / "data/manual/program_scores.csv"
PROGRAMS_FILE = ROOT / "data/manual/programs.csv"
EVIDENCE_FILE = ROOT / "data/manual/evidence.csv"
COLUMNS = ['score_id','program_id','scoring_date','scorer'] + [x for f in SCORE_FIELDS for x in (f, f'{f}_confidence')] + ['overall_notes','missing_evidence_notes','source_evidence_ids']


def slugify(v: str) -> str:
    return '_'.join(''.join(ch.lower() if ch.isalnum() else ' ' for ch in v).split())[:80]


def write_rows(path: Path, rows: list[dict[str, str]]):
    with path.open('w', encoding='utf-8', newline='') as h:
        w=csv.DictWriter(h, fieldnames=COLUMNS); w.writeheader(); w.writerows(rows)


def score_program(args: argparse.Namespace) -> int:
    _, programs = read_csv(PROGRAMS_FILE)
    if args.program_id not in {p['program_id'] for p in programs}:
        print(f"ERROR: unknown program_id {args.program_id}", file=sys.stderr); return 2
    _, evidence = read_csv(EVIDENCE_FILE)
    known_evidence = {e['evidence_id'] for e in evidence}
    for eid in [x.strip() for x in args.source_evidence_ids.split(';') if x.strip()]:
        if eid not in known_evidence:
            print(f"ERROR: unknown evidence ID {eid}", file=sys.stderr); return 2
    updates: dict[str,str] = {}
    for field in SCORE_FIELDS:
        score = getattr(args, field)
        conf = getattr(args, f'{field}_confidence')
        if score and score not in ALLOWED_SCORES:
            print(f"ERROR: invalid score for {field}", file=sys.stderr); return 2
        if conf and conf not in ALLOWED_SCORE_CONFIDENCE:
            print(f"ERROR: invalid confidence for {field}", file=sys.stderr); return 2
        if score: updates[field] = score
        if conf: updates[f'{field}_confidence'] = conf
    scoring_date = args.scoring_date or date.today().isoformat()
    _, rows = read_csv(SCORES_FILE)
    target = None
    if not args.new_score:
        for row in rows:
            if row.get('program_id') == args.program_id and row.get('scorer') == args.scorer and row.get('scoring_date') == scoring_date:
                target = row; break
    if target is None:
        existing = {r.get('score_id','') for r in rows}
        base = f"score_{slugify(args.program_id)}_{slugify(args.scorer)}_{scoring_date.replace('-', '_')}"
        score_id = base; i=2
        while score_id in existing:
            score_id = f"{base}_{i}"; i += 1
        target = {c: '' for c in COLUMNS}
        target.update({'score_id': score_id, 'program_id': args.program_id, 'scoring_date': scoring_date, 'scorer': args.scorer})
        rows.append(target)
    target.update(updates)
    if args.overall_notes is not None: target['overall_notes'] = args.overall_notes
    if args.missing_evidence_notes is not None: target['missing_evidence_notes'] = args.missing_evidence_notes
    if args.source_evidence_ids is not None: target['source_evidence_ids'] = args.source_evidence_ids
    backup = SCORES_FILE.read_text(encoding='utf-8') if SCORES_FILE.exists() else ''
    write_rows(SCORES_FILE, rows)
    issues = validate_all()
    if issues:
        SCORES_FILE.write_text(backup, encoding='utf-8')
        for issue in issues:
            loc=f":{issue.row}" if issue.row else ''
            print(f"ERROR {issue.table}{loc} - {issue.message}", file=sys.stderr)
        print('Rolled back score changes.', file=sys.stderr)
        return 1
    print(f"Wrote score row {target['score_id']}")
    if args.generate_report:
        from generate_scoring_report import generate_report
        return generate_report()
    return 0


def build_parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('program_id'); p.add_argument('--scorer', required=True); p.add_argument('--scoring-date', default=''); p.add_argument('--new-score', action='store_true')
    for field in SCORE_FIELDS:
        p.add_argument(f'--{field.replace("_", "-")}', dest=field, default='')
        p.add_argument(f'--{field.replace("_", "-")}-confidence', dest=f'{field}_confidence', default='')
    p.add_argument('--overall-notes'); p.add_argument('--missing-evidence-notes'); p.add_argument('--source-evidence-ids', default=''); p.add_argument('--generate-report', action='store_true')
    return p

if __name__ == '__main__':
    raise SystemExit(score_program(build_parser().parse_args()))
