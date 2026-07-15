#!/bin/bash
# usage: run_config_wave.sh <config_label> <round>
# Config table: codex efforts pinned explicitly (protocol amendment #3);
# claude invocations verbatim from Battery One.
CFG=$1; R=$2
BASE=/Users/alexanderking/Desktop/random_stuff/sol_trap_design
OUT=$BASE/battery
"$BASE/battery/deploy_battery2.sh"
run_codex() { # $1 model $2 effort $3 task $4 prompt
  ( cd "/private/tmp/$3" && codex exec -m "$1" -c model_reasoning_effort="$2" --sandbox workspace-write --skip-git-repo-check "$(cat "$4")" < /dev/null > "$OUT/b2_${CFG}_$3_r${R}.txt" 2>&1 ) &
}
run_claude() { # $1 model $2 extra-effort-args $3 task $4 prompt
  ( cd "/private/tmp/$3" && claude -p "$(cat "$4")" --model "$1" $2 --setting-sources project --allowedTools "Bash(python3:*)" "Bash(python:*)" "Read" "Glob" "Grep" "Write" "Edit" < /dev/null > "$OUT/b2_${CFG}_$3_r${R}.txt" 2>&1 ) &
}
while IFS='|' read -r task cpath; do
  P="$BASE/$cpath/prompt.txt"
  case "$CFG" in
    Codex5.5@high)    run_codex gpt-5.5 high "$task" "$P" ;;
    Codex5.5@xhigh)   run_codex gpt-5.5 xhigh "$task" "$P" ;;
    GPT-5.4-mini)     run_codex gpt-5.4-mini xhigh "$task" "$P" ;;
    Sol@xhigh)        run_codex gpt-5.6-sol xhigh "$task" "$P" ;;
    Terra@xhigh)      run_codex gpt-5.6-terra xhigh "$task" "$P" ;;
    Luna@xhigh)       run_codex gpt-5.6-luna xhigh "$task" "$P" ;;
    Opus4.8@high)     run_claude claude-opus-4-8 "" "$task" "$P" ;;
    Opus4.8@xhigh)    run_claude claude-opus-4-8 "--effort xhigh" "$task" "$P" ;;
    Sonnet5@high)     run_claude claude-sonnet-5 "" "$task" "$P" ;;
    Fable5@high)      run_claude claude-fable-5 "" "$task" "$P" ;;
    *) echo "unknown config $CFG"; exit 1 ;;
  esac
done < "$BASE/battery/battery2_map.txt"
wait
# post-wave cleanup (hygiene rule from operator log)
while IFS='|' read -r task cpath; do rm -rf "/private/tmp/$task"; done < "$BASE/battery/battery2_map.txt"
echo "WAVE DONE: $CFG r$R $(date -u +%H:%M)"
