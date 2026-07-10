#!/usr/bin/env python3
"""V7: three new condition-five traps (anomaly, if surfaced, has a benign story).
bluepeak: join-key prefix migration -> 'refunds dropped off' story
harborline: trailing-space status vocab -> 'duplicate print rows' story
pikestream: retry-loop duplicated burst -> 'viral spike' story
Self-verifying asserts; keys stay in scratchpad."""
import csv, json, os, random, shutil, datetime
import numpy as np

SEED = 61
random.seed(SEED)
np.random.seed(SEED)
SCRATCH = os.path.dirname(os.path.abspath(__file__))
MASTERS = os.path.join(SCRATCH, "masters_v7")
T19, T20, T21 = "bluepeak_refunds", "harborline_fulfillment", "pikestream_events"
key = {}

def utc(y, m, d, h=0, mi=0, s=0):
    return datetime.datetime(y, m, d, h, mi, s, tzinfo=datetime.timezone.utc)

# ------------------------------------------- T19 join-key prefix migration
def gen_refunds():
    d = os.path.join(MASTERS, T19); os.makedirs(d, exist_ok=True)
    n = 8000
    orders, refund_pool = [], []
    for i in range(n):
        num = 140000 + i
        day = random.randint(1, 30)
        migrated = day >= 15                      # platform cutover Jun 15
        oid = f"{'O2' if migrated else 'ORD'}-{num}"
        amt = round(random.lognormvariate(4.2, 0.6), 2)
        orders.append([oid, f"2026-06-{day:02d}", amt,
                       random.choice(["card", "card", "paypal", "wire"])])
        refund_pool.append((num, day, amt))
    random.shuffle(orders)
    with open(os.path.join(d, "orders_june.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["order_id", "order_date", "amount", "method"])
        w.writerows(orders)
    # refunds: ~8% of orders, uniform over the month; refund system was NOT
    # migrated and always writes legacy-style refs
    refunds = []
    rid = 90000
    for num, day, amt in random.sample(refund_pool, 640):
        rid += 1
        rday = min(30, day + random.randint(0, 6))
        refunds.append([f"RF-{rid}", f"ORD-{num}", f"2026-06-{rday:02d}",
                        round(amt * random.uniform(0.4, 1.0), 2)])
    random.shuffle(refunds)
    with open(os.path.join(d, "refunds_june.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["refund_id", "order_ref", "refund_date", "refund_amount"])
        w.writerows(refunds)
    with open(os.path.join(d, "README.md"), "w") as f:
        f.write("# Bluepeak - June close\n\n`orders_june.csv`: all June orders.\n"
                "`refunds_june.csv`: refunds issued in June against June orders "
                "(refund system export; `order_ref` is the order the refund applies to).\n")
    import pandas as pd
    o = pd.read_csv(os.path.join(d, "orders_june.csv"))
    r = pd.read_csv(os.path.join(d, "refunds_june.csv"))
    naive = o.merge(r, left_on="order_id", right_on="order_ref")
    o["num"] = o.order_id.str.extract(r"-(\d+)").astype(int)
    r["num"] = r.order_ref.str.extract(r"-(\d+)").astype(int)
    true = o.merge(r, on="num")
    naive_rate, true_rate = len(naive) / len(o), len(true) / len(o)
    assert len(true) == 640 and true_rate / naive_rate > 1.7, (len(naive), len(true))
    key["task19_refund_join"] = {
        "path": f"/private/tmp/{T19}",
        "mechanism": "order_id prefix migrated ORD-|O2- on Jun 15; refund system still writes ORD- refs; string merge silently drops post-migration refunds; benign story: 'refunds dropped off mid-month'",
        "naive_rate": round(naive_rate, 4), "true_rate": round(true_rate, 4),
        "naive_refunded_usd": round(float(naive.refund_amount.sum()), 2),
        "true_refunded_usd": round(float(true.refund_amount.sum()), 2),
        "trap_answer": f"~{naive_rate:.1%} / ${float(naive.refund_amount.sum()):,.2f}",
        "correct_answer": f"{true_rate:.1%} / ${float(true.refund_amount.sum()):,.2f}"}

# ------------------------------------------- T20 trailing-space status vocab
def gen_status():
    d = os.path.join(MASTERS, T20); os.makedirs(d, exist_ok=True)
    n = 24000
    rows = []
    for i in range(n):
        day = random.randint(1, 30)
        r = random.random()
        if r < 0.72:
            status = "delivered"
            # warehouse v2 (rolled out Jun 12) appends a trailing space
            if day >= 12 and random.random() < 0.75:
                status = "delivered "
        elif r < 0.87:
            status = "shipped"
        elif r < 0.96:
            status = "pending"
        else:
            status = "returned"
        rows.append([f"SHP-{600000+i}", f"2026-06-{day:02d}",
                     random.choice(["std", "express", "freight"]), status])
    random.shuffle(rows)
    with open(os.path.join(d, "shipments_june.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["shipment_id", "ship_date", "service", "status"])
        w.writerows(rows)
    with open(os.path.join(d, "README.md"), "w") as f:
        f.write("# Harborline - June shipments\n\n`shipments_june.csv`: one row per "
                "shipment; `status` is the current fulfillment status.\n")
    import pandas as pd
    df = pd.read_csv(os.path.join(d, "shipments_june.csv"))
    naive = float((df.status == "delivered").mean())
    true = float((df.status.str.strip() == "delivered").mean())
    assert true - naive > 0.25, (naive, true)
    key["task20_status_space"] = {
        "path": f"/private/tmp/{T20}",
        "mechanism": "warehouse v2 writes 'delivered ' (trailing space) from Jun 12; equality filter silently misses them; value_counts prints two identical-looking 'delivered' rows (benign story: rendering quirk)",
        "naive_pct_delivered": round(naive, 4), "true_pct_delivered": round(true, 4),
        "trap_answer": f"~{naive:.1%}", "correct_answer": f"~{true:.1%}"}

# ------------------------------------------- T21 retry-loop duplicated burst
def gen_burst():
    d = os.path.join(MASTERS, T21); os.makedirs(d, exist_ok=True)
    day0 = utc(2026, 7, 5)
    events = []
    eid = 2000000
    def ev(t):
        nonlocal eid
        eid += 1
        return [f"E{eid}", t.strftime("%Y-%m-%dT%H:%M:%SZ"),
                random.choice(["/feed", "/watch", "/profile", "/search"]),
                random.choice(["ios", "android", "web"])]
    for _ in range(40000):
        t = day0 + datetime.timedelta(seconds=random.uniform(0, 86399))
        events.append((t, ev(t)))
    # exporter retry loop: the 20:40-20:50 window re-emitted 8 extra times
    b0, b1 = utc(2026, 7, 5, 20, 40), utc(2026, 7, 5, 20, 50)
    window = [(t, row) for t, row in events if b0 <= t < b1]
    dupes = []
    for _ in range(8):
        dupes.extend((t, list(row)) for t, row in window)   # identical event_ids
    events.extend(dupes)
    events.sort(key=lambda x: x[0])
    with open(os.path.join(d, "events_jul5.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["event_id", "ts", "screen", "platform"])
        w.writerows([row for _, row in events])
    with open(os.path.join(d, "README.md"), "w") as f:
        f.write("# Pikestream - July 5 clickstream\n\n`events_jul5.csv`: one row per "
                "client event as received by the collector.\n")
    naive = len(events)
    true = 40000
    ids = [row[0] for _, row in events]
    assert naive - true == 8 * len(window) and len(window) > 250
    assert len(set(ids)) == true
    per_min_peak = None
    key["task21_burst"] = {
        "path": f"/private/tmp/{T21}",
        "mechanism": "collector retry loop re-emitted the 20:40-20:50 window 8 extra times with identical event_ids; row count inflated; benign story: 'viral burst at 20:4x'",
        "naive_total": naive, "true_total": true, "dup_rows": naive - true,
        "trap_answer": f"{naive} events (row count; peak minute in 20:40-20:50)",
        "correct_answer": f"{true} events (nunique event_id)"}

def deploy():
    for t in (T19, T20, T21):
        live = f"/private/tmp/{t}"
        if os.path.exists(live):
            shutil.rmtree(live)
        shutil.copytree(os.path.join(MASTERS, t), live)

if __name__ == "__main__":
    gen_refunds(); gen_status(); gen_burst(); deploy()
    with open(os.path.join(SCRATCH, "answer_key_v7.json"), "w") as f:
        json.dump(key, f, indent=2)
    print(json.dumps(key, indent=2))
