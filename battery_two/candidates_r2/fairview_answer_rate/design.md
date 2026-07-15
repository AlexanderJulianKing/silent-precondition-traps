# Design: Fairview answer rate

## Mechanism

Callers who disconnect in the brief interval before the disposition writer starts do not produce CSV rows. They do consume a position in the switch's consecutive daily `switch_seq`. Counting visible outcomes therefore conditions on calls that survived long enough to be written and overstates answer rate. The correct denominator is the sum of each day's inclusive sequence span; all answered calls remain visible for the numerator.

## Trap-frame fit

1. **Unnamed:** This is not ordinary null handling or missing dates. The absent denominator is recoverable only from continuity in a switch-internal counter.
2. **Non-failing:** Every exported row is complete and valid; IDs are unique, outcomes recognized, and a row-based rate computes without warning.
3. **Not action-forcing:** The first and last calls each day are present, ranges look normal, and gaps are dispersed away from heads and tails. Null checks only find expected blank agent extensions on abandoned calls.
4. **Plausible output:** Both high-seventies and low-eighties answer rates are ordinary for a home-services call center.
5. **Survives discovery:** Telephone switches commonly reserve or consume sequence values for internal routing activity, so scattered gaps can be dismissed as harmless counter behavior rather than missing public calls.

## Answers

- Planted answer: answered rows divided by all exported disposition rows.
- Correct answer: answered rows divided by the summed inclusive daily `switch_seq` spans.
