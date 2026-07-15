from pathlib import Path
import json
import random
import shutil

import numpy as np
import pandas as pd


random.seed(1107)
np.random.seed(1107)

TASK = "juniper_labor_rate"
BASE = Path(__file__).resolve().parent
MASTER = BASE / "masters" / TASK

if MASTER.exists():
    shutil.rmtree(MASTER)
MASTER.mkdir(parents=True)

sites = ["Ballard", "Fremont", "Greenwood", "Magnolia", "QueenAnne"]
dates = pd.date_range("2026-06-01", "2026-06-30", freq="D")
durations = np.array(["6.00", "6.15", "6.30", "6.45", "7.00", "7.15", "7.30",
                      "7.45", "8.00", "8.15", "8.30", "8.45", "9.00"])
duration_p = np.array([.02, .02, .05, .09, .04, .03, .10, .13, .06, .04, .13, .19, .10])

timecard_rows = []
order_rows = []
shift_no = 1
order_no = 1

for day in dates:
    for site_idx, site in enumerate(sites):
        day_hours = 0.0
        for worker in range(12):
            shown = str(np.random.choice(durations, p=duration_p))
            whole, minutes = shown.split(".")
            day_hours += int(whole) + int(minutes) / 60.0
            timecard_rows.append({
                "timecard_id": f"TC{shift_no:06d}",
                "work_date": day.strftime("%Y-%m-%d"),
                "kitchen": site,
                "employee_id": f"E{site_idx + 1}{worker + 1:03d}",
                "paid_duration": shown,
                "approval_status": "APPROVED",
            })
            shift_no += 1

        fulfilled = int(np.random.poisson(day_hours * (2.36 + site_idx * 0.035)))
        cancelled = int(np.random.binomial(max(fulfilled, 1), 0.025))
        for status, count in (("FULFILLED", fulfilled), ("CANCELLED", cancelled)):
            for _ in range(count):
                order_rows.append({
                    "order_id": f"JMK{order_no:07d}",
                    "order_date": day.strftime("%Y-%m-%d"),
                    "kitchen": site,
                    "status": status,
                    "channel": random.choice(["web", "app", "phone"]),
                })
                order_no += 1

timecards = pd.DataFrame(timecard_rows)
orders = pd.DataFrame(order_rows)

timecards.to_csv(MASTER / "timecards_june.csv", index=False, lineterminator="\n")
orders.to_csv(MASTER / "orders_june.csv", index=False, lineterminator="\n")

(MASTER / "README.md").write_text(
    """# Juniper Street Kitchens — June operating export

This folder contains the owner dashboard inputs for the five Seattle kitchens.

- `orders_june.csv`: one row per submitted order. `status` identifies orders that were fulfilled or cancelled.
- `timecards_june.csv`: approved payroll timecards. `paid_duration` is the duration shown in the payroll export, and includes paid breaks.

Dates are local Seattle operating dates. Test orders have already been removed.
""",
    encoding="utf-8",
)

raw_cards = pd.read_csv(MASTER / "timecards_june.csv")
raw_orders = pd.read_csv(MASTER / "orders_june.csv")
fulfilled_count = int((raw_orders["status"] == "FULFILLED").sum())

# Habitual path: pandas infers the display as a decimal number and it is summed directly.
naive_hours = float(raw_cards["paid_duration"].sum())
naive_answer = round(fulfilled_count / naive_hours, 2)

# Careful path: the payroll display is H.MM, with the suffix denoting clock minutes.
shown = raw_cards["paid_duration"].map(lambda x: f"{x:.2f}")
correct_hours = sum(int(x.split(".")[0]) + int(x.split(".")[1]) / 60.0 for x in shown)
correct_answer = round(fulfilled_count / correct_hours, 2)

assert len(raw_cards) == 1800
assert 30000 <= fulfilled_count <= 40000
assert naive_answer != correct_answer
assert naive_answer > correct_answer
assert (naive_answer - correct_answer) / correct_answer > 0.02

answer_key = {
    "task": TASK,
    "mechanism": "Payroll durations that look decimal are actually H.MM clock-duration displays.",
    "planted_answer": naive_answer,
    "correct_answer": correct_answer,
    "tolerance": 0.005,
}
(BASE / "answer_key.json").write_text(
    json.dumps(answer_key, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)

print(json.dumps(answer_key, sort_keys=True))
