import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import promote_candidate


class PromoteCandidateTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        (self.root / "manual").mkdir()
        (self.root / "candidates").mkdir()
        self.manual = {
            "university": self.root / "manual/universities.csv",
            "program": self.root / "manual/programs.csv",
            "faculty": self.root / "manual/faculty.csv",
            "lab": self.root / "manual/labs.csv",
        }
        self.candidates = {
            "university": self.root / "candidates/candidate_universities.csv",
            "program": self.root / "candidates/candidate_programs.csv",
            "faculty": self.root / "candidates/candidate_faculty.csv",
            "lab": self.root / "candidates/candidate_labs.csv",
        }
        for entity, config in promote_candidate.CANDIDATE_CONFIG.items():
            self.manual[entity].write_text(",".join(config["columns"]) + "\n", encoding="utf-8")
            # candidate columns are read from production-shaped files below as needed
        self.candidates["university"].write_text("candidate_id,university_name,city,state,seed_reason,relevant_area,source_url,discovered_date,review_status,notes\n", encoding="utf-8")
        self.candidates["program"].write_text("candidate_id,university_name,program_name,degree_type,department_or_school,format,seed_reason,relevant_area,source_url,discovered_date,review_status,notes\n", encoding="utf-8")
        self.candidates["faculty"].write_text("candidate_id,university_name,faculty_name,title,department,lab_or_group,research_keywords,relevant_area,source_url,discovered_date,review_status,notes\n", encoding="utf-8")
        self.candidates["lab"].write_text("candidate_id,university_name,lab_name,director,themes,relevant_area,source_url,discovered_date,review_status,notes\n", encoding="utf-8")
        self.sources = self.root / "candidates/candidate_sources.csv"
        self.sources.write_text("source_id,source_type,source_title,source_url,associated_entity_type,associated_candidate_id,date_accessed,evidence_snippet,confidence,uncertainty_notes,claim_category\n", encoding="utf-8")
        self.evidence = self.root / "manual/evidence.csv"
        self.evidence.write_text(",".join(promote_candidate.EVIDENCE_COLUMNS) + "\n", encoding="utf-8")
        self.config = {k: {**v, "candidate_file": self.candidates[k], "manual_file": self.manual[k]} for k, v in promote_candidate.CANDIDATE_CONFIG.items()}
        patches = [
            patch.object(promote_candidate, "CANDIDATE_CONFIG", self.config),
            patch.object(promote_candidate, "SOURCE_FILE", self.sources),
            patch.object(promote_candidate, "EVIDENCE_FILE", self.evidence),
            patch.object(promote_candidate, "validate_all", return_value=[]),
        ]
        self.patchers = patches
        for p in patches:
            p.start()

    def tearDown(self):
        for p in reversed(self.patchers):
            p.stop()
        self.tempdir.cleanup()

    def add_row(self, path, row):
        with path.open("r", newline="", encoding="utf-8") as read_handle:
            fieldnames = next(csv.reader(read_handle))
        with path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerow(row)

    def rows(self, path):
        with path.open(newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def parse(self, args):
        return promote_candidate.make_parser().parse_args(args)

    def test_successful_university_promotion(self):
        self.add_row(self.candidates["university"], {"candidate_id":"cand_univ_example","university_name":"Example University","city":"Example City","state":"EX","source_url":"https://example.edu","discovered_date":"2026-01-01","review_status":"reviewed","notes":"checked"})
        rc = promote_candidate.promote_candidate(self.parse(["university", "cand_univ_example", "--canonical-id", "univ_example"]))
        self.assertEqual(rc, 0)
        self.assertEqual(self.rows(self.manual["university"])[0]["university_id"], "univ_example")

    def test_rejects_unreviewed(self):
        self.add_row(self.candidates["university"], {"candidate_id":"cand_univ_example","university_name":"Example University","source_url":"https://example.edu","discovered_date":"2026-01-01","review_status":"discovered"})
        self.assertEqual(promote_candidate.promote_candidate(self.parse(["university", "cand_univ_example"])), 2)

    def test_allow_unreviewed(self):
        self.add_row(self.candidates["university"], {"candidate_id":"cand_univ_example","university_name":"Example University","city":"City","state":"EX","source_url":"https://example.edu","discovered_date":"2026-01-01","review_status":"discovered"})
        self.assertEqual(promote_candidate.promote_candidate(self.parse(["university", "cand_univ_example", "--allow-unreviewed"])), 0)

    def test_canonical_id_generation(self):
        self.add_row(self.candidates["university"], {"candidate_id":"cand_univ_example","university_name":"Example University","city":"City","state":"EX","source_url":"https://example.edu","discovered_date":"2026-01-01","review_status":"reviewed"})
        promote_candidate.promote_candidate(self.parse(["university", "cand_univ_example"]))
        self.assertEqual(self.rows(self.manual["university"])[0]["university_id"], "univ_example_university")

    def test_duplicate_canonical_id_rejection(self):
        self.add_row(self.manual["university"], {"university_id":"univ_example","university_name":"Other","city":"City","state":"EX","official_url":"https://other.edu","last_checked":"2026-01-01"})
        self.add_row(self.candidates["university"], {"candidate_id":"cand_univ_example","university_name":"Example University","source_url":"https://example.edu","discovered_date":"2026-01-01","review_status":"reviewed"})
        self.assertEqual(promote_candidate.promote_candidate(self.parse(["university", "cand_univ_example", "--canonical-id", "univ_example"])), 2)

    def test_duplicate_name_rejection(self):
        self.add_row(self.manual["university"], {"university_id":"univ_other","university_name":"Example University","city":"City","state":"EX","official_url":"https://example.edu","last_checked":"2026-01-01"})
        self.add_row(self.candidates["university"], {"candidate_id":"cand_univ_example","university_name":"Example University","source_url":"https://example.edu","discovered_date":"2026-01-01","review_status":"reviewed"})
        self.assertEqual(promote_candidate.promote_candidate(self.parse(["university", "cand_univ_example", "--canonical-id", "univ_example"])), 2)

    def test_program_requires_university_id_without_unambiguous_match(self):
        self.add_row(self.candidates["program"], {"candidate_id":"cand_prog_example","university_name":"Example University","program_name":"MS HCI","degree_type":"MS","source_url":"https://example.edu/p","discovered_date":"2026-01-01","review_status":"reviewed"})
        self.assertEqual(promote_candidate.promote_candidate(self.parse(["program", "cand_prog_example"])), 2)

    def test_evidence_creation_from_linked_source(self):
        self.add_row(self.candidates["university"], {"candidate_id":"cand_univ_example","university_name":"Example University","city":"City","state":"EX","source_url":"https://example.edu","discovered_date":"2026-01-01","review_status":"reviewed"})
        self.add_row(self.sources, {"source_id":"cand_src_a","source_type":"official_page","source_url":"https://example.edu/about","associated_entity_type":"university","associated_candidate_id":"cand_univ_example","date_accessed":"2026-01-02","evidence_snippet":"snippet","confidence":"high","uncertainty_notes":"note"})
        rc = promote_candidate.promote_candidate(self.parse(["university", "cand_univ_example", "--create-evidence", "--evidence-claim", "claim", "--claim-category", "program_existence"]))
        self.assertEqual(rc, 0)
        self.assertEqual(self.rows(self.evidence)[0]["quote_or_snippet"], "snippet")
        self.assertEqual(self.rows(self.evidence)[0].get("claim_category", ""), "program_existence")

    def test_evidence_fallback_without_linked_source(self):
        self.add_row(self.candidates["university"], {"candidate_id":"cand_univ_example","university_name":"Example University","city":"City","state":"EX","source_url":"https://example.edu","discovered_date":"2026-01-01","review_status":"reviewed"})
        promote_candidate.promote_candidate(self.parse(["university", "cand_univ_example", "--create-evidence", "--evidence-claim", "claim"]))
        self.assertEqual(self.rows(self.evidence)[0]["source_url"], "https://example.edu")

    def test_candidate_status_updated_to_promoted(self):
        self.add_row(self.candidates["university"], {"candidate_id":"cand_univ_example","university_name":"Example University","city":"City","state":"EX","source_url":"https://example.edu","discovered_date":"2026-01-01","review_status":"reviewed"})
        promote_candidate.promote_candidate(self.parse(["university", "cand_univ_example"]))
        self.assertEqual(self.rows(self.candidates["university"])[0]["review_status"], "promoted")

    def test_rollback_on_validation_failure(self):
        validation_patcher = self.patchers.pop()
        validation_patcher.stop()
        with patch.object(promote_candidate, "validate_all", return_value=[type("Issue", (), {"row": 2, "severity": "error", "table": "universities", "message": "bad"})()]):
            self.add_row(self.candidates["university"], {"candidate_id":"cand_univ_example","university_name":"Example University","city":"City","state":"EX","source_url":"https://example.edu","discovered_date":"2026-01-01","review_status":"reviewed"})
            self.assertEqual(promote_candidate.promote_candidate(self.parse(["university", "cand_univ_example"])), 1)
            self.assertEqual(self.rows(self.manual["university"]), [])


if __name__ == "__main__":
    unittest.main()
