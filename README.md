# The NULL Merchant — study artifacts

Reproducibility package for *The `NULL` Merchant and Other Silent Precondition Traps
for Data-Science Agents*.

## Contents
- `generators/` — seeded Python scripts that build every task environment
  (`gen_tasks.py` = v1; `gen_tasks_v2.py` … `gen_tasks_v81.py` = later battery
  generations). Each is deterministic: running it reproduces its environment
  byte-for-byte. Requires numpy 1.24.4, pandas 2.0.3, scikit-learn 1.6.1, python 3.9.
- `environments/` — the generated task folders (masters), i.e. the traps as evaluated.
- `prompts/` — the neutral task prompts and the warned-ablation hygiene preamble.
- `transcripts/` — every scored subject run (~635 files), one per (task, configuration, round).
- `scoring/` — the mechanical scorer (`score_battery.py`, `ledger.py`), the run
  ledger every figure derives from (`battery_ledger_final.json`), the per-generation
  answer keys, and the quote-fidelity checker (`quote_check.py`).
- `verification/` — the human-verification checklist and the quote audit.

## Battery Two (Sol-designed half)

`battery_two/` adds the second frozen battery: ten tasks designed by GPT-5.6 Sol under the
pre-registered protocol in `battery_two/PROTOCOL_SOL_BATTERY.md` (amendments and operator
log included). Contents: all design-session transcripts and designer prompts
(`design_sessions/`), every candidate from all three design rounds including failed and
discarded designs (`candidates_r1/`, `candidates_r2/`, `candidates_r3/`,
`discarded_parallel_r2/`), the frozen manifest with SHA-256 tree hashes
(`BATTERY_TWO_FROZEN.json`), all screening transcripts (`screening/round1..3`), the 500
battery-run transcripts with ledger, scorer, harness, and isolation probes (`battery/`).
In the ledgers, GPT-5.5 configurations appear under their CLI-era label `Codex5.5`, and
the halves are labeled Battery One and Battery Two.

`supplementary_report.md` is the development-history report referenced by the paper
(scrubbed of internal model-review quotations; see its release note).

## Provenance note
The v2–v8 generator sources were reconstructed after a file-management error during
data collection and re-verified by regenerating each environment and confirming it is
byte-identical to the preserved master (all 8 pass; v1 was recovered intact). The
environments, transcripts, and ledger were never affected.

## Reproduce a result
1. `cd generators && python3 gen_tasks_v8.py` — writes `masters_v8/` and deploys task
   folders to `/private/tmp/`.
2. Point an agent CLI at a task folder with the matching `prompts/` prompt.
3. Score the final answer with `scoring/score_battery.py`.
