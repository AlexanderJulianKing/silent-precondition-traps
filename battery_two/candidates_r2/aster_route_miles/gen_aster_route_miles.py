from pathlib import Path
import json
import random
import shutil

import numpy as np
import pandas as pd


random.seed(12031)
np.random.seed(12031)

TASK = "aster_route_miles"
BASE = Path(__file__).resolve().parent
MASTER = BASE / "masters" / TASK

if MASTER.exists():
    shutil.rmtree(MASTER)
MASTER.mkdir(parents=True)

templates = [f"RT-{i:03d}" for i in range(1, 61)]
template_miles = {template: 4.8 + i * 0.38 + (i % 6) * 0.7 for i, template in enumerate(templates)}
depots = ["Northgate", "SoDo", "Bellevue", "Kent"]
rows = []

for i in range(1, 12201):
    day = int(np.random.randint(1, 31))
    template = templates[int(np.random.randint(0, len(templates)))]
    actual_miles = max(2.0, template_miles[template] + float(np.random.normal(0, 0.42)))
    build = "4.9-L" if day < 19 or np.random.random() > 0.31 else "5.14-R"
    reading = actual_miles if build == "4.9-L" else actual_miles * 1.609344
    status = "COMPLETED" if np.random.random() > 0.024 else "CANCELLED"
    started = pd.Timestamp(2026, 8, day, 6 + (i % 13), (i * 17) % 60, i % 53)
    rows.append({
        "route_id": f"AR-{i:07d}",
        "service_date": started.strftime("%Y-%m-%d"),
        "started_at": started.strftime("%Y-%m-%d %H:%M:%S"),
        "depot": depots[i % len(depots)],
        "route_template": template,
        "handheld_build": build,
        "route_distance": round(reading, 2),
        "planned_stops": int(7 + np.random.poisson(actual_miles * 0.75)),
        "status": status,
    })

routes = pd.DataFrame(rows).sort_values(["service_date", "started_at", "route_id"]).reset_index(drop=True)
routes.to_csv(MASTER / "august_route_closeout.csv", index=False, lineterminator="\n", float_format="%.2f")

(MASTER / "README.md").write_text(
    """# Aster Home Courier — August route closeout

`august_route_closeout.csv` contains the dispatch closeout row emitted for every August route. Cancelled routes never left the depot. `route_distance` is the stabilized route reading returned by the driver's handheld at closeout.

Route templates are reused across depots and days; minor deviations reflect detours and customer changes. The handheld build is retained for support triage.
""",
    encoding="utf-8",
)

raw = pd.read_csv(MASTER / "august_route_closeout.csv")
completed = raw[raw["status"] == "COMPLETED"].copy()

# Habitual path: the domestic route-distance column is summed as miles.
naive_answer = round(float(completed["route_distance"].sum()), 1)

# Careful path: build 5.14-R silently reports the same route templates in kilometres.
completed["miles"] = completed["route_distance"]
metric_build = completed["handheld_build"] == "5.14-R"
completed.loc[metric_build, "miles"] = completed.loc[metric_build, "route_distance"] / 1.609344
correct_answer = round(float(completed["miles"].sum()), 1)

means = completed.groupby(["route_template", "handheld_build"])["route_distance"].mean().unstack()
ratios = (means["5.14-R"] / means["4.9-L"]).dropna()
assert len(raw) == 12200
assert len(ratios) == 60
assert 1.56 < float(ratios.median()) < 1.66
assert naive_answer > correct_answer
assert 0.05 < (naive_answer - correct_answer) / correct_answer < 0.10

answer_key = {
    "task": TASK,
    "mechanism": "One late-month handheld build records route distance in kilometres inside an otherwise mile-like column.",
    "planted_answer": naive_answer,
    "correct_answer": correct_answer,
    "tolerance": 0.05,
}
(BASE / "answer_key.json").write_text(json.dumps(answer_key, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(answer_key, sort_keys=True))
