"""Independent data validation. Ground-truth labels are not used to decide outcomes."""
from pathlib import Path
import json
import pandas as pd

def validate(data_dir):
    d=Path(data_dir); checks=[]
    def ck(name, ok, detail=""): checks.append({"check":name,"passed":bool(ok),"detail":str(detail)})
    names=["Employee","PayGroup","PayPeriod","TimeEntry","LeaveRecord","Allowance","Deduction","PayrollInput","ValidationRule","Exception","Approval","PayrollExport","EventHistory","ground_truth"]
    t={n:pd.read_csv(d/f"{n}.csv") for n in names}
    for table,pk in [("Employee","employee_id"),("PayGroup","pay_group_id"),("PayPeriod","pay_period_id"),("TimeEntry","time_entry_id"),
                     ("LeaveRecord","leave_record_id"),("Allowance","allowance_id"),("Deduction","deduction_id"),("PayrollInput","payroll_input_id"),
                     ("ValidationRule","rule_id"),("Exception","exception_id"),("Approval","approval_id"),("PayrollExport","payroll_export_id"),("EventHistory","event_id")]:
        ck(f"{table} PK unique",t[table][pk].is_unique,int(t[table][pk].duplicated().sum()))
    for child in ["TimeEntry","LeaveRecord","Allowance","Deduction","PayrollInput"]:
        ck(f"{child} employee FK",t[child].employee_id.isin(t["Employee"].employee_id).all(),
           int((~t[child].employee_id.isin(t["Employee"].employee_id)).sum()))
        ck(f"{child} pay-period FK",t[child].pay_period_id.isin(t["PayPeriod"].pay_period_id).all(),
           int((~t[child].pay_period_id.isin(t["PayPeriod"].pay_period_id)).sum()))
    ck("PayGroup FK: Employee",t["Employee"].pay_group_id.isin(t["PayGroup"].pay_group_id).all())
    ck("PayGroup FK: PayPeriod",t["PayPeriod"].pay_group_id.isin(t["PayGroup"].pay_group_id).all())
    ck("Exception rule FK",t["Exception"].rule_id.isin(t["ValidationRule"].rule_id).all())
    ck("Exception payroll FK",t["Exception"].payroll_input_id.isin(t["PayrollInput"].payroll_input_id).all())
    ck("Approval payroll FK",t["Approval"].payroll_input_id.isin(t["PayrollInput"].payroll_input_id).all())
    ck("Export payroll FK",t["PayrollExport"].payroll_input_id.isin(t["PayrollInput"].payroll_input_id).all())
    ck("Export employee FK",t["PayrollExport"].employee_id.isin(t["Employee"].employee_id).all())
    ck("Export input unique",t["PayrollExport"].payroll_input_id.is_unique)
    ck("Time hours nonnegative",(t["TimeEntry"].hours>=0).all())
    ck("Leave hours nonnegative",(t["LeaveRecord"].hours>=0).all())
    ck("Allowance amounts nonnegative",(t["Allowance"].amount_inr>=0).all())
    ck("Deduction amounts nonnegative",(t["Deduction"].amount_inr>=0).all())
    ck("Period dates ordered",(t["PayPeriod"].period_start<=t["PayPeriod"].period_end).all())
    for source_table in ["TimeEntry","LeaveRecord","Allowance","Deduction","PayrollInput"]:
        ck(f"No ground-truth leakage: {source_table}",not ({"ground_truth","issue_type"} & set(t[source_table].columns)))
    ck("Gross arithmetic on clean records",all(abs(row.gross_pay_inr-(row.base_pay_inr+row.allowances_inr))<0.011 for row in t["PayrollInput"].itertuples() if row.reconciliation_status!="FAIL"))
    ck("Net arithmetic on clean records",all(abs(row.net_pay_inr-(row.gross_pay_inr-row.deductions_inr))<0.011 for row in t["PayrollInput"].itertuples() if row.reconciliation_status!="FAIL"))
    export=t["PayrollExport"].merge(t["PayrollInput"],on="payroll_input_id",suffixes=("_export","_input"))
    ck("Only approved inputs exported",((export["approval_status"]=="APPROVED") & (export["export_eligible"]==True) & (export["validation_status"]!="FAIL")).all(),len(export))
    gt=t["ground_truth"]
    exc_types=set(t["Exception"].issue_type.astype(str))
    for typ in gt.issue_type.unique():
        # The payroll reconciliation issue is named identically; source anomaly types are represented as exception families.
        if typ=="HOURS_EXCEED_PERIOD_MAX": ok="PERIOD_HOURS_MAX" in exc_types
        elif typ=="UNAPPROVED_TIME": ok="UNAPPROVED_TIME" in exc_types
        elif typ=="DUPLICATE_TIME_SUBMISSION": ok="DUPLICATE_TIME" in exc_types
        elif typ=="DUPLICATE_ALLOWANCE": ok="DUPLICATE_ALLOWANCE" in exc_types
        elif typ=="LEAVE_DEDUCTION_APPLIED_TWICE": ok="LEAVE_DEDUCTION_DUPLICATE" in exc_types
        elif typ=="RECONCILIATION_MISMATCH": ok="RECONCILIATION_MISMATCH" in exc_types
        else: ok=False
        ck(f"Ground truth anomaly detected: {typ}",ok)
    result={"checks_passed":sum(x["passed"] for x in checks),"checks_total":len(checks),"checks":checks,
            "exception_count":len(t["Exception"]),"export_count":len(t["PayrollExport"]),"payroll_input_count":len(t["PayrollInput"])}
    (d/"validation_report.json").write_text(json.dumps(result,indent=2))
    return result
