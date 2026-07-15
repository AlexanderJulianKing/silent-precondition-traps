from pathlib import Path
import json
import random
import shutil

import numpy as np
import pandas as pd


random.seed(18089)
np.random.seed(18089)

TASK = "lilac_damage_rate"
BASE = Path(__file__).resolve().parent
MASTER = BASE / "masters" / TASK

if MASTER.exists():
    shutil.rmtree(MASTER)
MASTER.mkdir(parents=True)

reasons = ["DMG", "FIT", "MIND", "LATE", "OTHER"]
reason_p = [0.26, 0.12, 0.27, 0.19, 0.16]
notes = {
    "DMG": ["arrived with a cracked panel", "broken latch on arrival", "frame was dented", "bottle was leaking"],
    "FIT": ["size was too small", "item was too large", "did not fit the space", "wrong size for customer"],
    "MIND": ["customer changed mind", "item no longer needed", "duplicate purchase", "preferred another color"],
    "LATE": ["arrived late for event", "delivery delay missed deadline", "package came after trip", "late arrival no longer useful"],
    "OTHER": ["ordered by mistake", "gift recipient declined", "different model preferred", "no reason supplied"],
}
stores = [f"LIL-{i:02d}" for i in range(1, 13)]
rows = []

for i in range(12000):
    day_offset = i % 91
    returned = pd.Timestamp("2026-04-01 09:00:00") + pd.Timedelta(days=day_offset, minutes=(i * 23) % 660)
    true_reason = str(np.random.choice(reasons, p=reason_p))
    if returned < pd.Timestamp("2026-05-01"):
        build = "till-7.1"
    elif returned < pd.Timestamp("2026-06-06"):
        build = "till-7.2"
    else:
        build = "till-7.3"
    selected_code = true_reason
    if build == "till-7.2":
        if true_reason == "DMG":
            selected_code = "FIT"
        elif true_reason == "FIT":
            selected_code = "DMG"
    rows.append({
        "return_id": f"LRT-{i + 1:07d}",
        "returned_at": returned.strftime("%Y-%m-%d %H:%M:%S"),
        "store_id": stores[i % len(stores)],
        "till_build": build,
        "reason_code": selected_code,
        "customer_note": random.choice(notes[true_reason]),
        "refund_amount": round(float(np.clip(np.random.lognormal(3.55, 0.58), 8, 260)), 2),
        "status": "COMPLETED",
    })

returns = pd.DataFrame(rows).sort_values(["returned_at", "return_id"]).reset_index(drop=True)
returns.to_csv(MASTER / "q2_completed_returns.csv", index=False, lineterminator="\n", float_format="%.2f")

(MASTER / "README.md").write_text(
    """# Lilac Lane Housewares — Q2 returns export

`q2_completed_returns.csv` contains one row per completed Q2 return from the twelve stores. `reason_code` is the return option selected at the till, and `customer_note` is the short note transcribed by the associate. Refund values are after any restocking charge.

Cancelled return attempts and warranty replacements are excluded.
""",
    encoding="utf-8",
)

raw = pd.read_csv(MASTER / "q2_completed_returns.csv")

# Habitual path: use the structured cashier-selected code.
naive_answer = round(100.0 * float(raw["reason_code"].eq("DMG").mean()), 1)

# Careful path: note language exposes a complete DMG/FIT option permutation in till-7.2.
damage_terms = ("cracked", "broken", "dented", "leaking")
note_damage = raw["customer_note"].str.contains("|".join(damage_terms), case=False, regex=True)
correct_answer = round(100.0 * float(note_damage.mean()), 1)

affected = raw[raw["till_build"] == "till-7.2"]
affected_note_damage = affected["customer_note"].str.contains("|".join(damage_terms), case=False, regex=True)
assert len(raw) == 12000
assert raw["return_id"].is_unique
assert ((affected["reason_code"] == "FIT") == affected_note_damage).all()
assert naive_answer < correct_answer - 4.0
assert 17.0 <= naive_answer <= 23.0
assert 23.0 <= correct_answer <= 29.0

answer_key = {
    "task": TASK,
    "mechanism": "One till build permutes the damage and fit option codes while notes retain their ordinary meanings.",
    "planted_answer": naive_answer,
    "correct_answer": correct_answer,
    "tolerance": 0.05,
}
(BASE / "answer_key.json").write_text(
    json.dumps(answer_key, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)

print(json.dumps(answer_key, sort_keys=True))
