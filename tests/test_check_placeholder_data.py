import tempfile
import unittest
from pathlib import Path

from scripts import check_placeholder_data


class PlaceholderDataTests(unittest.TestCase):
    def test_scan_detects_placeholder_values(self):
        with tempfile.TemporaryDirectory() as tempdir:
            data_dir = Path(tempdir)
            csv_path = data_dir / "candidate_universities.csv"
            csv_path.write_text("candidate_id,university_name,source_url\n1,Example University,https://example.edu\n", encoding="utf-8")

            findings = check_placeholder_data.scan((data_dir,))

            self.assertEqual(len(findings), 2)
            self.assertEqual({finding.pattern for finding in findings}, {"Example University", "example.edu"})

    def test_scan_ignores_non_placeholder_values(self):
        with tempfile.TemporaryDirectory() as tempdir:
            data_dir = Path(tempdir)
            csv_path = data_dir / "universities.csv"
            csv_path.write_text("university_id,university_name,official_url\nu_test,Test Institution,https://institution.test\n", encoding="utf-8")

            self.assertEqual(check_placeholder_data.scan((data_dir,)), [])


if __name__ == "__main__":
    unittest.main()
