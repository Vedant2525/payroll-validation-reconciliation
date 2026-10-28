"""Optional Streamlit dashboard for generated payroll validation outputs."""
from pathlib import Path
import json
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Payroll Validation",layout="wide")
st.title("Payroll Validation & Reconciliation")
st.caption("Synthetic demonstration dataset — not for production payroll calculations.")
data_dir=st.sidebar.text_input("Dataset folder","output")
d=Path(data_dir)
if not (d/"PayrollInput.csv").exists():
    st.info("Generate a dataset first: `python -m src.cli generate --out output --employees 100 --transactions 3000`")
    st.stop()
pins=pd.read_csv(d/"PayrollInput.csv")
exc=pd.read_csv(d/"Exception.csv")
exports=pd.read_csv(d/"PayrollExport.csv")
gt=pd.read_csv(d/"ground_truth.csv")
a,b,c,e=st.columns(4)
a.metric("Payroll inputs",f"{len(pins):,}")
b.metric("Exceptions",f"{len(exc):,}")
c.metric("Exported",f"{len(exports):,}")
e.metric("Export rate",f"{len(exports)/max(1,len(pins)):.1%}")
st.subheader("Payroll input status")
st.bar_chart(pins["validation_status"].value_counts())
st.subheader("Exceptions")
if len(exc):
    counts=exc.groupby(["issue_type","severity"]).size().reset_index(name="count")
    st.dataframe(counts,use_container_width=True,hide_index=True)
    options=["All"]+sorted(exc.issue_type.astype(str).unique().tolist())
    choice=st.selectbox("Filter exception type",options)
    view=exc if choice=="All" else exc[exc.issue_type==choice]
    st.dataframe(view,use_container_width=True,hide_index=True)
else:
    st.success("No exceptions.")
st.subheader("Export gate")
blocked=pins[~pins["payroll_input_id"].isin(exports["payroll_input_id"])]
st.write(f"{len(blocked):,} payroll inputs are not exported.")
st.dataframe(blocked[["payroll_input_id","employee_id","pay_period_id","validation_status","reconciliation_status","approval_status"]].head(100),use_container_width=True,hide_index=True)
st.subheader("Ground-truth evaluation cases (evaluation only)")
st.dataframe(gt,use_container_width=True,hide_index=True)
