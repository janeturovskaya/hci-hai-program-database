# Modified PR 32 draft PR plan

Date: 2026-06-19.

This note creates a separate post-PR31 change set for the modified PR 32 work, so the next GitHub pull request can be opened as a draft without reusing the already-merged PR 31 branch.

## Base state

- PR 31 has been merged into the current branch history.
- The current branch starts from the merge commit for PR 31, so any follow-up PR should be reviewed as a separate delta after the expanded candidate comparison work.
- This change intentionally does not alter candidate data, scoring data, generated reports, or pilot findings.

## Draft PR scope

The draft PR should be used as a coordination and review container for the modified PR 32 follow-up. Keep the branch focused on changes that are meant to land after PR 31, and avoid mixing in already-merged PR 31 content.

Recommended draft PR checklist:

1. Confirm the draft PR base is the branch that already contains PR 31.
2. Add only the modified PR 32 follow-up files or edits.
3. Re-run the repository validation checks before marking the draft ready for review.
4. In the PR description, call out that PR 31 is already merged and this branch is the separate follow-up delta.

## Validation before promotion from draft

Run the standard lightweight checks used for this repository:

```bash
python -m pytest
python scripts/validate_manual_data.py
python scripts/check_placeholder_data.py
```
