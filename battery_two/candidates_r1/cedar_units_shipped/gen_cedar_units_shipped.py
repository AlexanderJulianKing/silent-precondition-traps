from pathlib import Path
import json
import random
import shutil

import numpy as np
import pandas as pd


random.seed(7727)
np.random.seed(7727)

TASK = "cedar_units_shipped"
BASE = Path(__file__).resolve().parent
MASTER = BASE / "masters" / TASK

if MASTER.exists():
    shutil.rmtree(MASTER)
MASTER.mkdir(parents=True)

skus = [f"CB-{i:04d}" for i in range(1, 81)]
changed_skus = set(skus[3::4])  # 20 ordinary items changed case configuration during Q2.
catalog_rows = []
notice_rows = []

for i, sku in enumerate(skus, start=1):
    if sku in changed_skus:
        current_pack = 20
        old_pack = 24
        effective = pd.Timestamp("2026-05-15") + pd.Timedelta(days=i % 7)
        notice_rows.append({
            "notice_id": f"SUP-N-{i:04d}",
            "sku": sku,
            "notice_type": "CASE_CONFIGURATION",
            "effective_ship_date": effective.strftime("%Y-%m-%d"),
            "prior_units_per_case": old_pack,
            "new_units_per_case": current_pack,
            "reason": "carton footprint refresh",
        })
    else:
        current_pack = [12, 24, 30][i % 3]
    catalog_rows.append({
        "sku": sku,
        "brand": ["Cinder", "Pine", "Rill", "Orchard"][i % 4],
        "flavor_family": ["citrus", "berry", "herbal", "cola", "tonic"][i % 5],
        "units_per_case": current_pack,
        "catalog_as_of": "2026-06-30",
    })

shipment_rows = []
for line_no in range(1, 9601):
    ship_date = pd.Timestamp("2026-04-01") + pd.Timedelta(days=int(np.random.randint(0, 91)))
    sku = skus[int(np.random.randint(0, len(skus)))]
    cases = int(1 + np.random.poisson(5.8))
    shipment_rows.append({
        "shipment_line_id": f"SL-{line_no:07d}",
        "shipment_id": f"SHP-{1 + (line_no - 1) // 3:06d}",
        "ship_date": ship_date.strftime("%Y-%m-%d"),
        "sku": sku,
        "cases_shipped": cases,
        "warehouse": ["Portland", "Salem", "Vancouver"][line_no % 3],
    })

catalog = pd.DataFrame(catalog_rows)
notices = pd.DataFrame(notice_rows)
shipments = pd.DataFrame(shipment_rows).sort_values(["ship_date", "shipment_line_id"]).reset_index(drop=True)
shipments.to_csv(MASTER / "q2_shipment_lines.csv", index=False, lineterminator="\n")
catalog.to_csv(MASTER / "current_item_catalog.csv", index=False, lineterminator="\n")
notices.to_csv(MASTER / "supplier_item_notices.csv", index=False, lineterminator="\n")

(MASTER / "README.md").write_text(
    """# Cedar Bend Beverage Co. — Q2 shipment archive

This directory contains the shipped-line export used by operations, the June 30 item catalog, and supplier item notices retained during the quarter.

- `q2_shipment_lines.csv`: one row per shipped SKU line; quantities are full cases.
- `current_item_catalog.csv`: active item attributes as of June 30.
- `supplier_item_notices.csv`: archived supplier notices for active items.

Samples, damaged cases, and cancelled picks are excluded from the shipment export.
""",
    encoding="utf-8",
)

lines = pd.read_csv(MASTER / "q2_shipment_lines.csv", parse_dates=["ship_date"])
current = pd.read_csv(MASTER / "current_item_catalog.csv")

# Habitual path: join the compact current catalog and multiply cases by pack size.
naive = lines.merge(current[["sku", "units_per_case"]], on="sku", how="left", validate="many_to_one")
naive_answer = int((naive["cases_shipped"] * naive["units_per_case"]).sum())

# Careful path: reconstruct the pack size that was effective on each shipment date.
history = pd.read_csv(MASTER / "supplier_item_notices.csv", parse_dates=["effective_ship_date"])
careful = naive.merge(history, on="sku", how="left", validate="many_to_one")
careful["effective_units"] = careful["units_per_case"]
before_change = careful["effective_ship_date"].notna() & (careful["ship_date"] < careful["effective_ship_date"])
careful.loc[before_change, "effective_units"] = careful.loc[before_change, "prior_units_per_case"]
correct_answer = int((careful["cases_shipped"] * careful["effective_units"]).sum())

assert len(lines) == 9600
assert current["sku"].is_unique
assert len(history) == 20
assert naive_answer < correct_answer
assert (correct_answer - naive_answer) / correct_answer > 0.02
assert 1_000_000 <= correct_answer <= 2_000_000

answer_key = {
    "task": TASK,
    "mechanism": "A quarter-end catalog's current case size is applied to shipments made before midquarter carton changes.",
    "planted_answer": naive_answer,
    "correct_answer": correct_answer,
    "tolerance": 0.5,
}
(BASE / "answer_key.json").write_text(
    json.dumps(answer_key, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)

print(json.dumps(answer_key, sort_keys=True))
