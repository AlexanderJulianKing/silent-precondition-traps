from pathlib import Path
import json
import random
import shutil

import numpy as np
import pandas as pd


random.seed(15061)
np.random.seed(15061)

TASK = "lark_room_hours"
BASE = Path(__file__).resolve().parent
MASTER = BASE / "masters" / TASK

if MASTER.exists():
    shutil.rmtree(MASTER)
MASTER.mkdir(parents=True)

rooms = [f"STUDIO-{i:02d}" for i in range(1, 25)]
rows = []
session_no = 1

for day in pd.date_range("2026-06-01", "2026-06-30", freq="D"):
    for room_idx, room in enumerate(rooms):
        cursor = day + pd.Timedelta(hours=8, minutes=int(np.random.randint(0, 21)))
        close = day + pd.Timedelta(hours=20)
        while cursor < close - pd.Timedelta(minutes=35):
            duration = int(np.random.randint(38, 76))
            end = min(cursor + pd.Timedelta(minutes=duration), close)
            rows.append({
                "session_id": f"LCS-{session_no:07d}",
                "room_id": room,
                "started_at": cursor.strftime("%Y-%m-%d %H:%M:%S"),
                "ended_at": end.strftime("%Y-%m-%d %H:%M:%S"),
                "booking_source": ["member_app", "front_desk", "recurring"][session_no % 3],
                "status": "COMPLETED",
            })
            session_no += 1
            if np.random.random() < 0.34:
                cursor = end - pd.Timedelta(minutes=int(np.random.randint(6, 19)))
            else:
                cursor = end + pd.Timedelta(minutes=int(np.random.randint(7, 27)))

sessions = pd.DataFrame(rows).sort_values(["started_at", "room_id", "session_id"]).reset_index(drop=True)
sessions.to_csv(MASTER / "studio_presence_sessions.csv", index=False, lineterminator="\n")

(MASTER / "README.md").write_text(
    """# Lark Creative Studios — June access export

`studio_presence_sessions.csv` contains completed room-presence sessions from the access controller for Lark's 24 reservable studios. Timestamps are local and fall within the 08:00–20:00 operating day. Cancelled reservations and staff maintenance access are excluded.

Sessions come from member-app, front-desk, and recurring bookings and retain their original booking identifiers.
""",
    encoding="utf-8",
)

raw = pd.read_csv(MASTER / "studio_presence_sessions.csv", parse_dates=["started_at", "ended_at"])

# Habitual path: sum the valid completed-session durations.
naive_answer = round(float((raw["ended_at"] - raw["started_at"]).dt.total_seconds().sum() / 3600.0), 1)

# Careful path: a physical room can only contribute once at any instant, so union intervals.
union_seconds = 0.0
overlap_pairs = 0
for room, group in raw.sort_values(["room_id", "started_at", "ended_at"]).groupby("room_id"):
    current_start = None
    current_end = None
    for row in group.itertuples(index=False):
        if current_start is None:
            current_start, current_end = row.started_at, row.ended_at
        elif row.started_at <= current_end:
            overlap_pairs += 1
            current_end = max(current_end, row.ended_at)
        else:
            union_seconds += (current_end - current_start).total_seconds()
            current_start, current_end = row.started_at, row.ended_at
    union_seconds += (current_end - current_start).total_seconds()
correct_answer = round(float(union_seconds / 3600.0), 1)

assert len(raw) >= 6500
assert raw["session_id"].is_unique
assert raw.duplicated().sum() == 0
assert overlap_pairs > 1500
assert naive_answer > correct_answer
assert (naive_answer - correct_answer) / correct_answer > 0.05
assert 5_000 <= correct_answer <= 8_000

answer_key = {
    "task": TASK,
    "mechanism": "Individually valid booking sessions overlap, so summing durations double-counts physical room occupancy.",
    "planted_answer": naive_answer,
    "correct_answer": correct_answer,
    "tolerance": 0.05,
}
(BASE / "answer_key.json").write_text(
    json.dumps(answer_key, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)

print(json.dumps(answer_key, sort_keys=True))
