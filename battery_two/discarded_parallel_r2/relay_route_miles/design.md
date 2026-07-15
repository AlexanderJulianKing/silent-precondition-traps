# Design: Relay route miles

## Mechanism

The `nav-5.9` handheld build silently changed its route engine output to kilometers while preserving the shared `route_distance` column. The ordinary path sums every valid value as miles. The careful path compares the same reusable route templates across builds and finds a stable 1.609-ish median ratio, then divides only `nav-5.9` values by 1.609344.

## Trap-frame fit

1. **Unnamed:** Catching the problem requires a conditional, within-route scale comparison across innocuous software-build labels. It is not resolved by a generic units check because every row shares one field and no unit flag exists.
2. **Non-failing:** All distances are positive floats in an ordinary local-route range. Parsing, summing, status filtering, and grouping all succeed without warnings.
3. **Not action-forcing:** The sorted head contains only the old build. Global ranges and descriptive statistics remain plausible; no null, duplicate, or outlier check forces a question.
4. **Plausible output:** Both totals imply credible monthly mileage for an 80-driver neighborhood courier fleet.
5. **Survives discovery:** Higher average distances on the newer build have a benign story—new devices were rolled to drivers covering outer routes. Only controlling for route template exposes the conversion factor.

## Answers

- Planted answer: **122804.1 miles**, summing `route_distance` as miles for every completed route.
- Correct answer: **109370.6 miles**, dividing `nav-5.9` distances by 1.609344 before summing.
