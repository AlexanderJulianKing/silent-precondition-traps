#!/usr/bin/env python3
"""V6 generalization battery: same mechanism (silently violated instrument
precondition, hidden from habitual sampling, plausible wrong output), five
different instruments. Self-verifying asserts for both the trap and the truth."""
import csv, gzip, json, os, random, shutil, datetime
import numpy as np

SEED = 53
random.seed(SEED)
np.random.seed(SEED)
SCRATCH = os.path.dirname(os.path.abspath(__file__))
MASTERS = os.path.join(SCRATCH, "masters_v6")
T14, T15, T16, T17, T18 = ("crestline_growth", "pulsepay_events",
                           "relaycdn_ops", "cascade_commerce", "vertexweb_analytics")
key = {}

def utc(y, m, d, h=0, mi=0, s=0):
    return datetime.datetime(y, m, d, h, mi, s, tzinfo=datetime.timezone.utc)

# ---------------------------------------------- T14 pandas na_values ("NA" region)
def gen_na_region():
    d = os.path.join(MASTERS, T14); os.makedirs(d, exist_ok=True)
    regions = [("NA", 0.38), ("EMEA", 0.27), ("APAC", 0.22), ("LATAM", 0.13)]
    rows = []
    for i in range(9000):
        r = random.random(); acc = 0
        for reg, w in regions:
            acc += w
            if r < acc: break
        rows.append([f"SGN-{300000+i}", f"2026-06-{random.randint(1,30):02d}",
                     reg, random.choice(["starter", "growth", "scale"])])
    random.shuffle(rows)
    with open(os.path.join(d, "signups_june.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["signup_id", "signup_date", "region", "plan"])
        w.writerows(rows)
    with open(os.path.join(d, "README.md"), "w") as f:
        f.write("# Crestline - June signups\n\n`signups_june.csv`: one row per new "
                "signup. `region` is the billing region assigned at signup.\n")
    import pandas as pd
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("error")            # prove the naive read is silent
        df = pd.read_csv(os.path.join(d, "signups_june.csv"))
    naive_counts = df.region.value_counts()       # NaN rows invisible
    true_counts = df.region.fillna("NA").value_counts()
    assert df.region.isna().sum() > 3000
    assert naive_counts.idxmax() == "EMEA" and true_counts.idxmax() == "NA"
    key["task14_na_region"] = {
        "path": f"/private/tmp/{T14}",
        "mechanism": "region code 'NA' is in pandas default na_values -> NaN; groupby/value_counts silently drop it; head of raw file shows NA plainly",
        "naive_top": f"EMEA ({int(naive_counts.max())})",
        "true_top": f"NA ({int(true_counts.max())})",
        "trap_answer": f"EMEA with {int(naive_counts.max())} signups",
        "correct_answer": f"NA with {int(true_counts.max())} signups"}

# ---------------------------------------------- T15 JSONL field rename mid-stream
def gen_jsonl_rename():
    d = os.path.join(MASTERS, T15); os.makedirs(d, exist_ok=True)
    n = 30000
    cut = int(n * 0.55)                            # v2 rollout Jun 17
    recs = []
    for i in range(n):
        day = random.randint(1, 16) if i < cut else random.randint(17, 30)
        ts = utc(2026, 6, day, random.randint(0, 23), random.randint(0, 59),
                 random.randint(0, 59)).strftime("%Y-%m-%dT%H:%M:%SZ")
        amt = round(random.lognormvariate(3.4, 0.6), 2)
        rec = {"event_id": f"EV{800000+i}", "ts": ts, "type": "purchase"}
        if i < cut:
            rec["amount"] = amt
        else:
            rec["amount_usd"] = amt                # payments-service v2 field name
        recs.append((ts, rec))
    recs.sort(key=lambda x: x[0])
    with open(os.path.join(d, "events.jsonl"), "w") as f:
        for _, r in recs:
            f.write(json.dumps(r) + "\n")
    with open(os.path.join(d, "README.md"), "w") as f:
        f.write("# PulsePay - June purchase events\n\n`events.jsonl`: one JSON object "
                "per purchase event, as emitted by the payments service.\n")
    import pandas as pd
    df = pd.read_json(os.path.join(d, "events.jsonl"), lines=True)
    naive = float(df["amount"].sum())              # NaN-skipping, silent
    true = float(df["amount"].fillna(df["amount_usd"]).sum())
    assert (true - naive) / true > 0.30
    key["task15_jsonl_rename"] = {
        "path": f"/private/tmp/{T15}",
        "mechanism": "field renamed amount->amount_usd at v2 rollout (Jun 17); sum('amount') NaN-skips 45% of revenue silently",
        "naive_sum": round(naive, 2), "true_sum": round(true, 2),
        "trap_answer": f"~${naive:,.2f}", "correct_answer": f"~${true:,.2f}"}

# ---------------------------------------------- T16 copytruncate overlap
def gen_copytruncate():
    d = os.path.join(MASTERS, T16, "logs"); os.makedirs(d, exist_ok=True)
    paths = ["/edge/asset", "/edge/api", "/edge/img", "/edge/video"]
    def line(t):
        return (f"{random.randint(4,220)}.{random.randint(0,255)}.{random.randint(0,255)}"
                f".{random.randint(1,254)} [{t.strftime('%Y-%m-%dT%H:%M:%SZ')}] "
                f"\"GET {random.choice(paths)}/{random.randint(1,999)} HTTP/1.1\" 200 "
                f"{random.randint(500, 90000)}\n")
    day0 = utc(2026, 7, 7)
    all_lines = []
    for i in range(88000):                          # July 7, 00:00 -> 23:59:59
        t = day0 + datetime.timedelta(seconds=random.uniform(0, 86399))
        all_lines.append((t, line(t)))
    all_lines.sort(key=lambda x: x[0])
    rot = utc(2026, 7, 7, 18, 12, 44)               # rotation moment
    ov0 = rot - datetime.timedelta(minutes=10)      # copytruncate race window
    older = [ln for t, ln in all_lines if t < rot]
    overlap = [ln for t, ln in all_lines if ov0 <= t < rot]   # duplicated verbatim
    newer = [ln for t, ln in all_lines if t >= rot]
    with open(os.path.join(d, "requests.log.1"), "w") as f:
        f.writelines(older)
    with open(os.path.join(d, "requests.log"), "w") as f:
        f.writelines(overlap + newer)               # overlap re-appears at head
    with open(os.path.join(MASTERS, T16, "README.md"), "w") as f:
        f.write("# RelayCDN - edge node request logs\n\nlogs/ holds the current "
                "`requests.log` and the previous rotation `requests.log.1`.\n")
    naive = len(older) + len(overlap) + len(newer)
    true = len(all_lines)
    assert naive - true == len(overlap) and len(overlap) > 400
    key["task16_copytruncate"] = {
        "path": f"/private/tmp/{T16}",
        "mechanism": "copytruncate rotation duplicated the 10 min before 18:12:44 verbatim in both files; files are not disjoint; per-file time ranges overlap",
        "naive_total": naive, "true_total": true, "dup_lines": len(overlap),
        "trap_answer": f"{naive} requests (sum of both files)",
        "correct_answer": f"{true} requests (dedup the overlap window)"}

# ---------------------------------------------- T17 unsorted first-purchase
def gen_first_purchase():
    d = os.path.join(MASTERS, T17); os.makedirs(d, exist_ok=True)
    n_users = 6000
    both = int(n_users * 0.70)                      # longtime customers
    new_rows, legacy_rows = [], []
    oid = 500000
    for u in range(n_users):
        uid = f"CU{10000+u}"
        if u < both:
            # true first order: legacy era, promo-heavy launch campaign
            t = utc(2024, random.randint(1, 12), random.randint(1, 28))
            promo = random.random() < 0.55
            legacy = [(uid, t, promo)]
            for _ in range(random.randint(0, 2)):   # later legacy orders
                t2 = t + datetime.timedelta(days=random.randint(30, 400))
                if t2 < utc(2025, 9, 1):
                    legacy.append((uid, t2, random.random() < 0.12))
            legacy.sort(key=lambda x: x[1], reverse=True)   # legacy export: desc per user
            legacy_rows.extend(legacy)
            n_new = random.randint(1, 4)
        else:
            n_new = random.randint(1, 3)
        base = utc(2025, 9, 1) + datetime.timedelta(days=random.uniform(0, 280))
        for k in range(n_new):
            t = base + datetime.timedelta(days=30 * k + random.uniform(0, 20))
            promo = random.random() < (0.20 if u >= both else 0.18)
            new_rows.append((uid, t, promo))
    new_rows.sort(key=lambda x: x[1])               # new system: global chrono asc
    rows = []
    for uid, t, promo in new_rows + legacy_rows:    # legacy backfill APPENDED
        oid += 1
        rows.append([f"ORD-{oid}", uid, t.strftime("%Y-%m-%d"),
                     round(random.lognormvariate(4.0, 0.6), 2),
                     "LAUNCH15" if promo else ""])
    with open(os.path.join(d, "orders_all.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["order_id", "customer_id", "order_date", "amount", "promo_code"])
        w.writerows(rows)
    with open(os.path.join(d, "README.md"), "w") as f:
        f.write("# Cascade Commerce - full order history\n\n`orders_all.csv`: every "
                "order since founding (2024), consolidated from the legacy system and "
                "the current platform.\n")
    import pandas as pd
    df = pd.read_csv(os.path.join(d, "orders_all.csv"))
    naive_first = df.drop_duplicates("customer_id", keep="first")
    naive = float((naive_first.promo_code == "LAUNCH15").mean())
    srt = df.sort_values(["order_date", "order_id"]).drop_duplicates("customer_id", keep="first")
    true = float((srt.promo_code == "LAUNCH15").mean())
    assert true - naive > 0.15, (naive, true)
    key["task17_first_purchase"] = {
        "path": f"/private/tmp/{T17}",
        "mechanism": "file = new-system block (chrono asc) + appended legacy backfill (desc per user); keep='first' without sorting picks non-first orders for 70% of users",
        "naive_promo_rate": round(naive, 4), "true_promo_rate": round(true, 4),
        "trap_answer": f"~{naive:.1%}", "correct_answer": f"~{true:.1%}"}

# ---------------------------------------------- T18 epoch window (family replication)
def gen_epoch_window():
    d = os.path.join(MASTERS, T18); os.makedirs(d, exist_ok=True)
    paths = ["/home", "/pricing", "/docs", "/blog", "/signup"]
    E0, E1 = utc(2026, 7, 3, 9), utc(2026, 7, 3, 15)     # exporter-bug window
    rows = []
    vid = 700000
    def add(t):
        nonlocal vid
        vid += 1
        if E0 <= t < E1:
            ts = str(int(t.timestamp()))                  # epoch seconds
        else:
            ts = t.strftime("%Y-%m-%dT%H:%M:%SZ")
        rows.append((t, [f"V{vid}", ts, random.choice(paths)]))
    for _ in range(60000):                                # Jul 2-4 background
        add(utc(2026, 7, 2) + datetime.timedelta(seconds=random.uniform(0, 3 * 86400)))
    for _ in range(9000):                                 # spike inside epoch window
        add(utc(2026, 7, 3, 10) + datetime.timedelta(seconds=random.uniform(0, 3 * 3600)))
    for _ in range(1800):                                 # secondary bump, ISO format
        add(utc(2026, 7, 3, 17) + datetime.timedelta(seconds=random.uniform(0, 3600)))
    rows.sort(key=lambda x: x[0])
    with open(os.path.join(d, "page_views.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["view_id", "ts", "path"])
        w.writerows([r for _, r in rows])
    with open(os.path.join(d, "README.md"), "w") as f:
        f.write("# VertexWeb - page view export\n\n`page_views.csv`: one row per page "
                "view, July 2-4. `ts` is the view timestamp (UTC).\n")
    jul3 = [t for t, _ in rows if utc(2026, 7, 3) <= t < utc(2026, 7, 4)]
    true = len(jul3)
    hours = {}
    for t in jul3:
        hours[t.hour] = hours.get(t.hour, 0) + 1
    true_peak = max(hours, key=hours.get)
    naive = sum(1 for t, r in rows if r[1].startswith("2026-07-03"))
    nh = {}
    for t, r in rows:
        if r[1].startswith("2026-07-03"):
            nh[t.hour] = nh.get(t.hour, 0) + 1
    naive_peak = max(nh, key=nh.get)
    assert (true - naive) / true > 0.30 and true_peak != naive_peak
    key["task18_epoch_window"] = {
        "path": f"/private/tmp/{T18}",
        "mechanism": "ts serialized as epoch seconds 09:00-15:00 Jul 3 (exporter bug, reverted); string-prefix filters and to_datetime(errors='coerce') both silently drop the window; spike inside it",
        "true_views_jul3": true, "true_peak_hour": true_peak,
        "naive_views": naive, "naive_peak_hour": naive_peak,
        "trap_answer": f"~{naive} views, peak {naive_peak}:00",
        "correct_answer": f"{true} views, peak {true_peak}:00"}

def deploy():
    for t in (T14, T15, T16, T17, T18):
        live = f"/private/tmp/{t}"
        if os.path.exists(live):
            shutil.rmtree(live)
        shutil.copytree(os.path.join(MASTERS, t), live)

if __name__ == "__main__":
    gen_na_region(); gen_jsonl_rename(); gen_copytruncate()
    gen_first_purchase(); gen_epoch_window(); deploy()
    with open(os.path.join(SCRATCH, "answer_key_v6.json"), "w") as f:
        json.dump(key, f, indent=2)
    print(json.dumps(key, indent=2))
