# Data dictionary

Requiredness is relative to this synthetic workflow. `PK` = primary key; `FK` = foreign key. Money is INR decimal rounded to 2 places; hours are decimal hours.

| Entity | Field | Type | Required | Constraint / validation |
|---|---|---|---|---|
| Employee | employee_id | string | yes | PK, `EMP-000001` |
| Employee | first_name,last_name | string | yes | Synthetic identity only |
| Employee | email | string | yes | Unique synthetic `.invalid` email |
| Employee | department,job_title | enum/string | yes | Generated from documented lists |
| Employee | hire_date | date | yes | ISO date |
| Employee | employment_status | enum | yes | ACTIVE/INACTIVE |
| Employee | pay_group_id | string | yes | FK PayGroup |
| Employee | bank_account_token | string/null | no | Synthetic token; missing blocks export |
| Employee | tax_id_token | string/null | no | Synthetic token; missing blocks export |
| Employee | annual_salary_inr | decimal | yes | Non-negative INR |
| Employee | effective_start/end | date/null | yes/no | Start <= end if end exists |
| PayGroup | pay_group_id | string | yes | PK |
| PayGroup | name,currency,frequency,country | string/enum | yes | Currency INR; frequency MONTHLY |
| PayGroup | standard_hours,max_period_hours | decimal | yes | Positive; standard <= max |
| PayPeriod | pay_period_id | string | yes | PK `PP-YYYY-MM` |
| PayPeriod | period_start,period_end,pay_date | date | yes | start <= end; pay date >= period end |
| PayPeriod | pay_group_id | string | yes | FK PayGroup |
| PayPeriod | status | enum | yes | OPEN/CLOSED_FOR_INPUT/APPROVED/EXPORTED |
| TimeEntry | time_entry_id | string | yes | PK, immutable |
| TimeEntry | employee_id,pay_period_id | string | yes | FKs Employee, PayPeriod |
| TimeEntry | work_date | date | yes | Within period |
| TimeEntry | hours | decimal | yes | >= 0; maximum checked by rule |
| TimeEntry | submission_id,status | string/enum | yes | status SUBMITTED/APPROVED/REJECTED |
| TimeEntry | approved_by | string/null | conditional | Required for APPROVED |
| TimeEntry | source_time_entry_id | string/null | no | Links duplicate/correction provenance |
| TimeEntry | source_time_entry_id | string/null | no | Links duplicate/correction provenance; evaluation labels are kept only in separate ground_truth file |
| LeaveRecord | leave_record_id | string | yes | PK |
| LeaveRecord | employee_id,pay_period_id | string | yes | FKs |
| LeaveRecord | leave_date,leave_type,hours,status | date/enum/decimal | yes | date in period; hours >= 0 |
| LeaveRecord | approved_by | string/null | conditional | Required for APPROVED; evaluation labels are separate from source data |
| Allowance | allowance_id | string | yes | PK |
| Allowance | employee_id,pay_period_id | string | yes | FKs |
| Allowance | allowance_type,amount_inr,currency | enum/decimal/string | yes | amount >= 0; INR |
| Allowance | eligibility_status,approval_status | enum | yes | ELIGIBLE/INELIGIBLE; APPROVED/PENDING/REJECTED |
| Allowance | effective_start/end,source_record_id | date/string | yes | Effective date ordering; duplicate key checked |
| Deduction | deduction_id | string | yes | PK |
| Deduction | employee_id,pay_period_id | string | yes | FKs |
| Deduction | deduction_type,amount_inr,currency | enum/decimal/string | yes | amount >= 0; INR |
| Deduction | leave_record_id | string/null | no | Optional FK LeaveRecord |
| Deduction | eligibility_status,approval_status | enum | yes | Eligibility and approval gates |
| PayrollInput | payroll_input_id | string | yes | PK `PIN-<employee-id>-<period>` |
| PayrollInput | employee_id,pay_period_id | string | yes | FKs; unique employee-period pair |
| PayrollInput | approved_hours | decimal | yes | Derived from approved nonduplicate time |
| PayrollInput | base_pay,allowances,gross,deductions,net | decimal | yes | Derived; arithmetic must reconcile |
| PayrollInput | validation_status,reconciliation_status,approval_status | enum | yes | PENDING/PASS/FAIL/APPROVED/REJECTED as appropriate |
| PayrollInput | export_eligible | boolean | yes | True only after validation and approval |
| ValidationRule | rule_id | string | yes | PK `VR-###` |
| ValidationRule | rule_code,severity,description,enabled | string/enum/bool | yes | Unique rule code; ERROR/WARNING |
| Exception | exception_id | string | yes | PK `PEX-YYYY-000001` |
| Exception | payroll_input_id,rule_id | string | yes | FKs |
| Exception | issue_type,severity,status,description | string/enum | yes | OPEN/IN_REVIEW/RESOLVED/REJECTED |
| Exception | detected_at,resolved_at | timestamp/null | yes/no | Resolution timestamp only after resolution |
| Approval | approval_id | string | yes | PK |
| Approval | payroll_input_id,approver_role,approver_id | string | yes | FK PayrollInput; approver and role required |
| Approval | decision,decision_at,version | enum/timestamp/int | yes | APPROVED/REJECTED; version >= 1 |
| PayrollExport | payroll_export_id | string | yes | PK |
| PayrollExport | payroll_input_id,employee_id,pay_period_id | string | yes | FKs; unique payroll_input_id |
| PayrollExport | batch_id,status,exported_at,net_pay,currency | string/timestamp/decimal | yes | Export only if approved and eligible |
| EventHistory | event_id | string | yes | PK |
| EventHistory | entity_type,entity_id,event_type,from_state,to_state | string | yes | Append-only audit event |
| EventHistory | actor_id,event_at,details_json | string/timestamp/JSON | yes | Timestamp and actor required |
