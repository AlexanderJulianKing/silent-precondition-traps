# Design: Aster route miles

## Mechanism

Most handhelds write `route_distance` in miles. Build `5.14-R`, introduced partway through the month, writes kilometres into the same unlabelled numeric field. The correction is not documented in a support table: it is recoverable because every recurring route template has a within-template mean ratio near 1.609 between builds. Summing the column directly produces the planted total.

## Trap-frame fit

1. **Unnamed:** Catching the issue requires conditioning on an operational software build *within reused route templates* and recognizing a physical conversion ratio. Generic unit checks see only plausible domestic route lengths.
2. **Non-failing:** Every value is numeric, positive, in range, and attached to a valid completed route. No parser, join, or warning exposes the switch.
3. **Not action-forcing:** The export is date-sorted, so heads contain only the old build. Global ranges, null counts, status counts, and duplicate checks are clean. The new build's longer readings still fit suburban routes.
4. **Plausible output:** The planted total is only several percent high and remains credible for a regional courier fleet.
5. **Survives discovery:** The new build was deployed during a busy late-month period and can plausibly have been assigned to longer routes. Only controlling for `route_template` turns that benign explanation into a precise 1.609 pattern.

## Answers

- Planted answer: sum `route_distance` for completed routes as miles.
- Correct answer: divide build `5.14-R` readings by 1.609344 before summing.
