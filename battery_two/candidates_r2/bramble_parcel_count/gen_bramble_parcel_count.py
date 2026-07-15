from pathlib import Path
import json
import random
import shutil

import numpy as np
import pandas as pd


random.seed(23041)
np.random.seed(23041)

TASK = "bramble_parcel_count"
BASE = Path(__file__).resolve().parent
MASTER = BASE / "masters" / TASK

if MASTER.exists():
    shutil.rmtree(MASTER)
MASTER.mkdir(parents=True)

physical_count = 17000
relabel_pool = np.array([i for i in range(3501, physical_count + 1) if 1 + ((i * 13) % 31) >= 11])
relabel_ids = set(int(x) for x in np.random.choice(relabel_pool, 950, replace=False))
collision_ids = set(int(x) for x in np.random.choice(np.arange(2001, physical_count + 1), 90, replace=False))
rows = []
row_no = 1

for package_id in range(1, physical_count + 1):
    day = 1 + ((package_id * 13) % 31)
    accepted = pd.Timestamp(2026, 7, day, 7 + package_id % 12, (package_id * 19) % 60, package_id % 47)
    destination = f"Z{1000 + (package_id * 37) % 5200:04d}"
    weight = round(float(np.clip(np.random.lognormal(1.25, 0.48), 0.4, 18.0)), 2)
    length = int(np.random.choice([24, 28, 32, 36, 42, 48]))
    width = int(np.random.choice([18, 22, 26, 30, 34]))
    height = int(np.random.choice([8, 12, 16, 20, 24]))
    scale_sample = 100000 + ((package_id * 7919) % 900000)
    if package_id in collision_ids:
        scale_sample = 100000 + (((package_id - 137) * 7919) % 900000)

    copies = 2 if package_id in relabel_ids else 1
    for copy in range(copies):
        scan_time = accepted + pd.Timedelta(seconds=copy * int(25 + package_id % 51))
        rows.append({
            "manifest_row": f"MR-{row_no:07d}",
            "tracking_number": f"BPC{8800000000 + row_no}",
            "accepted_at": scan_time.strftime("%Y-%m-%d %H:%M:%S"),
            "lane": f"L{1 + package_id % 14:02d}",
            "destination_hash": destination,
            "weight_kg": weight,
            "length_cm": length,
            "width_cm": width,
            "height_cm": height,
            "scale_sample": scale_sample,
            "service": ["GROUND", "TWO_DAY", "ECONOMY"][package_id % 3],
            "carrier_response": "ACCEPTED",
        })
        row_no += 1

scans = pd.DataFrame(rows).sort_values(["accepted_at", "manifest_row"]).reset_index(drop=True)
scans.to_csv(MASTER / "july_carrier_acceptances.csv", index=False, lineterminator="\n", float_format="%.2f")

(MASTER / "README.md").write_text(
    """# Bramble Box & Paper — July carrier handoff

`july_carrier_acceptances.csv` is the shipping-lane closeout received from the carrier gateway. Each row has a unique tracking number and an `ACCEPTED` carrier response. Dimensions and the short load-cell sample are retained for packing-line diagnostics.

Rejected labels, test scans, and warehouse transfers are not present.
""",
    encoding="utf-8",
)

raw = pd.read_csv(MASTER / "july_carrier_acceptances.csv")
naive_answer = int((raw["carrier_response"] == "ACCEPTED").sum())

# A reprinted/reissued label repeats the physical scan fingerprint even though every
# manifest row and tracking number is unique.
fingerprint = ["destination_hash", "weight_kg", "length_cm", "width_cm", "height_cm", "scale_sample"]
correct_answer = int(raw.loc[raw["carrier_response"] == "ACCEPTED"].drop_duplicates(fingerprint).shape[0])

assert len(raw) == physical_count + len(relabel_ids)
assert raw["tracking_number"].is_unique and raw["manifest_row"].is_unique
assert correct_answer == physical_count
assert naive_answer > correct_answer
assert 0.05 < (naive_answer - correct_answer) / correct_answer < 0.07

answer_key = {
    "task": TASK,
    "mechanism": "Carrier-accepted replacement labels create unique records for the same physically scanned parcel.",
    "planted_answer": naive_answer,
    "correct_answer": correct_answer,
    "tolerance": 0.5,
}
(BASE / "answer_key.json").write_text(json.dumps(answer_key, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(answer_key, sort_keys=True))
