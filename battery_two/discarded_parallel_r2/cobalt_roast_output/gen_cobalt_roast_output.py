from pathlib import Path
import json
import random
import shutil

import numpy as np
import pandas as pd


random.seed(16067)
np.random.seed(16067)

TASK = "cobalt_roast_output"
BASE = Path(__file__).resolve().parent
MASTER = BASE / "masters" / TASK

if MASTER.exists():
    shutil.rmtree(MASTER)
MASTER.mkdir(parents=True)

carts = [f"CART-{i:03d}" for i in range(1, 46)]
affected = set(carts[5::3])  # 14 carts whose controller retained gross cart weight.
tare = {cart: (round(4.7 + (idx % 8) * 0.21, 2) if cart in affected else 0.0) for idx, cart in enumerate(carts)}
profiles = ["house", "espresso", "light", "decaf"]
rows = []

# Production captures are intentionally the overwhelming, ordinary row type.
for i in range(8000):
    cart = carts[i % len(carts)]
    when = pd.Timestamp("2026-06-01 05:10:00") + pd.Timedelta(minutes=i * 5)
    true_output = round(float(np.clip(np.random.normal(79.5 + (i % 4) * 1.2, 4.8), 62.0, 96.0)), 2)
    rows.append({
        "capture_id": f"CSC-{i + 1:07d}",
        "recorded_at": when.strftime("%Y-%m-%d %H:%M:%S"),
        "cart_id": cart,
        "batch_ref": f"RB-{i + 1:07d}",
        "roast_profile": profiles[i % len(profiles)],
        "output_kg": round(true_output + tare[cart], 2),
        "release_status": "RELEASED",
    })

# Routine empty-cycle captures occur away from the file head. Their values expose the
# retained cart baselines only if excluded controls are analyzed by cart.
control_no = 1
for day in (8, 15, 22, 29):
    for cart_idx, cart in enumerate(carts):
        when = pd.Timestamp(2026, 6, day, 4, 42) + pd.Timedelta(seconds=cart_idx * 11)
        rows.append({
            "capture_id": f"CSC-C{control_no:05d}",
            "recorded_at": when.strftime("%Y-%m-%d %H:%M:%S"),
            "cart_id": cart,
            "batch_ref": f"SVC-{day:02d}-{cart_idx + 1:03d}",
            "roast_profile": "baseline",
            "output_kg": tare[cart],
            "release_status": "VERIFIED",
        })
        control_no += 1

captures = pd.DataFrame(rows).sort_values(["recorded_at", "capture_id"]).reset_index(drop=True)
captures.to_csv(MASTER / "cooling_scale_captures.csv", index=False, lineterminator="\n", float_format="%.2f")

(MASTER / "README.md").write_text(
    """# Cobalt Row Roasters — June cooling-scale export

`cooling_scale_captures.csv` contains the June controller captures from 45 cooling carts. Released roast batches use `RB-` references; routine controller service cycles remain in the export with their own references and status.

`output_kg` is the weight recorded when a cycle closed. Only `RELEASED` roast batches count as finished production.
""",
    encoding="utf-8",
)

raw = pd.read_csv(MASTER / "cooling_scale_captures.csv")
production = raw[raw["release_status"] == "RELEASED"].copy()

# Habitual path: sum the released production weight reported by the scale.
naive_answer = int(round(float(production["output_kg"].sum())))

# Careful path: verified sub-10 kg cycles reveal the persistent empty-cart baseline.
controls = raw[(raw["release_status"] == "VERIFIED") & (raw["output_kg"] < 10)]
baseline = controls.groupby("cart_id")["output_kg"].median()
production["baseline_kg"] = production["cart_id"].map(baseline)
production["net_output_kg"] = production["output_kg"] - production["baseline_kg"]
correct_answer = int(round(float(production["net_output_kg"].sum())))

assert len(production) == 8000
assert len(controls) == 45 * 4
assert baseline.gt(0).sum() == len(affected)
assert production["baseline_kg"].notna().all()
assert naive_answer > correct_answer
assert (naive_answer - correct_answer) / correct_answer > 0.02
assert 600_000 <= correct_answer <= 700_000

answer_key = {
    "task": TASK,
    "mechanism": "A subset of cooling-cart controllers records a stable empty-cart baseline inside released batch weights.",
    "planted_answer": naive_answer,
    "correct_answer": correct_answer,
    "tolerance": 0.5,
}
(BASE / "answer_key.json").write_text(
    json.dumps(answer_key, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)

print(json.dumps(answer_key, sort_keys=True))
