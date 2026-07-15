#!/bin/bash
# Battery Two: 5 rounds x 10 configs x 10 tasks = 500 runs.
# Lab-alternating config order to spread provider load.
BASE=/Users/alexanderking/Desktop/random_stuff/sol_trap_design/battery
CONFIGS=("Codex5.5@high" "Opus4.8@high" "Codex5.5@xhigh" "Opus4.8@xhigh" "GPT-5.4-mini" "Sonnet5@high" "Sol@xhigh" "Fable5@high" "Terra@xhigh" "Luna@xhigh")
for R in 1 2 3 4 5; do
  for CFG in "${CONFIGS[@]}"; do
    bash "$BASE/run_config_wave.sh" "$CFG" "$R"
  done
  echo "ROUND $R COMPLETE $(date -u +%H:%M)"
done
echo "BATTERY_TWO_ALL_RUNS_DONE"
