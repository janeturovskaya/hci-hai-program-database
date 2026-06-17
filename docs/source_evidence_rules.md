# Source evidence rules

Use these rules when collecting candidate source evidence for the HCI/HAI program database. Prefer official institutional sources. Do not scrape the web, invent facts, or promote unsupported claims.

## University evidence

Acceptable university evidence includes:

- an official university page;
- an official department or school page;
- an official center, institute, or lab directory hosted by the institution.

University evidence should support the institution name, location when used, and the reason it is relevant to HCI/HAI review. Avoid relying only on rankings, blogs, marketing listicles, or third-party summaries.

## Program evidence

Acceptable program evidence includes:

- an official program page;
- an official admissions page;
- an official curriculum, degree requirements, course catalog, or course page.

Program evidence should support the degree type, graduate level, department or school, format, and relevance to HCI/HAI when possible. If different pages support different fields, add source rows or uncertainty notes so reviewers can see which evidence supports which claim.

## Faculty evidence

Acceptable faculty evidence includes:

- an official faculty profile;
- an official lab profile;
- an official publication, project, or research page.

Faculty evidence should support the person's name, department, title, lab or group affiliation when available, and research relevance. If research relevance is inferred from publications or projects rather than directly stated, mark the confidence appropriately and explain the uncertainty.

## Lab evidence

Acceptable lab evidence includes:

- an official lab page;
- an official center or institute page;
- an official project or publication page connected to the lab.

Lab evidence should support the lab name, director when available, themes, and HCI/HAI relevance. If director or student opportunity information is missing, leave those fields blank rather than guessing.

## Candidate source snippets

Candidate source snippets should:

- be short and focused;
- be copied exactly or closely paraphrased;
- support the specific claim or field being added;
- avoid long copied page text or full copyrighted pages;
- include uncertainty notes when evidence is indirect, partial, or split across multiple sources.

A snippet is not a substitute for review. It is a traceable reminder of why a human researcher thought the source supported the candidate record.

## Confidence values

Use the existing `confidence` values consistently:

- `high`: an official source directly supports the claim and the field mapping is clear.
- `medium`: an official source supports most of the claim, but some context is indirect, split across pages, or needs reviewer interpretation.
- `low`: the source is incomplete, indirect, or not ideal; use this for leads that need more review before promotion.

Do not use confidence to make unsupported data look more certain. If evidence is weak, keep the candidate in review or reject it.


## Relevant area evidence

Use `relevant_area` as the candidate row's primary controlled classification. Use `secondary_relevant_areas` only for additional controlled categories that are supported by the same source evidence or clearly documented reviewer notes. This is especially helpful for interdisciplinary Information Science programs that combine HCI, UX research, social computing, and AI-product relevance. Leave secondary areas blank when evidence does not support additional categories.

## Claim categories

Canonical evidence and candidate source rows may include optional `claim_category` values. The category identifies what kind of claim the evidence supports, for example `program_existence`, `hci_strength`, `hai_strength`, `faculty_lab_fit`, `research_access_for_masters`, `quant_data_ai_curriculum`, `methods_fit`, `career_relevance`, `practical_fit`, `cost`, `deadline`, `prerequisites`, `online_available`, `duration`, `capstone`, or `other`.

Legacy rows may leave `claim_category` blank. New or edited evidence should use the most specific supported category. Do not assign a category unless the quoted snippet actually supports that claim; use uncertainty notes when the evidence is indirect.
