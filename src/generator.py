"""Deterministic synthetic payroll data generation."""
from __future__ import annotations
import hashlib, json, random
from pathlib import Path
from datetime import date, timedelta
import pandas as pd

PERIODS = [("PP-2026-01", date(2026,1,1), date(2026,1,31)),
           ("PP-2026-02", date(2026,2,1), date(2026,2,28)),
           ("PP-2026-03", date(2026,3,1), date(2026,3,31))]
FIRST = ["Aarav","Ishita","Kabir","Meera","Reyansh","Anaya","Vivaan","Saanvi","Arjun","Kiara","Advik","Diya"]
LAST = ["Sharma","Singh","Kaur","Verma","Patel","Gupta","Khan","Das","Rao","Joshi","Bedi","Nair"]
DEPARTMENTS = ["Engineering","Operations","Finance","HR","Sales","Support","Product","IT"]
ROLES = ["Analyst","Engineer","Specialist","Associate","Manager","Consultant"]
RULES = [
 ("VR-001","MISSING_BANK","ERROR","Employee bank token is missing"),
 ("VR-002","MISSING_TAX","ERROR","Employee tax token is missing"),
 ("VR-003","PERIOD_HOURS_MAX","ERROR","Approved hours exceed pay-group maximum"),
 ("VR-004","DUPLICATE_TIME","ERROR","Duplicate time submission detected"),
 ("VR-005","DUPLICATE_ALLOWANCE","ERROR","Duplicate allowance source record detected"),
 ("VR-006","UNAPPROVED_TIME","ERROR","Time entry is not approved"),
 ("VR-007","LEAVE_DEDUCTION_DUPLICATE","ERROR","Same leave record deducted more than once"),
 ("VR-008","RECONCILIATION_MISMATCH","ERROR","Payroll arithmetic does not reconcile"),
 ("VR-009","PAY_OUTLIER","WARNING","Net pay outside broad plausibility threshold"),
 ("VR-010","MISSING_APPROVAL","ERROR","Required payroll approval is missing"),
]
def money(x): return round(float(x), 2)
def write_table(out, name, rows):
    df = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    df.to_csv(out/f"{name}.csv", index=False)
    df.to_json(out/f"{name}.json", orient="records", indent=2, date_format="iso")
    return df
def generate(out_dir, employees_n=3000, transactions_n=100000, seed=20261022):
    out=Path(out_dir); out.mkdir(parents=True,exist_ok=True); r=random.Random(seed)
    n=max(1,int(employees_n)); txn=max(3,int(transactions_n))
    paygroups=[{"pay_group_id":"PG-MONTHLY-IN","name":"India Monthly","currency":"INR","frequency":"MONTHLY","standard_hours":176,"max_period_hours":240,"country":"IN"}]
    emps=[]
    for i in range(1,n+1):
        emp=f"EMP-{i:06d}"
        emps.append({"employee_id":emp,"first_name":r.choice(FIRST),"last_name":r.choice(LAST),
          "email":f"{emp.lower()}@example.invalid","department":r.choice(DEPARTMENTS),"job_title":r.choice(ROLES),
          "hire_date":str(date(2021,1,1)+timedelta(days=r.randint(0,1800))),"employment_status":"ACTIVE",
          "pay_group_id":paygroups[0]["pay_group_id"],"bank_account_token":None if i%137==0 else f"SYNTH-BANK-{i:07d}",
          "tax_id_token":None if i%149==0 else f"SYNTH-TAX-{i:07d}","annual_salary_inr":r.randrange(360000,2400000,12000),
          "effective_start":"2026-01-01","effective_end":None,"synthetic_record":True})
    periods=[{"pay_period_id":pid,"period_start":str(st),"period_end":str(en),"pay_date":str(en+timedelta(days=5)),
      "pay_group_id":paygroups[0]["pay_group_id"],"status":"CLOSED_FOR_INPUT","effective_start":str(st),"effective_end":str(en)} for pid,st,en in PERIODS]
    nr_time=max(1,int(txn*.70)); nr_allow=max(1,int(txn*.15)); nr_ded=max(1,txn-nr_time-nr_allow)
    time=[]; leave=[]; allowances=[]; deductions=[]; truth=[]
    for j in range(nr_time):
        e=emps[r.randrange(n)]; pid,st,en=PERIODS[r.randrange(3)]; day=st+timedelta(days=r.randrange((en-st).days+1))
        time.append({"time_entry_id":f"TIME-{e['employee_id']}-{day.isoformat()}-{j+1:06d}","employee_id":e["employee_id"],
          "pay_period_id":pid,"work_date":str(day),"hours":float(r.choice([4,6,7.5,8,8,8,8,9])),
          "submission_id":f"SUB-{j+1:08d}","status":"APPROVED","approved_by":f"MGR-{(int(e['employee_id'][-6:])%250)+1:04d}",
          "source_time_entry_id":None,"issue_type":None,"ground_truth":"NORMAL","created_at":str(day+timedelta(days=1))})
    for i in range(max(1,n//3)):
        e=emps[(i*7)%n]; pid,st,en=PERIODS[i%3]; day=st+timedelta(days=(i*3)%(en-st).days)
        leave.append({"leave_record_id":f"LEV-{i+1:08d}","employee_id":e["employee_id"],"pay_period_id":pid,
          "leave_date":str(day),"leave_type":"UNPAID" if i%7==0 else r.choice(["ANNUAL","SICK","CASUAL"]),
          "hours":8 if i%7==0 else 4,"status":"APPROVED","approved_by":f"MGR-{i%250+1:04d}",
          "effective_start":str(day),"effective_end":str(day),"issue_type":None,"ground_truth":"NORMAL"})
    for j in range(nr_allow):
        e=emps[r.randrange(n)]; pid,st,en=PERIODS[r.randrange(3)]; typ=r.choice(["MEAL","TRAVEL","INTERNET","SHIFT"])
        allowances.append({"allowance_id":f"ALW-{j+1:08d}","employee_id":e["employee_id"],"pay_period_id":pid,
          "allowance_type":typ,"amount_inr":money(r.choice([500,750,1000,1500,2000,2500])),"currency":"INR",
          "eligibility_status":"ELIGIBLE","approval_status":"APPROVED","effective_start":str(st),"effective_end":str(en),
          "source_record_id":f"ALW-SRC-{j+1:08d}","issue_type":None,"ground_truth":"NORMAL"})
    for j in range(nr_ded):
        e=emps[r.randrange(n)]; pid,st,en=PERIODS[r.randrange(3)]
        deductions.append({"deduction_id":f"DED-{j+1:08d}","employee_id":e["employee_id"],"pay_period_id":pid,
          "deduction_type":r.choice(["PF","TAX","INSURANCE","UNPAID_LEAVE"]),
          "amount_inr":money(r.choice([250,500,750,1000,1500,2500,4000])),"currency":"INR",
          "eligibility_status":"ELIGIBLE","approval_status":"APPROVED","effective_start":str(st),"effective_end":str(en),
          "source_record_id":f"DED-SRC-{j+1:08d}","leave_record_id":None,"issue_type":None,"ground_truth":"NORMAL"})
    # Plant labelled anomaly examples without corrupting unrelated rows.
    if time:
        time[0].update(hours=260.0,issue_type="HOURS_EXCEED_PERIOD_MAX",ground_truth="ANOMALY")
        truth.append({"record_type":"TimeEntry","record_id":time[0]["time_entry_id"],"issue_type":"HOURS_EXCEED_PERIOD_MAX","expected_decision":"BLOCK","rule_id":"VR-003","reason":"Hours exceed 240"})
        time[1].update(status="SUBMITTED",issue_type="UNAPPROVED_TIME",ground_truth="ANOMALY")
        truth.append({"record_type":"TimeEntry","record_id":time[1]["time_entry_id"],"issue_type":"UNAPPROVED_TIME","expected_decision":"BLOCK","rule_id":"VR-006","reason":"Time is not approved"})
        dup=dict(time[2]); dup.update(time_entry_id=time[2]["time_entry_id"]+"-DUP",source_time_entry_id=time[2]["time_entry_id"],
             issue_type="DUPLICATE_TIME_SUBMISSION",ground_truth="ANOMALY")
        time.append(dup)
        truth.append({"record_type":"TimeEntry","record_id":dup["time_entry_id"],"issue_type":"DUPLICATE_TIME_SUBMISSION","expected_decision":"BLOCK_DUPLICATE","rule_id":"VR-004","reason":"Duplicate submission fingerprint"})
    if allowances:
        dup=dict(allowances[0]); dup.update(allowance_id=f"ALW-{nr_allow+1:08d}",issue_type="DUPLICATE_ALLOWANCE",ground_truth="ANOMALY")
        allowances.append(dup)
        truth.append({"record_type":"Allowance","record_id":dup["allowance_id"],"issue_type":"DUPLICATE_ALLOWANCE","expected_decision":"BLOCK_DUPLICATE","rule_id":"VR-005","reason":"Duplicate source record"})
    if deductions and leave:
        deductions[0].update(issue_type="LEAVE_DEDUCTION_APPLIED_TWICE",ground_truth="ANOMALY",leave_record_id=leave[0]["leave_record_id"])
        dup=dict(deductions[0]); dup.update(deduction_id=f"DED-{nr_ded+1:08d}")
        deductions.append(dup)
        truth.append({"record_type":"Deduction","record_id":dup["deduction_id"],"issue_type":"LEAVE_DEDUCTION_APPLIED_TWICE","expected_decision":"BLOCK_DUPLICATE","rule_id":"VR-007","reason":"Same leave record is deducted twice"})
    # Build aggregate inputs from approved time and source transactions.
    time_agg={}
    for t in time:
        if t["status"]=="APPROVED" and not t["source_time_entry_id"]:
            k=(t["employee_id"],t["pay_period_id"]); time_agg[k]=time_agg.get(k,0)+t["hours"]
    allow_agg={}; ded_agg={}
    for a in allowances:
        k=(a["employee_id"],a["pay_period_id"]); allow_agg[k]=allow_agg.get(k,0)+a["amount_inr"]
    for d in deductions:
        k=(d["employee_id"],d["pay_period_id"]); ded_agg[k]=ded_agg.get(k,0)+d["amount_inr"]
    salary={e["employee_id"]:e["annual_salary_inr"]/12 for e in emps}
    pins=[]
    for e in emps:
        for pid,_,_ in PERIODS:
            k=(e["employee_id"],pid); base=money(salary[e["employee_id"]]); allow=money(allow_agg.get(k,0)); ded=money(ded_agg.get(k,0))
            pins.append({"payroll_input_id":f"PIN-{e['employee_id']}-{pid[-7:]}","employee_id":e["employee_id"],"pay_period_id":pid,
              "approved_hours":round(time_agg.get(k,0),2),"base_pay_inr":base,"allowances_inr":allow,
              "gross_pay_inr":money(base+allow),"deductions_inr":ded,"net_pay_inr":money(base+allow-ded),"currency":"INR",
              "reconciliation_status":"PENDING","validation_status":"PENDING","approval_status":"PENDING",
              "export_eligible":False,"version":1,"created_at":"2026-04-01T00:00:00"})
    # One explicit reconciliation failure with ground truth.
    pins[0]["gross_pay_inr"]=money(pins[0]["gross_pay_inr"]+1)
    truth.append({"record_type":"PayrollInput","record_id":pins[0]["payroll_input_id"],"issue_type":"RECONCILIATION_MISMATCH",
      "expected_decision":"BLOCK","rule_id":"VR-008","reason":"Gross pay intentionally differs by INR 1.00"})
    rule_rows=[{"rule_id":a,"rule_code":b,"severity":c,"description":d,"enabled":True} for a,b,c,d in RULES]
    # Validate inputs and emit exceptions, approvals, event log and exports.
    empmap={e["employee_id"]:e for e in emps}; pmap={p["pay_period_id"]:p for p in periods}
    time_group={}; allow_group={}; ded_group={}
    for t in time: time_group.setdefault((t["employee_id"],t["pay_period_id"]),[]).append(t)
    for a in allowances: allow_group.setdefault((a["employee_id"],a["pay_period_id"]),[]).append(a)
    for d in deductions: ded_group.setdefault((d["employee_id"],d["pay_period_id"]),[]).append(d)
    exceptions=[]; approvals=[]; exports=[]; events=[]
    for pin in pins:
        eid,pid=pin["employee_id"],pin["pay_period_id"]; e=empmap[eid]; issues=[]
        if not e["bank_account_token"]: issues.append(("VR-001","MISSING_BANK","ERROR","Synthetic bank token is missing"))
        if not e["tax_id_token"]: issues.append(("VR-002","MISSING_TAX","ERROR","Synthetic tax token is missing"))
        ts=time_group.get((eid,pid),[])
        hours=sum(t["hours"] for t in ts if t["status"]=="APPROVED" and not t["source_time_entry_id"])
        if hours>240: issues.append(("VR-003","PERIOD_HOURS_MAX","ERROR",f"Approved hours {hours} exceed 240"))
        if any(t["status"]!="APPROVED" for t in ts): issues.append(("VR-006","UNAPPROVED_TIME","ERROR","At least one time entry is not approved"))
        if any(t["source_time_entry_id"] for t in ts): issues.append(("VR-004","DUPLICATE_TIME","ERROR","Duplicate time submission linked to this period"))
        als=allow_group.get((eid,pid),[])
        allowance_sources=[a["source_record_id"] for a in als]
        if len(allowance_sources)!=len(set(allowance_sources)):
            issues.append(("VR-005","DUPLICATE_ALLOWANCE","ERROR","Duplicate allowance source record detected"))
        ds=ded_group.get((eid,pid),[])
        leave_refs=[d.get("leave_record_id") for d in ds if d.get("leave_record_id") is not None]
        if len(leave_refs)!=len(set(leave_refs)):
            issues.append(("VR-007","LEAVE_DEDUCTION_DUPLICATE","ERROR","Same leave record deducted twice"))
        if pin["gross_pay_inr"] != money(pin["base_pay_inr"]+pin["allowances_inr"]):
            issues.append(("VR-008","RECONCILIATION_MISMATCH","ERROR","Gross pay does not reconcile to base plus allowances"))
        if pin["net_pay_inr"] != money(pin["gross_pay_inr"]-pin["deductions_inr"]):
            issues.append(("VR-008","RECONCILIATION_MISMATCH","ERROR","Net pay does not reconcile to gross less deductions"))
        if pin["net_pay_inr"] < 0: issues.append(("VR-009","NEGATIVE_NET_PAY","ERROR","Deductions exceed gross pay"))
        for rule,typ,sev,msg in issues:
            exceptions.append({"exception_id":f"PEX-2026-{len(exceptions)+1:06d}","payroll_input_id":pin["payroll_input_id"],
              "employee_id":eid,"pay_period_id":pid,"rule_id":rule,"issue_type":typ,"severity":sev,"description":msg,
              "status":"OPEN","detected_at":"2026-04-01T00:00:00","resolved_at":None,"resolution_event_id":None})
        blocked=any(x[2]=="ERROR" for x in issues)
        pin["reconciliation_status"]="FAIL" if any(x[1]=="RECONCILIATION_MISMATCH" for x in issues) else "PASS"
        pin["validation_status"]="FAIL" if blocked else ("WARNING" if issues else "PASS")
        pin["approval_status"]="PENDING" if blocked else "APPROVED"
        pin["export_eligible"]=not blocked
        if not blocked:
            approvals.append({"approval_id":f"APR-{len(approvals)+1:08d}","payroll_input_id":pin["payroll_input_id"],
              "approver_role":"HR_PARTNER","approver_id":"HR-SYNTH-001","decision":"APPROVED",
              "decision_at":"2026-04-02T09:00:00","comment":"Synthetic approval after validation passed","version":1})
            exports.append({"payroll_export_id":f"EXP-{len(exports)+1:08d}","payroll_input_id":pin["payroll_input_id"],
              "employee_id":eid,"pay_period_id":pid,"export_batch_id":f"BATCH-{pid}","export_status":"EXPORTED",
              "exported_at":"2026-04-03T09:00:00","net_pay_inr":pin["net_pay_inr"],"currency":"INR"})
        events.append({"event_id":f"EVT-{len(events)+1:08d}","entity_type":"PayrollInput","entity_id":pin["payroll_input_id"],
          "event_type":"VALIDATION_COMPLETED","from_state":"PENDING","to_state":pin["validation_status"],
          "actor_id":"SYSTEM-VALIDATOR","event_at":"2026-04-01T00:00:00","details_json":json.dumps({"issue_count":len(issues)},sort_keys=True)})
    # Data dictionary rows are also written in machine-readable form.
    dictionary=[]
    for ent, fields in {
      "Employee":["employee_id","first_name","last_name","email","department","job_title","hire_date","employment_status","pay_group_id","bank_account_token","tax_id_token","annual_salary_inr","effective_start","effective_end"],
      "PayGroup":["pay_group_id","name","currency","frequency","standard_hours","max_period_hours","country"],
      "PayPeriod":["pay_period_id","period_start","period_end","pay_date","pay_group_id","status","effective_start","effective_end"],
      "TimeEntry":["time_entry_id","employee_id","pay_period_id","work_date","hours","submission_id","status","approved_by","source_time_entry_id","created_at"],
      "LeaveRecord":["leave_record_id","employee_id","pay_period_id","leave_date","leave_type","hours","status","approved_by","effective_start","effective_end"],
      "Allowance":["allowance_id","employee_id","pay_period_id","allowance_type","amount_inr","currency","eligibility_status","approval_status","effective_start","effective_end","source_record_id"],
      "Deduction":["deduction_id","employee_id","pay_period_id","deduction_type","amount_inr","currency","eligibility_status","approval_status","effective_start","effective_end","source_record_id","leave_record_id"],
      "PayrollInput":["payroll_input_id","employee_id","pay_period_id","approved_hours","base_pay_inr","allowances_inr","gross_pay_inr","deductions_inr","net_pay_inr","currency","reconciliation_status","validation_status","approval_status","export_eligible","version","created_at"],
      "ValidationRule":["rule_id","rule_code","severity","description","enabled"],
      "Exception":["exception_id","payroll_input_id","employee_id","pay_period_id","rule_id","issue_type","severity","description","status","detected_at","resolved_at","resolution_event_id"],
      "Approval":["approval_id","payroll_input_id","approver_role","approver_id","decision","decision_at","comment","version"],
      "PayrollExport":["payroll_export_id","payroll_input_id","employee_id","pay_period_id","export_batch_id","export_status","exported_at","net_pay_inr","currency"],
      "EventHistory":["event_id","entity_type","entity_id","event_type","from_state","to_state","actor_id","event_at","details_json"],
    }.items():
        for f in fields:
            dictionary.append({"entity":ent,"field":f,"type":"see docs/DATA_DICTIONARY.md","required_or_optional":"see docs","uniqueness":"PK/FK per docs","validation_rule":"see docs/BUSINESS_RULES.md"})
    # Keep evaluation labels out of operational source tables. Ground truth is a separate artifact.
    time_df=pd.DataFrame(time).drop(columns=["ground_truth","issue_type"],errors="ignore")
    leave_df=pd.DataFrame(leave).drop(columns=["ground_truth","issue_type"],errors="ignore")
    allowance_df=pd.DataFrame(allowances).drop(columns=["ground_truth","issue_type"],errors="ignore")
    deduction_df=pd.DataFrame(deductions).drop(columns=["ground_truth","issue_type"],errors="ignore")
    tables={
      "Employee":pd.DataFrame(emps),"PayGroup":pd.DataFrame(paygroups),"PayPeriod":pd.DataFrame(periods),
      "TimeEntry":time_df,"LeaveRecord":leave_df,"Allowance":allowance_df,
      "Deduction":deduction_df,"PayrollInput":pd.DataFrame(pins),"ValidationRule":pd.DataFrame(rule_rows),
      "Exception":pd.DataFrame(exceptions),"Approval":pd.DataFrame(approvals),"PayrollExport":pd.DataFrame(exports),
      "EventHistory":pd.DataFrame(events),"DataDictionary":pd.DataFrame(dictionary),
      "ground_truth":pd.DataFrame(truth,columns=["record_type","record_id","issue_type","expected_decision","rule_id","reason"])
    }
    manifest=[]
    for name,df in tables.items():
        write_table(out,name,df)
        csv=out/f"{name}.csv"
        manifest.append({"file":csv.name,"rows":len(df),"sha256":hashlib.sha256(csv.read_bytes()).hexdigest()})
    # Checks focus on structural invariants and documented planted failure behavior.
    checks=[]
    def ck(name, passed, detail): checks.append({"check":name,"passed":bool(passed),"detail":str(detail)})
    ck("Employee PK unique",tables["Employee"].employee_id.is_unique,len(emps))
    ck("PayGroup PK unique",tables["PayGroup"].pay_group_id.is_unique,len(paygroups))
    ck("PayPeriod PK unique",tables["PayPeriod"].pay_period_id.is_unique,len(periods))
    ck("TimeEntry PK unique",tables["TimeEntry"].time_entry_id.is_unique,len(time))
    for child in ["TimeEntry","LeaveRecord","Allowance","Deduction","PayrollInput"]:
        df=tables[child]
        ck(f"Employee FK: {child}",df.employee_id.isin(tables["Employee"].employee_id).all(),int((~df.employee_id.isin(tables["Employee"].employee_id)).sum()))
        ck(f"PayPeriod FK: {child}",df.pay_period_id.isin(tables["PayPeriod"].pay_period_id).all(),int((~df.pay_period_id.isin(tables["PayPeriod"].pay_period_id)).sum()))
    for pin in pins:
        if pin["payroll_input_id"] not in {x["record_id"] for x in truth if x["record_type"]=="PayrollInput"}:
            ck_gross = pin["gross_pay_inr"]==money(pin["base_pay_inr"]+pin["allowances_inr"])
            ck_net = pin["net_pay_inr"]==money(pin["gross_pay_inr"]-pin["deductions_inr"])
            if not ck_gross or not ck_net: break
    clean=[p for p in pins if not (p["payroll_input_id"]==pins[0]["payroll_input_id"])]
    ck("Gross arithmetic on non-planted rows",all(p["gross_pay_inr"]==money(p["base_pay_inr"]+p["allowances_inr"]) for p in clean),len(clean))
    ck("Net arithmetic on non-planted rows",all(p["net_pay_inr"]==money(p["gross_pay_inr"]-p["deductions_inr"]) for p in clean),len(clean))
    ck("Reconciliation anomaly blocked",pins[0]["validation_status"]=="FAIL" and not pins[0]["export_eligible"],pins[0]["payroll_input_id"])
    export_ids={x["payroll_input_id"] for x in exports}
    ck("Export inputs approved",all(next(p for p in pins if p["payroll_input_id"]==x)["approval_status"]=="APPROVED" for x in export_ids),len(exports))
    ck("Ground truth separated", "ground_truth" in tables and "ground_truth" not in ["Employee","TimeEntry","PayrollInput"],len(truth))
    summary={"seed":seed,"employees_requested":n,"source_transactions_requested":txn,
      "actual_source_rows":{"TimeEntry":len(time),"LeaveRecord":len(leave),"Allowance":len(allowances),"Deduction":len(deductions)},
      "payroll_inputs":len(pins),"exceptions":len(exceptions),"exports":len(exports),"ground_truth_cases":len(truth),
      "checks_passed":sum(x["passed"] for x in checks),"checks_total":len(checks),"checks":checks}
    (out/"validation_summary.json").write_text(json.dumps(summary,indent=2))
    (out/"source_manifest.json").write_text(json.dumps({"provenance":"Synthetic only; no external data used","seed":seed,"files":manifest},indent=2))
    return summary
