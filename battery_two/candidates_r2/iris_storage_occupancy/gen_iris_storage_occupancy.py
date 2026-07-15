from pathlib import Path
import json
import random
import shutil

import numpy as np
import pandas as pd


random.seed(67091)
np.random.seed(67091)

TASK = "iris_storage_occupancy"
BASE = Path(__file__).resolve().parent
MASTER = BASE / "masters" / TASK

if MASTER.exists():
    shutil.rmtree(MASTER)
MASTER.mkdir(parents=True)

sites = [f"IS-{i:02d}" for i in range(1, 13)]
pair_members = list(range(41, 65))  # 24 door controllers serving 12 double-door units.
pair_lookup = {member: 41 + 2 * ((member - 41) // 2) for member in pair_members}
rows = []
reading_no = 1

for site_idx, site in enumerate(sites):
    units = []
    for sensor_num in range(1, 121):
        if sensor_num in pair_members and sensor_num % 2 == 0:
            continue
        members = [sensor_num]
        if sensor_num in pair_members:
            members = [sensor_num, sensor_num + 1]

        # Produce persistent but non-identical monthly occupancy signatures. Rejection
        # prevents accidental all-month synchronization between unrelated units.
        while True:
            state = bool(np.random.random() < 0.72)
            signature = []
            for day in range(30):
                if day:
                    draw = np.random.random()
                    if state and draw < 0.08:
                        state = False
                    elif (not state) and draw < 0.20:
                        state = True
                signature.append(int(state))
            if tuple(signature) not in {u[1] for u in units}:
                break
        units.append((members, tuple(signature)))

    for members, signature in units:
        for sensor_num in members:
            for day, occupied in enumerate(signature, start=1):
                rows.append({
                    "reading_id": f"IOR-{reading_no:08d}",
                    "site_id": site,
                    "locker_controller": f"LC-{sensor_num:03d}",
                    "snapshot_date": f"2026-06-{day:02d}",
                    "occupied_flag": occupied,
                    "controller_bank": f"B{1 + (sensor_num - 1) // 12:02d}",
                    "health": "OK",
                })
                reading_no += 1

readings = pd.DataFrame(rows)
ordinary = readings[~readings["locker_controller"].isin([f"LC-{x:03d}" for x in pair_members])].sample(frac=1, random_state=67091)
ordinary_ids = set(ordinary.iloc[:160]["reading_id"])
middle = readings[~readings["reading_id"].isin(ordinary_ids)].sample(frac=1, random_state=67092)
readings = pd.concat([ordinary.iloc[:80], middle, ordinary.iloc[80:160]], ignore_index=True)
readings.to_csv(MASTER / "june_door_occupancy.csv", index=False, lineterminator="\n")

(MASTER / "README.md").write_text(
    """# Iris Self Storage — June occupancy archive

`june_door_occupancy.csv` contains the nightly occupied/unoccupied state returned by each locker-door controller at 12 facilities. Every controller/date key is complete and all devices reported `OK` health.

Controllers are numbered within site and grouped into installation banks for maintenance. Units held for facility use are outside the export.
""",
    encoding="utf-8",
)

raw = pd.read_csv(MASTER / "june_door_occupancy.csv")

# Habitual path: one healthy door controller is treated as one rental unit.
daily_sensor_count = raw.groupby(["site_id", "snapshot_date"])["occupied_flag"].sum()
naive_answer = round(float(daily_sensor_count.mean()), 1)

# Careful path: two door controllers on a double-door unit have identical 30-day state
# signatures; the unit contributes one occupied state, not two.
site_daily_unit_counts = []
duplicate_group_sizes = []
for site, group in raw.groupby("site_id"):
    pivot = group.pivot(index="locker_controller", columns="snapshot_date", values="occupied_flag")
    signature_groups = {}
    for controller, row in pivot.iterrows():
        signature_groups.setdefault(tuple(int(x) for x in row.to_list()), []).append(controller)
    duplicate_group_sizes.extend(len(v) for v in signature_groups.values() if len(v) > 1)
    representatives = [controllers[0] for controllers in signature_groups.values()]
    collapsed = pivot.loc[representatives]
    site_daily_unit_counts.extend(collapsed.sum(axis=0).to_list())
correct_answer = round(float(np.mean(site_daily_unit_counts)), 1)

assert len(raw) == len(sites) * 120 * 30
assert raw[["site_id", "locker_controller", "snapshot_date"]].duplicated().sum() == 0
assert duplicate_group_sizes == [2] * (len(sites) * 12)
assert naive_answer > correct_answer + 6.0
assert 65.0 < correct_answer < 90.0

answer_key = {
    "task": TASK,
    "mechanism": "Double-door rental units emit two perfectly synchronized controller histories and are counted twice as lockers.",
    "planted_answer": naive_answer,
    "correct_answer": correct_answer,
    "tolerance": 0.05,
}
(BASE / "answer_key.json").write_text(json.dumps(answer_key, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(answer_key, sort_keys=True))
