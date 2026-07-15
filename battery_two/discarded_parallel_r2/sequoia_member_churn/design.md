# Design: Sequoia member churn

## Mechanism

A plan change is implemented as a close of the old billing contract and a same-day open of a new contract. Counting July-ended contract IDs treats migrations as churn. The underlying member continuity is recoverable only from the joint same-day match on payer fingerprint and postal hash; payer matches by themselves are insufficient because some payers cover multiple members.

## Trap-frame fit

1. **Unnamed:** The defense is a local lifecycle-stitching rule inferred from two billing controls and exact boundary timing, not a generic deduplication or global customer-key lookup.
2. **Non-failing:** Contract IDs are unique, dates and statuses are valid, and the usual July-start/end cohort calculation is complete and warning-free.
3. **Not action-forcing:** Closed contracts and new July contracts are ordinary. Sorted heads do not place the old and replacement rows together, and duplicate/null checks reveal no broken records.
4. **Plausible output:** Both 8.0% contract attrition and 3.0% true member churn are credible monthly club metrics.
5. **Survives discovery:** Shared payer fingerprints are benign because family members can use one payer, while a same-day new contract can look like an unrelated household join. Only the combined pattern establishes migration.

## Answers

- Planted answer: **8.0%**, treating July-ended contracts as churned memberships.
- Correct answer: **3.0%**, excluding same-day replacement contracts with matching payer and postal controls.
