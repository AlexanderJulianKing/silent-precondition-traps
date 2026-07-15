from pathlib import Path
import json
import random
import shutil

import numpy as np
import pandas as pd


random.seed(4417)
np.random.seed(4417)

TASK = "willow_pack_revenue"
BASE = Path(__file__).resolve().parent
MASTER = BASE / "masters" / TASK

if MASTER.exists():
    shutil.rmtree(MASTER)
MASTER.mkdir(parents=True)

shops = ["Ashland", "Bend", "Corvallis", "Eugene"]
invoice_rows = []
invoice_no = 1

for day in pd.date_range("2025-12-20", "2026-02-10", freq="D"):
    dow_factor = 1.18 if day.dayofweek in (4, 5) else 0.94
    season_factor = 1.14 if day.month == 12 else (0.98 if day.month == 1 else 0.91)
    daily_n = int(np.random.poisson(205 * dow_factor))
    for j in range(daily_n):
        amount = round(float(np.clip(np.random.lognormal(4.12, 0.62) * season_factor, 14, 580)), 2)
        status = "VOID" if np.random.random() < 0.028 else "POSTED"
        invoice_rows.append({
            "invoice_id": f"WSH-{invoice_no:07d}",
            "invoice_date": day.strftime("%Y-%m-%d"),
            "shop": shops[(invoice_no + j) % len(shops)],
            "status": status,
            "net_revenue": amount,
            "tender": random.choice(["card", "cash", "financing"]),
        })
        invoice_no += 1

invoices = pd.DataFrame(invoice_rows)
invoices.to_csv(MASTER / "invoice_export.csv", index=False, lineterminator="\n", float_format="%.2f")

close_control = pd.DataFrame([
    {"pack_label": "December 2025", "period_open": "2025-12-01", "period_close": "2026-01-04", "controller_signoff": "2026-01-07"},
    {"pack_label": "January 2026", "period_open": "2026-01-05", "period_close": "2026-02-01", "controller_signoff": "2026-02-04"},
    {"pack_label": "February 2026", "period_open": "2026-02-02", "period_close": "2026-03-01", "controller_signoff": "2026-03-04"},
])
close_control.to_csv(MASTER / "controller_close_control.csv", index=False, lineterminator="\n")

(MASTER / "README.md").write_text(
    """# Willow & Grain Home — finance export

This directory holds the invoice detail used for the winter owner operating packs and the controller's close-control extract.

- `invoice_export.csv`: posted and void retail invoices from all four Oregon shops. `net_revenue` is after discounts and returns.
- `controller_close_control.csv`: pack labels, covered trading dates, and sign-off dates retained with the monthly close archive.

Owner packs use the controller's merchandising-month labels. The invoice extract includes surrounding dates so adjacent packs can be reconciled.
""",
    encoding="utf-8",
)

tx = pd.read_csv(MASTER / "invoice_export.csv", parse_dates=["invoice_date"])
posted = tx[tx["status"] == "POSTED"]

# Habitual path: “January” is treated as the calendar month.
naive_mask = (posted["invoice_date"] >= "2026-01-01") & (posted["invoice_date"] < "2026-02-01")
naive_answer = round(float(posted.loc[naive_mask, "net_revenue"].sum()), 2)

# Careful path: use the controller's date coverage for the labeled operating pack.
control = pd.read_csv(MASTER / "controller_close_control.csv")
jan = control.loc[control["pack_label"] == "January 2026"].iloc[0]
correct_mask = (posted["invoice_date"] >= jan["period_open"]) & (posted["invoice_date"] <= jan["period_close"])
correct_answer = round(float(posted.loc[correct_mask, "net_revenue"].sum()), 2)

assert len(tx) >= 10000
assert naive_answer > correct_answer
assert abs(naive_answer - correct_answer) / correct_answer > 0.05
assert 350_000 <= correct_answer <= 600_000

answer_key = {
    "task": TASK,
    "mechanism": "A month-labeled owner pack follows controller close dates rather than calendar-month dates.",
    "planted_answer": naive_answer,
    "correct_answer": correct_answer,
    "tolerance": 0.005,
}
(BASE / "answer_key.json").write_text(
    json.dumps(answer_key, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)

print(json.dumps(answer_key, sort_keys=True))
