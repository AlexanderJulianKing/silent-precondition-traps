# Design: Harbor water usage

## Mechanism

Ten machines received new physical pulse registers midway through June. A natural per-machine `max - min` treats readings on both register origins as one cumulative series. The new register's low initial value becomes the machine minimum while the retired register often supplies the maximum, losing a large part of the two true spans. Correct usage is the sum of `max - min` for each `(machine_id, meter_serial)`.

## Trap-frame fit

1. **Unnamed:** The defense depends on recognizing physical register identity as the continuity boundary; ordinary machine-level cumulative-meter logic is otherwise appropriate.
2. **Non-failing:** All readings are valid integers with `OK` quality, and both groupbys execute cleanly without negative values or warnings.
3. **Not action-forcing:** Files are sorted by machine, and early machines have no exchange. A global describe shows an ordinary range of cumulative readings; the ten same-time handoffs are tiny within thousands of rows.
4. **Plausible output:** Both totals imply reasonable water consumption for 30 commercial washers, and the planted total is only moderately low.
5. **Survives discovery:** Scheduled meter replacement is benign facilities activity. Because the machine itself remains the consuming asset, an agent can acknowledge the service work yet retain machine as the seemingly natural aggregation key.

## Answers

- Planted answer: sum of each machine's June register range.
- Correct answer: sum of each physical meter serial's June register range.
