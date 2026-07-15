from pathlib import Path
import json
import random
import shutil

import numpy as np
import pandas as pd


random.seed(5519)
np.random.seed(5519)

TASK = "granite_shrink_rate"
BASE = Path(__file__).resolve().parent
MASTER = BASE / "masters" / TASK

if MASTER.exists():
    shutil.rmtree(MASTER)
MASTER.mkdir(parents=True)

warehouses = ["GRT-NORTH", "GRT-CENTRAL", "GRT-SOUTH"]
rows = []
for sku_num in range(1, 2501):
    for wh_idx, warehouse in enumerate(warehouses):
        expected = int(80 + np.random.poisson(115 + wh_idx * 12))
        rows.append({
            "sku": f"BP-{sku_num:05d}",
            "warehouse": warehouse,
            "erp_qty": expected,
            "counted_qty": 0,
            "count_session": f"JUL31-{warehouse[-1]}-{1 + sku_num % 18:02d}",
        })

stock = pd.DataFrame(rows)
transfer_indices = np.random.choice(stock.index.to_numpy(), size=460, replace=False)
open_by_row = {int(idx): 0 for idx in stock.index}
transfer_rows = []

for transfer_no, idx in enumerate(sorted(int(x) for x in transfer_indices), start=1):
    destination = stock.at[idx, "warehouse"]
    source = warehouses[(warehouses.index(destination) - 1) % len(warehouses)]
    units = int(np.random.randint(31, 66))
    open_by_row[idx] += units
    dispatch_minute = int((transfer_no * 17) % 600)
    dispatched = pd.Timestamp("2026-07-31 10:00:00") + pd.Timedelta(minutes=dispatch_minute)
    transfer_rows.append({
        "transfer_id": f"TX-{transfer_no:06d}",
        "sku": stock.at[idx, "sku"],
        "from_warehouse": source,
        "to_warehouse": destination,
        "units": units,
        "dispatched_at": dispatched.strftime("%Y-%m-%d %H:%M:%S"),
        "received_at": "",
        "status": "IN_TRANSIT",
    })

for idx in stock.index:
    transfer_units = open_by_row[int(idx)]
    physically_expected = int(stock.at[idx, "erp_qty"]) - transfer_units
    true_loss = int(np.random.binomial(physically_expected, 0.0118))
    stock.at[idx, "counted_qty"] = physically_expected - true_loss

transfers = pd.DataFrame(transfer_rows)
stock.to_csv(MASTER / "july31_stocktake.csv", index=False, lineterminator="\n")
transfers.to_csv(MASTER / "open_transfer_register.csv", index=False, lineterminator="\n")

(MASTER / "README.md").write_text(
    """# Granite Ridge Bicycle Supply — July 31 close

The files are the network inventory-close exports for the three warehouses.

- `july31_stocktake.csv`: final blind-count result joined to the ERP quantity at close.
- `open_transfer_register.csv`: carrier-dispatched transfers that had not received a destination scan when the count sessions closed.

Quantities are individual saleable units. Damaged goods already posted to disposal are excluded from both exports.
""",
    encoding="utf-8",
)

counted = pd.read_csv(MASTER / "july31_stocktake.csv")
open_tx = pd.read_csv(MASTER / "open_transfer_register.csv")

# Habitual path: use the ready-made book-versus-count columns as the shrink variance.
naive_missing = int((counted["erp_qty"] - counted["counted_qty"]).sum())
naive_answer = round(100.0 * naive_missing / float(counted["erp_qty"].sum()), 2)

# Careful path: dispatched units booked to destinations were not physically on hand there.
dest_units = open_tx.groupby(["to_warehouse", "sku"], as_index=False)["units"].sum()
careful = counted.merge(
    dest_units,
    left_on=["warehouse", "sku"],
    right_on=["to_warehouse", "sku"],
    how="left",
    validate="one_to_one",
)
careful["units"] = careful["units"].fillna(0).astype(int)
careful["physical_book_qty"] = careful["erp_qty"] - careful["units"]
correct_missing = int((careful["physical_book_qty"] - careful["counted_qty"]).sum())
correct_answer = round(100.0 * correct_missing / float(careful["physical_book_qty"].sum()), 2)

assert len(counted) == 7500
assert len(open_tx) == 460
assert (careful["physical_book_qty"] >= careful["counted_qty"]).all()
assert 2.5 <= naive_answer <= 3.5
assert 0.9 <= correct_answer <= 1.5
assert naive_answer > correct_answer + 1.2

answer_key = {
    "task": TASK,
    "mechanism": "Destination-booked units still on transfer trucks are mistaken for missing warehouse stock.",
    "planted_answer": naive_answer,
    "correct_answer": correct_answer,
    "tolerance": 0.005,
}
(BASE / "answer_key.json").write_text(
    json.dumps(answer_key, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)

print(json.dumps(answer_key, sort_keys=True))
