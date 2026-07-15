#!/usr/bin/env python3
import json
import random
import shutil
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

random.seed(31008)
np.random.seed(31008)

TASK = "palisade_spray_acres"
ROOT = Path(__file__).resolve().parent
MASTER = ROOT / "masters" / TASK
SQFT_PER_ACRE = 43560.0


def rectangle_union_area(rectangles):
    xs = sorted({x for rect in rectangles for x in (rect[0], rect[1])})
    area = 0.0
    for left, right in zip(xs, xs[1:]):
        if right <= left:
            continue
        mid = (left + right) / 2
        intervals = sorted((y0, y1) for x0, x1, y0, y1 in rectangles if x0 <= mid < x1)
        covered = 0.0
        if intervals:
            cur_start, cur_end = intervals[0]
            for start, end in intervals[1:]:
                if start <= cur_end:
                    cur_end = max(cur_end, end)
                else:
                    covered += cur_end - cur_start
                    cur_start, cur_end = start, end
            covered += cur_end - cur_start
        area += (right - left) * covered
    return area


def main():
    if MASTER.exists():
        shutil.rmtree(MASTER)
    MASTER.mkdir(parents=True)

    rows = []
    pass_no = 1
    true_rectangles = {}
    for field_idx in range(1, 261):
        field = f"PF-{field_idx:04d}"
        width = int(np.random.randint(720, 1321))
        length = int(np.random.randint(850, 2101))
        origin_x = int(np.random.randint(5000, 90000))
        origin_y = int(np.random.randint(5000, 90000))
        boom_width = int(np.random.choice([48, 54, 60]))
        overlap = int(np.random.choice([2, 3, 4]))
        field_application = str(
            np.random.choice(["FUNGICIDE", "HERBICIDE", "NUTRIENT"], p=[0.38, 0.42, 0.20])
        )
        step = boom_width - overlap
        x = 0
        pass_idx = 0
        rectangles = []
        while x < width:
            local_right = min(x + boom_width, width)
            x0, x1 = origin_x + x, origin_x + local_right
            y0, y1 = origin_y, origin_y + length
            rectangles.append((x0, x1, y0, y1))
            date = datetime(2026, 8, 1) + timedelta(
                days=(field_idx * 13 + pass_idx * 3) % 31,
                minutes=6 * 60 + (field_idx * 19 + pass_idx * 11) % 720,
            )
            acres = (x1 - x0) * (y1 - y0) / SQFT_PER_ACRE
            rows.append(
                {
                    "pass_id": f"SP-{pass_no:08d}",
                    "completed_at": date.strftime("%Y-%m-%d %H:%M:%S"),
                    "field_id": field,
                    "rig_id": f"RG-{1 + field_idx % 14:02d}",
                    "west_ft": x0,
                    "east_ft": x1,
                    "south_ft": y0,
                    "north_ft": y1,
                    "controller_acres": round(acres, 4),
                    "application": field_application,
                    "status": "COMPLETE",
                }
            )
            pass_no += 1
            pass_idx += 1
            x += step
        true_rectangles[field] = rectangles

    frame = pd.DataFrame(rows).sort_values(["completed_at", "field_id", "pass_id"]).reset_index(drop=True)
    frame.to_csv(MASTER / "august_completed_passes.csv", index=False, lineterminator="\n")

    (MASTER / "README.md").write_text(
        "# Palisade Crop Care — August application archive\n\n"
        "`august_completed_passes.csv` contains each completed sprayer-pass close for crop "
        "protection work performed in August. `controller_acres` is the boom controller's "
        "closed-pass area. The local GPS envelope is retained for agronomy review and the "
        "coordinates use feet within each farm's survey grid.\n\n"
        "Cancelled passes, road travel, tank calibration, and non-crop perimeter work are "
        "outside the archive.\n",
        encoding="utf-8",
    )

    naive = round(float(frame["controller_acres"].sum()), 1)
    union_sqft = 0.0
    for field, group in frame.groupby("field_id"):
        rects = list(group[["west_ft", "east_ft", "south_ft", "north_ft"]].itertuples(index=False, name=None))
        inferred_area = rectangle_union_area(rects)
        expected_area = rectangle_union_area(true_rectangles[field])
        assert inferred_area == expected_area
        union_sqft += inferred_area
    careful = round(union_sqft / SQFT_PER_ACRE, 1)

    assert frame["pass_id"].is_unique
    assert len(frame) > 4500
    assert naive > careful * 1.045

    key = {
        "task": TASK,
        "mechanism": "Boom controllers close each pass independently, so deliberate edge overlap is counted twice even though the land was covered once.",
        "planted_answer": naive,
        "correct_answer": careful,
        "tolerance": 0.05,
    }
    (ROOT / "answer_key.json").write_text(json.dumps(key, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(key, sort_keys=True))


if __name__ == "__main__":
    main()
