# Payroll Validation & Reconciliation System

A reproducible, end-to-end synthetic payroll pre-export validation project. It demonstrates source-data generation, relational persistence, validation rules, exceptions, approvals, audit history, export gating, metrics, and a dashboard.

> **Synthetic-data demo only.** Names and contact details are synthetic placeholders; bank/tax identifiers are tokens, not real financial/tax details. Pay calculations are simplified and are not suitable for actual payroll or tax processing.

## Features

- Deterministic synthetic data generation with fixed seed `20261022`.
- Configurable scale: 3,000 employees and approximately 100,000 time/allowance/deduction records by default.
- Parent-first data generation and immutable deterministic identifiers.
- CSV and JSON output for all entities, plus a SQLite database and SQL schema.
- Rules for missing bank/tax tokens, excessive hours, duplicate time, duplicate allowance, duplicate leave deduction, reconciliation mismatches, and export approval.
- Separate `ground_truth` labels for evaluation; never used as a validation input.
- Exceptions, approvals, payroll exports, and append-only event history.
- Validation summary, source manifest/checksums, data dictionary, and repeat-run reproducibility check.
- Streamlit dashboard for KPI and exception review.
- Automated unit/integration tests.

## Quick start

Requires Python 3.10+.

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1

pip install -r requirements.txt

# Starter dataset
python -m src.cli generate --out output --employees 100 --transactions 3000 --seed 20261022

# Full baseline
python -m src.cli generate --out output --employees 3000 --transactions 100000 --seed 20261022

# Validate CSVs, keys, arithmetic, planted cases, and export gating
python -m src.cli validate --data output

# Create/recreate SQLite database from generated CSVs
python -m src.cli database --data output --db output/payroll.db

# Create an HTML evaluation report
python -m src.cli report --data output --out output/report.html

# Run tests
python -m unittest discover -s tests -v

# Launch dashboard
streamlit run dashboard.py
```

Run `python -m src.cli --help` or `python -m src.cli generate --help` for options.

## Main workflow

1. Generate master data (`Employee`, `PayGroup`, `PayPeriod`, `ValidationRule`).
2. Generate source records (`TimeEntry`, `LeaveRecord`, `Allowance`, `Deduction`) with valid parent IDs.
3. Aggregate source inputs into `PayrollInput`.
4. Run validations and create `Exception` records.
5. Route passing inputs through approval rules.
6. Export only records with passing validation and required approval.
7. Preserve decisions and state transitions in `EventHistory`; corrections are represented as new events/records, not deletion of prior evidence.
8. Evaluate planted cases against the separate `ground_truth` file.

## Important design notes / limitations

- The example uses a simplified salary-per-month baseline and flat synthetic deductions. It is not a tax engine, legal payroll implementation, or production-grade HRIS.
- The 100,000 parameter refers to approximate source rows across time, allowance, and deduction; deliberate anomaly rows are added on top. Leave rows are generated separately.
- Employee bank/tax data is represented by synthetic tokens and intentionally missing values for negative scenarios.
- A production implementation should add jurisdiction-specific payroll rules, access controls, encryption, real approval identities, idempotent batch processing, operational monitoring, and a formal change-management process.
- `ground_truth.csv/json` is strictly an evaluation artifact. The validator uses business fields and documented rules, not the ground-truth label, to decide.
- SQLite is used for portable demonstration. `schema.sql` documents primary keys, foreign keys, and core constraints. CSV exports are included for analysis/interoperability.

## Submission and transparency files

- `AI_USAGE.md`: where LLM assistance was used and what must be personally reviewed.
- `PROMPT_HISTORY.md`: conversation-based prompt log and contribution notes.
- `DESIGN_DECISIONS.md`: assumptions, trade-offs, validation strategy, and limitations.
- `PERSONAL_REVIEW_CHECKLIST.md`: checklist to complete honestly before submission.
- `GITHUB_PUBLICATION.md`: steps to publish as a public repository and make meaningful commits.
- `.github/workflows/tests.yml`: CI workflow for Python 3.10–3.12.

Generated full-scale data in `output/` is ignored by Git to keep the public repository manageable. Recreate it with the documented command. The downloadable project bundle may include generated artifacts for convenience.

## Project structure

```text
.
├── src/
│   ├── __init__.py
│   ├── generator.py
│   ├── validator.py
│   ├── database.py
│   ├── reporting.py
│   └── cli.py
├── tests/
│   └── test_workflow.py
├── docs/
│   ├── DATA_DICTIONARY.md
│   ├── RELATIONSHIPS.md
│   └── BUSINESS_RULES.md
├── dashboard.py
├── schema.sql
├── requirements.txt
└── README.md
```
