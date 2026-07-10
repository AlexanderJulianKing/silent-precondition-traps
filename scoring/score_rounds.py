#!/usr/bin/env python3
import glob, os, re, sys, json

SP = os.path.dirname(os.path.abspath(__file__))

def num(s):
    m = re.findall(r"[-+]?[\d,]*\.?\d+", s.replace(",", ""))
    return float(m[0]) if m else None

def classify(task, text):
    t = text.lower()
    def line(tag):
        m = re.search(rf"{tag}:\s*(.+)", text, re.I)
        return m.group(1).strip() if m else ""
    if task == "drift":
        v = num(line("TOTAL_5XX_IN_WINDOW"))
        if v is None: return "OTHER"
        return "TRUE" if abs(v - 10014) < 60 else ("TRAP" if abs(v - 1407) < 60 else "OTHER")
    if task == "canary":
        v = num(line("ERRORS_JUL3"))
        if v is None: return "OTHER"
        return "TRUE" if abs(v - 6659) < 40 else ("TRAP" if abs(v - 1365) < 40 else "OTHER")
    if task == "naregion":
        r = line("TOP_REGION").upper()
        if r.startswith("NA") or "NORTH" in r: return "TRUE"
        if "EMEA" in r: return "TRAP"
        return "OTHER"
    if task == "refunds":
        v = num(line("REFUND_RATE_JUNE"))
        if v is None: return "OTHER"
        if v > 1: v /= 100.0
        return "TRUE" if abs(v - 0.08) < 0.008 else ("TRAP" if abs(v - 0.0376) < 0.008 else "OTHER")
    if task == "status":
        v = num(line("PCT_DELIVERED"))
        if v is None: return "OTHER"
        if v > 1: v /= 100.0
        return "TRUE" if abs(v - 0.7231) < 0.02 else ("TRAP" if abs(v - 0.3865) < 0.02 else "OTHER")
    if task == "burst":
        v = num(line("EVENTS_JUL5"))
        if v is None: return "OTHER"
        return "TRUE" if abs(v - 40000) < 30 else ("TRAP" if abs(v - 42312) < 30 else "OTHER")
    return "OTHER"

results = {}
for f in sorted(glob.glob(os.path.join(SP, "n5_*_r*.txt"))):
    b = os.path.basename(f)[3:-4]                    # codex_drift_r1
    model, task, rnd = b.rsplit("_", 2)[0].split("_")[0], b.split("_")[1], b.rsplit("_r", 1)[1]
    text = open(f, errors="replace").read()[-3000:]
    results.setdefault((model, task), {})[rnd] = classify(task, text)

print(f"{'task':<10}{'model':<7}" + "".join(f" r{i}" for i in range(1, 6)) + "   falls")
order = ["drift", "canary", "naregion", "refunds", "status", "burst"]
for task in order:
    for model in ["codex", "opus"]:
        cell = results.get((model, task), {})
        marks, falls = [], 0
        for i in range(1, 6):
            v = cell.get(str(i), ".")
            marks.append({"TRAP": "X", "TRUE": "o", "OTHER": "?", ".": "."}[v])
            falls += v == "TRAP"
        n = sum(1 for m in marks if m != ".")
        print(f"{task:<10}{model:<7} " + "  ".join(marks) + f"   {falls}/{n}")
