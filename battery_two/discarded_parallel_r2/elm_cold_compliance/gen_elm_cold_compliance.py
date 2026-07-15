from pathlib import Path
import json
import random
import shutil

import numpy as np
import pandas as pd


random.seed(17077)
np.random.seed(17077)

TASK = "elm_cold_compliance"
BASE = Path(__file__).resolve().parent
MASTER = BASE / "masters" / TASK

if MASTER.exists():
    shutil.rmtree(MASTER)
MASTER.mkdir(parents=True)

start = pd.Timestamp("2026-06-01 00:00:00")
end = pd.Timestamp("2026-07-01 00:00:00")
coolers = [f"COLD-{i:02d}" for i in range(1, 19)]
rows = []
reading_no = 1

for cooler_idx, cooler in enumerate(coolers):
    current = start
    in_range = True
    while current < end:
        if in_range:
            temperature = round(float(np.random.uniform(34.2, 39.8)), 1)
            interval_minutes = int(np.random.randint(20, 56))
            if np.random.random() < 0.0105:
                next_state = False
            else:
                next_state = True
        else:
            if np.random.random() < 0.5:
                temperature = round(float(np.random.uniform(31.0, 33.8)), 1)
            else:
                temperature = round(float(np.random.uniform(40.2, 44.0)), 1)
            interval_minutes = int(np.random.randint(125, 281))
            if np.random.random() < 0.31:
                next_state = True
            else:
                next_state = False
        rows.append({
            "reading_id": f"ECT-{reading_no:08d}",
            "cooler_id": cooler,
            "recorded_at": current.strftime("%Y-%m-%d %H:%M:%S"),
            "temperature_f": temperature,
            "quality": "VALID",
        })
        reading_no += 1
        current = min(current + pd.Timedelta(minutes=interval_minutes), end)
        in_range = next_state

readings = pd.DataFrame(rows).sort_values(["recorded_at", "cooler_id", "reading_id"]).reset_index(drop=True)
readings.to_csv(MASTER / "june_cooler_telemetry.csv", index=False, lineterminator="\n", float_format="%.1f")

(MASTER / "README.md").write_text(
    """# Elm & Iron Creamery — June cold-room telemetry

`june_cooler_telemetry.csv` contains the valid June temperature observations received from the creamery's 18 ingredient coolers. Temperatures are Fahrenheit. The June monitoring window is midnight June 1 through midnight July 1.

The food-safety band for these rooms is 34.0°F through 40.0°F, inclusive.
""",
    encoding="utf-8",
)

raw = pd.read_csv(MASTER / "june_cooler_telemetry.csv", parse_dates=["recorded_at"])
in_band = raw["temperature_f"].between(34.0, 40.0, inclusive="both")

# Habitual path: percentage of valid observations in the compliance band.
naive_answer = round(100.0 * float(in_band.mean()), 1)

# Careful path: observations are change-driven and persist until the next record.
ordered = raw.sort_values(["cooler_id", "recorded_at"]).copy()
ordered["next_at"] = ordered.groupby("cooler_id")["recorded_at"].shift(-1)
ordered["next_at"] = ordered["next_at"].fillna(end)
ordered["minutes"] = (ordered["next_at"] - ordered["recorded_at"]).dt.total_seconds() / 60.0
ordered["in_band"] = ordered["temperature_f"].between(34.0, 40.0, inclusive="both")
correct_answer = round(100.0 * float(ordered.loc[ordered["in_band"], "minutes"].sum() / ordered["minutes"].sum()), 1)

assert len(raw) >= 14000
assert raw["reading_id"].is_unique
assert ordered["minutes"].gt(0).all()
assert abs(float(ordered["minutes"].sum()) - 18 * 30 * 24 * 60) < 0.01
assert naive_answer > correct_answer + 7.0
assert 75.0 <= correct_answer <= 92.0
assert 90.0 <= naive_answer <= 99.5

answer_key = {
    "task": TASK,
    "mechanism": "Change-driven telemetry oversamples volatile compliant periods and undersamples long stable excursions.",
    "planted_answer": naive_answer,
    "correct_answer": correct_answer,
    "tolerance": 0.05,
}
(BASE / "answer_key.json").write_text(
    json.dumps(answer_key, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)

print(json.dumps(answer_key, sort_keys=True))
