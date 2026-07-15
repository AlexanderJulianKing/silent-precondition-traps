from pathlib import Path
import json
import random
import shutil

import numpy as np
import pandas as pd


random.seed(89119)
np.random.seed(89119)

TASK = "linden_field_hours"
BASE = Path(__file__).resolve().parent
MASTER = BASE / "masters" / TASK

if MASTER.exists():
    shutil.rmtree(MASTER)
MASTER.mkdir(parents=True)

rows = []
activity_no = 1
technicians = [f"LT-{i:03d}" for i in range(1, 91)]

for tech_idx, tech in enumerate(technicians):
    for day in range(1, 31):
        for visit in range(3):
            start = pd.Timestamp(2026, 11, day, 7 + visit * 4, (tech_idx * 7 + day) % 35)
            duration = int(np.random.randint(62, 132))
            end = start + pd.Timedelta(minutes=duration)
            job = f"JOB-{day:02d}-{tech_idx + 1:03d}-{visit + 1}"
            rows.append({
                "activity_id": f"ACT-{activity_no:07d}",
                "job_id": job,
                "technician_id": tech,
                "activity_code": "CUSTOMER_VISIT",
                "started_at": start.strftime("%Y-%m-%d %H:%M:%S"),
                "ended_at": end.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "COMPLETE",
            })
            activity_no += 1

            if np.random.random() < 0.34:
                nested_start = start + pd.Timedelta(minutes=int(np.random.randint(8, 31)))
                max_nested = max(12, int((end - nested_start).total_seconds() / 60) - 4)
                nested_duration = int(np.random.randint(12, min(48, max_nested) + 1))
                nested_end = nested_start + pd.Timedelta(minutes=nested_duration)
                rows.append({
                    "activity_id": f"ACT-{activity_no:07d}",
                    "job_id": job,
                    "technician_id": tech,
                    "activity_code": ["DIAGNOSTIC", "PARTS_LOOKUP", "CUSTOMER_NOTES"][(tech_idx + day + visit) % 3],
                    "started_at": nested_start.strftime("%Y-%m-%d %H:%M:%S"),
                    "ended_at": nested_end.strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "COMPLETE",
                })
                activity_no += 1

activities = pd.DataFrame(rows).sample(frac=1, random_state=89119).reset_index(drop=True)
activities.to_csv(MASTER / "november_mobile_timers.csv", index=False, lineterminator="\n")

(MASTER / "README.md").write_text(
    """# Linden Appliance Repair — November field timers

`november_mobile_timers.csv` contains completed mobile activity timers for customer jobs. Technicians may use several activity codes during a job; each timer has its own activity identifier. Travel to the first job and home from the last job is excluded.

All timestamps are local and November had no daylight-saving transition in the covered operating region.
""",
    encoding="utf-8",
)

raw = pd.read_csv(MASTER / "november_mobile_timers.csv", parse_dates=["started_at", "ended_at"])
complete = raw[raw["status"] == "COMPLETE"].copy()
complete["hours"] = (complete["ended_at"] - complete["started_at"]).dt.total_seconds() / 3600.0
naive_answer = round(float(complete["hours"].sum()), 1)

# Some technicians start a task timer without stopping the enclosing customer-visit
# timer. Physical technician-hours are the union of intervals, not timer-hours.
union_seconds = 0.0
for _, group in complete.sort_values(["technician_id", "started_at", "ended_at"]).groupby("technician_id"):
    current_start = None
    current_end = None
    for row in group.itertuples(index=False):
        if current_start is None:
            current_start, current_end = row.started_at, row.ended_at
        elif row.started_at <= current_end:
            current_end = max(current_end, row.ended_at)
        else:
            union_seconds += (current_end - current_start).total_seconds()
            current_start, current_end = row.started_at, row.ended_at
    union_seconds += (current_end - current_start).total_seconds()
correct_answer = round(union_seconds / 3600.0, 1)

assert len(raw) >= 10000
assert raw["activity_id"].is_unique
assert naive_answer > correct_answer
assert 0.08 < (naive_answer - correct_answer) / correct_answer < 0.16
assert 8000 < correct_answer < 15000

answer_key = {
    "task": TASK,
    "mechanism": "Nested mobile task timers overlap an enclosing visit timer for the same technician.",
    "planted_answer": naive_answer,
    "correct_answer": correct_answer,
    "tolerance": 0.05,
}
(BASE / "answer_key.json").write_text(json.dumps(answer_key, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(answer_key, sort_keys=True))
