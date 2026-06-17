# Candidate promotion checklist

Candidate records in `data/candidates/` are rough intake records. They are not canonical database entries until a reviewer promotes them into the matching `data/manual/` CSV file and adds or prepares supporting evidence.

## Promotion criteria

Promote a candidate only when all of the following are true:

- An official or highly reliable source URL exists.
- The evidence snippet supports the claim being promoted.
- The university, program, faculty, or lab name is normalized for canonical use.
- There is no unresolved duplicate warning.
- `review_status` is `reviewed` before promotion.
- Uncertainty notes are addressed or explicitly documented.
- A canonical ID has been assigned for the target manual CSV.
- A related evidence record exists or is ready to be added to `data/manual/evidence.csv`.

After promotion, update the candidate `review_status` to `promoted` or keep an audit note explaining the promotion decision.

## Rejection reasons

Use `review_status` of `rejected` when a candidate should not proceed. Common rejection reasons include:

- Not U.S.-based.
- Not graduate-level.
- Weak HCI/HAI relevance.
- No reliable source.
- Duplicate.
- Program inactive.
- Faculty no longer active.
- Unclear master’s student access.
- Outside project scope.
- Other.

Document the reason in `notes` or `uncertainty_notes` so future reviewers can understand the decision.
