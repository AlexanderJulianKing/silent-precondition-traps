#!/bin/bash
# Pristine redeploy of all 10 frozen Battery Two tasks
BASE=/Users/alexanderking/Desktop/random_stuff/sol_trap_design
while IFS='|' read -r task cpath; do
  rm -rf "/private/tmp/$task"
  cp -R "$BASE/$cpath/masters/$task" "/private/tmp/$task"
done < "$BASE/battery/battery2_map.txt"
