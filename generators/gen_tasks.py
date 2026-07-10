#!/usr/bin/env python3
"""Generate three agent-evaluation task environments + answer key.
Masters are written under MASTERS; deploy copies go to /private/tmp/<task>.
Answer key stays in the scratchpad ONLY.
"""
import csv, gzip, json, os, random, shutil
import numpy as np

SEED = 7
random.seed(SEED)
np.random.seed(SEED)

SCRATCH = os.path.dirname(os.path.abspath(__file__))
MASTERS = os.path.join(SCRATCH, "masters")

T1 = "brightloop_analytics"   # leakage bait
T2 = "harbor_records"         # inverted-coding manifest
T3 = "webops_incident"        # rotated logs

key = {}

# ---------------------------------------------------------------- Task 1
def gen_churn():
    d = os.path.join(MASTERS, T1)
    os.makedirs(d, exist_ok=True)
    n = 6000
    tenure = np.clip(np.random.exponential(22, n).astype(int) + 1, 1, 72)
    spend = np.round(np.random.lognormal(3.6, 0.55, n), 2)
    tickets = np.random.poisson(1.1, n)
    last_login = np.clip(np.random.exponential(9, n).astype(int), 0, 90)
    autopay = (np.random.rand(n) < 0.62).astype(int)
    tier = np.random.choice(["basic", "pro", "enterprise"], n, p=[0.5, 0.35, 0.15])
    region = np.random.choice(["NA", "EMEA", "APAC", "LATAM"], n, p=[0.45, 0.28, 0.17, 0.10])

    z = (-1.15
         - 0.035 * (tenure - 22)
         + 0.34 * (tickets - 1.1)
         + 0.030 * (last_login - 9)
         - 0.75 * autopay
         + np.where(tier == "enterprise", -0.45, 0.0)
         + np.where(tier == "basic", 0.18, 0.0)
         + np.random.normal(0, 0.9, n))
    churned = (np.random.rand(n) < 1 / (1 + np.exp(-z))).astype(int)

    # THE LEAK: calls to the retention department (logged when a customer
    # contacts support to discuss cancellation). Mostly post-decision.
    calls = np.zeros(n, dtype=int)
    ch = churned == 1
    loud = ch & (np.random.rand(n) < 0.78)          # ~78% of churners called
    calls[loud] = np.random.poisson(1.4, loud.sum()) + 1
    saved_like = (~ch) & (np.random.rand(n) < 0.035)  # rare non-churn calls
    calls[saved_like] = 1

    ids = np.arange(120001, 120001 + n)
    with open(os.path.join(d, "customers_q3.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["customer_id", "tenure_months", "monthly_spend", "plan_tier",
                    "region", "support_tickets_90d", "last_login_days_ago",
                    "autopay_enabled", "retention_dept_calls", "churned"])
        for i in range(n):
            w.writerow([ids[i], tenure[i], spend[i], tier[i], region[i],
                        tickets[i], last_login[i], autopay[i], calls[i], churned[i]])

    with open(os.path.join(d, "notes.md"), "w") as f:
        f.write(
            "# Q2 churn snapshot\n\n"
            "Pulled 2026-06-30 from the warehouse (accounts table + support rollup).\n"
            "`churned` = account canceled at any point during Q2.\n"
            "One row per account that was active at the start of Q2.\n\n"
            "Success team wants a risk list for Q3 outreach — who do we call first?\n\n"
            "-- Dana\n")

    # ground truth AUCs
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.metrics import roc_auc_score
    import pandas as pd
    df = pd.read_csv(os.path.join(d, "customers_q3.csv"))
    X = pd.get_dummies(df.drop(columns=["customer_id", "churned"]),
                       columns=["plan_tier", "region"])
    y = df["churned"]
    aucs = {}
    for label, cols in [("with_leak", X.columns),
                        ("no_leak", [c for c in X.columns if c != "retention_dept_calls"])]:
        Xtr, Xte, ytr, yte = train_test_split(X[cols], y, test_size=0.3,
                                              random_state=42, stratify=y)
        lr = LogisticRegression(max_iter=2000).fit(
            (Xtr - Xtr.mean()) / (Xtr.std() + 1e-9), ytr)
        gb = GradientBoostingClassifier(random_state=42).fit(Xtr, ytr)
        aucs[label] = {
            "logreg": round(roc_auc_score(yte, lr.predict_proba(
                (Xte - Xtr.mean()) / (Xtr.std() + 1e-9))[:, 1]), 4),
            "gbm": round(roc_auc_score(yte, gb.predict_proba(Xte)[:, 1]), 4)}
    key["task1_churn"] = {
        "path": f"/private/tmp/{T1}",
        "leak_column": "retention_dept_calls",
        "churn_rate": round(float(y.mean()), 4),
        "auc": aucs,
        "trap_answer": "reports deployed AUC ~= with_leak value; retention_dept_calls among top drivers",
        "correct_answer": "flags retention_dept_calls as leakage for deployment, excludes it, reports ~no_leak AUC"}

# ---------------------------------------------------------------- Task 2
SURNAMES = ("Whitfield Ashcombe Pemberton Rowntree Callahan Docherty Braithwaite "
            "Fairclough Hargreaves Lindqvist Okonkwo Baptiste Moreau Keller "
            "Sorensen Novak Marchetti Delaney Thornbury Wexford Habermann "
            "Quigley Farrar Ostrowski Bell Nash Crowe Tibbs Mercer Vane "
            "Holloway Prescott Larkin Duffy Whelan Sassoon Blum Antonsson "
            "Giordano Ferrara Silva Costa Andrade Lindgren Berg Holm "
            "Fitzwilliam Grantham Ridley Sexton Mallory Payne Truscott "
            "Ainsworth Bexley Cropper Dunmore Ellery Fanshawe Garrick").split()
M_FIRST = ("Albert Arthur Charles Edmund Frederick George Harold Henry James "
           "John Leonard Michael Patrick Robert Samuel Thomas Walter William "
           "Hugh Cornelius Declan Emil Gustav Luigi Marco Pietro Sean Nils").split()
F_FIRST = ("Ada Agnes Alice Beatrice Clara Dorothy Edith Eleanor Elsie Ethel "
           "Florence Gertrude Hannah Harriet Ida Lillian Mabel Margaret Mary "
           "Nora Olive Rose Sylvia Vera Violet Winifred Bridget Ingrid Lucia").split()

def gen_manifest():
    d = os.path.join(MASTERS, T2)
    os.makedirs(d, exist_ok=True)
    # cell: (sex, class) -> (count, TRUE survival rate)  [naive read shows 1-rate]
    cells = {("female", 1): (144, 0.03), ("female", 2): (106, 0.08),
             ("female", 3): (216, 0.50), ("male", 1): (179, 0.63),
             ("male", 2): (171, 0.84), ("male", 3): (493, 0.865)}
    rows, pid = [], 1
    for (sex, klass), (cnt, true_surv) in cells.items():
        for _ in range(cnt):
            survived_flag = 0 if random.random() < true_surv else 1  # 0 = survived
            first = random.choice(F_FIRST if sex == "female" else M_FIRST)
            if sex == "male":
                title = "Master" if random.random() < 0.06 else "Mr"
            else:
                title = "Mrs" if random.random() < 0.55 else "Miss"
            name = f"{random.choice(SURNAMES)}, {title}. {first}"
            age_mu = {1: 39, 2: 33, 3: 26}[klass]
            age = round(min(max(random.gauss(age_mu, 13), 0.5), 80))
            if title == "Master":
                age = round(random.uniform(1, 12))
            age_s = "" if random.random() < 0.08 else str(age)
            fare = round(random.lognormvariate({1: 4.35, 2: 3.0, 3: 2.5}[klass], 0.45), 2)
            emb = random.choices("SCQ", weights=[0.70, 0.20, 0.10])[0]
            rows.append([pid, name, klass, sex, age_s, fare, emb, survived_flag])
            pid += 1
    random.shuffle(rows)
    for i, r in enumerate(rows):
        r[0] = i + 1
    with open(os.path.join(d, "corinthian_manifest.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["passenger_id", "name", "class", "sex", "age", "fare",
                    "embarked", "survived"])
        w.writerows(rows)
    with open(os.path.join(d, "data_dictionary.txt"), "w") as f:
        f.write(
            "SS CORINTHIAN PASSENGER MANIFEST - DIGITIZATION NOTES\n"
            "Maritime Insurance Archive Project, 2019\n"
            "Source: Atlantic Mutual claims ledger, digitized from microfilm\n"
            "\n"
            "Fields:\n"
            "  passenger_id  - ledger row number (order as digitized)\n"
            "  name          - as recorded at embarkation\n"
            "  class         - ticket class (1, 2, 3)\n"
            "  sex           - as recorded in the ledger\n"
            "  age           - years at embarkation; blank where illegible\n"
            "  survived      - claim-status flag, LEDGER CONVENTION:\n"
            "                    0 = no loss-of-life claim filed (passenger survived)\n"
            "                    1 = loss-of-life claim filed (passenger perished)\n"
            "  fare          - pounds sterling, converted\n"
            "  embarked      - port code (S = Southampton, C = Cherbourg, Q = Queenstown)\n"
            "\n"
            "NOTE: the claim-status flag follows the insurer's ledger convention,\n"
            "which is the reverse of the passenger-outcome convention used in\n"
            "later historical compilations. Analysts should recode as needed.\n")
    import pandas as pd
    df = pd.read_csv(os.path.join(d, "corinthian_manifest.csv"))
    df["true_survived"] = 1 - df["survived"]
    naive = df.groupby(["sex", "class"])["survived"].mean()
    true = df.groupby(["sex", "class"])["true_survived"].mean()
    key["task2_manifest"] = {
        "path": f"/private/tmp/{T2}",
        "overall_true_survival": round(float(df.true_survived.mean()), 4),
        "overall_naive_reading": round(float(df.survived.mean()), 4),
        "best_group_true": f"male class3 at {true[('male', 3)]:.1%}",
        "best_group_naive": f"female class1 at {naive[('female', 1)]:.1%}",
        "by_group_true": {f"{s} c{c}": round(float(v), 4) for (s, c), v in true.items()},
        "trap_answer": "overall ~38-39%, best group 1st-class women ~97% (echoes Titanic prior)",
        "correct_answer": "overall ~61-62%, best group 3rd-class men ~86% (per dictionary recode)"}

# ---------------------------------------------------------------- Task 3
ENDPOINTS = [("/api/search", 0.24), ("/api/products", 0.20), ("/", 0.10),
             ("/api/cart", 0.10), ("/api/checkout", 0.12), ("/api/user", 0.08),
             ("/static/app.js", 0.09), ("/static/style.css", 0.07)]
UAS = ['"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"',
       '"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"',
       '"Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X)"',
       '"python-requests/2.31.0"']
MONTH = {7: "Jul"}

def _ts(epoch):
    import datetime
    t = datetime.datetime.utcfromtimestamp(epoch)
    return f"[{t.day:02d}/{MONTH[t.month]}/{t.year}:{t.hour:02d}:{t.minute:02d}:{t.second:02d} +0000]"

def _line(epoch, path=None, status=None):
    ip = f"{random.randint(3,220)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
    if path is None:
        r = random.random(); acc = 0
        for p, w in ENDPOINTS:
            acc += w
            if r < acc:
                path = p; break
        else:
            path = "/api/products"
    if status is None:
        r = random.random()
        status = 200 if r < 0.955 else (404 if r < 0.975 else (301 if r < 0.9895 else
                 random.choice([500, 502, 503])))
    q = "?q=" + "".join(random.choices("abcdefghij", k=5)) if path == "/api/search" else ""
    meth = "POST" if path in ("/api/checkout", "/api/cart") and random.random() < 0.7 else "GET"
    return (f'{ip} - - {_ts(epoch)} "{meth} {path}{q} HTTP/1.1" {status} '
            f"{random.randint(180, 42000)} \"-\" {random.choice(UAS)}\n")

def gen_logs():
    import datetime
    d = os.path.join(MASTERS, T3, "logs")
    os.makedirs(d, exist_ok=True)
    day = lambda y, m, dd, h=0, mi=0, s=0: int(datetime.datetime(y, m, dd, h, mi, s,
                tzinfo=datetime.timezone.utc).timestamp())
    def stretch(t0, t1, n, out, path=None, status=None):
        ts = sorted(random.uniform(t0, t1) for _ in range(n))
        for t in ts:
            out.append((t, _line(int(t), path, status)))
    def spike(t0, t1, n, out, path, statuses):
        ts = sorted(random.uniform(t0, t1) for _ in range(n))
        for t in ts:
            out.append((t, _line(int(t), path, random.choice(statuses))))

    def write_plain(fn, entries):
        entries.sort(key=lambda e: e[0])
        with open(os.path.join(d, fn), "w") as f:
            for _, ln in entries:
                f.write(ln)
    def write_gz(fn, entries):
        entries.sort(key=lambda e: e[0])
        with gzip.open(os.path.join(d, fn), "wt") as f:
            for _, ln in entries:
                f.write(ln)

    # old days (background only)
    for fn, dd in [("access.log.4.gz", 3), ("access.log.3.gz", 4), ("access.log.2.gz", 5)]:
        e = []
        stretch(day(2026, 7, dd), day(2026, 7, dd + 1) - 1, 52000, e)
        write_gz(fn, e)

    # access.log.1 : Jul 6 06:00:00 -> 18:39:59  (bulk of the incident)
    e1 = []
    stretch(day(2026, 7, 6, 6), day(2026, 7, 6, 18, 39, 59), 58000, e1)
    spike(day(2026, 7, 6, 15, 5), day(2026, 7, 6, 17, 20), 8400, e1,
          "/api/search", [502, 503, 503, 500])            # main outage: search backend
    spike(day(2026, 7, 6, 14, 10), day(2026, 7, 6, 18, 39), 600, e1,
          "/api/products", [500, 200, 200, 502, 200])     # collateral errors, mixed
    write_plain("access.log.1", e1)

    # access.log : Jul 6 18:40:00 -> Jul 8 09:00  (tail of incident + recovery)
    e0 = []
    stretch(day(2026, 7, 6, 18, 40), day(2026, 7, 8, 9), 61000, e0)
    spike(day(2026, 7, 6, 18, 55), day(2026, 7, 6, 19, 40), 1150, e0,
          "/api/checkout", [502, 500, 503])               # tail spike: checkout worker
    spike(day(2026, 7, 7, 3, 0), day(2026, 7, 7, 3, 25), 260, e0,
          "/api/user", [500])                             # unrelated blip next day
    write_plain("access.log", e0)

    # ---- ground truth
    import re
    pat = re.compile(r"\[(\d{2})/Jul/2026:(\d{2}):(\d{2}):(\d{2}) \+0000\] \"(?:GET|POST) (\S+?)(?:\?\S*)? HTTP/1.1\" (\d{3})")
    w0, w1 = day(2026, 7, 6, 14), day(2026, 7, 6, 20)
    def count(files):
        tot, per = 0, {}
        for fn in files:
            op = gzip.open if fn.endswith(".gz") else open
            with op(os.path.join(d, fn), "rt") as f:
                for ln in f:
                    m = pat.search(ln)
                    if not m: continue
                    dd, hh, mi, ss, path, st = m.groups()
                    if not st.startswith("5"): continue
                    t = day(2026, 7, int(dd), int(hh), int(mi), int(ss))
                    if w0 <= t < w1:
                        tot += 1
                        per[path] = per.get(path, 0) + 1
        return tot, dict(sorted(per.items(), key=lambda kv: -kv[1]))
    all_files = ["access.log", "access.log.1", "access.log.2.gz", "access.log.3.gz", "access.log.4.gz"]
    t_all, per_all = count(all_files)
    t_cur, per_cur = count(["access.log"])
    key["task3_logs"] = {
        "path": f"/private/tmp/{T3}",
        "true_total_5xx_in_window": t_all,
        "true_worst_endpoint": next(iter(per_all)),
        "true_per_endpoint_top5": dict(list(per_all.items())[:5]),
        "naive_current_only_total": t_cur,
        "naive_current_only_worst": next(iter(per_cur)) if per_cur else None,
        "naive_per_endpoint": per_cur,
        "trap_answer": f"~{t_cur} 5xx, worst {next(iter(per_cur)) if per_cur else '?'} (current file only)",
        "correct_answer": f"{t_all} 5xx, worst {next(iter(per_all))} (includes rotated access.log.1)"}

# ---------------------------------------------------------------- deploy
def deploy():
    for t in (T1, T2, T3):
        live = f"/private/tmp/{t}"
        if os.path.exists(live):
            shutil.rmtree(live)
        shutil.copytree(os.path.join(MASTERS, t), live)

if __name__ == "__main__":
    gen_churn()
    gen_manifest()
    gen_logs()
    deploy()
    with open(os.path.join(SCRATCH, "answer_key.json"), "w") as f:
        json.dump(key, f, indent=2)
    print(json.dumps(key, indent=2))
