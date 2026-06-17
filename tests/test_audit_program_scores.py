import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import audit_program_scores


class AuditProgramScoresTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.programs = self.root / "programs.csv"
        self.universities = self.root / "universities.csv"
        self.scores = self.root / "program_scores.csv"
        self.evidence = self.root / "evidence.csv"
        self.report = self.root / "program_scoring_audit.md"
        self.write_csv(self.universities, ["university_id", "university_name"], [
            {"university_id": "univ_1", "university_name": "Example University"},
        ])
        self.write_csv(self.programs, ["program_id", "university_id", "program_name"], [
            {"program_id": "prog_1", "university_id": "univ_1", "program_name": "Scored Program"},
            {"program_id": "prog_2", "university_id": "univ_1", "program_name": "Unscored Program"},
        ])
        self.write_csv(self.evidence, ["evidence_id", "claim_category"], [
            {"evidence_id": "ev_1", "claim_category": "hci_strength"},
            {"evidence_id": "ev_blank", "claim_category": ""},
        ])
        fields = ["score_id", "program_id", "scorer", "source_evidence_ids", "missing_evidence_notes"]
        for field in audit_program_scores.SCORE_FIELDS:
            fields.extend([field, f"{field}_confidence"])
        self.score_fields = fields
        self.write_csv(self.scores, fields, [self.base_score()])
        self.patches = [
            patch.object(audit_program_scores, "ROOT", self.root),
            patch.object(audit_program_scores, "PROGRAMS_FILE", self.programs),
            patch.object(audit_program_scores, "UNIVERSITIES_FILE", self.universities),
            patch.object(audit_program_scores, "SCORES_FILE", self.scores),
            patch.object(audit_program_scores, "EVIDENCE_FILE", self.evidence),
            patch.object(audit_program_scores, "REPORT_FILE", self.report),
            patch.object(audit_program_scores, "validate_all", lambda: []),
        ]
        for item in self.patches:
            item.start()

    def tearDown(self):
        for item in reversed(self.patches):
            item.stop()
        self.tmp.cleanup()

    def write_csv(self, path, fields, rows):
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def base_score(self):
        row = {field: "" for field in self.score_fields}
        row.update({
            "score_id": "score_1",
            "program_id": "prog_1",
            "scorer": "tester",
            "hci_strength": "3",
            "hci_strength_confidence": "high",
            "hai_strength": "IE",
            "missing_evidence_notes": "Need HAI evidence.",
            "source_evidence_ids": "ev_1;ev_blank;ev_missing",
        })
        return row

    def run_audit(self):
        self.assertEqual(audit_program_scores.audit_program_scores(), 0)
        return self.report.read_text(encoding="utf-8")

    def test_audit_report_generation(self):
        text = self.run_audit()
        self.assertIn("# Program scoring audit", text)
        self.assertIn("* Canonical programs: 2", text)
        self.assertIn("* Score rows: 1", text)

    def test_unscored_program_warning(self):
        text = self.run_audit()
        self.assertIn("Canonical program has no score row: Example University — Unscored Program", text)

    def test_ie_dimension_summary(self):
        text = self.run_audit()
        self.assertIn("* `hai_strength`: 1", text)
        self.assertIn("Need HAI evidence.", text)

    def test_evidence_id_existence_checks(self):
        text = self.run_audit()
        self.assertIn("references missing evidence ID `ev_missing`", text)
        self.assertIn("Evidence IDs exist: no", text)

    def test_blank_claim_category_warning(self):
        text = self.run_audit()
        self.assertIn("uses evidence `ev_blank` with blank claim_category", text)
        self.assertIn("Blank claim_category evidence IDs: `ev_blank`", text)

    def test_dimension_coverage_counts(self):
        text = self.run_audit()
        self.assertIn("### `hci_strength`", text)
        self.assertIn("* Numeric scores: 1", text)
        self.assertIn("* High confidence: 1", text)


if __name__ == "__main__":
    unittest.main()
