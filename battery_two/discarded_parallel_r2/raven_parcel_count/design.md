# Design: Raven parcel count

## Mechanism

When an accepted label is unreadable at induction, the same parcel is labeled again seconds later. The old accepted record is retained, and the second record has a distinct tracking ID and timestamp, so counting unique tracking IDs produces the planted answer. A careful analyst identifies pairs with the same lane, destination, precise weight, dimensions, and a 0–90 second gap. Similar cartons recurring days apart are legitimate and must not be collapsed.

## Trap-frame fit

1. **Unnamed:** The defense is a domain-specific spatiotemporal fingerprint for physical label replacement, not an exact-duplicate or key-uniqueness check.
2. **Non-failing:** Every row has a unique accepted tracking number and valid dimensions; all common parsing and counting routes succeed.
3. **Not action-forcing:** Relabels begin well after the sorted head. Full-row duplicates are zero, IDs are unique, and recurring identical subscription cartons make repeated physical attributes unsurprising.
4. **Plausible output:** The wrong count is only several percent above the true parcel volume, entirely credible for a busy fulfillment shop.
5. **Survives discovery:** Two identical cartons at one lane can be consecutive subscription orders. Only the combined destination/scale/dimension/time signature separates relabels from legitimate repeated cartons.

## Answers

- Planted answer: **15847 parcels**, counting unique accepted tracking IDs.
- Correct answer: **15000 parcels**, collapsing same-lane physical signatures repeated within 90 seconds.
