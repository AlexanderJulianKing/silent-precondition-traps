#!/usr/bin/env python3
import json
import random
import shutil
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

random.seed(31002)
np.random.seed(31002)

TASK = "birch_rush_weight"
ROOT = Path(__file__).resolve().parent
MASTER = ROOT / "masters" / TASK
SERVICES = ("STANDARD", "RUSH", "OVERNIGHT")
CHARGE_FACTORS = {"STANDARD": 1.05, "RUSH": 1.65, "OVERNIGHT": 2.40}


def infer_service(frame):
    basis = frame["measured_kg"] + 0.8 * frame["destination_zone"]
    observed_index = frame["carrier_charge"] / basis
    centers = {
        service: float(observed_index[frame["service"] == service].median())
        for service in SERVICES
    }
    center_names = list(centers)
    center_values = np.array([centers[name] for name in center_names])
    nearest = np.abs(observed_index.to_numpy()[:, None] - center_values[None, :]).argmin(axis=1)
    return pd.Series([center_names[idx] for idx in nearest], index=frame.index)


def main():
    if MASTER.exists():
        shutil.rmtree(MASTER)
    MASTER.mkdir(parents=True)

    rows = []
    parcel_no = 1
    affected_lanes = {"L04", "L09", "L13", "L17"}
    service_probs = [0.66, 0.24, 0.10]

    for day in range(1, 32):
        date = datetime(2026, 10, day)
        for lane_num in range(1, 19):
            lane = f"L{lane_num:02d}"
            count = 29 + ((day * 7 + lane_num * 3) % 5)
            actual_services = list(np.random.choice(SERVICES, size=count, p=service_probs))
            lagged = lane in affected_lanes and day >= 8
            recorded_services = actual_services.copy()
            if lagged:
                for idx in range(1, count):
                    recorded_services[idx] = actual_services[idx - 1]

            minute_cursor = 7 * 60 + lane_num
            for seq_idx, (actual, recorded) in enumerate(zip(actual_services, recorded_services), start=1):
                if actual == "STANDARD":
                    weight = np.random.gamma(3.0, 2.0) + 2.2
                elif actual == "RUSH":
                    weight = np.random.gamma(2.0, 1.25) + 0.45
                else:
                    weight = np.random.gamma(2.4, 1.45) + 0.75
                weight = round(float(min(weight, 24.0)), 2)
                zone = int(np.random.randint(2, 9))
                carrier_charge = round(CHARGE_FACTORS[actual] * (weight + 0.8 * zone), 2)
                minute_cursor += int(np.random.randint(5, 14))
                packed_at = date + timedelta(minutes=minute_cursor, seconds=int(np.random.randint(0, 60)))
                rows.append(
                    {
                        "parcel_id": f"BP-{parcel_no:08d}",
                        "packed_at": packed_at.strftime("%Y-%m-%d %H:%M:%S"),
                        "lane_id": lane,
                        "lane_seq": seq_idx,
                        "destination_zone": zone,
                        "measured_kg": weight,
                        "service": recorded,
                        "carrier_charge": carrier_charge,
                        "carrier_status": "ACCEPTED",
                        "_actual_service": actual,
                    }
                )
                parcel_no += 1

    full = pd.DataFrame(rows).sort_values(["packed_at", "lane_id", "lane_seq"]).reset_index(drop=True)
    export = full.drop(columns="_actual_service")
    export.to_csv(MASTER / "october_carrier_closeout.csv", index=False, lineterminator="\n")

    (MASTER / "README.md").write_text(
        "# Birch Outfitters — October parcel closeout\n\n"
        "`october_carrier_closeout.csv` contains one accepted carrier closeout per parcel "
        "packed during October. `measured_kg` is the stabilized packing-lane scale reading, "
        "and `service` is the service value carried on the closeout row. Lane sequence and "
        "the carrier charge are retained for invoice support.\n\n"
        "Rejected labels, test parcels, and warehouse transfers are excluded.\n",
        encoding="utf-8",
    )

    naive = round(float(export.loc[export["service"] == "RUSH", "measured_kg"].sum()), 1)
    inferred = infer_service(export)
    assert (inferred.to_numpy() == full["_actual_service"].to_numpy()).all()
    careful = round(float(export.loc[inferred == "RUSH", "measured_kg"].sum()), 1)

    assert naive != careful
    assert abs(naive - careful) > careful * 0.06
    assert len(export) > 16000
    assert export["parcel_id"].is_unique

    key = {
        "task": TASK,
        "mechanism": "On several lanes the service field is attached one parcel late, while weight and carrier charge remain on the correct row.",
        "planted_answer": naive,
        "correct_answer": careful,
        "tolerance": 0.05,
    }
    (ROOT / "answer_key.json").write_text(json.dumps(key, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(key, sort_keys=True))


if __name__ == "__main__":
    main()
