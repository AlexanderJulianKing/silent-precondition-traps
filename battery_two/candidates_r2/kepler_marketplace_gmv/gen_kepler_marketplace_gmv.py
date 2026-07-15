from pathlib import Path
import json
import random
import shutil

import numpy as np
import pandas as pd


random.seed(78101)
np.random.seed(78101)

TASK = "kepler_marketplace_gmv"
BASE = Path(__file__).resolve().parent
MASTER = BASE / "masters" / TASK

if MASTER.exists():
    shutil.rmtree(MASTER)
MASTER.mkdir(parents=True)

currencies = ["USD", "EUR", "GBP", "CAD"]
currency_p = [0.30, 0.30, 0.28, 0.12]
skus = [f"KM-{i:04d}" for i in range(1, 51)]
base_price = {sku: round(18.0 + i * 1.85 + (i % 7) * 2.4, 2) for i, sku in enumerate(skus)}
discounts = {"NONE": 0.0, "WELCOME": 0.10, "MEMBER": 0.05, "FLASH": 0.15}
rows = []

for i in range(1, 9201):
    day = 1 + ((i * 19) % 31)
    sku = skus[int(np.random.randint(0, len(skus)))]
    qty = int(np.random.choice([1, 1, 1, 2, 2, 3]))
    promo = str(np.random.choice(list(discounts), p=[0.60, 0.13, 0.20, 0.07]))
    # The marketplace order service stores merchant-ledger USD while retaining the
    # shopper's selected checkout currency as order context.
    amount = round(base_price[sku] * qty * (1.0 - discounts[promo]), 2)
    currency = str(np.random.choice(currencies, p=currency_p))
    rows.append({
        "order_id": f"KPL-{i:07d}",
        "order_date": f"2026-10-{day:02d}",
        "market": ["US", "EU", "UK", "CA"][currencies.index(currency)],
        "sku": sku,
        "quantity": qty,
        "promo_code": promo,
        "order_amount": amount,
        "currency": currency,
        "status": "PAID" if np.random.random() > 0.026 else "CANCELLED",
    })

orders = pd.DataFrame(rows).sort_values(["order_date", "order_id"]).reset_index(drop=True)
orders.to_csv(MASTER / "october_marketplace_orders.csv", index=False, lineterminator="\n", float_format="%.2f")

fx_rows = []
for day in range(1, 32):
    wobble = math_sin = float(np.sin(day / 4.2))
    rates = {
        "USD": 1.0,
        "EUR": 1.085 + 0.008 * wobble,
        "GBP": 1.265 + 0.010 * wobble,
        "CAD": 0.742 + 0.006 * wobble,
    }
    for currency in currencies:
        fx_rows.append({
            "rate_date": f"2026-10-{day:02d}",
            "currency": currency,
            "usd_per_currency_unit": round(rates[currency], 6),
        })
fx = pd.DataFrame(fx_rows)
fx.to_csv(MASTER / "october_treasury_reference.csv", index=False, lineterminator="\n", float_format="%.6f")

(MASTER / "README.md").write_text(
    """# Kepler Handmade Market — October order archive

- `october_marketplace_orders.csv`: checkout orders with SKU, quantity, promotion, order amount, market, and checkout currency retained by the order service.
- `october_treasury_reference.csv`: the daily USD treasury reference used by finance for foreign-currency reporting.

Cancelled orders were not charged. Shipping, tax, and seller fees are outside `order_amount`.
""",
    encoding="utf-8",
)

raw = pd.read_csv(MASTER / "october_marketplace_orders.csv")
paid = raw[raw["status"] == "PAID"].copy()
rates = pd.read_csv(MASTER / "october_treasury_reference.csv")

# Habitual path: treat order_amount as denominated by the adjacent currency and convert.
converted = paid.merge(rates, left_on=["order_date", "currency"], right_on=["rate_date", "currency"], validate="many_to_one")
naive_answer = round(float((converted["order_amount"] * converted["usd_per_currency_unit"]).sum()), 2)

# Careful path: order_amount is already merchant-ledger USD; currency is shopper display context.
correct_answer = round(float(paid["order_amount"].sum()), 2)

# The same SKU/quantity/promo price grid is invariant across all four currencies.
price_variants = paid.groupby(["sku", "quantity", "promo_code"])["order_amount"].nunique()
assert len(raw) == 9200
assert raw["order_id"].is_unique
assert int(price_variants.max()) == 1
assert naive_answer > correct_answer
assert 0.05 < (naive_answer - correct_answer) / correct_answer < 0.10

answer_key = {
    "task": TASK,
    "mechanism": "Checkout currency is presentation metadata while the adjacent order amount is already merchant-ledger USD.",
    "planted_answer": naive_answer,
    "correct_answer": correct_answer,
    "tolerance": 0.005,
}
(BASE / "answer_key.json").write_text(json.dumps(answer_key, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(answer_key, sort_keys=True))
