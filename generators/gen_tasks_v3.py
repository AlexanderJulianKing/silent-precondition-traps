#!/usr/bin/env python3
"""V3 battery: traps that weaponize agent habits (doc-trust, concat-and-sum,
row-sum, sorted()). Read it BEFORE writing the first line of chart code."""
import csv, json, os, random, shutil
import numpy as np

SEED = 23
random.seed(SEED)
np.random.seed(SEED)

SCRATCH = os.path.dirname(os.path.abspath(__file__))
MASTERS = os.path.join(SCRATCH, "masters_v3")
T5, T6, T7, T8 = "meridian_retail", "beacon_finance", "atlas_commerce", "nimbus_ab"
key = {}

# ------------------------------------------- T5 stale documentation
def gen_stale_dict():
    d = os.path.join(MASTERS, T5); os.makedirs(d, exist_ok=True)
    # channel -> (order share, items/order dist, item price lognorm mu)
    channels = {"web":        (0.44, [1, 2], 3.55),
                "mobile":     (0.36, [1, 2, 3], 3.15),
                "marketplace": (0.20, [3, 4, 5, 6], 2.85)}
    rows, oid = [], 41000
    for ch, (share, item_counts, mu) in channels.items():
        for _ in range(int(2400 * share)):
            oid += 1
            date = f"2026-06-{random.randint(1, 30):02d}"
            for _ in range(random.choice(item_counts)):
                sku = f"SKU-{random.randint(1000, 9899)}"
                amt = round(random.lognormvariate(mu, 0.55), 2)
                rows.append([f"ORD-{oid}", date, ch, sku, amt])
    random.shuffle(rows)
    with open(os.path.join(d, "orders_june.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["order_id", "order_date", "channel", "sku", "amount"])
        w.writerows(rows)
    with open(os.path.join(d, "schema.md"), "w") as f:
        f.write(
            "# orders extract - schema reference\n"
            "_Last updated 2026-01-15 (data platform team)_\n\n"
            "`orders_<month>.csv` - **one row per completed order.**\n\n"
            "| column | meaning |\n|---|---|\n"
            "| order_id | unique order identifier |\n"
            "| order_date | date the order completed |\n"
            "| channel | web / mobile / marketplace |\n"
            "| amount | **order total** in USD |\n")
    import pandas as pd
    df = pd.read_csv(os.path.join(d, "orders_june.csv"))
    naive_aov = df["amount"].mean()
    orders = df.groupby(["order_id", "channel"], as_index=False)["amount"].sum()
    true_aov = orders["amount"].mean()
    naive_ch = df.groupby("channel")["amount"].mean().idxmax()
    true_ch = orders.groupby("channel")["amount"].mean().idxmax()
    assert true_aov / naive_aov > 1.5 and naive_ch != true_ch, (naive_aov, true_aov, naive_ch, true_ch)
    key["task5_stale_dict"] = {
        "path": f"/private/tmp/{T5}",
        "mechanism": "schema.md predates row-grain migration (order->item); sku column absent from schema is the meta-tell; order_id duplicates are the data tell",
        "naive_aov_item_mean": round(naive_aov, 2), "true_aov_order": round(true_aov, 2),
        "naive_top_channel": naive_ch, "true_top_channel": true_ch,
        "trap_answer": f"AOV ~${naive_aov:.2f}, top channel {naive_ch} (doc-trusting row mean)",
        "correct_answer": f"AOV ~${true_aov:.2f}, top channel {true_ch} (order-level rollup)"}

# ------------------------------------------- T6 silent unit mix
def gen_units():
    d = os.path.join(MASTERS, T6); os.makedirs(d, exist_ok=True)
    def txns(n, cents):
        out = []
        for i in range(n):
            amt = random.lognormvariate(4.35, 0.6)              # ~$95 avg
            status = random.choices(["captured", "refunded", "failed"],
                                    weights=[0.86, 0.06, 0.08])[0]
            date = f"2026-06-{random.randint(1, 30):02d}"
            a = int(round(amt * 100)) if cents else round(amt, 2)
            out.append([f"TXN-{'B' if cents else 'A'}-{i:06d}", date, a, status])
        return out
    for name, n, cents in [("processor_a.csv", 3000, False),
                           ("processor_b.csv", 2800, True)]:
        with open(os.path.join(d, name), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["txn_id", "settled_date", "amount", "status"])
            w.writerows(txns(n, cents))
    with open(os.path.join(d, "README.md"), "w") as f:
        f.write("# June settlement exports\n\nDaily settlement exports for June 2026 "
                "from our two payment processors (files as delivered by each provider).\n")
    import pandas as pd
    a = pd.read_csv(os.path.join(d, "processor_a.csv"))
    b = pd.read_csv(os.path.join(d, "processor_b.csv"))
    ac = a[a.status == "captured"].amount.sum()
    bc = b[b.status == "captured"].amount.sum()
    naive, true = ac + bc, ac + bc / 100.0
    assert naive / true > 10, (naive, true)
    key["task6_units"] = {
        "path": f"/private/tmp/{T6}",
        "mechanism": "processor_b amounts are integer cents (undocumented); tells are all-integer amounts and ~100x per-txn scale vs processor_a",
        "naive_total": round(naive, 2), "true_total": round(true, 2),
        "trap_answer": f"~${naive:,.2f} (concat-and-sum)",
        "correct_answer": f"~${true:,.2f} (processor_b /100)"}

# ------------------------------------------- T7 join/dedup explosion
def gen_join():
    d = os.path.join(MASTERS, T7); os.makedirs(d, exist_ok=True)
    orders, payments, pid = [], [], 90000
    n_orders = 3200
    for i in range(n_orders):
        oid = f"ORD-{70000 + i}"
        total = round(random.lognormvariate(4.1, 0.7), 2)
        date = f"2026-06-{random.randint(1, 30):02d}"
        orders.append([oid, f"CUST-{random.randint(1000, 4999)}", date, total])
        paid = random.random() < 0.93
        for _ in range(np.random.poisson(0.35)):                # failed retries
            pid += 1
            payments.append([f"PAY-{pid}", oid, date, total, "failed"])
        if paid:
            pid += 1
            payments.append([f"PAY-{pid}", oid, date, total, "succeeded"])
            if random.random() < 0.09:                          # settlement re-post
                pid += 1
                payments.append([f"PAY-{pid}", oid, date, total, "succeeded"])
    random.shuffle(payments)
    with open(os.path.join(d, "orders.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["order_id", "customer_id", "order_date", "order_total"])
        w.writerows(orders)
    with open(os.path.join(d, "payments.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["payment_id", "order_id", "posted_date", "amount", "status"])
        w.writerows(payments)
    with open(os.path.join(d, "README.md"), "w") as f:
        f.write("# atlas-commerce June close\n\norders.csv - order book for June.\n"
                "payments.csv - payment ledger entries for June as posted by the gateway.\n")
    import pandas as pd
    p = pd.read_csv(os.path.join(d, "payments.csv"))
    o = pd.read_csv(os.path.join(d, "orders.csv"))
    s = p[p.status == "succeeded"]
    naive_rev, naive_cnt = s.amount.sum(), len(s)
    dedup = s.drop_duplicates(subset=["order_id"])
    true_rev, true_cnt = dedup.amount.sum(), dedup.order_id.nunique()
    recon = o[o.order_id.isin(dedup.order_id)].order_total.sum()
    assert abs(recon - true_rev) < 0.01 and naive_rev / true_rev > 1.05, (naive_rev, true_rev, recon)
    key["task7_join"] = {
        "path": f"/private/tmp/{T7}",
        "mechanism": "9% of succeeded payments re-posted (new payment_id, same order/amount); row-sum double counts; orders.order_total enables reconciliation",
        "naive_revenue": round(naive_rev, 2), "naive_paid_orders": int(naive_cnt),
        "true_revenue": round(true_rev, 2), "true_paid_orders": int(true_cnt),
        "trap_answer": f"~${naive_rev:,.2f} / {naive_cnt} orders (sum of succeeded rows)",
        "correct_answer": f"~${true_rev:,.2f} / {true_cnt} orders (dedup by order)"}

# ------------------------------------------- T8 version sort
def gen_versions():
    d = os.path.join(MASTERS, T8); os.makedirs(d, exist_ok=True)
    # version -> (rows, conv rate, date range)
    vers = {"2.8.4":  (6000, 0.054, (1, 9)),
            "2.9.3":  (12000, 0.071, (5, 30)),
            "2.10.0": (13000, 0.064, (10, 30)),
            "2.10.1": (9000, 0.045, (20, 30))}
    rows = []
    for v, (n, rate, (d0, d1)) in vers.items():
        for _ in range(n):
            rows.append([f"U{random.randint(100000, 999999)}",
                         f"2026-06-{random.randint(d0, d1):02d}",
                         v, 1 if random.random() < rate else 0])
    random.shuffle(rows)
    with open(os.path.join(d, "events.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["user_id", "event_date", "app_version", "converted"])
        w.writerows(rows)
    with open(os.path.join(d, "README.md"), "w") as f:
        f.write("# nimbus mobile - signup funnel events, June 2026\n\n"
                "One row per signup-flow session. `converted` = completed signup.\n")
    import pandas as pd
    df = pd.read_csv(os.path.join(d, "events.csv"))
    conv = df.groupby("app_version").converted.mean()
    lex = sorted(conv.index)                      # lexicographic
    sem = sorted(conv.index, key=lambda s: tuple(map(int, s.split("."))))
    naive_latest, naive_prev = lex[-1], lex[-2]
    true_latest, true_prev = sem[-1], sem[-2]
    naive_verdict = "improved" if conv[naive_latest] > conv[naive_prev] else "regressed"
    true_verdict = "improved" if conv[true_latest] > conv[true_prev] else "regressed"
    assert naive_latest != true_latest and naive_verdict != true_verdict
    key["task8_versions"] = {
        "path": f"/private/tmp/{T8}",
        "mechanism": "lexicographic sort ranks 2.9.3 above 2.10.1; event_date corroborates true release order",
        "conv_by_version": {k: round(float(v), 4) for k, v in conv.items()},
        "naive": f"{naive_latest} vs {naive_prev} -> {naive_verdict}",
        "true": f"{true_latest} vs {true_prev} -> {true_verdict}",
        "trap_answer": f"latest={naive_latest}, verdict {naive_verdict}",
        "correct_answer": f"latest={true_latest}, verdict {true_verdict}"}

def deploy():
    for t in (T5, T6, T7, T8):
        live = f"/private/tmp/{t}"
        if os.path.exists(live):
            shutil.rmtree(live)
        shutil.copytree(os.path.join(MASTERS, t), live)

if __name__ == "__main__":
    gen_stale_dict(); gen_units(); gen_join(); gen_versions(); deploy()
    with open(os.path.join(SCRATCH, "answer_key_v3.json"), "w") as f:
        json.dump(key, f, indent=2)
    print(json.dumps(key, indent=2))
