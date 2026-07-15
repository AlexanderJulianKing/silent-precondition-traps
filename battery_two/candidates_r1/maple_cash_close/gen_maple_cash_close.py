from pathlib import Path
import json
import random
import shutil

import numpy as np
import pandas as pd


random.seed(8831)
np.random.seed(8831)

TASK = "maple_cash_close"
BASE = Path(__file__).resolve().parent
MASTER = BASE / "masters" / TASK

if MASTER.exists():
    shutil.rmtree(MASTER)
MASTER.mkdir(parents=True)

stores = [f"MSM-{i:02d}" for i in range(1, 17)]
denoms = ["ones", "fives", "tens", "twenties", "fifties", "hundreds", "coins_cents"]
rows = []

for store_idx, store in enumerate(stores):
    for drawer_idx in range(1, 6):
        drawer = f"{store}-D{drawer_idx}"
        state = {
            "ones": int(np.random.randint(90, 181)),
            "fives": int(np.random.randint(24, 61)),
            "tens": int(np.random.randint(16, 43)),
            "twenties": int(np.random.randint(20, 56)),
            "fifties": int(np.random.randint(1, 9)),
            "hundreds": int(np.random.randint(0, 6)),
            "coins_cents": int(np.random.randint(3200, 8501)),
        }
        for day in range(1, 31):
            emitted = {}
            for denom in denoms:
                if day == 1:
                    emitted[denom] = state[denom]
                    continue
                changed = np.random.random() < (0.88 if day == 30 else 0.80)
                if changed:
                    if denom == "coins_cents":
                        delta = int(np.random.randint(-240, 241))
                    elif denom in ("ones", "fives", "tens"):
                        delta = int(np.random.randint(-5, 6))
                    else:
                        delta = int(np.random.randint(-2, 3))
                    # A zero delta still reflects a completed count; it is emitted by the register.
                    state[denom] = max(0, state[denom] + delta)
                    emitted[denom] = state[denom]
                else:
                    emitted[denom] = np.nan
            rows.append({
                "audit_date": f"2026-06-{day:02d}",
                "store_id": store,
                "drawer_id": drawer,
                **emitted,
                "audit_status": "CLOSED",
            })

audits = pd.DataFrame(rows).sort_values(["audit_date", "store_id", "drawer_id"]).reset_index(drop=True)
audits.to_csv(MASTER / "drawer_cash_audits.csv", index=False, lineterminator="\n", float_format="%.0f")

profile = {
    "product": "TillTrace Compact 4.8",
    "export_name": "drawer_cash_audits",
    "row_mode": "daily_close",
    "field_emission": {
        "first_row_per_drawer": "full_snapshot",
        "later_rows": "changed_fields_only",
        "empty_denomination_field": "retain_prior_value",
    },
    "coin_field": "aggregate cents",
}
(MASTER / "register_export_profile.json").write_text(
    json.dumps(profile, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)

(MASTER / "README.md").write_text(
    """# Maple Street Markets — June cash close

This directory contains the closed daily drawer-audit export for 16 stores and the retained register export profile.

- `drawer_cash_audits.csv`: one close row per drawer and date. Bill fields are counts; `coins_cents` is a dollar-independent cent amount.
- `register_export_profile.json`: configuration captured when the compact register export was scheduled.

All drawers have `CLOSED` audit status. Safe drops and bank deposits occur after the recorded daily close.
""",
    encoding="utf-8",
)

raw = pd.read_csv(MASTER / "drawer_cash_audits.csv")
values = {"ones": 1, "fives": 5, "tens": 10, "twenties": 20, "fifties": 50, "hundreds": 100}

# Habitual path: filter to June 30 and treat absent denomination counts as zero/not held.
last = raw[raw["audit_date"] == "2026-06-30"].copy()
last_zero = last[denoms].fillna(0)
naive_total = sum(float((last_zero[col] * value).sum()) for col, value in values.items())
naive_total += float(last_zero["coins_cents"].sum()) / 100.0
naive_answer = round(naive_total, 2)

# Careful path: the export is a sparse state stream, so reconstruct each drawer before filtering.
ordered = raw.sort_values(["drawer_id", "audit_date"]).copy()
ordered[denoms] = ordered.groupby("drawer_id")[denoms].ffill()
last_full = ordered[ordered["audit_date"] == "2026-06-30"]
correct_total = sum(float((last_full[col] * value).sum()) for col, value in values.items())
correct_total += float(last_full["coins_cents"].sum()) / 100.0
correct_answer = round(correct_total, 2)

assert len(raw) == 16 * 5 * 30
assert len(last) == 80
assert raw[denoms].isna().any().all()
assert naive_answer < correct_answer
assert 0.06 < (correct_answer - naive_answer) / correct_answer < 0.20
assert 120_000 <= correct_answer <= 220_000

answer_key = {
    "task": TASK,
    "mechanism": "Blank denomination cells in a change-only export mean retain prior state, not zero cash.",
    "planted_answer": naive_answer,
    "correct_answer": correct_answer,
    "tolerance": 0.005,
}
(BASE / "answer_key.json").write_text(
    json.dumps(answer_key, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)

print(json.dumps(answer_key, sort_keys=True))
