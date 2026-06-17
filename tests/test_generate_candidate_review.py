import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import generate_candidate_review


class GenerateCandidateReviewTests(unittest.TestCase):
    def test_report_shows_secondary_relevant_areas(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate_dir = root / "candidates"
            candidate_dir.mkdir()
            report_path = root / "candidate_review.md"
            (candidate_dir / "candidate_universities.csv").write_text(
                "candidate_id,university_name,relevant_area,secondary_relevant_areas,source_url,review_status,notes\n"
                "cand_univ_example,Example University,core_hci,human_ai_interaction; other,https://example.edu,needs_review,\n",
                encoding="utf-8",
            )
            for name in ["programs", "faculty", "labs"]:
                (candidate_dir / f"candidate_{name}.csv").write_text(
                    "candidate_id,university_name,relevant_area,secondary_relevant_areas,source_url,review_status,notes\n",
                    encoding="utf-8",
                )
            (candidate_dir / "candidate_sources.csv").write_text(
                "source_id,associated_entity_type,associated_candidate_id,evidence_snippet\n", encoding="utf-8"
            )
            files = {
                "university": candidate_dir / "candidate_universities.csv",
                "program": candidate_dir / "candidate_programs.csv",
                "faculty": candidate_dir / "candidate_faculty.csv",
                "lab": candidate_dir / "candidate_labs.csv",
            }
            with patch.object(generate_candidate_review, "CANDIDATE_DIR", candidate_dir), \
                patch.object(generate_candidate_review, "REPORT_PATH", report_path), \
                patch.object(generate_candidate_review, "FILES", files), \
                patch.object(generate_candidate_review, "validate_all", return_value=[]):
                status = generate_candidate_review.main()
            self.assertEqual(status, 0)
            self.assertIn("Secondary relevant areas: human_ai_interaction; other", report_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
