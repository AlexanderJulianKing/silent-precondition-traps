#!/usr/bin/env python3
"""V4: replication of the instrument-precondition trap in a new skin.
service.log spans Jul 2-4. A canary logfmt rollout (Jul 3 09:30-14:00, rolled
back) changes 'ERROR' lines to 'level=error' mid-window. The Jul 3 error spike
(payments-db pool exhaustion, 10:20-12:40) sits inside the canary window.
Naive `grep ERROR` sees only classic-format errors -> plausible undercount and
wrong peak hour."""
import json, os, random, shutil, datetime
import numpy as np

SEED = 31
random.seed(SEED)
np.random.seed(SEED)
SCRATCH = os.path.dirname(os.path.abspath(__file__))
MASTERS = os.path.join(SCRATCH, "masters_v4")
T9 = "svcops_review"

HOSTS = ["web-3", "web-5", "web-7", "api-2", "api-4", "worker-1"]
MODS = ["checkout", "search", "auth", "cart", "billing", "notify"]
CLASSIC_MSGS = ["request completed", "cache refresh ok", "session issued",
                "queue depth nominal", "healthcheck ok", "config reloaded"]
ERR_MSGS = ["db pool exhausted acquiring connection", "upstream timeout after 5000ms",
            "failed to persist payment intent", "lock wait timeout on orders row"]

def iso(t):
    return datetime.datetime.utcfromtimestamp(t).strftime("%Y-%m-%dT%H:%M:%SZ")

def classic(t, level, mod, msg):
    return f"{iso(t)} {random.choice(HOSTS)} {level} [{mod}] {msg}\n"

def logfmt(t, level, mod, msg):
    return (f'ts={iso(t)} host={random.choice(HOSTS)} level={level.lower()} '
            f'module={mod} msg="{msg}"\n')

def gen():
    d = os.path.join(MASTERS, T9, "logs")
    os.makedirs(d, exist_ok=True)
    day = lambda dd, h=0, m=0, s=0: int(datetime.datetime(2026, 7, dd, h, m, s,
                tzinfo=datetime.timezone.utc).timestamp())
    CAN0, CAN1 = day(3, 9, 30), day(3, 14, 0)      # canary logfmt window
    entries = []
    def emit(t, level, mod, msg):
        fn = logfmt if CAN0 <= t < CAN1 else classic
        entries.append((t, fn(t, level, mod, msg)))
    # background: Jul 2 00:00 -> Jul 4 23:59, ~140k lines, 1.2% ERROR
    t0, t1 = day(2), day(5) - 1
    for _ in range(140000):
        t = random.uniform(t0, t1)
        r = random.random()
        if r < 0.012:
            emit(t, "ERROR", random.choice(MODS), random.choice(ERR_MSGS))
        elif r < 0.06:
            emit(t, "WARN", random.choice(MODS), "slow response 1800ms")
        else:
            emit(t, "INFO", random.choice(MODS), random.choice(CLASSIC_MSGS))
    # spike: Jul 3 10:20-12:40, payments-db pool exhaustion, inside canary
    for _ in range(5200):
        t = random.uniform(day(3, 10, 20), day(3, 12, 40))
        emit(t, "ERROR", "billing", ERR_MSGS[0])
    # secondary bump OUTSIDE canary: Jul 3 16:10-16:40 auth upstream, classic fmt
    for _ in range(900):
        t = random.uniform(day(3, 16, 10), day(3, 16, 40))
        emit(t, "ERROR", "auth", ERR_MSGS[1])
    entries.sort(key=lambda e: e[0])
    with open(os.path.join(d, "service.log"), "w") as f:
        for _, ln in entries:
            f.write(ln)
    # ground truth for Jul 3 00:00-24:00
    w0, w1 = day(3), day(4)
    tot = naive = 0
    per_hour, naive_hour = {}, {}
    with open(os.path.join(d, "service.log")) as f:
        for ln in f:
            if ln.startswith("ts="):
                ts = ln[3:23]; lvl = "ERROR" if "level=error" in ln else "X"
            else:
                ts = ln[0:20]; lvl = ln.split(" ", 3)[2] if ln.count(" ") > 2 else "X"
            t = int(datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
                    .replace(tzinfo=datetime.timezone.utc).timestamp())
            if not (w0 <= t < w1) or lvl != "ERROR":
                continue
            hr = datetime.datetime.utcfromtimestamp(t).hour
            tot += 1; per_hour[hr] = per_hour.get(hr, 0) + 1
            if "ERROR" in ln:                      # what grep ERROR sees
                naive += 1; naive_hour[hr] = naive_hour.get(hr, 0) + 1
    peak = max(per_hour, key=per_hour.get)
    naive_peak = max(naive_hour, key=naive_hour.get)
    assert tot - naive > 4000 and peak != naive_peak, (tot, naive, peak, naive_peak)
    key = {"task9_logfmt_canary": {
        "path": f"/private/tmp/{T9}",
        "mechanism": "canary logfmt rollout 09:30-14:00 Jul 3 (rolled back); ERROR -> level=error inside canary; spike 10:20-12:40 inside canary",
        "true_errors_jul3": tot, "true_peak_hour_utc": peak,
        "naive_grep_ERROR": naive, "naive_peak_hour_utc": naive_peak,
        "trap_answer": f"~{naive} errors, peak hour {naive_peak}:00 (grep ERROR misses logfmt lines)",
        "correct_answer": f"{tot} errors, peak hour {peak}:00 (both formats parsed)"}}
    live = f"/private/tmp/{T9}"
    if os.path.exists(live):
        shutil.rmtree(live)
    shutil.copytree(os.path.join(MASTERS, T9), live)
    with open(os.path.join(SCRATCH, "answer_key_v4.json"), "w") as f:
        json.dump(key, f, indent=2)
    print(json.dumps(key, indent=2))

if __name__ == "__main__":
    gen()
