# Pilot scoring rubric

This first scoring framework is exploratory. It supports review of evidence for fit with the goal: **find U.S. graduate programs that are strong fits for a UX researcher with a psychology background who wants to deepen HCI, Human-AI Interaction, Human-Centered AI, and AI-product evaluation expertise.** Scores are not rankings and must not be treated as final recommendations.

## Common scale

* `0` = no evidence / not relevant.
* `1` = weak evidence.
* `2` = moderate evidence.
* `3` = strong evidence.
* `NA` = not applicable.
* `IE` = insufficient evidence.

Confidence is `high`, `medium`, or `low`. Leave confidence blank only when the score is blank. Use `IE` when the dimension matters but repository evidence is missing or too indirect. Do not score from reputation, memory, rankings, or unsupported inference.

## Dimensions

### hci_strength
Measures explicit HCI depth in the program. Strong evidence includes program titles, official curriculum, required HCI courses, or official outcomes naming HCI/UX research. Weak evidence includes a generic technology degree with one design elective.

### hai_strength
Measures Human-AI Interaction, Human-Centered AI, responsible AI, or AI-product evaluation fit. Strong evidence includes official courses, labs, faculty, or program tracks focused on HAI/HCAI. Weak evidence includes broad AI buzzwords without human-centered evaluation.

### faculty_lab_fit
Measures availability of relevant faculty, labs, centers, or groups. Strong evidence links named faculty/labs to HCI/HAI/UX methods. Weak evidence is department-level reputation without named people or groups.

### research_access_for_masters
Measures whether master's students can access research, directed research, theses, labs, or advisor-supervised projects. Strong evidence is official master's research access language. Weak evidence is general university research strength.

### quant_data_ai_curriculum
Measures quantitative, data, AI, ML, evaluation, experimental, or computational curriculum useful for AI-product UXR. Strong evidence includes required or elective courses in these areas. Weak evidence is a vague statement that the program is technical.

### methods_fit_for_uxr_psychology_background
Measures fit for psychology-trained UX research: mixed methods, human subjects research, experimentation, usability, interviews, surveys, behavioral/social-science grounding. Strong evidence includes official methods courses or outcomes. Weak evidence is only product design language.

### career_relevance_for_ai_uxr
Measures career fit for UX researcher / AI product evaluation roles. Strong evidence includes official outcomes in UX research, HCI, product research/design, or AI evaluation. Weak evidence is general tech career language.

### practical_fit
Measures pragmatic fit using recorded details such as duration, format, online availability, deadlines, prerequisites, and cost notes. Strong evidence covers multiple practical constraints with current official sources. Weak evidence covers only one partial detail.

### evidence_quality
Measures quality of the evidence supporting the row. Strong evidence uses multiple current official sources and clear snippets tied to claims. Weak evidence is outdated, partial, indirect, or candidate-only.

## When not to score

Do not score a dimension when evidence is absent, stale, candidate-only without promotion, or supports a different claim. Use `IE` and explain missing evidence. Use `NA` only when a dimension is truly not applicable, not as a substitute for missing data.

## Dimension-specific evidence categories

Evidence rows may now include an optional `claim_category` value that identifies what kind of claim the evidence supports. For scoring, prefer evidence whose `claim_category` matches the dimension being scored, such as `hci_strength`, `hai_strength`, `faculty_lab_fit`, `research_access_for_masters`, `quant_data_ai_curriculum`, `methods_fit`, `career_relevance`, or `practical_fit`.

`source_evidence_ids` in `data/manual/program_scores.csv` remains a semicolon-separated list so one score row can cite multiple evidence records. The category field does not replace evidence IDs; it makes the cited evidence easier to audit and helps reviewers see when a score depends on indirect or mismatched evidence.

## Audit before interpretation

Before interpreting exploratory score rows, run the scoring report and scoring audit workflows. The audit checks completeness, IE patterns, low-confidence dimensions, evidence ID validity, and whether cited evidence has relevant `claim_category` values. Treat audit findings as evidence-collection guidance, not as a ranking signal.
