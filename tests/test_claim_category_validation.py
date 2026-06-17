import tempfile
import unittest
from pathlib import Path

from scripts import validate_manual_data


class ClaimCategoryValidationTests(unittest.TestCase):
    def validate_row(self, claim_category):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / 'evidence.csv'
            path.write_text(
                'evidence_id,entity_type,entity_id,claim,source_url,source_type,quote_or_snippet,date_accessed,confidence,uncertainty_notes,claim_category\n'
                f'ev_1,program,prog_1,claim,https://example.edu,official_page,snippet,2026-06-17,high,,{claim_category}\n',
                encoding='utf-8',
            )
            spec = {
                'file': 'evidence.csv',
                'primary_key': 'evidence_id',
                'required': ['evidence_id', 'entity_type', 'entity_id', 'claim', 'source_url', 'source_type', 'date_accessed', 'confidence'],
                'columns': ['evidence_id', 'entity_type', 'entity_id', 'claim', 'source_url', 'source_type', 'quote_or_snippet', 'date_accessed', 'confidence', 'uncertainty_notes', 'claim_category'],
            }
            config = {'validation': {'allowed_confidence': ['high', 'medium', 'low'], 'allowed_entity_types': ['program'], 'allowed_review_statuses': [], 'allowed_relevant_areas': []}}
            return validate_manual_data.validate_table('evidence', spec, root, config)

    def test_valid_claim_category_allowed(self):
        self.assertEqual(self.validate_row('hci_strength'), [])

    def test_invalid_claim_category_rejected(self):
        issues = self.validate_row('not_a_category')
        self.assertTrue(any('claim_category must be one of' in issue.message for issue in issues))

    def test_blank_claim_category_allowed_for_legacy_rows(self):
        self.assertEqual(self.validate_row(''), [])


if __name__ == '__main__':
    unittest.main()
