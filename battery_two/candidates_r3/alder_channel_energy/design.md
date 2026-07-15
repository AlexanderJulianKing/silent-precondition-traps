# Design: Alder channel energy

## Mechanism

Each workshop has ten equipment channels and two opaque upstream channels covering small pairs of those same machines. The upstream readings are independent meters with realistic noise, not duplicate rows, but adding every channel counts the covered cells twice. The topology table is absent. A careful path finds, within each site, the two channel histories that are near-additive copies of combinations of other histories and excludes those redundant upstream measurements.

## Trap-frame fit

1. **Unnamed:** The defense is a per-site subset search over longitudinal numeric signatures. There is no `parent_channel`, equipment type, repeated identifier, or standard join check that exposes the hierarchy.
2. **Non-failing:** All channel/date keys are complete, every value is positive, and all devices report `OK`; a direct sum is entirely clean.
3. **Not action-forcing:** Rows are shuffled, opaque channel IDs have identical formats, and feeder magnitudes overlap ordinary high-draw equipment. Heads, ranges, nulls, date coverage, and duplicate checks look ideal.
4. **Plausible output:** Both totals are credible monthly production-energy use for twelve small workshops, with a moderate rather than absurd inflation.
5. **Survives discovery:** Equipment in the same production cell is co-scheduled, so very high correlation and approximate additivity can be absorbed as ordinary coordinated load unless combinations are tested across the full month.

## Answers

- Planted answer: sum `kwh` across every exported channel.
- Correct answer: identify and exclude the two redundant upstream channel series per site, then sum the equipment channels.
