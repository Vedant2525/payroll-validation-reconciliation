# Business rules

| Rule | Severity | Logic | Expected action |
|---|---|---|---|
| VR-001 MISSING_BANK | ERROR | Employee bank token missing | Block export; create exception |
| VR-002 MISSING_TAX | ERROR | Employee tax token missing | Block export; create exception |
| VR-003 PERIOD_HOURS_MAX | ERROR | Approved period hours exceed pay-group maximum | Block export; create exception |
| VR-004 DUPLICATE_TIME | ERROR | Same employee/date/submission fingerprint occurs more than once | Exclude duplicate; create exception |
| VR-005 DUPLICATE_ALLOWANCE | ERROR | Same employee/period/type/source key appears more than once | Block export; create exception |
| VR-006 UNAPPROVED_TIME | ERROR | A submitted time entry is not approved | Block export; create exception |
| VR-007 LEAVE_DEDUCTION_DUPLICATE | ERROR | Same leave record is deducted more than once | Block export; create exception |
| VR-008 RECONCILIATION_MISMATCH | ERROR | Gross != base + allowances or net != gross - deductions | Block export; create exception |
| VR-009 PAY_OUTLIER | WARNING | Net pay outside broad plausibility threshold | Warn and require review in production policy |
| VR-010 MISSING_APPROVAL | ERROR | Required approval absent or not approved | Block export |

## Simplified calculation
- Monthly base pay = annual salary / 12.
- Gross pay = monthly base pay + eligible allowance total.
- Net pay = gross pay - eligible deduction total.
- Approved time and leave are validated as payroll inputs; this demo does not calculate hourly wages or country-specific tax.

## Lifecycle
- Exception: OPEN → IN_REVIEW → RESOLVED or REJECTED. Each transition should append an event.
- Approval: PENDING → APPROVED or REJECTED. A rejected approval blocks export.
- Payroll input: PENDING → VALIDATED / EXCEPTION → APPROVED → EXPORTED. Failed validation blocks the transition to APPROVED/EXPORTED.
- Export rows are generated only after validation and approval gates pass.
