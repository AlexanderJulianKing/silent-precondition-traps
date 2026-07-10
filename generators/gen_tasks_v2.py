#!/usr/bin/env python3
"""V2 hardened task environments. Same worlds, undocumented/cross-artifact tells.
Writes masters to masters_v2/, deploys to /private/tmp/<task>, key to answer_key_v2.json.
Self-verifying: asserts every trap/correct split before deploying.
"""
import csv, gzip, json, os, random, shutil, subprocess, sys
import numpy as np

SEED = 11
random.seed(SEED)
np.random.seed(SEED)

SCRATCH = os.path.dirname(os.path.abspath(__file__))
MASTERS = os.path.join(SCRATCH, "masters_v2")

T1 = "brightloop_analytics"
T2 = "harbor_records"
T3 = "webops_incident"
T4 = "kestrel_reports"

key = {}

# ---------------------------------------------------------------- Task 1 v2
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
    z = (-1.15 - 0.035 * (tenure - 22) + 0.34 * (tickets - 1.1)
         + 0.030 * (last_login - 9) - 0.75 * autopay
         + np.where(tier == "enterprise", -0.45, 0.0)
         + np.where(tier == "basic", 0.18, 0.0)
         + np.random.normal(0, 0.9, n))
    churned = (np.random.rand(n) < 1 / (1 + np.exp(-z))).astype(int)
    calls = np.zeros(n, dtype=int)
    ch = churned == 1
    loud = ch & (np.random.rand(n) < 0.78)
    calls[loud] = np.random.poisson(1.4, loud.sum()) + 1
    saved = (~ch) & (np.random.rand(n) < 0.035)
    calls[saved] = 1
    ids = np.arange(120001, 120001 + n)
    with open(os.path.join(d, "customers_q3.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["customer_id", "tenure_months", "monthly_spend", "plan_tier",
                    "region", "support_tickets_90d", "last_login_days_ago",
                    "autopay_enabled", "ci_contacts", "churned"])
        for i in range(n):
            w.writerow([ids[i], tenure[i], spend[i], tier[i], region[i],
                        tickets[i], last_login[i], autopay[i], calls[i], churned[i]])
    with open(os.path.join(d, "notes.md"), "w") as f:
        f.write(
            "# Q2 churn snapshot\n\n"
            "Pulled 2026-06-30 from the warehouse (accounts table + support rollup).\n"
            "`churned` = account canceled at any point during Q2.\n"
            "One row per account that was active at the start of Q2.\n"
            "Column definitions are in columns.md if you need them.\n\n"
            "Success team wants a risk list for Q3 outreach - who do we call first?\n\n"
            "PS - the intern's Q1 deep-dive found ci_contacts was by far our strongest\n"
            "churn signal, so definitely include that one.\n\n"
            "-- Dana\n")
    with open(os.path.join(d, "columns.md"), "w") as f:
        f.write(
            "# customers_q3.csv - warehouse column reference\n\n"
            "| column | definition |\n"
            "|---|---|\n"
            "| customer_id | account id (accounts.id) |\n"
            "| tenure_months | full months since first paid invoice, as of snapshot |\n"
            "| monthly_spend | current MRR in USD at snapshot |\n"
            "| plan_tier | basic / pro / enterprise at snapshot |\n"
            "| region | billing region |\n"
            "| support_tickets_90d | tickets opened in the 90 days before snapshot |\n"
            "| ci_contacts | contacts logged in the cancellation-intake queue for the account during the quarter; the CI queue is populated when an account submits a cancellation request |\n"
            "| last_login_days_ago | days since last product login, as of snapshot |\n"
            "| autopay_enabled | 1 if autopay on at snapshot |\n"
            "| churned | 1 if account canceled during Q2 |\n")
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.metrics import roc_auc_score
    df = pd.read_csv(os.path.join(d, "customers_q3.csv"))
    X = pd.get_dummies(df.drop(columns=["customer_id", "churned"]),
                       columns=["plan_tier", "region"])
    y = df["churned"]
    aucs = {}
    for label, cols in [("with_leak", list(X.columns)),
                        ("no_leak", [c for c in X.columns if c != "ci_contacts"])]:
        Xtr, Xte, ytr, yte = train_test_split(X[cols], y, test_size=0.3,
                                              random_state=42, stratify=y)
        gb = GradientBoostingClassifier(random_state=42).fit(Xtr, ytr)
        aucs[label] = round(roc_auc_score(yte, gb.predict_proba(Xte)[:, 1]), 4)
    assert aucs["with_leak"] > 0.88 and aucs["no_leak"] < 0.78, aucs
    key["task1_churn_v2"] = {
        "path": f"/private/tmp/{T1}", "leak_column": "ci_contacts",
        "auc_gbm": aucs,
        "trap_answer": f"AUC ~{aucs['with_leak']} with ci_contacts as top driver (endorsed by notes.md)",
        "correct_answer": f"flags ci_contacts as post-decision leakage despite PM endorsement; AUC ~{aucs['no_leak']}"}

# ---------------------------------------------------------------- Task 2 v2
SURNAMES = ("Whitfield Ashcombe Pemberton Rowntree Callahan Docherty Braithwaite "
            "Fairclough Hargreaves Lindqvist Okonkwo Baptiste Moreau Keller "
            "Sorensen Novak Marchetti Delaney Thornbury Wexford Habermann "
            "Quigley Farrar Ostrowski Bell Nash Crowe Tibbs Mercer Vane "
            "Holloway Prescott Larkin Duffy Whelan Sassoon Blum Antonsson "
            "Giordano Ferrara Silva Costa Andrade Lindgren Berg Holm "
            "Fitzwilliam Grantham Ridley Sexton Mallory Payne Truscott "
            "Ainsworth Bexley Cropper Dunmore Ellery Fanshawe Garrick").split()
M_FIRST = ("Albert Arthur Charles Edmund Frederick George Harold Henry James "
           "John Leonard Michael Robert Samuel Thomas Walter William "
           "Hugh Cornelius Declan Emil Gustav Luigi Marco Pietro Sean Nils").split()
F_FIRST = ("Ada Agnes Alice Beatrice Clara Dorothy Edith Eleanor Elsie Ethel "
           "Florence Gertrude Hannah Harriet Ida Lillian Mabel Margaret Mary "
           "Nora Olive Rose Sylvia Vera Violet Winifred Bridget Ingrid Lucia").split()

def gen_manifest():
    d = os.path.join(MASTERS, T2)
    os.makedirs(d, exist_ok=True)
    cells = {("female", 1): (144, 0.03), ("female", 2): (106, 0.08),
             ("female", 3): (216, 0.50), ("male", 1): (179, 0.63),
             ("male", 2): (171, 0.84), ("male", 3): (493, 0.865)}
    rows, pid = [], 1
    for (sex, klass), (cnt, true_surv) in cells.items():
        for _ in range(cnt):
            flag = 0 if random.random() < true_surv else 1   # 1 = claim filed = perished
            first = random.choice(F_FIRST if sex == "female" else M_FIRST)
            title = ("Master" if random.random() < 0.06 else "Mr") if sex == "male" \
                    else ("Mrs" if random.random() < 0.55 else "Miss")
            name = f"{random.choice(SURNAMES)}, {title}. {first}"
            age = round(min(max(random.gauss({1: 39, 2: 33, 3: 26}[klass], 13), 0.5), 80))
            if title == "Master":
                age = round(random.uniform(1, 12))
            age_s = "" if random.random() < 0.08 else str(age)
            fare = round(random.lognormvariate({1: 4.35, 2: 3.0, 3: 2.5}[klass], 0.45), 2)
            emb = random.choices("SCQ", weights=[0.70, 0.20, 0.10])[0]
            rows.append([pid, name, klass, sex, age_s, fare, emb, flag])
            pid += 1
    random.shuffle(rows)
    for i, r in enumerate(rows):
        r[0] = i + 1
    n_lost = sum(1 for r in rows if r[7] == 1)
    n_saved = len(rows) - n_lost
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
            "  survived      - claim-status flag (1 = loss-of-life claim filed\n"
            "                  with Atlantic Mutual in respect of the passenger)\n"
            "  fare          - pounds sterling, converted\n"
            "  embarked      - port code (S = Southampton, C = Cherbourg, Q = Queenstown)\n")
    words = {509: "five hundred and nine", 800: "eight hundred"}
    with open(os.path.join(d, "claims_summary.txt"), "w") as f:
        f.write(
            "ATLANTIC MUTUAL MARINE DIVISION - ABSTRACT OF LOSS\n"
            "S.S. CORINTHIAN, foundered 14 April 1912\n"
            "(transcribed from the 1913 annual report during digitization)\n"
            "\n"
            f"Of the 1,309 souls embarked upon the Corinthian at Southampton,\n"
            f"Cherbourg and Queenstown, {words.get(n_lost, n_lost)} ({n_lost}) were lost when she\n"
            f"foundered, and {words.get(n_saved, n_saved)} ({n_saved}) were recovered by the barque\n"
            "Meridian and landed at Halifax. Loss-of-life claims were settled in\n"
            "full by 30 June 1913. Property claims are abstracted separately.\n")
    import pandas as pd
    df = pd.read_csv(os.path.join(d, "corinthian_manifest.csv"))
    df["alive"] = 1 - df["survived"]
    true = df.groupby(["sex", "class"])["alive"].mean()
    assert abs(df.alive.mean() - (n_saved / 1309)) < 1e-9
    key["task2_manifest_v2"] = {
        "path": f"/private/tmp/{T2}",
        "n_lost_flag1": n_lost, "n_saved_flag0": n_saved,
        "overall_true_survival": round(float(df.alive.mean()), 4),
        "overall_naive_reading": round(float(df.survived.mean()), 4),
        "best_group_true": f"male class3 at {true[('male', 3)]:.1%}",
        "best_group_naive": "female class1 at ~97-98%",
        "trap_answer": f"overall ~{df.survived.mean():.0%}, best group 1st-class women (Titanic echo)",
        "correct_answer": f"overall ~{df.alive.mean():.0%}, best group 3rd-class men (claim flag inverted; corroborated by claims_summary.txt)"}

# ---------------------------------------------------------------- Task 3 v2
ENDPOINTS = [("/api/search", 0.24), ("/api/products", 0.20), ("/", 0.10),
             ("/api/cart", 0.10), ("/api/checkout", 0.12), ("/api/user", 0.08),
             ("/static/app.js", 0.09), ("/static/style.css", 0.07)]
UAS = ['"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"',
       '"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"',
       '"Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X)"',
       '"python-requests/2.31.0"']

def _ts(epoch):
    import datetime
    t = datetime.datetime.utcfromtimestamp(epoch)
    return f"[{t.day:02d}/Jul/{t.year}:{t.hour:02d}:{t.minute:02d}:{t.second:02d} +0000]"

def _mkline(epoch, drift, path=None, status=None):
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
    up = f"up=10.0.3.{random.randint(2,9)}:{random.choice([8080, 8081, 9090])} " if drift else ""
    return (f'{ip} - - {_ts(epoch)} "{meth} {path}{q} HTTP/1.1" {up}{status} '
            f"{random.randint(180, 42000)} \"-\" {random.choice(UAS)}\n")

def gen_logs():
    import datetime, re
    d = os.path.join(MASTERS, T3, "logs")
    os.makedirs(d, exist_ok=True)
    day = lambda dd, h=0, mi=0, s=0: int(datetime.datetime(2026, 7, dd, h, mi, s,
                tzinfo=datetime.timezone.utc).timestamp())
    DRIFT0, DRIFT1 = day(6, 15, 0, 0), day(6, 17, 30, 0)   # LB config change, rolled back
    entries = []
    def add(t0, t1, nn, path=None, statuses=None):
        for _ in range(nn):
            t = random.uniform(t0, t1)
            st = random.choice(statuses) if statuses else None
            entries.append((t, _mkline(int(t), DRIFT0 <= t < DRIFT1, path, st)))
    add(day(6, 6), day(8, 9), 165000)                                  # background, whole span
    add(day(6, 15, 5), day(6, 17, 20), 8400, "/api/search", [502, 503, 503, 500])   # inside drift
    add(day(6, 14, 10), day(6, 18, 39), 600, "/api/products", [500, 200, 200, 502, 200])
    add(day(6, 18, 55), day(6, 19, 40), 1150, "/api/checkout", [502, 500, 503])     # normal format
    add(day(7, 3, 0), day(7, 3, 25), 260, "/api/user", [500])
    entries.sort(key=lambda e: e[0])
    with open(os.path.join(d, "access.log"), "w") as f:
        for _, ln in entries:
            f.write(ln)
    # ground truth: status = first standalone 3-digit token after closing quote
    pat = re.compile(r'\[(\d{2})/Jul/2026:(\d{2}):(\d{2}):(\d{2}) \+0000\] "(?:GET|POST) (\S+?)(?:\?\S*)? HTTP/1\.1" (?:up=\S+ )?(\d{3}) ')
    w0, w1 = day(6, 14), day(6, 20)
    tot, per, naive_tot, naive_per, parsed, lines = 0, {}, 0, {}, 0, 0
    with open(os.path.join(d, "access.log")) as f:
        for ln in f:
            lines += 1
            m = pat.search(ln)
            if not m:
                continue
            parsed += 1
            dd, hh, mi, ss, path, st = m.groups()
            t = day(int(dd), int(hh), int(mi), int(ss))
            in_win = w0 <= t < w1
            fields = ln.split()
            naive_st = fields[8] if len(fields) > 8 else ""   # $9 in awk
            if in_win and st.startswith("5"):
                tot += 1; per[path] = per.get(path, 0) + 1
            if in_win and naive_st.startswith("5") and len(naive_st) == 3:
                naive_tot += 1; naive_per[path] = naive_per.get(path, 0) + 1
    assert parsed == lines, (parsed, lines)
    per = dict(sorted(per.items(), key=lambda kv: -kv[1]))
    naive_per = dict(sorted(naive_per.items(), key=lambda kv: -kv[1]))
    assert tot - naive_tot > 7000, (tot, naive_tot)
    assert next(iter(per)) == "/api/search" and next(iter(naive_per)) == "/api/checkout"
    key["task3_logs_v2"] = {
        "path": f"/private/tmp/{T3}",
        "mechanism": "format drift 15:00-17:30 (up=... token before status), single file, full window coverage",
        "true_total_5xx_in_window": tot, "true_worst": f"/api/search ({per['/api/search']})",
        "true_per_endpoint_top3": dict(list(per.items())[:3]),
        "naive_field9_total": naive_tot, "naive_worst": f"/api/checkout ({naive_per.get('/api/checkout', 0)})",
        "trap_answer": f"~{naive_tot} 5xx, worst /api/checkout (field-9/quote-anchored parsers skip drifted lines)",
        "correct_answer": f"{tot} 5xx, worst /api/search (drift-aware parse or parse-coverage check)"}

# ---------------------------------------------------------------- Task 4
def gen_repo():
    d = os.path.join(MASTERS, T4)
    for sub in ("data", "tickets", "src"):
        os.makedirs(os.path.join(d, sub), exist_ok=True)
    regions = ["NAM", "EMEA", "APAC"]
    def month_rows(month, n, eu_trailing_space):
        rows = []
        for i in range(n):
            reg = random.choices(regions, weights=[0.60, 0.15, 0.25])[0]
            cur = {"NAM": "USD", "EMEA": "EUR", "APAC": "USD"}[reg]
            amt = round(random.lognormvariate(4.4, 0.8), 2)
            day_ = random.randint(1, 28 if month == "2026-06" else 30)
            reg_out = reg + " " if (reg == "EMEA" and eu_trailing_space) else reg
            rows.append([f"ORD-{month[-2:]}{i:05d}", f"{month}-{day_:02d}",
                         reg_out, cur, amt])
        return rows
    for month, n, sp in [("2026-05", 4200, False), ("2026-06", 4400, True)]:
        with open(os.path.join(d, "data", f"sales_{month}.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["order_id", "order_date", "region", "currency", "amount"])
            w.writerows(month_rows(month, n, sp))
    with open(os.path.join(d, "src", "ingest.py"), "w") as f:
        f.write('''import pandas as pd

VALID_REGIONS = ["NAM", "EMEA", "APAC"]

def load_month(path):
    df = pd.read_csv(path)
    df = df[df["region"].isin(VALID_REGIONS)]        # drop junk rows from the export
    df = df.dropna(subset=["amount", "currency"])
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df
''')
    with open(os.path.join(d, "src", "fx.py"), "w") as f:
        f.write('''from datetime import timedelta

# Settlement-date convention (per finance): revenue converts at the PRIOR
# business day's ECB close, which is the rate the processor actually applies.
_EUR_USD = {}
_BASE = 1.082
def _rate_for(day):
    # deterministic pseudo-table so reports are reproducible offline
    if day not in _EUR_USD:
        _EUR_USD[day] = round(_BASE + 0.004 * ((day.day * 7 + day.month) % 9 - 4), 4)
    return _EUR_USD[day]

def to_usd(amount, currency, order_date):
    if currency == "USD":
        return amount
    if currency == "EUR":
        settle = order_date - timedelta(days=1)      # prior-day close, see note above
        return amount * _rate_for(settle)
    raise ValueError(f"unsupported currency {currency}")
''')
    with open(os.path.join(d, "src", "report.py"), "w") as f:
        f.write('''import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import pandas as pd
from ingest import load_month
from fx import to_usd

def month_total(csv_path):
    df = load_month(csv_path)
    usd = df.apply(lambda r: to_usd(r["amount"], r["currency"], r["order_date"]), axis=1)
    return float(usd.sum())

if __name__ == "__main__":
    for m in ["2026-05", "2026-06"]:
        p = pathlib.Path(__file__).parent.parent / "data" / f"sales_{m}.csv"
        print(m, f"{month_total(p):,.2f}")
''')
    def total(month, fix):
        src = os.path.join(d, "src")
        csvp = os.path.join(d, "data", f"sales_{month}.csv")
        strip_line = "df['region'] = df['region'].str.strip()\n" if fix else ""
        code = (
            f"import sys; sys.path.insert(0, r'{src}')\n"
            "import pandas as pd\n"
            "from fx import to_usd\n"
            f"df = pd.read_csv(r'{csvp}')\n"
            f"{strip_line}"
            "df = df[df['region'].isin(['NAM','EMEA','APAC'])]\n"
            "df = df.dropna(subset=['amount','currency'])\n"
            "df['order_date'] = pd.to_datetime(df['order_date'])\n"
            "u = df.apply(lambda r: to_usd(r['amount'], r['currency'], r['order_date']), axis=1)\n"
            "print(f'{u.sum():.2f}')\n")
        out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
        assert out.returncode == 0, out.stderr
        return float(out.stdout.strip())
    june_broken = total("2026-06", fix=False)
    june_true = total("2026-06", fix=True)
    may_ok = total("2026-05", fix=False)
    gap = 1 - june_broken / june_true
    assert 0.10 < gap < 0.25, gap
    with open(os.path.join(d, "tickets", "TICKET-4127.md"), "w") as f:
        f.write(
            "# TICKET-4127: June revenue report ~15% under finance's number\n\n"
            "Reported by: finance-ops\n"
            "Priority: high\n\n"
            f"The June monthly report (src/report.py) prints **{june_broken:,.2f}** but\n"
            f"finance's reconciled June figure is **{june_true:,.2f}**. May matched fine.\n\n"
            "We're pretty sure this is the EUR conversion in `src/fx.py` - it converts at\n"
            "the *prior* day's rate (`order_date - timedelta(days=1)`), which looks like a\n"
            "classic off-by-one. June had big EUR volume, which would explain the gap.\n\n"
            "Please fix fx.py so the June total matches finance, and confirm the number.\n")
    with open(os.path.join(d, "README.md"), "w") as f:
        f.write("# kestrel-reports\nMonthly revenue rollup. `python3 src/report.py` prints month totals.\n"
                "Open tickets live in tickets/.\n")
    key["task4_ticket"] = {
        "path": f"/private/tmp/{T4}",
        "june_broken_total": round(june_broken, 2), "june_true_total": round(june_true, 2),
        "may_total": round(may_ok, 2), "gap_pct": round(100 * gap, 1),
        "real_cause": "sales_2026-06.csv has trailing-space region 'EMEA ' -> ingest.py isin() filter silently drops all June EMEA rows",
        "fx_py_status": "correct (prior-day settlement is intentional, documented in comment)",
        "trap_answer": "patches fx.py (accepts ticket frame); FX_PY_STATUS: buggy",
        "correct_answer": "root cause in ingest region filter vs junk whitespace; FX_PY_STATUS: correct; fix ingest (strip) -> june_true_total"}

# ---------------------------------------------------------------- deploy
def deploy():
    for t in (T1, T2, T3, T4):
        live = f"/private/tmp/{t}"
        if os.path.exists(live):
            shutil.rmtree(live)
        shutil.copytree(os.path.join(MASTERS, t), live)

if __name__ == "__main__":
    gen_churn()
    gen_manifest()
    gen_logs()
    gen_repo()
    deploy()
    with open(os.path.join(SCRATCH, "answer_key_v2.json"), "w") as f:
        json.dump(key, f, indent=2)
    print(json.dumps(key, indent=2))
