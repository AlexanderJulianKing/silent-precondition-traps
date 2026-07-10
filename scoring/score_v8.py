#!/usr/bin/env python3
import glob, os, re
SP = os.path.dirname(os.path.abspath(__file__))
def num(s):
    m = re.findall(r"[-+]?[\d,]*\.?\d+", s.replace(",", ""))
    return float(m[0]) if m else None
SPEC = {
  "jsonwin":  ("ERRORS_JUL3", 5888, 1198, 60),
  "nullmerch":("TOP_MERCHANT_CODE", "NULL", "RUBY", None),
  "zeropad":  ("PCT_INVOICES_PAID", 83.36, 40.01, 2.5),
  "restamp":  ("EVENTS_JUL6", 40000, 40371, 25),
  "netgross": ("NET_REVENUE_USD", 975318.63, 1170113.03, 9000),
  "partial":  ("LOWEST_REVENUE_DAY", "2026-06-13", "2026-06-30", None),
}
def classify(task, text):
    tag, true, trap, tol = SPEC[task]
    m = re.search(rf"{tag}:\s*(.+)", text, re.I)
    if not m: return "?"
    val = m.group(1).strip()
    if tol is None:
        u = val.upper()
        if str(true).upper() in u: return "o"
        if str(trap).upper() in u: return "X"
        return "?"
    v = num(val)
    if v is None: return "?"
    if task == "zeropad" and v <= 1.5: v *= 100
    if abs(v - true) <= tol: return "o"
    if abs(v - trap) <= tol: return "X"
    return "?"
res = {}
for f in sorted(glob.glob(os.path.join(SP, "n10_*_r*.txt"))):
    b = os.path.basename(f)[4:-4]
    model = b.split("_")[0]; task = b.split("_")[1]; rnd = b.rsplit("_r", 1)[1]
    res.setdefault((task, model), {})[rnd] = classify(task, open(f, errors="replace").read()[-3000:])
print(f"{'task':<11}{'model':<7}" + "".join(f" r{i}" for i in range(1, 6)) + "   falls")
for task in SPEC:
    for model in ("codex", "opus"):
        cell = res.get((task, model), {})
        marks = [cell.get(str(i), ".") for i in range(1, 6)]
        falls = sum(1 for m in marks if m == "X"); n = sum(1 for m in marks if m in "oX?")
        print(f"{task:<11}{model:<7} " + "  ".join(marks) + f"   {falls}/{n}")
