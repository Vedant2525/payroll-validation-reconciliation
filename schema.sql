PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS PayGroup (
  pay_group_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  currency TEXT NOT NULL CHECK(currency = 'INR'),
  frequency TEXT NOT NULL CHECK(frequency IN ('MONTHLY')),
  standard_hours REAL NOT NULL CHECK(standard_hours > 0),
  max_period_hours REAL NOT NULL CHECK(max_period_hours >= standard_hours),
  country TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS Employee (
  employee_id TEXT PRIMARY KEY,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  department TEXT NOT NULL,
  job_title TEXT NOT NULL,
  hire_date TEXT NOT NULL,
  employment_status TEXT NOT NULL CHECK(employment_status IN ('ACTIVE','INACTIVE')),
  pay_group_id TEXT NOT NULL REFERENCES PayGroup(pay_group_id),
  bank_account_token TEXT,
  tax_id_token TEXT,
  annual_salary_inr REAL NOT NULL CHECK(annual_salary_inr >= 0),
  effective_start TEXT NOT NULL,
  effective_end TEXT
);
CREATE TABLE IF NOT EXISTS PayPeriod (
  pay_period_id TEXT PRIMARY KEY,
  period_start TEXT NOT NULL,
  period_end TEXT NOT NULL,
  pay_date TEXT NOT NULL,
  pay_group_id TEXT NOT NULL REFERENCES PayGroup(pay_group_id),
  status TEXT NOT NULL,
  effective_start TEXT NOT NULL,
  effective_end TEXT NOT NULL,
  CHECK(period_start <= period_end),
  CHECK(pay_date >= period_end)
);
CREATE TABLE IF NOT EXISTS TimeEntry (
  time_entry_id TEXT PRIMARY KEY,
  employee_id TEXT NOT NULL REFERENCES Employee(employee_id),
  pay_period_id TEXT NOT NULL REFERENCES PayPeriod(pay_period_id),
  work_date TEXT NOT NULL,
  hours REAL NOT NULL CHECK(hours >= 0),
  submission_id TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('SUBMITTED','APPROVED','REJECTED')),
  approved_by TEXT,
  source_time_entry_id TEXT,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS LeaveRecord (
  leave_record_id TEXT PRIMARY KEY,
  employee_id TEXT NOT NULL REFERENCES Employee(employee_id),
  pay_period_id TEXT NOT NULL REFERENCES PayPeriod(pay_period_id),
  leave_date TEXT NOT NULL,
  leave_type TEXT NOT NULL,
  hours REAL NOT NULL CHECK(hours >= 0),
  status TEXT NOT NULL,
  approved_by TEXT,
  effective_start TEXT NOT NULL,
  effective_end TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS Allowance (
  allowance_id TEXT PRIMARY KEY,
  employee_id TEXT NOT NULL REFERENCES Employee(employee_id),
  pay_period_id TEXT NOT NULL REFERENCES PayPeriod(pay_period_id),
  allowance_type TEXT NOT NULL,
  amount_inr REAL NOT NULL CHECK(amount_inr >= 0),
  currency TEXT NOT NULL CHECK(currency = 'INR'),
  eligibility_status TEXT NOT NULL,
  approval_status TEXT NOT NULL,
  effective_start TEXT NOT NULL,
  effective_end TEXT NOT NULL,
  source_record_id TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS Deduction (
  deduction_id TEXT PRIMARY KEY,
  employee_id TEXT NOT NULL REFERENCES Employee(employee_id),
  pay_period_id TEXT NOT NULL REFERENCES PayPeriod(pay_period_id),
  deduction_type TEXT NOT NULL,
  amount_inr REAL NOT NULL CHECK(amount_inr >= 0),
  currency TEXT NOT NULL CHECK(currency = 'INR'),
  eligibility_status TEXT NOT NULL,
  approval_status TEXT NOT NULL,
  effective_start TEXT NOT NULL,
  effective_end TEXT NOT NULL,
  source_record_id TEXT NOT NULL,
  leave_record_id TEXT REFERENCES LeaveRecord(leave_record_id)
);
CREATE TABLE IF NOT EXISTS PayrollInput (
  payroll_input_id TEXT PRIMARY KEY,
  employee_id TEXT NOT NULL REFERENCES Employee(employee_id),
  pay_period_id TEXT NOT NULL REFERENCES PayPeriod(pay_period_id),
  approved_hours REAL NOT NULL CHECK(approved_hours >= 0),
  base_pay_inr REAL NOT NULL,
  allowances_inr REAL NOT NULL,
  gross_pay_inr REAL NOT NULL,
  deductions_inr REAL NOT NULL,
  net_pay_inr REAL NOT NULL,
  currency TEXT NOT NULL,
  reconciliation_status TEXT NOT NULL,
  validation_status TEXT NOT NULL,
  approval_status TEXT NOT NULL,
  export_eligible INTEGER NOT NULL CHECK(export_eligible IN (0,1)),
  version INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  UNIQUE(employee_id, pay_period_id)
);
CREATE TABLE IF NOT EXISTS ValidationRule (
  rule_id TEXT PRIMARY KEY,
  rule_code TEXT NOT NULL UNIQUE,
  severity TEXT NOT NULL,
  description TEXT NOT NULL,
  enabled INTEGER NOT NULL CHECK(enabled IN (0,1))
);
CREATE TABLE IF NOT EXISTS Exception (
  exception_id TEXT PRIMARY KEY,
  payroll_input_id TEXT NOT NULL REFERENCES PayrollInput(payroll_input_id),
  employee_id TEXT NOT NULL REFERENCES Employee(employee_id),
  pay_period_id TEXT NOT NULL REFERENCES PayPeriod(pay_period_id),
  rule_id TEXT NOT NULL REFERENCES ValidationRule(rule_id),
  issue_type TEXT NOT NULL,
  severity TEXT NOT NULL,
  description TEXT NOT NULL,
  status TEXT NOT NULL,
  detected_at TEXT NOT NULL,
  resolved_at TEXT,
  resolution_event_id TEXT
);
CREATE TABLE IF NOT EXISTS Approval (
  approval_id TEXT PRIMARY KEY,
  payroll_input_id TEXT NOT NULL REFERENCES PayrollInput(payroll_input_id),
  approver_role TEXT NOT NULL,
  approver_id TEXT NOT NULL,
  decision TEXT NOT NULL CHECK(decision IN ('APPROVED','REJECTED','PENDING')),
  decision_at TEXT NOT NULL,
  comment TEXT,
  version INTEGER NOT NULL CHECK(version >= 1)
);
CREATE TABLE IF NOT EXISTS PayrollExport (
  payroll_export_id TEXT PRIMARY KEY,
  payroll_input_id TEXT NOT NULL UNIQUE REFERENCES PayrollInput(payroll_input_id),
  employee_id TEXT NOT NULL REFERENCES Employee(employee_id),
  pay_period_id TEXT NOT NULL REFERENCES PayPeriod(pay_period_id),
  export_batch_id TEXT NOT NULL,
  export_status TEXT NOT NULL,
  exported_at TEXT NOT NULL,
  net_pay_inr REAL NOT NULL,
  currency TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS EventHistory (
  event_id TEXT PRIMARY KEY,
  entity_type TEXT NOT NULL,
  entity_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  from_state TEXT,
  to_state TEXT,
  actor_id TEXT NOT NULL,
  event_at TEXT NOT NULL,
  details_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_time_employee_period ON TimeEntry(employee_id,pay_period_id);
CREATE INDEX IF NOT EXISTS ix_allowance_employee_period ON Allowance(employee_id,pay_period_id);
CREATE INDEX IF NOT EXISTS ix_deduction_employee_period ON Deduction(employee_id,pay_period_id);
CREATE INDEX IF NOT EXISTS ix_exception_status ON Exception(status,severity);
