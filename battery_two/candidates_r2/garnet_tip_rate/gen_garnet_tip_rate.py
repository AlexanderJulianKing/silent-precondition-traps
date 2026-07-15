from pathlib import Path
import json
import random
import shutil

import numpy as np
import pandas as pd


random.seed(56081)
np.random.seed(56081)

TASK = "garnet_tip_rate"
BASE = Path(__file__).resolve().parent
MASTER = BASE / "masters" / TASK

if MASTER.exists():
    shutil.rmtree(MASTER)
MASTER.mkdir(parents=True)

venues = ["Canal", "Foundry", "Market", "Terrace"]
rows = []

for i in range(1, 15001):
    large_party = np.random.random() < 0.275
    party_size = int(np.random.randint(8, 15)) if large_party else int(np.random.randint(1, 8))
    per_guest = float(np.clip(np.random.normal(31.0, 7.5), 16.0, 58.0))
    pretax = round(party_size * per_guest + float(np.random.uniform(0, 18)), 2)
    if large_party:
        tip = round(pretax * 0.20, 2)
    else:
        if np.random.random() < 0.055:
            pct = 0.0
        elif np.random.random() < 0.18:
            pct = float(np.random.choice([0.15, 0.18, 0.20]))
        else:
            pct = float(np.clip(np.random.normal(0.158, 0.035), 0.06, 0.27))
        tip = round(pretax * pct, 2)
    day = 1 + ((i * 17) % 30)
    closed = pd.Timestamp(2026, 9, day, 11 + i % 12, (i * 23) % 60, i % 51)
    rows.append({
        "check_id": f"GNT-{i:07d}",
        "closed_at": closed.strftime("%Y-%m-%d %H:%M:%S"),
        "venue": venues[i % len(venues)],
        "party_size": party_size,
        "pretax_food_beverage": pretax,
        "tip_amount": tip,
        "tender": ["card", "mobile", "cash"][i % 3],
        "status": "CLOSED",
    })

checks = pd.DataFrame(rows)
rate = checks["tip_amount"] / checks["pretax_food_beverage"]
ordinary = checks[(checks["party_size"] < 8) & (rate.sub(0.20).abs() > 0.002)].sample(frac=1, random_state=56081)
ordinary_ids = set(ordinary.iloc[:120]["check_id"])
middle = checks[~checks["check_id"].isin(ordinary_ids)].sample(frac=1, random_state=56082)
checks = pd.concat([ordinary.iloc[:60], middle, ordinary.iloc[60:120]], ignore_index=True)
checks.to_csv(MASTER / "september_closed_checks.csv", index=False, lineterminator="\n", float_format="%.2f")

(MASTER / "README.md").write_text(
    """# Garnet Table — September check export

`september_closed_checks.csv` contains one row per closed dining check at the four Garnet Table venues. `pretax_food_beverage` excludes tax and retail merchandise. `tip_amount` is the gratuity line returned by the point-of-sale close.

Voids, training checks, and open tabs are excluded.
""",
    encoding="utf-8",
)

raw = pd.read_csv(MASTER / "september_closed_checks.csv")
naive_answer = round(100.0 * float(raw["tip_amount"].sum()) / float(raw["pretax_food_beverage"].sum()), 2)

# The unlabeled large-party POS line is a fixed service charge, not a customer-selected
# tip. Its exact conditional rule is visible only in the joint amount/party-size pattern.
optional = raw[raw["party_size"] < 8]
correct_answer = round(100.0 * float(optional["tip_amount"].sum()) / float(optional["pretax_food_beverage"].sum()), 2)

large = raw[raw["party_size"] >= 8]
large_rate = large["tip_amount"] / large["pretax_food_beverage"]
assert len(raw) == 15000
assert raw["check_id"].is_unique
assert float((large_rate.sub(0.20).abs() < 0.00008).mean()) > 0.99
assert naive_answer > correct_answer + 2.0
assert 14.0 < correct_answer < 17.0

answer_key = {
    "task": TASK,
    "mechanism": "A fixed large-party service charge is exported in the same gratuity field as customer-selected tips.",
    "planted_answer": naive_answer,
    "correct_answer": correct_answer,
    "tolerance": 0.005,
}
(BASE / "answer_key.json").write_text(json.dumps(answer_key, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(answer_key, sort_keys=True))
