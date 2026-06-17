import tempfile
import unittest
from pathlib import Path

from scripts.validate_manual_data import (
    validate_candidate_source_associations,
    validate_row_values,
    validate_table,
)


CONFIG = {
    "validation": {
        "allowed_confidence": ["low", "medium", "high"],
        "allowed_entity_types": ["university", "program", "faculty", "lab"],
        "allowed_review_statuses": ["discovered", "needs_source", "needs_review", "reviewed", "promoted", "rejected"],
        "allowed_relevant_areas": ["core_hci", "human_ai_interaction", "other"],
    }
}


class CandidateValidationTests(unittest.TestCase):
    def test_review_status_validation_rejects_unknown_status(self):
        issues = validate_row_values(
            "candidate_programs",
            2,
            {"review_status": "maybe"},
            set(CONFIG["validation"]["allowed_confidence"]),
            set(CONFIG["validation"]["allowed_entity_types"]),
            set(CONFIG["validation"]["allowed_review_statuses"]),
            set(CONFIG["validation"]["allowed_relevant_areas"]),
        )
        self.assertTrue(any("review_status" in issue.message for issue in issues))

    def test_relevant_area_validation_rejects_unknown_area(self):
        issues = validate_row_values(
            "candidate_faculty",
            2,
            {"relevant_area": "unsupported_area"},
            set(CONFIG["validation"]["allowed_confidence"]),
            set(CONFIG["validation"]["allowed_entity_types"]),
            set(CONFIG["validation"]["allowed_review_statuses"]),
            set(CONFIG["validation"]["allowed_relevant_areas"]),
        )
        self.assertTrue(any("relevant_area" in issue.message for issue in issues))

    def test_duplicate_candidate_id_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "candidate_programs.csv"
            path.write_text(
                "candidate_id,source_url,discovered_date,review_status\n"
                "cand-1,https://example.edu,2026-01-01,discovered\n"
                "cand-1,https://example.edu/2,2026-01-02,needs_review\n",
                encoding="utf-8",
            )
            spec = {
                "file": "candidate_programs.csv",
                "primary_key": "candidate_id",
                "required": ["candidate_id", "source_url", "discovered_date", "review_status"],
                "columns": ["candidate_id", "source_url", "discovered_date", "review_status"],
            }
            issues = validate_table("candidate_programs", spec, root, CONFIG)
        self.assertTrue(any("Duplicate candidate_id" in issue.message for issue in issues))

    def test_candidate_source_association_requires_existing_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate_path = root / "candidate_programs.csv"
            source_path = root / "candidate_sources.csv"
            for name in ["candidate_universities.csv", "candidate_faculty.csv", "candidate_labs.csv"]:
                (root / name).write_text("candidate_id\n", encoding="utf-8")
            candidate_path.write_text("candidate_id\ncand-known\n", encoding="utf-8")
            source_path.write_text(
                "source_id,associated_entity_type,associated_candidate_id\n"
                "src-1,program,cand-missing\n",
                encoding="utf-8",
            )
            schema = {
                "candidate_universities": {"file": "candidate_universities.csv"},
                "candidate_programs": {"file": "candidate_programs.csv"},
                "candidate_faculty": {"file": "candidate_faculty.csv"},
                "candidate_labs": {"file": "candidate_labs.csv"},
                "candidate_sources": {"file": "candidate_sources.csv"},
            }
            issues = validate_candidate_source_associations(schema, root)
        self.assertTrue(any("was not found" in issue.message for issue in issues))


if __name__ == "__main__":
    unittest.main()
