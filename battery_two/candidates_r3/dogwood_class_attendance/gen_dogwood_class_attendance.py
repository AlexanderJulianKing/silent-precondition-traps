#!/usr/bin/env python3
import json
import random
import shutil
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

random.seed(31004)
np.random.seed(31004)

TASK = "dogwood_class_attendance"
ROOT = Path(__file__).resolve().parent
MASTER = ROOT / "masters" / TASK


def infer_series_leaders(frame):
    leaders = set()
    for series, group in frame.groupby("class_series"):
        instance_count = group["class_instance"].nunique()
        appearances = group.groupby("badge_token")["class_instance"].nunique()
        candidates = appearances[appearances == instance_count].index.tolist()
        assert len(candidates) == 1, (series, candidates)
        leaders.add(candidates[0])
    return leaders


def main():
    if MASTER.exists():
        shutil.rmtree(MASTER)
    MASTER.mkdir(parents=True)

    disciplines = ["FLOW", "STRENGTH", "PILATES", "MOBILITY", "CYCLE", "BARRE"]
    slots = [(7, 0), (9, 0), (12, 0), (15, 30), (17, 30), (19, 0)]
    instructor_numbers = set(np.random.choice(np.arange(1, 8001), size=150, replace=False).tolist())
    instructor_badges = [f"DB-{i:06d}" for i in sorted(instructor_numbers)]
    customer_badges = [f"DB-{i:06d}" for i in range(1, 8001) if i not in instructor_numbers]
    series_instructor = {}
    rows = []
    admission_no = 1
    instance_no = 1

    for studio_idx in range(1, 9):
        studio = f"DS-{studio_idx:02d}"
        for day in range(1, 32):
            date = datetime(2026, 12, day)
            weekday = date.weekday()
            for slot_idx, (hour, minute) in enumerate(slots):
                discipline = disciplines[(studio_idx * 2 + weekday + slot_idx) % len(disciplines)]
                series = f"{studio}-W{weekday + 1}-{hour:02d}{minute:02d}-{discipline}"
                if series not in series_instructor:
                    # Instructors teach several recurring series, producing plausible heavy users.
                    series_instructor[series] = instructor_badges[(studio_idx * 17 + weekday * 7 + slot_idx * 3) % len(instructor_badges)]
                instructor = series_instructor[series]
                instance = f"CL-{instance_no:06d}"
                starts_at = date.replace(hour=hour, minute=minute)

                class_rows = []
                instructor_offset = -int(np.random.randint(8, 13))
                class_rows.append((instructor, instructor_offset, "APP"))

                customer_count = int(np.clip(np.random.poisson(10.2), 4, 18))
                customers = list(np.random.choice(customer_badges, size=customer_count, replace=False))
                for badge in customers:
                    if np.random.random() < 0.035:
                        offset = -int(np.random.randint(13, 18))
                    else:
                        offset = int(np.random.randint(-7, 6))
                    booked = str(np.random.choice(["APP", "WEB", "FRONT_DESK"], p=[0.68, 0.23, 0.09]))
                    class_rows.append((badge, offset, booked))

                for badge, offset, booked in class_rows:
                    scan_time = starts_at + timedelta(minutes=offset, seconds=int(np.random.randint(0, 60)))
                    rows.append(
                        {
                            "admission_id": f"DA-{admission_no:08d}",
                            "scanned_at": scan_time.strftime("%Y-%m-%d %H:%M:%S"),
                            "studio_id": studio,
                            "class_instance": instance,
                            "class_series": series,
                            "discipline": discipline,
                            "badge_token": badge,
                            "booked_via": booked,
                            "gate_result": "ADMITTED",
                            "_instructor_scan": badge == instructor,
                        }
                    )
                    admission_no += 1
                instance_no += 1

    full = pd.DataFrame(rows).sort_values(["scanned_at", "studio_id", "class_instance"]).reset_index(drop=True)
    export = full.drop(columns="_instructor_scan")
    export.to_csv(MASTER / "december_class_admissions.csv", index=False, lineterminator="\n")

    (MASTER / "README.md").write_text(
        "# Dogwood Movement — December admissions\n\n"
        "`december_class_admissions.csv` contains the admitted badge scans written by the "
        "front gate for scheduled classes at eight studios. Class instance is unique to a "
        "scheduled meeting; class series links meetings that recur in the same weekly slot. "
        "Badge tokens and booking source are retained for capacity planning.\n\n"
        "Denied scans, open-gym visits, cancelled classes, and door tests are excluded.\n",
        encoding="utf-8",
    )

    leaders = infer_series_leaders(export)
    inferred_instructor = export["badge_token"].isin(leaders)
    assert np.array_equal(inferred_instructor.to_numpy(), full["_instructor_scan"].to_numpy(bool))
    naive = int(len(export))
    careful = int((~inferred_instructor).sum())

    assert export["admission_id"].is_unique
    assert naive > careful * 1.08
    assert len(export) > 15000

    key = {
        "task": TASK,
        "mechanism": "The admission gate records the instructor's ordinary badge alongside customers for every recurring class meeting.",
        "planted_answer": naive,
        "correct_answer": careful,
        "tolerance": 0.5,
    }
    (ROOT / "answer_key.json").write_text(json.dumps(key, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(key, sort_keys=True))


if __name__ == "__main__":
    main()
