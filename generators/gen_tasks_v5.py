#!/usr/bin/env python3
"""V5: statistical-instrument traps (beyond parsing). Each attacks a reflex an
analyst reaches for: unweighted mean, nunique on a silently-float ID, headline
aggregate without confound check, UTC hour extraction. Self-verifying."""
import csv, json, os, random, shutil, datetime
import numpy as np

SEED = 41
random.seed(SEED)
np.random.seed(SEED)
SCRATCH = os.path.dirname(os.path.abspath(__file__))
MASTERS = os.path.join(SCRATCH, "masters_v5")
T10, T11, T12, T13 = "summit_retail", "orion_identity", "helios_experiment", "lumen_engagement"
key = {}

# ------------------------------------------------ T10 average-of-averages
def gen_avg_of_avg():
    d = os.path.join(MASTERS, T10); os.makedirs(d, exist_ok=True)
    # high-volume formats carry LOW baskets; numerous low-volume kiosks carry high baskets
    fmt = {"flagship": (12, 900, 31.0), "express": (140, 700, 24.0),
           "kiosk": (260, 25, 58.0)}
    rows = []
    sid = 100
    for f, (nst, txn_mu, bmu) in fmt.items():
        for _ in range(nst):
            sid += 1
            for day in range(1, 31):
                txns = max(1, int(random.gauss(txn_mu, txn_mu * 0.2)))
                basket = round(random.gauss(bmu, bmu * 0.08), 2)
                rows.append([f"S{sid}", f, f"2026-06-{day:02d}", txns, basket])
    random.shuffle(rows)
    with open(os.path.join(d, "store_daily_june.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["store_id", "store_format", "date", "transactions", "avg_basket_usd"])
        w.writerows(rows)
    with open(os.path.join(d, "README.md"), "w") as f:
        f.write("# Summit Retail - June store performance\n\n"
                "`store_daily_june.csv`: one row per store per day. `avg_basket_usd` is that "
                "store-day's mean basket; `transactions` is that store-day's transaction count.\n")
    import pandas as pd
    df = pd.read_csv(os.path.join(d, "store_daily_june.csv"))
    naive = df.avg_basket_usd.mean()
    true = (df.avg_basket_usd * df.transactions).sum() / df.transactions.sum()
    assert abs(naive - true) / true > 0.15, (naive, true)
    key["task10_avg_of_avg"] = {
        "path": f"/private/tmp/{T10}",
        "mechanism": "flagship stores dominate transaction volume but are few rows; unweighted mean of avg_basket_usd overweights numerous low-volume kiosk/express rows",
        "naive_unweighted_mean": round(naive, 2), "true_weighted_mean": round(true, 2),
        "trap_answer": f"~${naive:.2f} (mean of avg_basket_usd)",
        "correct_answer": f"~${true:.2f} (transaction-weighted)"}

# ------------------------------------------------ T11 float64 ID collision
def gen_float_id():
    d = os.path.join(MASTERS, T11); os.makedirs(d, exist_ok=True)
    base = 10**18
    n_users = 5000
    uids = [base + random.randint(0, 2_000_000) for _ in range(n_users)]
    uids = list(dict.fromkeys(uids))                     # ensure distinct ints
    while len(uids) < n_users:
        uids.append(base + random.randint(0, 2_000_000))
    uids = list(dict.fromkeys(uids))[:n_users]
    rows = []
    for _ in range(52000):
        if random.random() < 0.03:
            uid = ""                                      # logged-out event -> forces float64
        else:
            uid = random.choice(uids)
        rows.append([uid, f"2026-06-{random.randint(1,30):02d}",
                     random.choice(["view", "click", "add_cart", "purchase"])])
    random.shuffle(rows)
    with open(os.path.join(d, "events.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["user_id", "event_date", "event_type"])
        w.writerows(rows)
    with open(os.path.join(d, "README.md"), "w") as f:
        f.write("# Orion - June product events\n\n`events.csv`: one row per event. "
                "`user_id` is the account id (blank for logged-out sessions).\n")
    import pandas as pd
    default = pd.read_csv(os.path.join(d, "events.csv"))
    as_str = pd.read_csv(os.path.join(d, "events.csv"), dtype={"user_id": str})
    naive = int(default.user_id.dropna().nunique())
    true = int(as_str.user_id.dropna().nunique())
    dtype = str(default.user_id.dtype)
    assert dtype == "float64" and (true - naive) / true > 0.08, (dtype, naive, true)
    key["task11_float_id"] = {
        "path": f"/private/tmp/{T11}",
        "mechanism": "user_id ~1e18 with blank rows -> pandas infers float64 -> distinct ids within ~128 ULP collapse; nunique undercounts unless read as str/Int64",
        "default_dtype": dtype, "naive_nunique_float": naive, "true_nunique": true,
        "trap_answer": f"~{naive} distinct users (float64 nunique)",
        "correct_answer": f"{true} distinct users (read id as string/Int64)"}

# ------------------------------------------------ T12 Simpson's reversal
def gen_simpson():
    d = os.path.join(MASTERS, T12); os.makedirs(d, exist_ok=True)
    # base rates: new users low, returning high. treatment lifts each by ~+6pp.
    # confound: treatment oversampled to 'new', control to 'returning'.
    def block(segment, variant, n, rate):
        return [[f"U{random.randint(10**6,10**7)}", segment, variant,
                 1 if random.random() < rate else 0] for _ in range(n)]
    rows = []
    rows += block("new", "control", 1200, 0.10)
    rows += block("new", "treatment", 4800, 0.16)
    rows += block("returning", "control", 4800, 0.42)
    rows += block("returning", "treatment", 1200, 0.48)
    random.shuffle(rows)
    with open(os.path.join(d, "experiment_results.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["user_id", "segment", "variant", "converted"])
        w.writerows(rows)
    with open(os.path.join(d, "README.md"), "w") as f:
        f.write("# Helios - onboarding experiment (June)\n\n`experiment_results.csv`: one row "
                "per enrolled user. `variant` = control/treatment, `converted` = 1 if activated. "
                "`segment` = new vs returning user at enrollment.\n")
    import pandas as pd
    df = pd.read_csv(os.path.join(d, "experiment_results.csv"))
    o = df.groupby("variant").converted.mean()
    seg = df.groupby(["segment", "variant"]).converted.mean().unstack()
    assert o["treatment"] < o["control"]
    assert (seg["treatment"] > seg["control"]).all()
    key["task12_simpson"] = {
        "path": f"/private/tmp/{T12}",
        "mechanism": "treatment oversampled into low-baseline 'new' segment; overall treatment<control but treatment>control within BOTH segments",
        "overall": {k: round(float(v), 4) for k, v in o.items()},
        "by_segment": {s: {v: round(float(seg.loc[s, v]), 4) for v in seg.columns} for s in seg.index},
        "trap_answer": "treatment hurt (overall lower) -> don't ship",
        "correct_answer": "Simpson's reversal: treatment wins in both segments; allocation imbalance drives the overall; treatment actually helps"}

# ------------------------------------------------ T13 timezone local-hour
def gen_tz():
    d = os.path.join(MASTERS, T13); os.makedirs(d, exist_ok=True)
    offsets = [-8, -7, -6, -5, 0, 1]                      # US + a little EU
    rows = []
    for _ in range(20000):
        off = random.choice(offsets)
        # local hour distribution: midday + evening peaks
        local_h = int(np.clip(random.choice(
            [random.gauss(12, 2), random.gauss(20, 2)]), 0, 23))
        day = random.randint(1, 30)
        # UTC = local - offset
        utc_dt = datetime.datetime(2026, 6, day, local_h,
                                   random.randint(0, 59), tzinfo=datetime.timezone.utc) \
                 - datetime.timedelta(hours=off)
        rows.append([f"ORD-{random.randint(10**5,10**6)}",
                     utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ"), off,
                     round(random.lognormvariate(3.9, 0.5), 2)])
    random.shuffle(rows)
    with open(os.path.join(d, "orders_june.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["order_id", "placed_at_utc", "utc_offset_hours", "amount"])
        w.writerows(rows)
    with open(os.path.join(d, "README.md"), "w") as f:
        f.write("# Lumen - June orders\n\n`orders_june.csv`: `placed_at_utc` is the order "
                "timestamp in UTC; `utc_offset_hours` is the customer's local offset from UTC.\n")
    import pandas as pd
    df = pd.read_csv(os.path.join(d, "orders_june.csv"))
    utc_h = pd.to_datetime(df.placed_at_utc).dt.hour
    naive = float(((utc_h >= 9) & (utc_h < 17)).mean())
    local_h = (utc_h + df.utc_offset_hours) % 24
    true = float(((local_h >= 9) & (local_h < 17)).mean())
    assert abs(naive - true) > 0.10, (naive, true)
    key["task13_tz"] = {
        "path": f"/private/tmp/{T13}",
        "mechanism": "business-hours fraction computed on UTC hour ignores utc_offset_hours; customers span -8..+1",
        "naive_utc_fraction": round(naive, 4), "true_local_fraction": round(true, 4),
        "trap_answer": f"~{naive:.1%} (UTC hour 9-17)",
        "correct_answer": f"~{true:.1%} (local hour after applying offset)"}

def deploy():
    for t in (T10, T11, T12, T13):
        live = f"/private/tmp/{t}"
        if os.path.exists(live):
            shutil.rmtree(live)
        shutil.copytree(os.path.join(MASTERS, t), live)

if __name__ == "__main__":
    gen_avg_of_avg(); gen_float_id(); gen_simpson(); gen_tz(); deploy()
    with open(os.path.join(SCRATCH, "answer_key_v5.json"), "w") as f:
        json.dump(key, f, indent=2)
    print(json.dumps(key, indent=2))
