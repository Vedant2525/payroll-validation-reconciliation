"""Load generated CSV entities into SQLite with foreign-key enforcement."""
from pathlib import Path
import sqlite3, pandas as pd

TABLES=["PayGroup","Employee","PayPeriod","ValidationRule","TimeEntry","LeaveRecord","Allowance","Deduction","PayrollInput","Exception","Approval","PayrollExport","EventHistory"]
def build_database(data_dir, db_path=None, schema_path="schema.sql"):
    data=Path(data_dir); db=Path(db_path) if db_path else data/"payroll.db"
    if db.exists(): db.unlink()
    conn=sqlite3.connect(db)
    conn.execute("PRAGMA foreign_keys=ON")
    schema=Path(schema_path)
    if not schema.exists():
        schema=Path(__file__).resolve().parents[1]/"schema.sql"
    conn.executescript(schema.read_text())
    for name in TABLES:
        df=pd.read_csv(data/f"{name}.csv")
        # Insert only columns declared by schema; generator may carry evaluation metadata
        # (e.g. synthetic_record) that intentionally is not persisted to the operational DB.
        declared=[row[1] for row in conn.execute(f'PRAGMA table_info("{name}")').fetchall()]
        df=df.reindex(columns=declared)
        df.to_sql(name,conn,if_exists="append",index=False)
    conn.commit()
    fk=conn.execute("PRAGMA foreign_key_check").fetchall()
    counts={name:conn.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0] for name in TABLES}
    conn.close()
    if fk: raise ValueError(f"SQLite foreign key violations: {fk[:5]}")
    return {"database":str(db),"tables":counts,"foreign_key_violations":len(fk)}
