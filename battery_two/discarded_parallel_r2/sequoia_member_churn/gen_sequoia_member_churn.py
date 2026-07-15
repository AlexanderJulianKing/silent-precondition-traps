from pathlib import Path
import json
import random
import shutil

import numpy as np
import pandas as pd


random.seed(14051)
np.random.seed(14051)

TASK = "sequoia_member_churn"
BASE = Path(__file__).resolve().parent
MASTER = BASE / "masters" / TASK

if MASTER.exists():
    shutil.rmtree(MASTER)
MASTER.mkdir(parents=True)

initial_count = 6000
true_churn_ids = set(np.random.choice(np.arange(initial_count), size=180, replace=False).tolist())
remaining = np.array(sorted(set(range(initial_count)) - true_churn_ids))
migration_ids = set(np.random.choice(remaining, size=300, replace=False).tolist())
plans = ["CORE", "PLUS", "FAMILY", "WEEKEND"]
rows = []
next_contract = 1

def contract_id():
    global next_contract
    value = f"SQM-{next_contract:07d}"
    next_contract += 1
    return value

for i in range(initial_count):
    payer = f"PAY-{i:08d}"
    postal = f"H{(i * 7919) % 99991:05d}"
    # A few households legitimately share a payer token, so token duplication alone
    # is not an identity rule.
    if i > 0 and i % 53 == 0:
        payer = f"PAY-{i - 1:08d}"
    start = pd.Timestamp("2024-01-01") + pd.Timedelta(days=int((i * 17) % 880))
    end = None
    if i in true_churn_ids or i in migration_ids:
        end = pd.Timestamp("2026-07-02") + pd.Timedelta(days=int((i * 7) % 28))
    rows.append({
        "contract_id": contract_id(),
        "contract_start": start.strftime("%Y-%m-%d"),
        "contract_end": "" if end is None else end.strftime("%Y-%m-%d"),
        "plan_code": plans[i % len(plans)],
        "monthly_fee": [39, 59, 79, 49][i % 4],
        "payer_fingerprint": payer,
        "postal_hash": postal,
    })
    if i in migration_ids:
        rows.append({
            "contract_id": contract_id(),
            "contract_start": end.strftime("%Y-%m-%d"),
            "contract_end": "",
            "plan_code": plans[(i + 1) % len(plans)],
            "monthly_fee": [39, 59, 79, 49][(i + 1) % 4],
            "payer_fingerprint": payer,
            "postal_hash": postal,
        })

# Ordinary first-time July joins are not in the July 1 base.
for j in range(2000):
    start = pd.Timestamp("2026-07-02") + pd.Timedelta(days=j % 29)
    rows.append({
        "contract_id": contract_id(),
        "contract_start": start.strftime("%Y-%m-%d"),
        "contract_end": "",
        "plan_code": plans[j % len(plans)],
        "monthly_fee": [39, 59, 79, 49][j % 4],
        "payer_fingerprint": f"NEWPAY-{j:07d}",
        "postal_hash": f"N{(j * 3571) % 99991:05d}",
    })

contracts = pd.DataFrame(rows).sort_values(["contract_start", "contract_id"]).reset_index(drop=True)
contracts.to_csv(MASTER / "membership_contracts_july.csv", index=False, lineterminator="\n")

(MASTER / "README.md").write_text(
    """# Sequoia Movement Club — July membership export

`membership_contracts_july.csv` is the July 31 billing-contract history for the club's four membership plans. Each row is one contract opened in the billing system. Blank `contract_end` values were still open at export; `payer_fingerprint` and `postal_hash` are non-reversible billing controls.

The club permits one payer to cover more than one household member.
""",
    encoding="utf-8",
)

raw = pd.read_csv(MASTER / "membership_contracts_july.csv", dtype={"contract_end": "string"})
raw["contract_start"] = pd.to_datetime(raw["contract_start"])
raw["contract_end"] = pd.to_datetime(raw["contract_end"], errors="coerce")
base = raw[raw["contract_start"] <= "2026-07-01"].copy()

# Habitual path: a July-ended contract is a churned membership.
ended_by_august = base["contract_end"].notna() & (base["contract_end"] < "2026-08-01")
naive_answer = round(100.0 * float(ended_by_august.mean()), 1)

# Careful path: same-day close/open pairs with both billing controls unchanged are plan migrations.
new_contracts = raw[raw["contract_start"] > "2026-07-01"]
replacement_keys = set(
    zip(
        new_contracts["contract_start"].dt.strftime("%Y-%m-%d"),
        new_contracts["payer_fingerprint"],
        new_contracts["postal_hash"],
    )
)
is_continuation = base.apply(
    lambda r: False if pd.isna(r["contract_end"]) else (
        r["contract_end"].strftime("%Y-%m-%d"), r["payer_fingerprint"], r["postal_hash"]
    ) in replacement_keys,
    axis=1,
)
true_churn = ended_by_august & ~is_continuation
correct_answer = round(100.0 * float(true_churn.mean()), 1)

assert len(raw) == initial_count + 300 + 2000
assert len(base) == initial_count
assert int(ended_by_august.sum()) == 480
assert int(is_continuation.sum()) == 300
assert int(true_churn.sum()) == 180
assert naive_answer == 8.0
assert correct_answer == 3.0

answer_key = {
    "task": TASK,
    "mechanism": "Same-day plan migrations close one billing contract and open another without ending the underlying membership.",
    "planted_answer": naive_answer,
    "correct_answer": correct_answer,
    "tolerance": 0.05,
}
(BASE / "answer_key.json").write_text(
    json.dumps(answer_key, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)

print(json.dumps(answer_key, sort_keys=True))
