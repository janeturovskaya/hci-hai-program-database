#!/usr/bin/env bash
# Placeholder pilot-batch commands for the HCI/HAI program database.
#
# These examples are NON-EXECUTING documentation snippets. They use fake
# placeholder data such as Example University and example.edu. Edit every value
# with manually reviewed official source information before running any command.
# Do not use this file to add real data without human review.

# This file intentionally contains commented commands only.

# Add a university candidate with linked source evidence.
# python scripts/add_candidate.py university \
#   --university-name "Example University" \
#   --city "Example City" \
#   --state "EX" \
#   --seed-reason "Pilot placeholder for an HCI/HAI-relevant institution" \
#   --relevant-area "human_ai_interaction" \
#   --source-url "https://example.edu/hci" \
#   --evidence-snippet "Short placeholder snippet from an official university page." \
#   --confidence "medium" \
#   --notes "Replace all placeholder values before use."

# Add a program candidate with linked source evidence.
# python scripts/add_candidate.py program \
#   --university-name "Example University" \
#   --program-name "Example HCI Program" \
#   --degree-type "MS" \
#   --department-or-school "Example School of Information" \
#   --format "in-person" \
#   --seed-reason "Pilot placeholder for graduate HCI/HAI curriculum" \
#   --relevant-area "core_hci" \
#   --source-url "https://example.edu/example-hci-program" \
#   --evidence-snippet "Short placeholder snippet from an official program page." \
#   --confidence "medium" \
#   --notes "Replace all placeholder values before use."

# Add a faculty candidate with linked source evidence.
# python scripts/add_candidate.py faculty \
#   --university-name "Example University" \
#   --faculty-name "Example Faculty Member" \
#   --title "Associate Professor" \
#   --department "Example Department" \
#   --lab-or-group "Example Human-AI Lab" \
#   --research-keywords "human-AI interaction; user studies" \
#   --relevant-area "human_ai_interaction" \
#   --source-url "https://example.edu/faculty/example-faculty-member" \
#   --evidence-snippet "Short placeholder snippet from an official faculty profile." \
#   --confidence "medium" \
#   --notes "Replace all placeholder values before use."

# Add a lab candidate with linked source evidence.
# python scripts/add_candidate.py lab \
#   --university-name "Example University" \
#   --lab-name "Example Human-AI Lab" \
#   --director "Example Faculty Member" \
#   --themes "human-AI collaboration; AI evaluation" \
#   --relevant-area "human_ai_interaction" \
#   --source-url "https://example.edu/example-human-ai-lab" \
#   --evidence-snippet "Short placeholder snippet from an official lab page." \
#   --confidence "medium" \
#   --notes "Replace all placeholder values before use."

# Generate the candidate review report after candidate intake.
# python scripts/generate_candidate_review.py

# Promote a reviewed university candidate.
# python scripts/promote_candidate.py university cand_univ_example_university \
#   --canonical-id univ_example_university \
#   --create-evidence \
#   --evidence-claim "Placeholder claim: replace with a claim supported by the official source."

# Promote a reviewed program candidate with an explicit canonical university ID.
# python scripts/promote_candidate.py program cand_prog_example_university_example_hci_program \
#   --canonical-id prog_example_university_example_hci_program \
#   --university-id univ_example_university \
#   --create-evidence \
#   --evidence-claim "Placeholder claim: replace with a claim supported by the official program source."

# Promote a reviewed faculty candidate with evidence.
# python scripts/promote_candidate.py faculty cand_fac_example_university_example_faculty_member \
#   --canonical-id fac_example_university_example_faculty_member \
#   --university-id univ_example_university \
#   --create-evidence \
#   --evidence-claim "Placeholder claim: replace with a claim supported by the official faculty source."

# Promote a reviewed lab candidate with evidence.
# python scripts/promote_candidate.py lab cand_lab_example_university_example_human_ai_lab \
#   --canonical-id lab_example_university_example_human_ai_lab \
#   --university-id univ_example_university \
#   --create-evidence \
#   --evidence-claim "Placeholder claim: replace with a claim supported by the official lab source."

# Run validation, placeholder guard, and tests.
# python scripts/validate_manual_data.py
# python scripts/check_placeholder_data.py
# python -m unittest discover
