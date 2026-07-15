from pathlib import Path
import json
import random
import shutil

import numpy as np
import pandas as pd


random.seed(19001)
np.random.seed(19001)

TASK = "swift_response_time"
BASE = Path(__file__).resolve().parent
MASTER = BASE / "masters" / TASK

if MASTER.exists():
    shutil.rmtree(MASTER)
MASTER.mkdir(parents=True)

channels = ["email", "web", "sms"]
rows = []

for i in range(9000):
    opened = pd.Timestamp(2026, 6, 1 + i % 30, 7 + (i * 5) % 14, (i * 17) % 60, i % 53)
    actual_seconds = int(round(45 + np.random.gamma(2.0, 360.0)))
    actual_seconds = max(55, min(actual_seconds, 3600))
    if i < 300:
        actual_seconds = min(actual_seconds, 840)
    reply = opened + pd.Timedelta(seconds=actual_seconds)
    rows.append({
        "ticket_id": f"SFT-{i + 1:07d}",
        "opened_at": opened.strftime("%Y-%m-%d %H:%M:%S"),
        "first_human_reply_at": reply.strftime("%Y-%m-%d %H:%M:%S"),
        "response_seconds": min(actual_seconds, 900),
        "channel": channels[i % len(channels)],
        "priority": ["normal", "normal", "normal", "urgent"][i % 4],
        "status": "ANSWERED",
    })

tickets = pd.DataFrame(rows).sort_values("ticket_id").reset_index(drop=True)
tickets.to_csv(MASTER / "june_answered_tickets.csv", index=False, lineterminator="\n")

(MASTER / "README.md").write_text(
    """# Swift Harbor Appliance Care — June support export

`june_answered_tickets.csv` contains tickets opened during June that received a first human reply. `response_seconds` is the queue KPI attached when the ticket was answered. System acknowledgements are not included in `first_human_reply_at`.

Timestamps are local. Spam and test tickets have already been removed.
""",
    encoding="utf-8",
)

raw = pd.read_csv(MASTER / "june_answered_tickets.csv", parse_dates=["opened_at", "first_human_reply_at"])

# Habitual path: average the ready-made queue response metric.
naive_answer = round(float(raw["response_seconds"].mean() / 60.0), 1)

# Careful path: the convenience metric saturates at 900, while timestamps retain the tail.
actual = (raw["first_human_reply_at"] - raw["opened_at"]).dt.total_seconds()
correct_answer = round(float(actual.mean() / 60.0), 1)

under_cap = actual < 900
assert len(raw) == 9000
assert raw["ticket_id"].is_unique
assert (raw.loc[under_cap, "response_seconds"].to_numpy() == actual.loc[under_cap].to_numpy()).all()
assert (raw.loc[~under_cap, "response_seconds"] == 900).all()
assert int((raw["response_seconds"] == 900).sum()) > 2200
assert correct_answer > naive_answer + 1.5
assert 8.0 <= naive_answer <= 11.0
assert 11.0 <= correct_answer <= 15.0

answer_key = {
    "task": TASK,
    "mechanism": "The ready-made response metric silently saturates at the 900-second SLA boundary.",
    "planted_answer": naive_answer,
    "correct_answer": correct_answer,
    "tolerance": 0.05,
}
(BASE / "answer_key.json").write_text(
    json.dumps(answer_key, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)

print(json.dumps(answer_key, sort_keys=True))
