# Design: Birch rush weight

## Mechanism

After a queue-buffer change, four packing lanes write the preceding parcel's service value onto the current closeout row; the parcel ID, weight, zone, time, and carrier charge remain aligned. IDs are unique and the lag preserves the marginal service mix, so a direct `service == RUSH` filter silently selects the wrong parcel weights. The actual service can be recovered because the carrier charge forms three tight weight-and-zone-normalized bands learned from the many correctly aligned rows.

## Trap-frame fit

1. **Unnamed:** This is a cross-row, single-field alignment defect. The defense requires learning an internal charge signature and comparing it with the nominal label; no duplicate, null, unit, or ordinary join check addresses it.
2. **Non-failing:** Every field is valid, every parcel is accepted, and each service and charge is individually plausible. Filtering and summing are warning-free.
3. **Not action-forcing:** The export is chronological and the early rows are aligned. Counts by service barely change because a one-row lag approximately preserves category totals, while charge variation by zone and weight looks normal.
4. **Plausible output:** Both weights are credible for a month of expedited parcels, and the planted result has the expected order of magnitude.
5. **Survives discovery:** Negotiated carrier prices, zone surcharges, and rounding provide a benign explanation for service/charge inconsistencies. Only normalizing the whole archive reveals three stable charge bands and the lane-local lag.

## Answers

- Planted answer: sum `measured_kg` where the exported `service` is `RUSH`.
- Correct answer: infer service from the stable carrier-charge signature and sum the truly RUSH parcel weights.
