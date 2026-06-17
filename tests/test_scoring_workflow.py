import csv
import tempfile
import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from unittest.mock import patch

from scripts import generate_scoring_report, score_program, validate_manual_data

COLS = score_program.COLUMNS


def write_csv(path, cols, rows):
    with path.open('w', encoding='utf-8', newline='') as h:
        w=csv.DictWriter(h, fieldnames=cols); w.writeheader(); w.writerows(rows)


class ScoringWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)
        self.programs=self.root/'programs.csv'; self.evidence=self.root/'evidence.csv'; self.scores=self.root/'program_scores.csv'; self.universities=self.root/'universities.csv'; self.report=self.root/'program_scoring.md'
        write_csv(self.programs, ['program_id','university_id','program_name'], [{'program_id':'prog_1','university_id':'univ_1','program_name':'Program One'}])
        write_csv(self.universities, ['university_id','university_name'], [{'university_id':'univ_1','university_name':'University One'}])
        write_csv(self.evidence, ['evidence_id'], [{'evidence_id':'ev_1'}])
        write_csv(self.scores, COLS, [])
        self.schema={'program_scores': {'file':'program_scores.csv'}, 'programs': {'file':'programs.csv'}, 'evidence': {'file':'evidence.csv'}}
        self.patches=[
            patch.object(score_program,'SCORES_FILE',self.scores), patch.object(score_program,'PROGRAMS_FILE',self.programs), patch.object(score_program,'EVIDENCE_FILE',self.evidence),
            patch.object(generate_scoring_report,'SCORES_FILE',self.scores), patch.object(generate_scoring_report,'PROGRAMS_FILE',self.programs), patch.object(generate_scoring_report,'UNIVERSITIES_FILE',self.universities), patch.object(generate_scoring_report,'REPORT_FILE',self.report),
            patch.object(validate_manual_data,'ROOT',self.root), patch.object(score_program,'ROOT',self.root), patch.object(generate_scoring_report,'ROOT',self.root),
            patch.object(score_program, 'validate_all', lambda: validate_manual_data.validate_table('program_scores', {'file':'program_scores.csv','primary_key':'score_id','required':['score_id','program_id','scorer'],'columns':COLS}, self.root, {'validation':{}}) + validate_manual_data.validate_program_scores(self.schema, self.root)),
            patch.object(generate_scoring_report, 'validate_all', lambda: validate_manual_data.validate_table('program_scores', {'file':'program_scores.csv','primary_key':'score_id','required':['score_id','program_id','scorer'],'columns':COLS}, self.root, {'validation':{}}) + validate_manual_data.validate_program_scores(self.schema, self.root)),
        ]
        for p in self.patches: p.start()
    def tearDown(self):
        for p in reversed(self.patches): p.stop()
        self.tmp.cleanup()
    def rows(self): return list(csv.DictReader(self.scores.open(encoding='utf-8')))
    def validate_rows(self, rows):
        write_csv(self.scores, COLS, rows)
        return validate_manual_data.validate_program_scores(self.schema, self.root)
    def base(self):
        r={c:'' for c in COLS}; r.update({'score_id':'s1','program_id':'prog_1','scorer':'me','hci_strength':'3','hci_strength_confidence':'high','source_evidence_ids':'ev_1'}); return r
    def test_valid_score_row_validation(self): self.assertEqual(self.validate_rows([self.base()]), [])
    def test_invalid_score_value(self):
        r=self.base(); r['hci_strength']='4'; self.assertTrue(self.validate_rows([r]))
    def test_invalid_confidence_value(self):
        r=self.base(); r['hci_strength_confidence']='certain'; self.assertTrue(self.validate_rows([r]))
    def test_missing_program_id(self):
        r=self.base(); r['program_id']=''; issues=self.validate_rows([r]); self.assertTrue(any('Missing required program_id' in i.message for i in validate_manual_data.validate_table('program_scores', {'file':'program_scores.csv','primary_key':'score_id','required':['program_id'],'columns':COLS}, self.root, {'validation':{}})))
    def test_unknown_program_id(self):
        r=self.base(); r['program_id']='missing'; self.assertTrue(any('was not found' in i.message for i in self.validate_rows([r])))
    def test_unknown_evidence_id(self):
        r=self.base(); r['source_evidence_ids']='ev_missing'; self.assertTrue(any('unknown evidence_id' in i.message for i in self.validate_rows([r])))
    def test_missing_evidence_notes_required_when_ie(self):
        r=self.base(); r['hai_strength']='IE'; self.assertTrue(any('missing_evidence_notes' in i.message for i in self.validate_rows([r])))
    def parse(self,args): return score_program.build_parser().parse_args(args)
    def test_score_program_adds_score(self):
        rc=score_program.score_program(self.parse(['prog_1','--scorer','me','--hci-strength','3','--hci-strength-confidence','high','--source-evidence-ids','ev_1']))
        self.assertEqual(rc,0); self.assertEqual(len(self.rows()),1)
    def test_score_program_updates_existing_score(self):
        args=['prog_1','--scorer','me','--scoring-date','2026-01-01','--hci-strength','3','--hci-strength-confidence','high']
        score_program.score_program(self.parse(args)); score_program.score_program(self.parse(args+['--overall-notes','updated']))
        self.assertEqual(len(self.rows()),1); self.assertEqual(self.rows()[0]['overall_notes'],'updated')
    def test_rollback_on_validation_failure(self):
        self.assertEqual(score_program.score_program(self.parse(['prog_1','--scorer','me','--hai-strength','IE'])),1)
        self.assertEqual(self.rows(),[])
    def test_scoring_report_generation(self):
        score_program.score_program(self.parse(['prog_1','--scorer','me','--hci-strength','3','--hci-strength-confidence','high']))
        self.assertEqual(generate_scoring_report.generate_report(),0)
        self.assertIn('University One', self.report.read_text(encoding='utf-8'))

if __name__ == '__main__': unittest.main()
