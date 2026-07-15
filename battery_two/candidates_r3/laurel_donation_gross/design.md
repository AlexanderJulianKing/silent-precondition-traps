# Design: Laurel donation gross

## Mechanism

The gateway's JSON serializer emits the same decoded `amount` name twice in each object: donor gross early in the payload under a Unicode-escaped spelling and processor-net settlement near the end under the plain spelling. Python's normal JSON loader and pandas' habitual JSON route accept the object without warning and keep only the last value. Summing the resulting `amount` column therefore produces net donations. A duplicate-preserving object-pairs parse reveals both values, with first amount equal to last amount plus processor fee on every event.

## Trap-frame fit

1. **Unnamed:** Standard JSON ingestion silently normalizes the payload. Catching it requires preserving ordered key-value pairs rather than applying an ordinary null, duplicate-row, or schema check.
2. **Non-failing:** Duplicate object names are accepted by the common Python loaders used in screening; every event parses, types infer, and aggregation succeeds with no warning.
3. **Not action-forcing:** Both values are plausible monetary amounts, separated by many metadata fields, and the first raw key uses a legal Unicode escape rather than repeating the visible spelling. Parsed heads, descriptions, status counts, and identifier checks show only the final value and look clean.
4. **Plausible output:** Processor net is only about three percent below donor gross, so the planted total looks exactly like a normal fundraising result.
5. **Survives discovery:** Last-value-wins is a common compatibility behavior for duplicate JSON names, and net settlement is a legitimate finance measure. Even seeing repeated names permits a benign parser story unless the fee identity is reconciled and the requested gross scope is enforced.

## Answers

- Planted answer: parse normally and sum the surviving `amount` value (processor net).
- Correct answer: preserve duplicate keys and sum the first `amount` value (donor gross), verified by gross = net + fee.
