# Design: Cinder terminal sales

## Mechanism

The terminal firmware sends low-value processor heartbeat approvals through the same closeout route as customer approvals. They receive unique event and customer-looking tokens, ordinary card networks, item counts, `APPROVED` responses, and plausible amounts. A heartbeat is recoverable only from a joint signature: approval code equals the low six digits of terminal sequence, amount cents echo the sequence's last two digits, and timestamp seconds echo sequence modulo 60.

## Trap-frame fit

1. **Unnamed:** The defense is a bespoke three-field protocol fingerprint, not a standard status, duplicate, outlier, or test-account filter.
2. **Non-failing:** Heartbeats conform to the schema and every common parser treats them as normal approved rows. All IDs are unique and all monetary values are valid.
3. **Not action-forcing:** Heartbeats are dispersed across stores and dates, live inside the customer amount range, and do not form conspicuous timestamp bursts. Heads and descriptive summaries look like ordinary small baskets.
4. **Plausible output:** The planted total is only a few percent high and is entirely credible for ten neighborhood stores.
5. **Survives discovery:** Payment processors sometimes echo merchant sequence values in fallback approval codes, and transaction cents naturally span every suffix. Any one relation is easy to dismiss; all three must be tested jointly before the non-customer protocol becomes clear.

## Answers

- Planted answer: sum `approved_amount` for every `APPROVED` row.
- Correct answer: remove rows matching the complete heartbeat fingerprint, then sum customer approvals.
