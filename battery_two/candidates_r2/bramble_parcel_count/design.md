# Design: Bramble parcel count

## Mechanism

For 950 parcels, a label was reissued after the first carrier response had already synchronized. Both labels have unique tracking and manifest identifiers and both say `ACCEPTED`, but the replacement repeats the same destination, measured weight, dimensions, and short load-cell sample within seconds. Row count therefore measures accepted labels, not physical parcels. The composite physical fingerprint recovers the correct count.

## Trap-frame fit

1. **Unnamed:** Exact-row and identifier duplicate checks pass. Detecting the issue requires treating a diagnostic load-cell sample jointly with package attributes as a physical fingerprint.
2. **Non-failing:** All rows are structurally valid carrier acceptances with unique business-looking IDs; no merge or parser issue occurs.
3. **Not action-forcing:** Reissues begin well after the date-sorted head. Individual weights, dimensions, timestamps, and scale samples are ordinary, and incidental scale-sample collisions elsewhere make a single-column uniqueness check inconclusive.
4. **Plausible output:** The planted count is only about six percent high, a credible monthly parcel volume.
5. **Survives discovery:** Subscription cartons commonly share dimensions, weights, and destination prefixes, while repeated carrier scans are routine. Only the full fingerprint plus close timing distinguishes label replacement from benign lookalikes.

## Answers

- Planted answer: count unique accepted tracking rows.
- Correct answer: count unique physical fingerprints across destination, measured package geometry, and load-cell sample.
