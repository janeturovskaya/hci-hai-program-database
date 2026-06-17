import csv
import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from scripts import add_candidate


COLUMNS = {
    "university": add_candidate.CANDIDATE_CONFIG["university"]["columns"],
    "program": add_candidate.CANDIDATE_CONFIG["program"]["columns"],
    "faculty": add_candidate.CANDIDATE_CONFIG["faculty"]["columns"],
    "lab": add_candidate.CANDIDATE_CONFIG["lab"]["columns"],
}


class AddCandidateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.files = {}
        for entity_type, columns in COLUMNS.items():
            path = self.root / f"candidate_{entity_type}.csv"
            path.write_text(",".join(columns) + "\n", encoding="utf-8")
            self.files[entity_type] = path
        self.source_file = self.root / "candidate_sources.csv"
        self.source_file.write_text(",".join(add_candidate.SOURCE_COLUMNS) + "\n", encoding="utf-8")
        self.config = {
            entity_type: {**config, "file": self.files[entity_type]}
            for entity_type, config in add_candidate.CANDIDATE_CONFIG.items()
        }
        self.patches = [
            patch.object(add_candidate, "CANDIDATE_CONFIG", self.config),
            patch.object(add_candidate, "SOURCE_FILE", self.source_file),
            patch.object(add_candidate, "run_validation_or_rollback", return_value=True),
            patch.object(add_candidate, "load_validation_config", return_value={
                "review_status": {"discovered", "needs_review"},
                "relevant_area": {"human_ai_interaction", "other"},
                "confidence": {"low", "medium", "high"},
            }),
        ]
        for active_patch in self.patches:
            active_patch.start()

    def tearDown(self):
        for active_patch in reversed(self.patches):
            active_patch.stop()
        self.tmp.cleanup()

    def read_rows(self, path):
        with path.open("r", encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))

    def test_id_generation_adds_numeric_suffix_for_existing_ids(self):
        existing = {"cand_univ_example_university"}
        generated = add_candidate.unique_id("cand_univ_", ["Example University"], existing)
        self.assertEqual(generated, "cand_univ_example_university_2")

    def test_duplicate_detection_matches_university_name(self):
        self.files["university"].write_text(
            ",".join(COLUMNS["university"]) + "\n"
            "cand_univ_example,Example University,Example City,CA,Known HCI lab,human_ai_interaction,https://example.edu,2026-06-17,discovered,\n",
            encoding="utf-8",
        )
        args = add_candidate.make_parser().parse_args([
            "university", "--university-name", "Example University", "--source-url", "https://example.edu/other"
        ])
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            status = add_candidate.add_candidate(args)
        self.assertEqual(status, 1)
        self.assertIn("cand_univ_example", stderr.getvalue())

    def test_add_university_candidate_with_source_evidence(self):
        args = add_candidate.make_parser().parse_args([
            "university",
            "--university-name", "Example University",
            "--city", "Example City",
            "--state", "CA",
            "--seed-reason", "Known HCI lab",
            "--relevant-area", "human_ai_interaction",
            "--source-url", "https://example.edu/hci",
            "--evidence-snippet", "Example evidence snippet",
        ])
        with redirect_stdout(io.StringIO()):
            status = add_candidate.add_candidate(args)
        self.assertEqual(status, 0)
        candidates = self.read_rows(self.files["university"])
        sources = self.read_rows(self.source_file)
        self.assertEqual(candidates[0]["candidate_id"], "cand_univ_example_university")
        self.assertEqual(sources[0]["associated_entity_type"], "university")
        self.assertEqual(sources[0]["associated_candidate_id"], candidates[0]["candidate_id"])
        self.assertEqual(sources[0]["confidence"], "medium")

    def test_add_program_without_evidence_prints_warning(self):
        args = add_candidate.make_parser().parse_args([
            "program",
            "--university-name", "Example University",
            "--program-name", "MS in Example HCI",
            "--source-url", "https://example.edu/program",
            "--relevant-area", "human_ai_interaction",
        ])
        stderr = io.StringIO()
        with redirect_stderr(stderr), redirect_stdout(io.StringIO()):
            status = add_candidate.add_candidate(args)
        self.assertEqual(status, 0)
        self.assertIn("No source evidence was added", stderr.getvalue())
        self.assertEqual(len(self.read_rows(self.files["program"])), 1)
        self.assertEqual(len(self.read_rows(self.source_file)), 0)

    def test_invalid_relevant_area_rejected(self):
        args = add_candidate.make_parser().parse_args([
            "faculty", "--university-name", "Example University", "--faculty-name", "Jane Example", "--source-url", "https://example.edu", "--relevant-area", "bad_area"
        ])
        with redirect_stderr(io.StringIO()) as stderr:
            status = add_candidate.add_candidate(args)
        self.assertEqual(status, 2)
        self.assertIn("relevant_area", stderr.getvalue())

    def test_invalid_confidence_rejected(self):
        args = add_candidate.make_parser().parse_args([
            "lab", "--university-name", "Example University", "--lab-name", "Example Lab", "--source-url", "https://example.edu", "--evidence-snippet", "snippet", "--confidence", "certain"
        ])
        with redirect_stderr(io.StringIO()) as stderr:
            status = add_candidate.add_candidate(args)
        self.assertEqual(status, 2)
        self.assertIn("confidence", stderr.getvalue())

    def test_source_association_correctness_for_lab(self):
        args = add_candidate.make_parser().parse_args([
            "lab",
            "--university-name", "Example University",
            "--lab-name", "Example Human-AI Lab",
            "--source-url", "https://example.edu/lab",
            "--evidence-snippet", "Example evidence snippet",
            "--confidence", "high",
        ])
        with redirect_stdout(io.StringIO()):
            status = add_candidate.add_candidate(args)
        self.assertEqual(status, 0)
        source = self.read_rows(self.source_file)[0]
        self.assertEqual(source["associated_entity_type"], "lab")
        self.assertEqual(source["associated_candidate_id"], "cand_lab_example_university_example_human_ai_lab")
        self.assertEqual(source["confidence"], "high")


if __name__ == "__main__":
    unittest.main()
