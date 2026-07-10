#!/usr/bin/env python3
"""Definitive battery ledger: 10 configs x 10 battery tasks x 5 rounds.
Outcomes: o correct / X planted / E other-error / N no-answer-or-missing."""
import glob, os, re, json
SP = os.path.dirname(os.path.abspath(__file__))
def num(s):
    m = re.findall(r"[-+]?[\d,]*\.?\d+", s.replace(",", ""))
    return float(m[0]) if m else None
SPEC = {
  "drift":("TOTAL_5XX_IN_WINDOW",10014,1407,60),"canary":("ERRORS_JUL3",6659,1365,40),
  "naregion":("TOP_REGION","NA","EMEA",None),"burst":("EVENTS_JUL5",40000,42312,30),
  "nullmerch":("TOP_MERCHANT_CODE","NULL","RUBY",None),"jsonwin":("ERRORS_JUL3",5888,1198,60),
  "partial":("LOWEST_REVENUE_DAY","2026-06-13","2026-06-30",None),
  "restampb":("EVENTS_JUL6",40000,40404,20),"netgrossb":("NET_REVENUE_USD",984925.57,1056863.26,9000),
  "trailspace":("PCT_INVOICES_PAID",82.61,39.79,2.5)}
TASKS = list(SPEC)
# config -> task -> filepattern
def simple(prefix): return {t: f"{prefix}_{t}_r{{r}}.txt" for t in TASKS}
CONFIGS = {
  "GPT-5.4-mini": simple("m54"), "Codex5.5@high": simple("ch"),
  "Sonnet5@high": simple("s5"), "Opus4.8@xhigh": simple("ox"),
  "Fable5@high": simple("f5"), "Sol@xhigh": simple("sol"),
  "Terra@xhigh": simple("terra"), "Luna@xhigh": simple("luna"),
  "Codex5.5@xhigh": {**{t: f"n5_codex_{t}_r{{r}}.txt" for t in ["drift","canary","naregion","burst"]},
                     **{t: f"n10_codex_{t}_r{{r}}.txt" for t in ["jsonwin","nullmerch","partial"]},
                     **{t: f"n11_codex_{t}_r{{r}}.txt" for t in ["trailspace","restampb","netgrossb"]}},
  "Opus4.8@high":  {**{t: f"n5_opus_{t}_r{{r}}.txt" for t in ["drift","canary","naregion","burst"]},
                    **{t: f"n10_opus_{t}_r{{r}}.txt" for t in ["jsonwin","nullmerch","partial"]},
                    **{t: f"n11_opus_{t}_r{{r}}.txt" for t in ["trailspace","restampb","netgrossb"]}},
}
def classify(task, path):
    if not os.path.exists(path): return "N"
    text = open(path, errors="replace").read()[-4000:]
    tag, true, trap, tol = SPEC[task]
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
    if tag == "PCT_INVOICES_PAID" and v <= 1.5: v *= 100
    if abs(v - true) <= tol: return "o"
    if abs(v - trap) <= tol: return "X"
    return "E"
grand = {"o":0,"X":0,"E":0,"N":0}
rows = []
print(f"{'config':<16}{'o':>4}{'X':>4}{'E':>3}{'N':>3}   fall% (X/(o+X+E))")
for cfg, tmap in CONFIGS.items():
    c = {"o":0,"X":0,"E":0,"N":0}
    for t in TASKS:
        for r in range(1,6):
            out = classify(t, os.path.join(SP, tmap[t].format(r=r)))
            c[out] += 1; rows.append((cfg,t,r,out))
    for k in grand: grand[k] += c[k]
    ans = c["o"]+c["X"]+c["E"]
    print(f"{cfg:<16}{c['o']:>4}{c['X']:>4}{c['E']:>3}{c['N']:>3}   {c['X']}/{ans} = {c['X']/ans:.0%}")
ans = grand["o"]+grand["X"]+grand["E"]
print(f"{'TOTAL(500)':<16}{grand['o']:>4}{grand['X']:>4}{grand['E']:>3}{grand['N']:>3}")
print(f"battery population: 500 design; answered {ans}; planted {grand['X']}; other-E {grand['E']}; no-answer/missing {grand['N']}")
print(f"answered-error concentration: {grand['X']}/{grand['X']+grand['E']} = {grand['X']/(grand['X']+grand['E']):.1%}")
print("N cells:", [(c,t,r) for c,t,r,o in rows if o=="N"])
print("E cells:", [(c,t,r) for c,t,r,o in rows if o=="E"])
json.dump(rows, open(os.path.join(SP,"battery_ledger.json"),"w"))
