# Design: Lark room hours

## Mechanism

Every access session is valid, but some sessions for the same physical studio overlap during handoffs and extended stays. Summing row durations counts the overlap twice. Correct room-hours are the union of time intervals within each room.

## Trap-frame fit

1. **Unnamed:** Catching the trap requires testing interval geometry for a physical resource, not a standard duplicate-row or unique-ID check.
2. **Non-failing:** All sessions have unique IDs, positive durations, completed status, and valid operating-hour timestamps. Direct duration summation is entirely clean.
3. **Not action-forcing:** The date-sorted head interleaves many rooms, so overlapping pairs are not adjacent. Describe, null, range, and full-duplicate checks look normal.
4. **Plausible output:** Both totals imply reasonable utilization across 24 studios and differ by only the accumulated handoff overlap.
5. **Survives discovery:** Overlaps have a benign booking explanation—one member stayed late as the next booking began—and sessions remain separately billable. An agent can accept them as legitimate records while still overcounting physical occupancy.

## Answers

- Planted answer: **7500.7 hours**, summing every completed session's duration.
- Correct answer: **7004.6 hours**, unioning overlapping intervals within each `room_id` before summing.
