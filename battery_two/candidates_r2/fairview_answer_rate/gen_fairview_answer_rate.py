from pathlib import Path
import json
import random
import shutil

import numpy as np
import pandas as pd


random.seed(45061)
np.random.seed(45061)

TASK = "fairview_answer_rate"
BASE = Path(__file__).resolve().parent
MASTER = BASE / "masters" / TASK

if MASTER.exists():
    shutil.rmtree(MASTER)
MASTER.mkdir(parents=True)

queues = ["repairs", "sales", "billing", "installations"]
rows = []
attempted_total = 0

for day in range(1, 31):
    attempts = int(np.random.randint(675, 756))
    seq_start = 500000 + day * 1000 + int(np.random.randint(20, 80))
    attempted_total += attempts
    for j in range(attempts):
        answered = np.random.random() < 0.787
        # Very short callers that disconnect before the disposition writer starts leave
        # only a consumed switch sequence. Preserve the first/last rows so the counter
        # bounds retain the full denominator.
        silent = (not answered) and (20 <= j < attempts - 20) and np.random.random() < 0.245
        if silent:
            continue
        received = pd.Timestamp(2026, 6, day, 8, 0, 0) + pd.Timedelta(seconds=j * 62 + (j % 17))
        wait = int(np.random.gamma(2.1, 31.0)) if answered else int(np.random.gamma(2.8, 44.0))
        rows.append({
            "call_id": f"FC-{day:02d}-{seq_start + j:07d}",
            "switch_seq": seq_start + j,
            "received_at": received.strftime("%Y-%m-%d %H:%M:%S"),
            "queue": queues[(j + day) % len(queues)],
            "outcome": "ANSWERED" if answered else "CALLER_ABANDONED",
            "wait_seconds": wait,
            "agent_extension": f"X{100 + (j * 7) % 180}" if answered else "",
        })

calls = pd.DataFrame(rows).sort_values(["received_at", "switch_seq"]).reset_index(drop=True)
calls.to_csv(MASTER / "june_inbound_calls.csv", index=False, lineterminator="\n")

(MASTER / "README.md").write_text(
    """# Fairview Heating & Air — June call export

`june_inbound_calls.csv` contains the completed inbound queue dispositions written by the phone switch. `switch_seq` is the switch-assigned sequence value and `wait_seconds` is measured from arrival at the public queue.

Outbound callbacks and employee extension-to-extension calls are outside this export.
""",
    encoding="utf-8",
)

raw = pd.read_csv(MASTER / "june_inbound_calls.csv", parse_dates=["received_at"])
answered_count = int((raw["outcome"] == "ANSWERED").sum())
naive_answer = round(100.0 * answered_count / len(raw), 2)

# The switch counter is consecutive within each public inbound day. Gaps are calls that
# disconnected before a disposition row could be written, but they remain attempts.
raw["call_date"] = raw["received_at"].dt.date
daily_attempts = raw.groupby("call_date")["switch_seq"].agg(lambda s: int(s.max() - s.min() + 1))
correct_answer = round(100.0 * answered_count / int(daily_attempts.sum()), 2)

assert len(raw) >= 19000
assert int(daily_attempts.sum()) == attempted_total
assert raw["call_id"].is_unique
assert naive_answer > correct_answer + 3.0
assert 75.0 < correct_answer < 82.0

answer_key = {
    "task": TASK,
    "mechanism": "Calls that disconnect before disposition are absent as rows but consume consecutive switch-sequence positions.",
    "planted_answer": naive_answer,
    "correct_answer": correct_answer,
    "tolerance": 0.005,
}
(BASE / "answer_key.json").write_text(json.dumps(answer_key, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(answer_key, sort_keys=True))
