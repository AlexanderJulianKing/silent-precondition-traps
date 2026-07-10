#!/usr/bin/env python3
"""Quote-fidelity checker. Extracts every quoted span from a document and
searches the source corpus for verbatim (normalized) presence.
Statuses: FOUND(file) / FRAGMENTS-FOUND(file, for ellipsis quotes) /
SELF-COINAGE (whitelisted term of art) / SHORT (below mechanical threshold) /
NOT-FOUND (human attention). Proves presence only — not attribution/context."""
import glob, json, os, re, sys, unicodedata

SP = os.path.dirname(os.path.abspath(__file__))
DOCS = sys.argv[1:]
MINLEN = 12

WHITELIST = ["your grep can go blind mid-file", "status is field 9", "errors match",
  "named-idiom boundary", "template-echo correction", "silent on every natural path",
  "invisible to standing checks", "non-failing on habitual paths",
  "not action-forcing under habitual checks", "an observant analyst catches these",
  "audit our ledger", "as-shipped", "quiet hours", "same-model-config blinded review",
  "finding-shaped object", "airtight", "fall", "falls", "leaky", "hunt-scan",
  "hunt-rate", "released", "will be released", "blinded", "registered",
  "45/45 across eight configurations"]  # self-retracted claim quoted in a correction note

def norm(s):
    s = unicodedata.normalize("NFKC", s)
    for a, b in [("“", '"'), ("”", '"'), ("‘", "'"), ("’", "'"),
                 ("…", "..."), ("—", "-"), ("–", "-"), (" ", " ")]:
        s = s.replace(a, b)
    s = re.sub(r"\[([a-z]+)\]", r"\1", s)          # appl[y] -> apply
    s = s.replace("**", "").replace("`", "")
    s = re.sub(r"\s+", " ", s)
    return s.strip()

corpus = {}
for f in glob.glob(os.path.join(SP, "*.txt")) + glob.glob(os.path.join(SP, "litcheck", "*")) \
         + [os.path.join(SP, "warn_preamble.txt")]:
    if os.path.isfile(f):
        try: corpus[os.path.basename(f)] = norm(open(f, errors="replace").read())
        except Exception: pass

def find(q):
    hits = [name for name, text in corpus.items() if q.lower() in text.lower()]
    return hits

report = []
for doc in DOCS:
    text = open(doc, errors="replace").read()
    spans = re.findall(r'[“"]([^“”"]{4,400}?)[”"]', text)
    seen = set()
    for raw in spans:
        q = norm(raw)
        if q in seen: continue
        seen.add(q)
        if any(w == q.lower() or (len(q) < 40 and w in q.lower() and len(w) > len(q) - 8) for w in WHITELIST):
            status, src = "SELF-COINAGE", ""
        elif len(q) < MINLEN:
            status, src = "SHORT (human judgment)", ""
        else:
            frags = [f.strip() for f in q.split("...") if len(f.strip()) >= MINLEN]
            if not frags:
                status, src = "SHORT (human judgment)", ""
            else:
                per = [set(find(f)) for f in frags]
                common = set.intersection(*per) if per else set()
                any_hits = set().union(*per) if per else set()
                if common:
                    status = "FOUND" if len(frags) == 1 else "FRAGMENTS-FOUND (same file)"
                    src = sorted(common)[0] + ("" if len(common) == 1 else f" +{len(common)-1}")
                elif any_hits:
                    status, src = "FRAGMENTS SPLIT ACROSS FILES (check ellipsis!)", ",".join(sorted(any_hits))[:80]
                else:
                    status, src = "NOT-FOUND (human attention)", ""
        report.append((os.path.basename(doc), status, q[:100], src))

order = {"NOT-FOUND (human attention)": 0, "FRAGMENTS SPLIT ACROSS FILES (check ellipsis!)": 1,
         "SHORT (human judgment)": 2, "FRAGMENTS-FOUND (same file)": 3, "FOUND": 4, "SELF-COINAGE": 5}
report.sort(key=lambda r: (order.get(r[1], 9), r[0]))
counts = {}
for r in report: counts[r[1]] = counts.get(r[1], 0) + 1
print("SUMMARY:", counts, "\n")
for doc, status, q, src in report:
    if order.get(status, 9) <= 2:
        print(f"[{status}] ({doc}) \"{q}\" {('-> '+src) if src else ''}")
lines = ["# Quote-fidelity audit (mechanical; proves presence, not attribution/context)", "",
         f"Summary: {counts}", ""]
for doc, status, q, src in report:
    lines.append(f"- **{status}** ({doc}): \"{q}\"" + (f" — `{src}`" if src else ""))
open("/Users/alexanderking/Desktop/random_stuff/simplebench_research/quote_audit.md", "w").write("\n".join(lines))
print("\nwrote quote_audit.md")
