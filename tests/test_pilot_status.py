import csv
import tempfile
import unittest
from pathlib import Path

from scripts import pilot_status


class PilotStatusTests(unittest.TestCase):
    def write_csv(self, path, fieldnames, rows):
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def test_build_summary_counts_statuses_and_warnings(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            candidate_files = {
                "universities": root / "candidate_universities.csv",
                "programs": root / "candidate_programs.csv",
                "faculty": root / "candidate_faculty.csv",
                "labs": root / "candidate_labs.csv",
            }
            for name, path in candidate_files.items():
                rows = []
                if name == "universities":
                    rows = [
                        {"candidate_id": "cand_univ_a", "review_status": "promoted", "source_url": "https://institution.test"},
                        {"candidate_id": "cand_univ_b", "review_status": "rejected", "source_url": ""},
                    ]
                self.write_csv(path, ["candidate_id", "review_status", "source_url"], rows)
            manual_files = {name: root / f"{name}.csv" for name in ["universities", "programs", "faculty", "labs", "evidence"]}
            for name, path in manual_files.items():
                self.write_csv(path, [f"{name}_id"], [{f"{name}_id": "row1"}] if name == "universities" else [])
            source_file = root / "candidate_sources.csv"
            self.write_csv(source_file, ["source_id", "associated_entity_type", "associated_candidate_id"], [{"source_id": "src1", "associated_entity_type": "university", "associated_candidate_id": "missing"}])

            summary = pilot_status.build_summary(candidate_files, manual_files, source_file)

            self.assertEqual(summary["status_counts"]["universities"]["promoted"], 1)
            self.assertEqual(summary["promoted_candidates"], 1)
            self.assertEqual(summary["rejected_candidates"], 1)
            self.assertEqual(summary["candidate_sources"], 1)
            self.assertEqual(summary["manual_counts"]["universities"], 1)
            self.assertEqual(len(summary["warnings"]), 2)

    def test_empty_files_have_no_warnings(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            candidate_files = {name: root / f"candidate_{name}.csv" for name in ["universities", "programs", "faculty", "labs"]}
            for path in candidate_files.values():
                self.write_csv(path, ["candidate_id", "review_status", "source_url"], [])
            manual_files = {name: root / f"{name}.csv" for name in ["universities", "programs", "faculty", "labs", "evidence"]}
            for path in manual_files.values():
                self.write_csv(path, ["id"], [])
            source_file = root / "candidate_sources.csv"
            self.write_csv(source_file, ["source_id", "associated_entity_type", "associated_candidate_id"], [])

            summary = pilot_status.build_summary(candidate_files, manual_files, source_file)

            self.assertEqual(summary["warnings"], [])
            self.assertEqual(summary["promoted_candidates"], 0)
            self.assertEqual(summary["rejected_candidates"], 0)


if __name__ == "__main__":
    unittest.main()
