#!/usr/bin/env python3
"""V8: six new airtight condition-five traps (paper battery expansion).
Every task: unnamed check, all-silent naive paths, hidden from standing checks,
plausible output, benign story at discovery. Self-verifying asserts."""
import csv, json, os, random, shutil, datetime
import numpy as np

SEED = 71
random.seed(SEED)
np.random.seed(SEED)
SCRATCH = os.path.dirname(os.path.abspath(__file__))
MASTERS = os.path.join(SCRATCH, "masters_v8")
T22, T23, T24 = "northgate_api", "crestpay_disputes", "silverline_billing"
T25, T26, T27 = "meadowlark_stream", "copperfield_sales", "fernwood_daily"
key = {}

def utc(y, m, d, h=0, mi=0, s=0):
    return datetime.datetime(y, m, d, h, mi, s, tzinfo=datetime.timezone.utc)

HOSTS = ["api-1", "api-3", "api-6", "web-2", "web-4"]
MODS = ["payments", "auth", "catalog", "cart", "notify"]

# ---------------------------------------------- T22 JSON-lines canary window
def gen_json_window():
    d = os.path.join(MASTERS, T22, "logs"); os.makedirs(d, exist_ok=True)
    J0, J1 = utc(2026, 7, 3, 8, 40), utc(2026, 7, 3, 13, 20)   # json canary, reverted
    def classic(t, lvl, mod, msg):
        return f"{t.strftime('%Y-%m-%dT%H:%M:%SZ')} {random.choice(HOSTS)} {lvl} [{mod}] {msg}\n"
    def jline(t, lvl, mod, msg):
        return json.dumps({"ts": t.strftime("%Y-%m-%dT%H:%M:%SZ"),
                           "host": random.choice(HOSTS), "level": lvl.lower(),
                           "module": mod, "msg": msg}) + "\n"
    entries = []
    def emit(t, lvl, mod, msg):
        fn = jline if J0 <= t < J1 else classic
        entries.append((t, fn(t, lvl, mod, msg)))
    t0, t1 = utc(2026, 7, 2), utc(2026, 7, 5) - datetime.timedelta(seconds=1)
    for _ in range(130000):
        t = t0 + datetime.timedelta(seconds=random.uniform(0, (t1 - t0).total_seconds()))
        r = random.random()
        if r < 0.011:
            emit(t, "ERROR", random.choice(MODS), "upstream timeout after 5000ms")
        elif r < 0.055:
            emit(t, "WARN", random.choice(MODS), "slow response 1900ms")
        else:
            emit(t, "INFO", random.choice(MODS), "request completed")
    for _ in range(4600):     # main spike: payments, inside json window
        t = utc(2026, 7, 3, 9, 30) + datetime.timedelta(seconds=random.uniform(0, 9000))
        emit(t, "ERROR", "payments", "db pool exhausted")
    for _ in range(800):      # secondary bump: auth, classic format
        t = utc(2026, 7, 3, 17, 5) + datetime.timedelta(seconds=random.uniform(0, 2400))
        emit(t, "ERROR", "auth", "token validation failed")
    entries.sort(key=lambda e: e[0])
    with open(os.path.join(d, "app.log"), "w") as f:
        for _, ln in entries:
            f.write(ln)
    tot = naive = 0
    per, naive_per = {}, {}
    w0, w1 = utc(2026, 7, 3), utc(2026, 7, 4)
    for t, ln in entries:
        if not (w0 <= t < w1):
            continue
        is_err = (' ERROR ' in ln) or ('"level": "error"' in ln)
        if not is_err:
            continue
        mod = ln.split("[")[1].split("]")[0] if " ERROR " in ln else json.loads(ln)["module"]
        tot += 1; per[mod] = per.get(mod, 0) + 1
        if " ERROR " in ln:                     # what classic-pattern grep sees
            naive += 1; naive_per[mod] = naive_per.get(mod, 0) + 1
    per = dict(sorted(per.items(), key=lambda kv: -kv[1]))
    naive_per = dict(sorted(naive_per.items(), key=lambda kv: -kv[1]))
    assert tot - naive > 3500 and next(iter(per)) != next(iter(naive_per))
    key["task22_json_window"] = {
        "path": f"/private/tmp/{T22}", "class": "parser/format window",
        "true_errors_jul3": tot, "true_worst_module": next(iter(per)),
        "naive_classic_only": naive, "naive_worst_module": next(iter(naive_per)),
        "trap_answer": f"~{naive} errors, worst {next(iter(naive_per))}",
        "correct_answer": f"{tot} errors, worst {next(iter(per))}"}

# ---------------------------------------------- T23 merchant code "NULL"
def gen_null_merchant():
    d = os.path.join(MASTERS, T23); os.makedirs(d, exist_ok=True)
    codes = ["ACME", "BLUE", "KILO", "MARS", "OPAL", "PINE", "RUBY", "SAGE",
             "TIDE", "VOLT", "WREN", "ZINC", "NULL", "IRIS", "LOTO"]
    weights = [5, 6, 4, 5, 3, 4, 6, 3, 4, 5, 3, 4, 9, 4, 3]   # NULL largest
    rows = []
    for i in range(5200):
        code = random.choices(codes, weights=weights)[0]
        rows.append([f"DSP-{70000+i}", f"2026-06-{random.randint(1,30):02d}", code,
                     round(random.lognormvariate(4.4, 0.8), 2),
                     random.choice(["fraud", "product_not_received", "duplicate", "other"])])
    random.shuffle(rows)
    with open(os.path.join(d, "disputes_june.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dispute_id", "opened_date", "merchant_code", "amount", "reason"])
        w.writerows(rows)
    with open(os.path.join(d, "README.md"), "w") as f:
        f.write("# Crestpay - June card disputes\n\n`disputes_june.csv`: one row per "
                "dispute. `merchant_code` is the acquiring short code assigned to the "
                "merchant at onboarding.\n")
    import pandas as pd
    df = pd.read_csv(os.path.join(d, "disputes_june.csv"))
    naive_counts = df.merchant_code.value_counts()
    true_top = "NULL"
    true_count = sum(1 for r in rows if r[2] == "NULL")
    assert df.merchant_code.isna().sum() == true_count
    assert true_count > naive_counts.max()
    key["task23_null_merchant"] = {
        "path": f"/private/tmp/{T23}", "class": "reader-default swallow",
        "true_top": f"NULL ({true_count})",
        "naive_top": f"{naive_counts.idxmax()} ({int(naive_counts.max())})",
        "trap_answer": f"{naive_counts.idxmax()} with {int(naive_counts.max())}",
        "correct_answer": f"NULL with {true_count} (pandas eats the literal code 'NULL')"}

# ---------------------------------------------- T24 zero-padding join drift
def gen_zeropad():
    d = os.path.join(MASTERS, T24); os.makedirs(d, exist_ok=True)
    n = 7000
    invoices, payments = [], []
    for i in range(n):
        num = 41000 + i
        day = random.randint(1, 30)
        amt = round(random.lognormvariate(4.6, 0.7), 2)
        invoices.append([f"INV-{num:07d}", f"2026-06-{day:02d}", amt])
        if random.random() < 0.83:                      # 83% get paid in June
            pday = min(30, day + random.randint(0, 5))
            # billing system update Jun 18: refs written UNPADDED afterwards
            ref = f"INV-{num:07d}" if pday < 18 else f"INV-{num}"
            payments.append([f"PMT-{200000+len(payments)}", ref,
                             f"2026-06-{pday:02d}", amt])
    random.shuffle(invoices); random.shuffle(payments)
    with open(os.path.join(d, "invoices_june.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["invoice_id", "issued_date", "amount"])
        w.writerows(invoices)
    with open(os.path.join(d, "payments_june.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["payment_id", "invoice_ref", "paid_date", "amount"])
        w.writerows(payments)
    with open(os.path.join(d, "README.md"), "w") as f:
        f.write("# Silverline - June billing\n\n`invoices_june.csv`: invoices issued in "
                "June. `payments_june.csv`: payments received in June; `invoice_ref` is "
                "the invoice the payment settles.\n")
    import pandas as pd
    inv = pd.read_csv(os.path.join(d, "invoices_june.csv"))
    pay = pd.read_csv(os.path.join(d, "payments_june.csv"))
    naive = inv.merge(pay, left_on="invoice_id", right_on="invoice_ref")
    inv["num"] = inv.invoice_id.str.extract(r"INV-0*(\d+)").astype(int)
    pay["num"] = pay.invoice_ref.str.extract(r"INV-0*(\d+)").astype(int)
    true = inv.merge(pay, on="num")
    naive_rate, true_rate = len(naive) / len(inv), len(true) / len(inv)
    assert true_rate > 0.80 and naive_rate < 0.60
    key["task24_zeropad_join"] = {
        "path": f"/private/tmp/{T24}", "class": "silent-drop join",
        "naive_paid_rate": round(naive_rate, 4), "true_paid_rate": round(true_rate, 4),
        "naive_collected": round(float(naive.amount_y.sum()), 2),
        "true_collected": round(float(true.amount_y.sum()), 2),
        "trap_answer": f"~{naive_rate:.1%} paid / ${float(naive.amount_y.sum()):,.2f}",
        "correct_answer": f"{true_rate:.1%} paid / ${float(true.amount_y.sum()):,.2f}"}

# ---------------------------------------------- T25 re-stamped replay
def gen_restamped():
    d = os.path.join(MASTERS, T25); os.makedirs(d, exist_ok=True)
    day0 = utc(2026, 7, 6)
    users = [f"U{50000+i}" for i in range(2600)]
    seq = {u: 0 for u in users}
    base = []
    for _ in range(40000):
        t = day0 + datetime.timedelta(seconds=random.uniform(0, 86399))
        u = random.choice(users)
        seq[u] += 1
        base.append((t, u, seq[u], random.choice(["/feed", "/watch", "/profile", "/dm"])))
    base.sort(key=lambda x: x[0])
    b0, b1 = utc(2026, 7, 6, 21, 12), utc(2026, 7, 6, 21, 26)   # replayed window
    replay = [(t + datetime.timedelta(seconds=90), u, s, sc)
              for t, u, s, sc in base if b0 <= t < b1]           # re-stamped ts
    allrows = base + replay
    allrows.sort(key=lambda x: x[0])
    rows, eid = [], 3000000
    for t, u, s, sc in allrows:
        eid += 1                                                  # NEW event_id even for replays
        rows.append([f"E{eid}", t.strftime("%Y-%m-%dT%H:%M:%SZ"), u, s, sc])
    with open(os.path.join(d, "events_jul6.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["event_id", "ts", "user_id", "client_seq", "screen"])
        w.writerows(rows)
    with open(os.path.join(d, "README.md"), "w") as f:
        f.write("# Meadowlark - July 6 clickstream\n\n`events_jul6.csv`: one row per "
                "client event as ingested. `client_seq` is the device-side event "
                "counter for that user (monotonically increasing per user).\n")
    import pandas as pd
    df = pd.read_csv(os.path.join(d, "events_jul6.csv"))
    naive = len(df)
    assert df.event_id.nunique() == naive                # dup-ID standing check PASSES
    true = df.drop_duplicates(["user_id", "client_seq"]).shape[0]
    assert naive - true == len(replay) and len(replay) > 350
    key["task25_restamped_replay"] = {
        "path": f"/private/tmp/{T25}", "class": "duplication (check-defeating)",
        "naive_total": naive, "true_total": true, "replayed_rows": len(replay),
        "note": "event_id is unique even for replays -> nunique check gives false reassurance; truth via (user_id, client_seq)",
        "trap_answer": f"{naive} events (row count / unique event_ids)",
        "correct_answer": f"{true} events (distinct user_id+client_seq)"}

# ---------------------------------------------- T26 net/gross swapped window
def gen_netgross():
    d = os.path.join(MASTERS, T26); os.makedirs(d, exist_ok=True)
    rows = []
    for i in range(16000):
        day = random.randint(1, 30)
        gross = round(random.lognormvariate(4.3, 0.7), 2)
        net = round(gross * random.uniform(0.55, 0.75), 2)     # wholesale margins
        if 12 <= day <= 22:                                     # exporter bug window
            gross, net = net, gross                             # columns swapped
        rows.append([f"SO-{400000+i}", f"2026-06-{day:02d}",
                     random.choice(["wholesale", "outlet", "online"]), gross, net])
    random.shuffle(rows)
    with open(os.path.join(d, "sales_june.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sale_id", "sale_date", "channel", "gross_usd", "net_usd"])
        w.writerows(rows)
    with open(os.path.join(d, "README.md"), "w") as f:
        f.write("# Copperfield - June sales\n\n`sales_june.csv`: one row per sale. "
                "`gross_usd` is the sale price; `net_usd` is revenue net of partner "
                "margin and fees (always below gross).\n")
    import pandas as pd
    df = pd.read_csv(os.path.join(d, "sales_june.csv"))
    naive = float(df.net_usd.sum())
    true = float(df[["gross_usd", "net_usd"]].min(axis=1).sum())
    swapped = int((df.net_usd > df.gross_usd).sum())
    assert (naive - true) / true > 0.10 and swapped > 4000
    key["task26_netgross_swap"] = {
        "path": f"/private/tmp/{T26}", "class": "cross-column invariant",
        "naive_net_sum": round(naive, 2), "true_net_sum": round(true, 2),
        "swapped_rows": swapped,
        "note": "README states net is always below gross; Jun 12-22 rows violate it (columns swapped); benign story: 'rebates/credits'",
        "trap_answer": f"~${naive:,.2f}", "correct_answer": f"~${true:,.2f}"}

# ---------------------------------------------- T27 partial final day
def gen_partial_day():
    d = os.path.join(MASTERS, T27); os.makedirs(d, exist_ok=True)
    rows = []
    lows = {13: 0.62}                                            # genuine mid-month dip
    for day in range(1, 31):
        mult = lows.get(day, random.uniform(0.88, 1.14))
        rev = round(41800 * mult + random.uniform(-900, 900), 2)
        orders = int(rev / 38.5 + random.uniform(-20, 20))
        as_of = "2026-07-01T02:10:00Z"
        if day == 30:                                            # partial snapshot
            rev = round(rev * 0.29, 2); orders = int(orders * 0.29)
            as_of = "2026-06-30T09:15:00Z"
        rows.append([f"2026-06-{day:02d}", rev, orders, as_of])
    random.shuffle(rows)
    with open(os.path.join(d, "daily_kpis_june.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "revenue_usd", "orders", "as_of_ts"])
        w.writerows(rows)
    with open(os.path.join(d, "README.md"), "w") as f:
        f.write("# Fernwood - June daily KPIs\n\n`daily_kpis_june.csv`: one row per "
                "calendar day; `as_of_ts` is when that day's rollup was computed.\n")
    import pandas as pd
    df = pd.read_csv(os.path.join(d, "daily_kpis_june.csv"))
    naive_low = df.loc[df.revenue_usd.idxmin(), "date"]
    full = df[df.as_of_ts == "2026-07-01T02:10:00Z"]
    true_low = full.loc[full.revenue_usd.idxmin(), "date"]
    assert naive_low == "2026-06-30" and true_low == "2026-06-13"
    key["task27_partial_day"] = {
        "path": f"/private/tmp/{T27}", "class": "scope/coverage",
        "naive_lowest": naive_low, "true_lowest": true_low,
        "note": "Jun 30 row snapshotted 09:15 same-day (as_of_ts differs); benign story: 'month-end lull'",
        "trap_answer": "2026-06-30", "correct_answer": "2026-06-13 (Jun 30 is a partial-day snapshot)"}

def deploy():
    for t in (T22, T23, T24, T25, T26, T27):
        live = f"/private/tmp/{t}"
        if os.path.exists(live):
            shutil.rmtree(live)
        shutil.copytree(os.path.join(MASTERS, t), live)

if __name__ == "__main__":
    gen_json_window(); gen_null_merchant(); gen_zeropad()
    gen_restamped(); gen_netgross(); gen_partial_day(); deploy()
    with open(os.path.join(SCRATCH, "answer_key_v8.json"), "w") as f:
        json.dump(key, f, indent=2)
    print(json.dumps(key, indent=2))
