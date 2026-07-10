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
