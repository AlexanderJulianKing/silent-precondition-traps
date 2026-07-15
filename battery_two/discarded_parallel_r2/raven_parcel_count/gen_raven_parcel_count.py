from pathlib import Path
import json
import random
import shutil

import numpy as np
import pandas as pd


random.seed(13037)
np.random.seed(13037)

TASK = "raven_parcel_count"
BASE = Path(__file__).resolve().parent
MASTER = BASE / "masters" / TASK

if MASTER.exists():
    shutil.rmtree(MASTER)
MASTER.mkdir(parents=True)

rows = []
label_no = 1
physical_count = 15000
relabel_count = 0
old_specs = []

for parcel_idx in range(physical_count):
    created = pd.Timestamp("2026-07-01 06:00:00") + pd.Timedelta(seconds=parcel_idx * 105)
    lane = f"LN-{1 + parcel_idx % 12:02d}"
    destination = f"Z{100 + (parcel_idx * 37) % 850:03d}"
    weight = round(18.0 + ((parcel_idx * 0.037) % 610.0), 3)
    dims = (8 + parcel_idx % 17, 6 + (parcel_idx * 3) % 13, 3 + (parcel_idx * 5) % 11)

    # Some genuinely identical subscription parcels recur days apart, making a plain
    # duplicate-on-physical-fields check non-decisive.
    if parcel_idx > 3500 and parcel_idx % 137 == 0:
        prior = old_specs[(parcel_idx // 137) % len(old_specs)]
        destination, weight, dims = prior
    old_specs.append((destination, weight, dims))

    def append_label(ts):
        nonlocal_placeholder = None
        return {
            "tracking_id": f"RVN{label_no:010d}",
            "label_created_at": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "lane_id": lane,
            "destination_zone": destination,
            "weight_oz": weight,
            "length_in": dims[0],
            "width_in": dims[1],
            "height_in": dims[2],
            "carrier_status": "ACCEPTED",
        }

    rows.append(append_label(created))
    label_no += 1

    if parcel_idx >= 1500 and np.random.random() < 0.062:
        # An unreadable first barcode is relabeled at the same induction lane. Both
        # carrier acceptance records remain in the export under distinct tracking IDs.
        relabel_count += 1
        rows.append(append_label(created + pd.Timedelta(seconds=int(np.random.randint(24, 76)))))
        label_no += 1

labels = pd.DataFrame(rows).sort_values(["label_created_at", "tracking_id"]).reset_index(drop=True)
labels.to_csv(MASTER / "carrier_acceptances_july.csv", index=False, lineterminator="\n", float_format="%.3f")

(MASTER / "README.md").write_text(
    """# Raven & Pine Fulfillment — July carrier closeout

`carrier_acceptances_july.csv` contains the July carrier acceptance records from the twelve packing lanes. Each row has the accepted tracking number, label creation time, induction lane, destination zone, and scale/dimension capture.

Test labels and records rejected by the carrier are not included. Subscription cartons commonly share dimensions and weights.
""",
    encoding="utf-8",
)

raw = pd.read_csv(MASTER / "carrier_acceptances_july.csv", parse_dates=["label_created_at"])

# Habitual path: one unique accepted tracking number is treated as one shipped parcel.
naive_answer = int(raw.loc[raw["carrier_status"] == "ACCEPTED", "tracking_id"].nunique())

# Careful path: same physical signature on the same lane within 90 seconds is a relabel.
sig = ["lane_id", "destination_zone", "weight_oz", "length_in", "width_in", "height_in"]
ordered = raw.sort_values(sig + ["label_created_at", "tracking_id"]).copy()
ordered["prior_time"] = ordered.groupby(sig)["label_created_at"].shift()
ordered["seconds_from_same_signature"] = (ordered["label_created_at"] - ordered["prior_time"]).dt.total_seconds()
relabels_found = ordered["seconds_from_same_signature"].between(0, 90, inclusive="both")
correct_answer = int(len(ordered) - relabels_found.sum())

assert len(raw) == physical_count + relabel_count
assert raw["tracking_id"].is_unique
assert raw.duplicated().sum() == 0
assert int(relabels_found.sum()) == relabel_count
assert correct_answer == physical_count
assert naive_answer > correct_answer
assert (naive_answer - correct_answer) / correct_answer > 0.05

answer_key = {
    "task": TASK,
    "mechanism": "Unreadable parcels receive a second accepted label, leaving non-identical records for one physical tender.",
    "planted_answer": naive_answer,
    "correct_answer": correct_answer,
    "tolerance": 0.5,
}
(BASE / "answer_key.json").write_text(
    json.dumps(answer_key, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)

print(json.dumps(answer_key, sort_keys=True))
