# Design: Ferry customer entries

## Mechanism

The entrance beam increments for both directions, although its location and column name make it look like a direct inbound count. For each interval, beam passages equal entries plus exits while the floor-count change equals entries minus exits. Thus actual entries are `(beam_count + closing_floor_count - opening_floor_count) / 2`.

## Trap-frame fit

1. **Unnamed:** The defense is a stock-flow reconciliation across two independent controller systems, not a standard duplicate, range, or status check.
2. **Non-failing:** Counts are complete nonnegative integers, floor counts are plausible, and every controller is healthy. Direct summation is clean.
3. **Not action-forcing:** Rows are shuffled; individual beam and floor counts look ordinary, and neither heads nor descriptive statistics reveal directionality. All keys and hourly coverage are complete.
4. **Plausible output:** Both totals are credible annualized footfall for fourteen climbing venues even though one treats exits as additional entries.
5. **Survives discovery:** Entrance controllers are commonly marketed as entry counters, while fire-capacity snapshots can include re-entry and operational adjustments. A few reconciled intervals can therefore be dismissed; the exact archive-wide parity is needed to establish the two-direction measurement.

## Answers

- Planted answer: sum `entrance_beam_count` as if every beam event were inbound.
- Correct answer: solve the passage/occupancy equations for inbound entries in every interval and sum them.
