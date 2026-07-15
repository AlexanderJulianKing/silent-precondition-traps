# Design: Cobalt session length

## Mechanism

The telemetry partition closes any open row at midnight and immediately opens a new row with a new `session_id`, even though the account/device activity is uninterrupted. A row-level duration mean therefore treats long overnight sessions as two shorter sessions. Correct analysis stitches exactly adjacent intervals for the same account and device before averaging.

## Trap-frame fit

1. **Unnamed:** This is not a duplicate-row or generic sessionization exercise: every identifier is unique and each row is a valid telemetry session record. The defense requires inferring an undocumented partition boundary from interval adjacency.
2. **Non-failing:** All end times follow starts, durations are plausible, IDs are unique, and ordinary datetime arithmetic is clean.
3. **Not action-forcing:** Rows are deterministically shuffled, so heads and tails do not display paired fragments. Null, range, and duplicate checks pass. Midnight timestamps are common in global software usage.
4. **Plausible output:** Both averages are credible courseware engagement lengths; the planted value is moderately lower.
5. **Survives discovery:** Overnight learners and scheduled client activity provide a benign explanation for exact-midnight starts and ends. Only pairing the same account/device with zero gap establishes export fragmentation.

## Answers

- Planted answer: average duration per exported `session_id`.
- Correct answer: stitch zero-gap account/device intervals, then average continuous-session durations.
