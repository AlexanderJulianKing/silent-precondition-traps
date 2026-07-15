from pathlib import Path
import json
import random
import shutil

import numpy as np
import pandas as pd


random.seed(2209)
np.random.seed(2209)

TASK = "meridian_repeat_rate"
BASE = Path(__file__).resolve().parent
MASTER = BASE / "masters" / TASK

if MASTER.exists():
    shutil.rmtree(MASTER)
MASTER.mkdir(parents=True)

stores = ["MDR-CAP", "MDR-LAK", "MDR-RIV"]
store_names = {"MDR-CAP": "Capitol Hill", "MDR-LAK": "Lake City", "MDR-RIV": "Riverton"}
member_rows = []
purchase_rows = []
purchase_no = 1

def add_purchase(store, customer_no, when, amount):
    global purchase_no
    purchase_rows.append({
        "purchase_id": f"P{purchase_no:07d}",
        "purchase_ts": pd.Timestamp(when).strftime("%Y-%m-%d %H:%M:%S"),
        "store_id": store,
        "customer_no": customer_no,
        "net_sales": round(float(amount), 2),
    })
    purchase_no += 1

for store_idx, store in enumerate(stores):
    for customer_no in range(1000, 3000):
        member_rows.append({
            "store_id": store,
            "customer_no": customer_no,
            "member_uuid": f"MBR-{store_idx + 1}-{customer_no:05d}-Q",
            "home_store": store_names[store],
            "marketing_opt_in": "Y" if (customer_no + store_idx) % 4 else "N",
        })

        if customer_no < 1500:  # established members
            first_day = 1 + ((customer_no * 7 + store_idx) % 27)
            add_purchase(store, customer_no, f"2026-04-{first_day:02d} {10 + store_idx:02d}:15:00", np.random.gamma(3.0, 13.0))
            for month in (4, 5, 6, 7):
                visits = int(np.random.poisson(0.9))
                for visit in range(visits):
                    day = 1 + int(np.random.randint(0, 28))
                    add_purchase(store, customer_no, f"2026-{month:02d}-{day:02d} {11 + (visit % 8):02d}:20:00", np.random.gamma(2.7, 14.0))
        elif customer_no < 2500:  # May acquisition cohort
            # The receipt number ranges are independently issued by each store. Matching
            # numbers happen to start on the same calendar day, keeping the global-ID
            # answer plausible rather than trivially reaching 100%.
            first_day = 1 + ((customer_no * 11) % 25)
            add_purchase(store, customer_no, f"2026-05-{first_day:02d} {9 + store_idx * 3:02d}:10:00", np.random.gamma(3.2, 12.0))
            if np.random.random() < 0.235:
                lag = int(np.random.randint(2, 31))
                later = pd.Timestamp(2026, 5, first_day, 12 + store_idx) + pd.Timedelta(days=lag)
                add_purchase(store, customer_no, later, np.random.gamma(2.9, 13.0))
                if np.random.random() < 0.12:
                    add_purchase(store, customer_no, later + pd.Timedelta(days=3), np.random.gamma(2.3, 12.0))
        else:  # customers first seen after the cohort month
            first_day = 1 + ((customer_no * 5 + store_idx) % 25)
            add_purchase(store, customer_no, f"2026-06-{first_day:02d} {10 + store_idx:02d}:40:00", np.random.gamma(3.0, 12.0))

members = pd.DataFrame(member_rows)
purchases = pd.DataFrame(purchase_rows).sort_values(["purchase_ts", "purchase_id"]).reset_index(drop=True)
members.to_csv(MASTER / "member_directory.csv", index=False, lineterminator="\n")
purchases.to_csv(MASTER / "purchases_apr_jul.csv", index=False, lineterminator="\n")

(MASTER / "README.md").write_text(
    """# Meridian Pet & Pantry — repeat-shopper extract

The extract covers identified purchases from April through July 2026 at three neighborhood stores.

- `purchases_apr_jul.csv`: one row per completed purchase; returns are already reflected in `net_sales`.
- `member_directory.csv`: the nightly membership-directory export. `customer_no` is the member number printed by the store register.

All timestamps are local. Guest purchases without a member number are outside this extract.
""",
    encoding="utf-8",
)

tx = pd.read_csv(MASTER / "purchases_apr_jul.csv", parse_dates=["purchase_ts"])

def repeat_rate(frame, keys):
    first = frame.groupby(keys, as_index=False)["purchase_ts"].min().rename(columns={"purchase_ts": "first_ts"})
    cohort = first[(first["first_ts"] >= "2026-05-01") & (first["first_ts"] < "2026-06-01")]
    joined = frame.merge(cohort, on=keys, how="inner")
    joined["day_lag"] = (joined["purchase_ts"].dt.normalize() - joined["first_ts"].dt.normalize()).dt.days
    repeated = joined.groupby(keys)["day_lag"].apply(lambda s: bool(((s >= 1) & (s <= 30)).any()))
    return round(100.0 * float(repeated.mean()), 1), len(cohort)

# Habitual path: the concise customer_no is assumed to be chainwide.
naive_answer, naive_n = repeat_rate(tx, ["customer_no"])
# Careful path: receipt numbers are namespaced by their issuing register/store.
correct_answer, correct_n = repeat_rate(tx, ["store_id", "customer_no"])

assert len(tx) >= 10000
assert naive_n == 1000
assert correct_n == 3000
assert naive_answer > correct_answer + 20.0
assert 45.0 <= naive_answer <= 65.0
assert 20.0 <= correct_answer <= 27.0

answer_key = {
    "task": TASK,
    "mechanism": "Store-local receipt customer numbers are mistaken for a chainwide person identifier.",
    "planted_answer": naive_answer,
    "correct_answer": correct_answer,
    "tolerance": 0.05,
}
(BASE / "answer_key.json").write_text(
    json.dumps(answer_key, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)

print(json.dumps(answer_key, sort_keys=True))
