# Design: Cedar units shipped

## Mechanism

The convenient item catalog is a June 30 current-state export. Twenty SKUs changed from 24 to 20 units per case during Q2 without changing SKU. Merging every shipment line to the current catalog applies 20 units to pre-change cases and undercounts individual units. The supplier notices provide the effective dates and prior pack sizes needed for an as-shipped conversion.

## Trap-frame fit

1. **Unnamed:** The check is a task-specific historical interpretation of a still-valid SKU, not a generic unit-conversion or duplicate-join warning.
2. **Non-failing:** Every shipment SKU matches exactly one current catalog row; the naive join is complete, validated, and warning-free.
3. **Not action-forcing:** Case counts, pack sizes, dates, and SKU uniqueness are all normal. Only a minority of routine supplier notices affects the result.
4. **Plausible output:** Both seven-figure unit totals fit the distributor's volume and differ by only a few percent.
5. **Survives discovery:** “Carton footprint refresh” is benign packaging maintenance, and the unchanged SKU makes the current catalog look like a reasonable canonical conversion source even after the notices are seen.

## Answers

- Planted answer: multiply every case by `current_item_catalog.units_per_case`.
- Correct answer: use the notice's prior pack size for shipments before each SKU's effective change date.
