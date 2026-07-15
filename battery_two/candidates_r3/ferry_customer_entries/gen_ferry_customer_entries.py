#!/usr/bin/env python3
import json
import random
import shutil
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

random.seed(31005)
np.random.seed(31005)

TASK = "ferry_customer_entries"
ROOT = Path(__file__).resolve().parent
MASTER = ROOT / "masters" / TASK


def main():
    if MASTER.exists():
        shutil.rmtree(MASTER)
    MASTER.mkdir(parents=True)

    rows = []
    reading_no = 1
    true_entries = []
    hours = list(range(7, 21))

    for venue_idx in range(1, 15):
        venue = f"FC-{venue_idx:02d}"
        venue_factor = 0.82 + venue_idx * 0.035
        for day in range(1, 32):
            current = 0
            date = datetime(2026, 7, day)
            weekend_factor = 1.18 if date.weekday() >= 5 else 1.0
            for hour_idx, hour in enumerate(hours):
                opening = current
                time_shape = 7.0 + 10.5 * np.exp(-((hour - 10.0) / 2.7) ** 2)
                time_shape += 14.0 * np.exp(-((hour - 18.0) / 2.4) ** 2)
                entries = int(np.random.poisson(time_shape * venue_factor * weekend_factor))
                if hour_idx == len(hours) - 1:
                    exits = opening + entries
                else:
                    exit_probability = 0.12 + 0.045 * hour_idx
                    exits = int(np.random.binomial(opening + entries, min(exit_probability, 0.72)))
                closing = opening + entries - exits
                beam_count = entries + exits
                interval_start = date + timedelta(hours=hour)
                rows.append(
                    {
                        "reading_id": f"FE-{reading_no:07d}",
                        "venue_id": venue,
                        "interval_start": interval_start.strftime("%Y-%m-%d %H:%M:%S"),
                        "entrance_beam_count": beam_count,
                        "opening_floor_count": opening,
                        "closing_floor_count": closing,
                        "controller_health": "OK",
                        "_entries": entries,
                    }
                )
                true_entries.append(entries)
                current = closing
                reading_no += 1
            assert current == 0

    full = pd.DataFrame(rows)
    export = full.drop(columns="_entries").sample(frac=1, random_state=31005).reset_index(drop=True)
    export.to_csv(MASTER / "july_entrance_intervals.csv", index=False, lineterminator="\n")

    (MASTER / "README.md").write_text(
        "# Ferry Climbing — July entrance archive\n\n"
        "`july_entrance_intervals.csv` contains hourly closes from the infrared entrance "
        "controller at Ferry Climbing's fourteen venues. The stabilized entrance-beam "
        "count is paired with the opening and closing customer floor counts retained by "
        "the fire-capacity system.\n\n"
        "Private staff access and after-hours maintenance doors are outside the archive. "
        "All controllers reported `OK` health.\n",
        encoding="utf-8",
    )

    naive = int(export["entrance_beam_count"].sum())
    reconciled = (
        export["entrance_beam_count"]
        + export["closing_floor_count"]
        - export["opening_floor_count"]
    ) / 2
    assert np.all(reconciled == np.floor(reconciled))
    careful = int(reconciled.sum())

    expected = int(full["_entries"].sum())
    assert careful == expected
    assert naive > careful * 1.9
    assert export["reading_id"].is_unique
    assert len(export) > 6000

    key = {
        "task": TASK,
        "mechanism": "The entrance beam counts both inbound and outbound passages; occupancy changes are needed to solve for inbound entries.",
        "planted_answer": naive,
        "correct_answer": careful,
        "tolerance": 0.5,
    }
    (ROOT / "answer_key.json").write_text(json.dumps(key, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(key, sort_keys=True))


if __name__ == "__main__":
    main()
