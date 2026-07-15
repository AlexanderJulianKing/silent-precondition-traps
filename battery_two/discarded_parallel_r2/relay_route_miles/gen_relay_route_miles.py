from pathlib import Path
import json
import random
import shutil

import numpy as np
import pandas as pd


random.seed(12031)
np.random.seed(12031)

TASK = "relay_route_miles"
BASE = Path(__file__).resolve().parent
MASTER = BASE / "masters" / TASK

if MASTER.exists():
    shutil.rmtree(MASTER)
MASTER.mkdir(parents=True)

route_ids = [f"RT-{i:03d}" for i in range(1, 31)]
route_base_miles = {route: 2.8 + i * 0.39 + (i % 4) * 0.42 for i, route in enumerate(route_ids)}
drivers = [f"DRV-{i:03d}" for i in range(1, 81)]
rows = []

for i in range(12000):
    day = 1 + (i % 30)
    minute_of_day = 7 * 60 + ((i * 17) % (12 * 60))
    completed_at = pd.Timestamp(2026, 6, day) + pd.Timedelta(minutes=minute_of_day, seconds=i % 41)
    route = route_ids[int(np.random.randint(0, len(route_ids)))]
    driver = drivers[i % len(drivers)]
    true_miles = float(np.clip(np.random.normal(route_base_miles[route], 0.22), 1.5, 18.0))

    # A quiet handheld rollout began late in the month. The export does not carry a unit flag.
    new_build = day >= 19 and (i % 5 in (0, 1, 2))
    build = "nav-5.9" if new_build else "nav-5.8"
    exported_distance = true_miles * 1.609344 if new_build else true_miles
    rows.append({
        "trip_id": f"RLY-{i + 1:07d}",
        "completed_at": completed_at.strftime("%Y-%m-%d %H:%M:%S"),
        "driver_id": driver,
        "route_template": route,
        "handheld_build": build,
        "route_distance": round(exported_distance, 3),
        "status": "COMPLETED",
    })

trips = pd.DataFrame(rows).sort_values(["completed_at", "trip_id"]).reset_index(drop=True)
trips.to_csv(MASTER / "completed_routes_june.csv", index=False, lineterminator="\n", float_format="%.3f")

(MASTER / "README.md").write_text(
    """# Relay Neighborhood Courier — June route export

`completed_routes_june.csv` is the dispatch closeout export for June 2026. Each row is one completed courier route. `route_distance` is the navigation distance returned by the driver's handheld at closeout; cancelled and training routes have already been removed.

Relay operates within the Portland metro area. Route templates are reused throughout the month as stops are assigned to different drivers.
""",
    encoding="utf-8",
)

raw = pd.read_csv(MASTER / "completed_routes_june.csv")

# Habitual path: treat the single distance column as miles and sum completed rows.
naive_answer = round(float(raw.loc[raw["status"] == "COMPLETED", "route_distance"].sum()), 1)

# Careful path: nav-5.9 values have a 1.609344 within-template scale relationship to nav-5.8.
corrected = raw["route_distance"].copy()
new_mask = raw["handheld_build"] == "nav-5.9"
corrected.loc[new_mask] = corrected.loc[new_mask] / 1.609344
correct_answer = round(float(corrected.sum()), 1)

medians = raw.groupby(["route_template", "handheld_build"])["route_distance"].median().unstack()
scale_ratio = float((medians["nav-5.9"] / medians["nav-5.8"]).median())
assert len(raw) == 12000
assert raw["trip_id"].is_unique
assert 1.58 < scale_ratio < 1.64
assert naive_answer > correct_answer
assert (naive_answer - correct_answer) / correct_answer > 0.12
assert 90_000 <= correct_answer <= 140_000

answer_key = {
    "task": TASK,
    "mechanism": "One handheld build silently exports route distance in kilometers into the same plausible-looking numeric column.",
    "planted_answer": naive_answer,
    "correct_answer": correct_answer,
    "tolerance": 0.05,
}
(BASE / "answer_key.json").write_text(
    json.dumps(answer_key, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)

print(json.dumps(answer_key, sort_keys=True))
