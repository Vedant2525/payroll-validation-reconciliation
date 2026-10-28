# Entity relationships and cardinality

- `Employee` 1:N `TimeEntry`, `LeaveRecord`, `Allowance`, `Deduction`, `PayrollInput`.
- `PayGroup` 1:N `Employee` and `PayPeriod`.
- `PayPeriod` 1:N `TimeEntry`, `LeaveRecord`, `Allowance`, `Deduction`, `PayrollInput`.
- `PayrollInput` 1:N `Exception`, `Approval`, and `EventHistory`.
- `PayrollInput` 0:1 `PayrollExport` in this demo (one export record per payroll input).
- `LeaveRecord` 0:N `Deduction`; the validator rejects repeated deductions for the same leave record.
- `ValidationRule` 1:N `Exception`.
- `PayrollExport` 1:N export line items in a production batch design; this simplified model stores one payroll input per export row.
- Many-to-many relationships (for example employees eligible for multiple allowance plans) should use bridge tables such as `EmployeeAllowanceEligibility(employee_id, allowance_plan_id, effective_start, effective_end)`. The current demo uses transaction-level eligibility flags instead.

All IDs are stable primary keys. Foreign keys are checked during CSV validation and enforced by SQLite schema when loading database rows. Effective dates are included on master/eligibility-like data. Event history is append-only.
