# Design: Maple cash close

## Mechanism

The register produces one row per drawer per day but serializes only denomination fields that changed since that drawer's prior close. Blank later fields mean “retain prior value,” as recorded in the export profile. Filtering June 30 first and treating blanks as zero yields a valid-looking but understated cash total. Correct analysis sorts within drawer, forward-fills the sparse state, and only then selects June 30.

## Trap-frame fit

1. **Unnamed:** This is an unusual vendor serialization contract: rows exist at a daily grain while individual columns carry state across rows. Generic missing-data advice does not determine the right interpretation.
2. **Non-failing:** Pandas reads blanks as ordinary nulls; `sum` skips them and `fillna(0)` is a natural, warning-free cash-count treatment.
3. **Not action-forcing:** Missing denomination fields are plausible zeros for cash drawers. Every row has a valid status and every drawer/date key is present, so basic completeness checks pass.
4. **Plausible output:** Both totals are credible cash holdings for 80 grocery drawers, with the planted result moderately lower.
5. **Survives discovery:** A blank count naturally means that denomination was absent, and the rows still look like completed daily audits. The innocuous compact-export profile is easy to regard as implementation metadata rather than a state-reconstruction rule.

## Answers

- Planted answer: filter June 30 and replace blank denomination fields with zero.
- Correct answer: forward-fill denomination state within drawer before filtering June 30.
