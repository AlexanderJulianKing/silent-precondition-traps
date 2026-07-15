# Design: Granite shrink rate

## Mechanism

The ERP quantity in the stocktake has already moved carrier-dispatched units to the destination warehouse, but those units were still on trucks and could not appear in destination blind counts. Treating the stocktake's ready-made `erp_qty - counted_qty` as shrink classifies every open transfer as loss. The physical-on-hand denominator and variance must first remove destination-bound in-transit units.

## Trap-frame fit

1. **Unnamed:** The critical fact is this distributor's transfer-booking moment relative to a physical close, not a generic duplicate/null/join rule.
2. **Non-failing:** The stocktake alone is internally complete and yields ordinary nonnegative variances. Incorporating the transfer register is also a clean keyed merge.
3. **Not action-forcing:** In-transit transfers at month end are routine. Heads, descriptive ranges, unique SKU-location checks, and null counts all look normal; blank receipt times agree with `IN_TRANSIT` status.
4. **Plausible output:** Both roughly three-percent and roughly one-percent shrink are credible small-distributor results.
5. **Survives discovery:** Open transfers are a benign close-review artifact, and an agent can assume the ERP stocktake quantity already accounts for them because it is explicitly called the ERP quantity.

## Answers

- Planted answer: total `erp_qty - counted_qty`, divided by total `erp_qty`.
- Correct answer: subtract destination-bound open-transfer units from ERP quantities before calculating both missing units and the physical-on-hand denominator.
