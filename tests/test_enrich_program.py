import csv
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import enrich_program


PROGRAM_COLUMNS = ["program_id", "university_id", "program_name", "degree_type", "department_or_school", "format", "duration", "research_orientation", "thesis_or_capstone", "online_available", "application_deadline", "prerequisites", "cost_notes", "official_url", "source_url", "last_checked", "notes"]


class EnrichProgramTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.programs = self.root / "programs.csv"
        self.evidence = self.root / "evidence.csv"
        self.write_rows(self.programs, PROGRAM_COLUMNS, [{
            "program_id": "prog_example", "university_id": "univ_example", "program_name": "MS HCI", "degree_type": "MS", "department_or_school": "School", "format": "in-person", "duration": "", "research_orientation": "old", "thesis_or_capstone": "", "online_available": "", "application_deadline": "", "prerequisites": "keep", "cost_notes": "", "official_url": "https://example.edu/old", "source_url": "https://example.edu/old", "last_checked": "2026-01-01", "notes": "existing note"
        }])
        self.write_rows(self.evidence, enrich_program.EVIDENCE_COLUMNS, [])
        self.patchers = [
            patch.object(enrich_program, "PROGRAMS_FILE", self.programs),
            patch.object(enrich_program, "EVIDENCE_FILE", self.evidence),
            patch.object(enrich_program, "validate_all", return_value=[]),
            patch.object(enrich_program, "allowed_confidence", return_value={"low", "medium", "high"}),
        ]
        for patcher in self.patchers:
            patcher.start()

    def tearDown(self):
        for patcher in reversed(self.patchers):
            patcher.stop()
        self.tempdir.cleanup()

    def write_rows(self, path, columns, rows):
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)

    def rows(self, path):
        with path.open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    def parse(self, extra):
        base = ["prog_example"]
        return enrich_program.make_parser().parse_args(base + extra)

    def evidence_args(self):
        return ["--evidence-claim", "claim", "--source-url", "https://example.edu/source", "--quote-or-snippet", "snippet", "--confidence", "high", "--claim-category", "duration"]

    def test_successful_program_enrichment_with_evidence_row_creation(self):
        rc = enrich_program.enrich_program(self.parse(["--duration", "12 months"] + self.evidence_args()))
        self.assertEqual(rc, 0)
        self.assertEqual(self.rows(self.programs)[0]["duration"], "12 months")
        evidence = self.rows(self.evidence)[0]
        self.assertEqual(evidence["entity_type"], "program")
        self.assertEqual(evidence["entity_id"], "prog_example")
        self.assertEqual(evidence["confidence"], "high")
        self.assertEqual(evidence.get("claim_category", ""), "duration")

    def test_only_explicitly_provided_fields_are_updated(self):
        enrich_program.enrich_program(self.parse(["--duration", "12 months"] + self.evidence_args()))
        row = self.rows(self.programs)[0]
        self.assertEqual(row["duration"], "12 months")
        self.assertEqual(row["research_orientation"], "old")
        self.assertEqual(row["prerequisites"], "keep")

    def test_unsupported_fields_cannot_be_updated(self):
        with self.assertRaises(SystemExit):
            self.parse(["--program-name", "New", "--no-evidence"])

    def test_missing_evidence_arguments_fail_unless_no_evidence_is_used(self):
        self.assertEqual(enrich_program.enrich_program(self.parse(["--duration", "12 months"])), 2)
        self.assertEqual(enrich_program.enrich_program(self.parse(["--duration", "12 months", "--no-evidence"])), 0)

    def test_no_evidence_warning_behavior(self):
        err = io.StringIO()
        with patch("sys.stderr", err):
            rc = enrich_program.enrich_program(self.parse(["--duration", "12 months", "--no-evidence"]))
        self.assertEqual(rc, 0)
        self.assertIn("WARNING", err.getvalue())
        self.assertEqual(self.rows(self.evidence), [])

    def test_clear_field_clears_only_allowed_fields(self):
        self.assertEqual(enrich_program.enrich_program(self.parse(["--clear-field", "prerequisites"] + self.evidence_args())), 0)
        self.assertEqual(self.rows(self.programs)[0]["prerequisites"], "")
        self.assertEqual(enrich_program.enrich_program(self.parse(["--clear-field", "program_id"] + self.evidence_args())), 2)

    def test_invalid_confidence_rejected(self):
        self.assertEqual(enrich_program.enrich_program(self.parse(["--duration", "12", "--evidence-claim", "claim", "--source-url", "https://example.edu", "--quote-or-snippet", "snippet", "--confidence", "certain"])), 2)

    def test_invalid_source_url_rejected(self):
        self.assertEqual(enrich_program.enrich_program(self.parse(["--duration", "12", "--evidence-claim", "claim", "--source-url", "ftp://example.edu", "--quote-or-snippet", "snippet", "--confidence", "high"])), 2)

    def test_notes_append_behavior(self):
        enrich_program.enrich_program(self.parse(["--notes", "new note"] + self.evidence_args()))
        self.assertEqual(self.rows(self.programs)[0]["notes"], "existing note | Enrichment note: new note")

    def test_replace_notes_behavior(self):
        enrich_program.enrich_program(self.parse(["--notes", "new note", "--replace-notes"] + self.evidence_args()))
        self.assertEqual(self.rows(self.programs)[0]["notes"], "new note")

    def test_rollback_on_validation_failure(self):
        self.patchers[2].stop()
        with patch.object(enrich_program, "validate_all", return_value=[type("Issue", (), {"row": 2, "severity": "error", "table": "programs", "message": "bad"})()]):
            rc = enrich_program.enrich_program(self.parse(["--duration", "12 months"] + self.evidence_args()))
        self.assertEqual(rc, 1)
        self.assertEqual(self.rows(self.programs)[0]["duration"], "")
        self.assertEqual(self.rows(self.evidence), [])
        self.patchers[2].start()

    def test_evidence_id_collision_handling(self):
        collision_id = enrich_program.build_evidence_id("prog_example", "claim")
        self.write_rows(self.evidence, enrich_program.EVIDENCE_COLUMNS, [{"evidence_id": collision_id, "entity_type": "program", "entity_id": "prog_example", "claim": "old", "source_url": "https://example.edu", "source_type": "official_page", "quote_or_snippet": "old", "date_accessed": "2026-01-01", "confidence": "high", "uncertainty_notes": ""}])
        enrich_program.enrich_program(self.parse(["--duration", "12 months"] + self.evidence_args()))
        ids = [row["evidence_id"] for row in self.rows(self.evidence)]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(any(value.endswith("_2") for value in ids))


if __name__ == "__main__":
    unittest.main()
