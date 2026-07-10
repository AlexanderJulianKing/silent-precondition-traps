import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import pandas as pd
from ingest import load_month
from fx import to_usd

def month_total(csv_path):
    df = load_month(csv_path)
    usd = df.apply(lambda r: to_usd(r["amount"], r["currency"], r["order_date"]), axis=1)
    return float(usd.sum())

if __name__ == "__main__":
    for m in ["2026-05", "2026-06"]:
        p = pathlib.Path(__file__).parent.parent / "data" / f"sales_{m}.csv"
        print(m, f"{month_total(p):,.2f}")
