"""Create a self-contained HTML evaluation report."""
from pathlib import Path
import json, pandas as pd, html
def create_report(data_dir, out_file=None):
    d=Path(data_dir); out=Path(out_file) if out_file else d/"report.html"
    summary=json.loads((d/"validation_summary.json").read_text())
    checks=json.loads((d/"validation_report.json").read_text()) if (d/"validation_report.json").exists() else summary
    exceptions=pd.read_csv(d/"Exception.csv")
    exports=pd.read_csv(d/"PayrollExport.csv")
    inputs=pd.read_csv(d/"PayrollInput.csv")
    status=exceptions.groupby(["issue_type","severity"]).size().reset_index(name="count") if len(exceptions) else pd.DataFrame(columns=["issue_type","severity","count"])
    def table(df): return df.to_html(index=False,escape=True,border=0,classes="data")
    content=f"""<!doctype html><html><head><meta charset="utf-8"><title>Payroll Validation Report</title>
<style>body{{font:16px system-ui;max-width:1100px;margin:32px auto;padding:0 20px;color:#202124}}h1,h2{{color:#172b4d}}.kpis{{display:flex;gap:14px;flex-wrap:wrap}}.kpi{{border:1px solid #ddd;border-radius:12px;padding:16px;min-width:140px}}.num{{font-size:28px;font-weight:700}}table{{border-collapse:collapse;width:100%;margin:14px 0}}th,td{{padding:8px;border-bottom:1px solid #ddd;text-align:left}}th{{background:#f3f5f7}}.note{{background:#fff8e1;padding:14px;border-radius:8px}}</style></head><body>
<h1>Payroll Validation & Reconciliation</h1><p>Seed: {summary['seed']} · Synthetic data only</p>
<div class="kpis"><div class="kpi">Employees<div class="num">{summary['employees_requested']:,}</div></div>
<div class="kpi">Payroll inputs<div class="num">{len(inputs):,}</div></div><div class="kpi">Exceptions<div class="num">{len(exceptions):,}</div></div>
<div class="kpi">Exported inputs<div class="num">{len(exports):,}</div></div><div class="kpi">Validation checks<div class="num">{checks['checks_passed']}/{checks['checks_total']}</div></div></div>
<h2>Exceptions by type and severity</h2>{table(status)}
<h2>Validation checks</h2>{table(pd.DataFrame(checks['checks']))}
<div class="note"><b>Scope:</b> this is a synthetic workflow demonstration. Salary, deduction, tax, and net pay calculations are simplified and must not be used for real payroll processing.</div>
</body></html>"""
    out.write_text(content)
    return str(out)
