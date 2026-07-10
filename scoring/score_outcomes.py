#!/usr/bin/env python3
"""Four-outcome rescoring per Sol review: correct / planted / other-error / no-answer."""
import glob, os, re
SP = os.path.dirname(os.path.abspath(__file__))
def num(s):
    m = re.findall(r"[-+]?[\d,]*\.?\d+", s.replace(",", ""))
    return float(m[0]) if m else None
BATT = {
  "drift":("TOTAL_5XX_IN_WINDOW",10014,1407,60),"canary":("ERRORS_JUL3",6659,1365,40),
  "naregion":("TOP_REGION","NA","EMEA",None),"burst":("EVENTS_JUL5",40000,42312,30),
  "nullmerch":("TOP_MERCHANT_CODE","NULL","RUBY",None),"jsonwin":("ERRORS_JUL3",5888,1198,60),
  "partial":("LOWEST_REVENUE_DAY","2026-06-13","2026-06-30",None),
  "restampb":("EVENTS_JUL6",40000,40404,20),"netgrossb":("NET_REVENUE_USD",984925.57,1056863.26,9000),
  "trailspace":("PCT_INVOICES_PAID",82.61,39.79,2.5)}
N5 = {"drift":BATT["drift"],"canary":BATT["canary"],"naregion":BATT["naregion"],"burst":BATT["burst"],
      "refunds":("REFUND_RATE_JUNE",8.0,3.76,0.8),"status":("PCT_DELIVERED",72.31,38.65,2.0)}
V8 = {"jsonwin":BATT["jsonwin"],"nullmerch":BATT["nullmerch"],"partial":BATT["partial"],
      "zeropad":("PCT_INVOICES_PAID",83.36,40.01,2.5),"restamp":("EVENTS_JUL6",40000,40371,25),
      "netgross":("NET_REVENUE_USD",975318.63,1170113.03,9000)}
V81 = {"trailspace":BATT["trailspace"],"restampb":BATT["restampb"],"netgrossb":BATT["netgrossb"]}
CORPORA = [("m54",BATT,"GPT-5.4-mini"),("ch",BATT,"Codex@high"),("s5",BATT,"Sonnet 5"),
           ("ox",BATT,"Opus@xhigh"),("f5",BATT,"Fable 5"),("sol",BATT,"Sol (partial)"),
           ("terra",BATT,"Terra (partial)"),("luna",BATT,"Luna (partial)"),
           ("n10",V8,"anchor v8 cells"),("n11",V81,"anchor v81 cells"),("n5",N5,"anchor n5 cells")]
def classify(spec, task, text):
    tag, true, trap, tol = spec[task]
    m = re.findall(rf"{tag}:\s*(.+)", text)
    if not m: return "N"
    val = m[-1].strip()
    if tol is None:
        u = val.upper()
        if str(true).upper() in u: return "o"
        if str(trap).upper() in u: return "X"
        return "E"
    v = num(val)
    if v is None: return "N"
    if tag in ("PCT_INVOICES_PAID","REFUND_RATE_JUNE","PCT_DELIVERED") and v <= 1.5: v *= 100
    if abs(v - true) <= tol: return "o"
    if abs(v - trap) <= tol: return "X"
    return "E"
tot = {"o":0,"X":0,"E":0,"N":0}
print(f"{'corpus':<18}{'n':>4}{'correct':>9}{'planted':>9}{'otherE':>8}{'noAns':>7}")
for pre, spec, label in CORPORA:
    c = {"o":0,"X":0,"E":0,"N":0}
    for f in sorted(glob.glob(os.path.join(SP, f"{pre}_*_r*.txt"))):
        parts = os.path.basename(f)[:-4].split("_")
        task = parts[2] if pre in ("n5","n10","n11") else parts[1]
        if task not in spec: continue
        c[classify(spec, task, open(f, errors="replace").read()[-4000:])] += 1
    n = sum(c.values())
    if n == 0: continue
    for k in tot: tot[k] += c[k]
    print(f"{label:<18}{n:>4}{c['o']:>9}{c['X']:>9}{c['E']:>8}{c['N']:>7}")
n = sum(tot.values())
print(f"{'TOTAL':<18}{n:>4}{tot['o']:>9}{tot['X']:>9}{tot['E']:>8}{tot['N']:>7}")
print(f"other-error rate: {tot['E']/n:.1%}   no-answer rate: {tot['N']/n:.1%}")
