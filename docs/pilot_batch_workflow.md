# Pilot batch workflow

Use this workflow to test the HCI/HAI program database process with a first pilot batch of **3–5 universities**. The pilot is for validating the workflow, schemas, review steps, and promotion process. It is **not** the start of full-scale database building.

Do not scrape the web, bulk import data, or infer missing facts. A human researcher should manually collect official source URLs, short evidence snippets, and uncertainty notes.

## 1. Choose 3–5 universities manually

Pick a small, intentionally varied sample so the workflow is exercised without overwhelming review:

- one university with an obvious HCI/HAI program;
- one university with relevant faculty but unclear program structure;
- one university with a relevant lab or center;
- optionally one or two edge cases where evidence may be incomplete.

Record why each university was selected in pilot notes, but do not treat selection notes as canonical data.

## 2. Collect official source URLs

For each candidate entity, collect official URLs where possible:

- university, department, school, center, or lab pages hosted by the institution;
- program, admissions, curriculum, or course catalog pages;
- faculty profile, lab profile, project, or publication pages.

Avoid relying only on rankings, blogs, news summaries, or third-party aggregators. See [`docs/source_evidence_rules.md`](source_evidence_rules.md) for evidence rules by entity type.

## 3. Copy short evidence snippets

For every candidate claim, copy a short snippet that supports the specific field or claim being entered. Keep snippets brief and focused. Do not copy full pages or long copyrighted passages.

Store rough human notes in `data/raw/pilot_notes/` if helpful. Structured candidate data should go into `data/candidates/*.csv` through the CLI.

## 4. Add candidates with `scripts/add_candidate.py`

Use `scripts/add_candidate.py` to add candidate universities, programs, faculty, and labs. Include linked candidate source evidence when a short snippet is available.

Start from the placeholder examples in [`examples/add_candidate_commands.sh`](../examples/add_candidate_commands.sh), replace every placeholder with reviewed source information, then run only the commands you have edited.

## 5. Generate the candidate review report

After candidate entry, generate the review report:

```bash
python scripts/generate_candidate_review.py
```

Open `reports/candidate_review.md` and review candidates by status, source, snippet, and notes.

## 6. Manually review each candidate

For each candidate row:

- confirm the source is official or otherwise highly reliable;
- confirm the snippet supports the candidate data;
- check for likely duplicates;
- document uncertainty in `notes` or candidate source `uncertainty_notes`;
- decide whether the candidate should be promoted, kept for more research, or rejected.

## 7. Change status to `reviewed` when evidence is sufficient

Only set `review_status` to `reviewed` after human review confirms the candidate has enough source support for promotion. Use `rejected` for out-of-scope or unsupported candidates, and keep `needs_source` or `needs_review` for incomplete records.

## 8. Promote reviewed candidates

Use `scripts/promote_candidate.py` to move reviewed rows into canonical manual CSVs. Create evidence rows where appropriate with `--create-evidence` and `--evidence-claim`.

Examples are available in [`examples/add_candidate_commands.sh`](../examples/add_candidate_commands.sh). For programs, faculty, and labs, provide `--university-id` unless the university can be resolved unambiguously from canonical manual data.

## 9. Run validation and tests

Run the full local check sequence:

```bash
python scripts/validate_manual_data.py
python scripts/generate_candidate_review.py
python scripts/check_placeholder_data.py
python -m unittest discover
```

If the placeholder check script is not present in a future branch, skip that command.

## 10. Inspect canonical `data/manual/` CSVs

Open the canonical manual CSV files and verify that promoted rows are clean, traceable, and properly linked:

- `data/manual/universities.csv`
- `data/manual/programs.csv`
- `data/manual/faculty.csv`
- `data/manual/labs.csv`
- `data/manual/evidence.csv`

Confirm that notes include candidate traceability and that evidence rows support the claims being promoted.

## 11. Document schema gaps and workflow pain points

At the end of the pilot, write down issues such as:

- fields that were missing or ambiguous;
- evidence that did not fit the current schema;
- confusing CLI prompts or validation messages;
- duplicate handling concerns;
- promotion or review steps that need clearer documentation.

Use these observations to improve the workflow before any larger data collection effort.
