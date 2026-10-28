"""Command-line interface."""
import argparse, json
from .generator import generate
from .validator import validate
from .database import build_database
from .reporting import create_report

def main():
    p=argparse.ArgumentParser(description="Synthetic payroll validation workflow")
    sub=p.add_subparsers(dest="command",required=True)
    g=sub.add_parser("generate"); g.add_argument("--out",default="output"); g.add_argument("--employees",type=int,default=3000); g.add_argument("--transactions",type=int,default=100000); g.add_argument("--seed",type=int,default=20261022)
    v=sub.add_parser("validate"); v.add_argument("--data",default="output")
    db=sub.add_parser("database"); db.add_argument("--data",default="output"); db.add_argument("--db",default=None)
    rp=sub.add_parser("report"); rp.add_argument("--data",default="output"); rp.add_argument("--out",default=None)
    args=p.parse_args()
    if args.command=="generate": result=generate(args.out,args.employees,args.transactions,args.seed)
    elif args.command=="validate": result=validate(args.data)
    elif args.command=="database": result=build_database(args.data,args.db)
    else: result={"report":create_report(args.data,args.out)}
    print(json.dumps(result,indent=2))
    if args.command=="validate" and result["checks_passed"] != result["checks_total"]:
        raise SystemExit(2)
if __name__=="__main__": main()
