#!/usr/bin/env python3
import glob, os, re, sys
SP = os.path.dirname(os.path.abspath(__file__))
PREFIX = sys.argv[1] if len(sys.argv) > 1 else "s5"
def num(s):
    m = re.findall(r"[-+]?[\d,]*\.?\d+", s.replace(",", ""))
    return float(m[0]) if m else None
SPEC = {
  "drift":     ("TOTAL_5XX_IN_WINDOW", 10014, 1407, 60),
  "canary":    ("ERRORS_JUL3", 6659, 1365, 40),
  "naregion":  ("TOP_REGION", "NA", "EMEA", None),
  "burst":     ("EVENTS_JUL5", 40000, 42312, 30),
  "nullmerch": ("TOP_MERCHANT_CODE", "NULL", "RUBY", None),
  "jsonwin":   ("ERRORS_JUL3", 5888, 1198, 60),
  "partial":   ("LOWEST_REVENUE_DAY", "2026-06-13", "2026-06-30", None),
  "restampb":  ("EVENTS_JUL6", 40000, 40404, 20),
  "netgrossb": ("NET_REVENUE_USD", 984925.57, 1056863.26, 9000),
  "trailspace":("PCT_INVOICES_PAID", 82.61, 39.79, 2.5),
}
def classify(task, text):
    tag, true, trap, tol = SPEC[task]
    m = re.findall(rf"{tag}:\s*(.+)", text)
    if not m: return "?"
    val = m[-1].strip()
    if tol is None:
        u = val.upper()
        if str(true).upper() in u.split()[0] if u else False: pass
        if str(true).upper() in u: return "o"
        if str(trap).upper() in u: return "X"
        return "?"
    v = num(val)
    if v is None: return "?"
    if task == "trailspace" and v <= 1.5: v *= 100
    if abs(v - true) <= tol: return "o"
    if abs(v - trap) <= tol: return "X"
    return "?"
res = {}
for f in sorted(glob.glob(os.path.join(SP, f"{PREFIX}_*_r*.txt"))):
    b = os.path.basename(f)[len(PREFIX)+1:-4]
    task, rnd = b.rsplit("_r", 1)
    if task not in SPEC: continue
    res.setdefault(task, {})[rnd] = classify(task, open(f, errors="replace").read()[-4000:])
print(f"{'task':<11}" + "".join(f" r{i}" for i in range(1,6)) + "   falls/n")
tot_f = tot_n = 0
for task in SPEC:
    cell = res.get(task, {})
    marks = [cell.get(str(i), ".") for i in range(1,6)]
    falls = sum(1 for m in marks if m == "X"); n = sum(1 for m in marks if m in "oX")
    tot_f += falls; tot_n += n
    print(f"{task:<11} " + "  ".join(marks) + f"   {falls}/{n}")
print(f"AGGREGATE {tot_f}/{tot_n}")
for task, cell in res.items():
    for rnd, v in cell.items():
        if v == "?":
            print(f"? {task} r{rnd}")
