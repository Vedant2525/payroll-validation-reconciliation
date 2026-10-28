# Design Decisions, Assumptions, Trade-offs, and Limitations

## Problem
Payroll inputs from time, leave, allowances, and deductions must be checked and reconciled before export. Errors should become explicit exceptions, and only approved, validated inputs should reach the export table.

## Assumptions

- Three monthly periods (January–March 2026) are used as a repeatable demonstration window.
- Currency is INR and pay groups use a monthly cadence.
- Employees, names, `.invalid` emails, bank tokens, and tax tokens are synthetic; no real financial or tax identifiers are present.
- Monthly base pay is annual salary divided by 12. Gross = base + allowances; net = gross − deductions. This deliberately simplified calculation is for workflow testing, not lawful payroll processing.
- A fixed seed makes random choices reproducible. IDs are stable and generated from deterministic counters and parent IDs.
- Deliberate anomalies are documented in a separate `ground_truth.csv/json` file. Operational source tables do not carry `issue_type` or `ground_truth` columns.

## Key decisions

1. **Generate parents first.** Employee, PayGroup, and PayPeriod exist before dependent transactions are generated.
2. **Use CSV/JSON plus SQLite.** Flat files are easy to inspect and distribute; SQLite provides relational constraints and local query capability without requiring a server.
3. **Separate labels from features.** The validator bases decisions on business fields and keys. The ground-truth file is reserved for evaluation only.
4. **Use append-oriented event history.** Validation and state changes are represented as events; a production correction should append a correction/reversal event rather than silently replace evidence.
5. **Fail closed at export.** Inputs with blocking errors are not exported. Approval records are required for exported inputs.
6. **Make the demo easy to run.** The CLI is the core interface; Streamlit is optional for visual review.

## Trade-offs

- SQLite keeps setup simple but is not a distributed production database.
- Synthetic records are reproducible and safe to share but do not reproduce every real payroll distribution or country-specific rule.
- The starter schema includes an event log, but a production-grade immutable audit system would need authorization, append-only database permissions, tamper-evident logs, and retention policies.
- The current approval decision is generated synthetically for records that pass validation. Real approvals must be explicit human actions in an authenticated workflow.
- `--transactions` approximately controls time, allowance, and deduction rows; injected anomalies add a few extra rows.

## Validation approach

- Primary-key uniqueness and selected foreign-key checks.
- Enum/amount/date checks where implemented.
- Arithmetic reconciliation for non-planted rows plus explicit detection of a planted mismatch.
- Anomaly-family detection against separately stored ground truth.
- Export gate checks that every exported input is approved and eligible.
- SQLite `PRAGMA foreign_key_check`.
- Unit/integration tests and a same-seed SHA-256 manifest comparison.

## Known limitations / next work

- This is not a tax engine or a production payroll product.
- Approval and exception resolution are demonstrated as records, not a fully authenticated interactive lifecycle UI.
- Full effective-date overlap rules, leave accrual policies, statutory tax rules, correction/reversal commands, idempotent export retries, and exhaustive relationship constraints need expansion.
- SQL seed export is represented by `schema.sql` plus CSV-driven SQLite population; portable SQL `INSERT` seed files are not currently emitted.
- The dashboard is a read-only review interface.
