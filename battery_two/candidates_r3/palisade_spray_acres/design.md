# Design: Palisade spray acres

## Mechanism

Adjacent boom passes intentionally overlap by two to four feet so no crop strip is missed. The controller closes and reports each pass independently; summing `controller_acres` counts edge strips twice. The actual field acreage reached is the geometric union of the per-field GPS rectangles.

## Trap-frame fit

1. **Unnamed:** The defense requires reconstructing two-dimensional coverage from thousands of survey-grid rectangles. Row duplicates, interval checks, group counts, and ordinary aggregation do not answer it.
2. **Non-failing:** Every pass is unique, complete, positive-area, in August, and `COMPLETE`. The ready-made acres column sums without any warning.
3. **Not action-forcing:** A few feet of overlap is invisible in coordinate ranges and random heads. Per-pass acreage, rig counts, timestamps, nulls, and statuses all look normal.
4. **Plausible output:** The planted total is only several percent high—the normal size of deliberate boom overlap—so both figures are credible contract acreage.
5. **Survives discovery:** Agronomists also use “applied acres” to mean cumulative boom work for chemical usage, where overlapped strips legitimately count twice. That benign operational convention lets an agent retain the controller sum even after noticing neighboring envelopes touch.

## Answers

- Planted answer: sum `controller_acres` over completed passes.
- Correct answer: compute the union of pass rectangles within each field and sum unique covered acreage.
