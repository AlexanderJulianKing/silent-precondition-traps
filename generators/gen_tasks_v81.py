#!/usr/bin/env python3
"""V8.1: redesigns of the three condition-violating tasks, self-grounding
(no doc hints; truth derivable from data invariants alone)."""
import csv, json, os, random, shutil, datetime
import numpy as np

SEED = 83
random.seed(SEED)
np.random.seed(SEED)
SCRATCH = os.path.dirname(os.path.abspath(__file__))
MASTERS = os.path.join(SCRATCH, "masters_v81")
T24b, T25b, T26b = "granitepeak_billing", "larkfield_stream", "cobaltworks_sales"
key = {}

def utc(y, m, d, h=0, mi=0, s=0):
    return datetime.datetime(y, m, d, h, mi, s, tzinfo=datetime.timezone.utc)

# ------------------------------------------ T24b trailing-space join keys
def gen_trailspace_join():
    d = os.path.join(MASTERS, T24b); os.makedirs(d, exist_ok=True)
    n = 7000
    invoices, payments = [], []
    for i in range(n):
        num = 61000 + i
        day = random.randint(1, 30)
        amt = round(random.lognormvariate(4.6, 0.7), 2)
        invoices.append([f"INV-{num:07d}", f"2026-06-{day:02d}", amt])
        if random.random() < 0.83:
            pday = min(30, day + random.randint(0, 5))
            # billing template update Jun 18: refs carry a trailing space after
            ref = f"INV-{num:07d}" + (" " if pday >= 18 else "")
            payments.append([f"PMT-{300000+len(payments)}", ref,
                             f"2026-06-{pday:02d}", amt])
    random.shuffle(invoices); random.shuffle(payments)
    with open(os.path.join(d, "invoices_june.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["invoice_id", "issued_date", "amount"])
        w.writerows(invoices)
    with open(os.path.join(d, "payments_june.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["payment_id", "invoice_ref", "paid_date", "amount"])
        w.writerows(payments)
    with open(os.path.join(d, "README.md"), "w") as f:
        f.write("# Granitepeak - June billing\n\n`invoices_june.csv`: invoices issued "
                "in June. `payments_june.csv`: payments received in June; `invoice_ref` "
                "is the invoice the payment settles.\n")
    import pandas as pd
    inv = pd.read_csv(os.path.join(d, "invoices_june.csv"))
    pay = pd.read_csv(os.path.join(d, "payments_june.csv"))
    naive = inv.merge(pay, left_on="invoice_id", right_on="invoice_ref")
    true = inv.merge(pay.assign(k=pay.invoice_ref.str.strip()),
                     left_on="invoice_id", right_on="k")
    nr, tr = len(naive) / len(inv), len(true) / len(inv)
    assert tr > 0.80 and nr < 0.60 and len(true) == len(pay)
    # verify the tell is print-invisible: repr of head differs only by the space
    key["task24b_trailspace_join"] = {
        "path": f"/private/tmp/{T24b}", "class": "silent-drop join (self-grounding)",
        "naive_paid_rate": round(nr, 4), "true_paid_rate": round(tr, 4),
        "naive_collected": round(float(naive.amount_y.sum()), 2),
        "true_collected": round(float(true.amount_y.sum()), 2),
        "trap_answer": f"~{nr:.1%} / ${float(naive.amount_y.sum()):,.2f}",
        "correct_answer": f"{tr:.1%} / ${float(true.amount_y.sum()):,.2f}"}

# ------------------------------------------ T25b re-stamped replay, terse docs
def gen_restamped_terse():
    d = os.path.join(MASTERS, T25b); os.makedirs(d, exist_ok=True)
    day0 = utc(2026, 7, 6)
    users = [f"U{80000+i}" for i in range(2600)]
    seq = {u: 0 for u in users}
    base = []
    for _ in range(40000):
        t = day0 + datetime.timedelta(seconds=random.uniform(0, 86399))
        u = random.choice(users)
        seq[u] += 1
        base.append((t, u, seq[u], random.choice(["/feed", "/watch", "/profile", "/dm"])))
    base.sort(key=lambda x: x[0])
    b0, b1 = utc(2026, 7, 6, 21, 12), utc(2026, 7, 6, 21, 26)
    replay = [(t + datetime.timedelta(seconds=90), u, s, sc)
              for t, u, s, sc in base if b0 <= t < b1]
    allrows = sorted(base + replay, key=lambda x: x[0])
    rows, eid = [], 5000000
    for t, u, s, sc in allrows:
        eid += 1
        rows.append([f"E{eid}", t.strftime("%Y-%m-%dT%H:%M:%SZ"), u, s, sc])
    with open(os.path.join(d, "events_jul6.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["event_id", "ts", "user_id", "client_seq", "screen"])
        w.writerows(rows)
    with open(os.path.join(d, "README.md"), "w") as f:
        f.write("# Larkfield - July 6 clickstream\n\n`events_jul6.csv`: one row per "
                "client event as ingested. Columns: event_id, ts, user_id, client_seq "
                "(device event counter), screen.\n")
    import pandas as pd
    df = pd.read_csv(os.path.join(d, "events_jul6.csv"))
    assert df.event_id.nunique() == len(df)
    true = df.drop_duplicates(["user_id", "client_seq"]).shape[0]
    assert len(df) - true == len(replay) and len(replay) > 350
    key["task25b_restamp_terse"] = {
        "path": f"/private/tmp/{T25b}", "class": "duplication, check-defeating (terse docs)",
        "naive_total": len(df), "true_total": true, "replayed": len(replay),
        "trap_answer": f"{len(df)}", "correct_answer": f"{true}"}

# ------------------------------------------ T26b net/gross swap, de-documented
def gen_netgross_quiet():
    d = os.path.join(MASTERS, T26b); os.makedirs(d, exist_ok=True)
    rows = []
    for i in range(16000):
        day = random.randint(1, 30)
        gross = round(random.lognormvariate(4.3, 0.7), 2)
        net = round(gross * random.uniform(0.55, 0.75), 2)
        if 19 <= day <= 22:                              # ~13% of rows
            gross, net = net, gross
        rows.append([f"CW-{700000+i}", f"2026-06-{day:02d}",
                     random.choice(["wholesale", "outlet", "online"]), gross, net])
    random.shuffle(rows)
    with open(os.path.join(d, "sales_june.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sale_id", "sale_date", "channel", "gross_usd", "net_usd"])
        w.writerows(rows)
    with open(os.path.join(d, "README.md"), "w") as f:
        f.write("# Cobaltworks - June sales\n\n`sales_june.csv`: one row per sale. "
                "`gross_usd` is the sale price; `net_usd` is revenue net of partner "
                "margin and fees.\n")
    import pandas as pd
    df = pd.read_csv(os.path.join(d, "sales_june.csv"))
    naive = float(df.net_usd.sum())
    true = float(df[["gross_usd", "net_usd"]].min(axis=1).sum())
    swapped = int((df.net_usd > df.gross_usd).sum())
    assert 0.03 < (naive - true) / true < 0.09 and 1800 < swapped < 2600
    key["task26b_netgross_quiet"] = {
        "path": f"/private/tmp/{T26b}", "class": "cross-column invariant (de-documented)",
        "naive_net_sum": round(naive, 2), "true_net_sum": round(true, 2),
        "swapped_rows": swapped,
        "trap_answer": f"~${naive:,.2f}", "correct_answer": f"~${true:,.2f}"}

def deploy():
    for t in (T24b, T25b, T26b):
        live = f"/private/tmp/{t}"
        if os.path.exists(live):
            shutil.rmtree(live)
        shutil.copytree(os.path.join(MASTERS, t), live)

if __name__ == "__main__":
    gen_trailspace_join(); gen_restamped_terse(); gen_netgross_quiet(); deploy()
    with open(os.path.join(SCRATCH, "answer_key_v81.json"), "w") as f:
        json.dump(key, f, indent=2)
    print(json.dumps(key, indent=2))
