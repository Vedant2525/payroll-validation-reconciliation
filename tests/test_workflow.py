import tempfile, unittest
from pathlib import Path
from src.generator import generate
from src.validator import validate
from src.database import build_database
from src.reporting import create_report

class PayrollWorkflowTests(unittest.TestCase):
    def test_starter_workflow_and_anomaly_gates(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/"data"
            summary=generate(out,employees_n=30,transactions_n=300,seed=20261022)
            self.assertEqual(summary["employees_requested"],30)
            result=validate(out)
            self.assertEqual(result["checks_passed"],result["checks_total"],result["checks"])
            self.assertGreater(result["exception_count"],0)
            self.assertGreater(result["export_count"],0)
            db=build_database(out,Path(td)/"payroll.db")
            self.assertEqual(db["foreign_key_violations"],0)
            report=create_report(out,Path(td)/"report.html")
            self.assertTrue(Path(report).exists())
    def test_reproducibility(self):
        with tempfile.TemporaryDirectory() as td:
            a=Path(td)/"a"; b=Path(td)/"b"
            generate(a,employees_n=20,transactions_n=150,seed=99)
            generate(b,employees_n=20,transactions_n=150,seed=99)
            self.assertEqual((a/"source_manifest.json").read_text(),(b/"source_manifest.json").read_text())
if __name__=="__main__": unittest.main()
