from pathlib import Path
import json
import random
import shutil

import numpy as np
import pandas as pd


random.seed(34057)
np.random.seed(34057)

TASK = "cobalt_session_length"
BASE = Path(__file__).resolve().parent
MASTER = BASE / "masters" / TASK

if MASTER.exists():
    shutil.rmtree(MASTER)
MASTER.mkdir(parents=True)

rows = []
segment_no = 1
continuous_sessions = 10500

for i in range(1, continuous_sessions + 1):
    account = f"CA-{1 + (i * 47) % 6200:05d}"
    device = f"DV-{1 + (i * 83) % 8100:05d}"
    day = int(np.random.randint(2, 29))
    crosses_midnight = np.random.random() < 0.235
    if crosses_midnight:
        start = pd.Timestamp(2026, 6, day, 21, 30) + pd.Timedelta(minutes=int(np.random.randint(0, 135)))
        duration_seconds = int(np.random.randint(165 * 60, 430 * 60))
    else:
        start = pd.Timestamp(2026, 6, day, int(np.random.randint(6, 22)), int(np.random.randint(0, 60)))
        duration_seconds = int(np.clip(np.random.lognormal(3.53, 0.62) * 60, 5 * 60, 150 * 60))
    end = start + pd.Timedelta(seconds=duration_seconds)
    total_events = int(max(2, np.random.poisson(duration_seconds / 150)))

    segment_start = start
    remaining_events = total_events
    while segment_start < end:
        midnight = segment_start.normalize() + pd.Timedelta(days=1)
        segment_end = min(end, midnight)
        share = (segment_end - segment_start).total_seconds() / duration_seconds
        events = max(1, int(round(total_events * share)))
        events = min(events, remaining_events) if segment_end == end else events
        remaining_events = max(0, remaining_events - events)
        rows.append({
            "session_id": f"CS-{segment_no:07d}",
            "account_id": account,
            "device_hash": device,
            "session_start": segment_start.strftime("%Y-%m-%d %H:%M:%S"),
            "session_end": segment_end.strftime("%Y-%m-%d %H:%M:%S"),
            "page_events": events,
            "client": ["web", "ios", "android"][i % 3],
        })
        segment_no += 1
        segment_start = segment_end

sessions = pd.DataFrame(rows)
boundary = sessions["session_start"].str.endswith("00:00:00") | sessions["session_end"].str.endswith("00:00:00")
normal = sessions.loc[~boundary].sample(frac=1, random_state=34057)
middle = pd.concat([normal.iloc[160:], sessions.loc[boundary]], ignore_index=True).sample(frac=1, random_state=34058)
sessions = pd.concat([normal.iloc[:80], middle, normal.iloc[80:160]], ignore_index=True)
sessions.to_csv(MASTER / "june_web_sessions.csv", index=False, lineterminator="\n")

(MASTER / "README.md").write_text(
    """# Cobalt Courseware — June engagement export

`june_web_sessions.csv` contains the June session rows emitted by the product telemetry pipeline. Timestamps are UTC, `page_events` excludes background keep-alives, and internal staff accounts have already been removed.

The three client values use the same session schema. Session identifiers are unique export identifiers.
""",
    encoding="utf-8",
)

raw = pd.read_csv(MASTER / "june_web_sessions.csv", parse_dates=["session_start", "session_end"])
raw["minutes"] = (raw["session_end"] - raw["session_start"]).dt.total_seconds() / 60.0
naive_answer = round(float(raw["minutes"].mean()), 1)

# The daily telemetry partition closes open sessions at midnight and emits a fresh
# export identifier immediately, without an interruption in customer activity.
stitched_lengths = []
for _, group in raw.sort_values(["account_id", "device_hash", "session_start"]).groupby(["account_id", "device_hash"]):
    current_start = None
    current_end = None
    for row in group.itertuples(index=False):
        if current_start is None:
            current_start, current_end = row.session_start, row.session_end
        elif row.session_start == current_end:
            current_end = max(current_end, row.session_end)
        else:
            stitched_lengths.append((current_end - current_start).total_seconds() / 60.0)
            current_start, current_end = row.session_start, row.session_end
    stitched_lengths.append((current_end - current_start).total_seconds() / 60.0)
correct_answer = round(float(np.mean(stitched_lengths)), 1)

assert len(raw) > continuous_sessions
assert raw["session_id"].is_unique
assert len(stitched_lengths) == continuous_sessions
assert naive_answer < correct_answer
assert (correct_answer - naive_answer) / correct_answer > 0.12

answer_key = {
    "task": TASK,
    "mechanism": "A daily telemetry partition gives uninterrupted sessions new IDs at midnight.",
    "planted_answer": naive_answer,
    "correct_answer": correct_answer,
    "tolerance": 0.05,
}
(BASE / "answer_key.json").write_text(json.dumps(answer_key, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(answer_key, sort_keys=True))
