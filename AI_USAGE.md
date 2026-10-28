# LLM Use Disclosure

This project was developed with assistance from ChatGPT (OpenAI). AI assistance is disclosed here so reviewers can distinguish generated scaffolding from the work that must be reviewed and owned by the submitter.

## Where AI accelerated work

- Proposed a relational model for employee/pay-group/pay-period/time/leave/allowance/deduction/payroll-input/validation/exception/approval/export/event entities.
- Drafted a deterministic synthetic-data generator, documented validation rules, SQLite schema, CLI, reporting, and an optional Streamlit dashboard.
- Drafted starter tests and installation/verification instructions.
- Helped identify a data-leakage issue: anomaly labels must be stored in a separate ground-truth file rather than source/input feature columns. The generator was revised to keep `issue_type` and `ground_truth` out of operational source CSVs and to detect duplicate allowance/leave deductions from business keys.
- Helped design repeatable validation and checksum comparison.

## Where AI was relied on heavily

The first drafts of much of the Python scaffolding, schema, documentation, and test structure were AI-generated. The submitter should not describe this as independently hand-written code unless that is true. The code must be understood and reviewed before submission.

## What must be personally reviewed and validated by the submitter

Use `PERSONAL_REVIEW_CHECKLIST.md` to record only work you actually completed. In particular:

- Run the installation commands in a clean environment.
- Read the generator, validator, schema, and tests and explain their behavior.
- Confirm source tables do not contain ground-truth labels.
- Inspect planted anomaly cases and confirm rules catch them for the intended reasons.
- Confirm export gating blocks failed/unapproved records.
- Review the generated database and report.
- Replace any project assumptions that do not match the intended payroll policy.
- Add your own meaningful commits and explain your changes. Do not fabricate review or commit history.

## Prompt history

A conversation-based prompt log is provided in `PROMPT_HISTORY.md`. It records the task prompts and the areas where AI assistance was requested. It is not a hidden model-internal reasoning trace; it is a record of user prompts and resulting assistance.
