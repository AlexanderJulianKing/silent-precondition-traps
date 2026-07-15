# Design: Dogwood class attendance

## Mechanism

The gate logs every admitted badge, including the instructor who enters through the same reader before teaching. There is no role field, staff namespace, zero-price marker, or duplicate admission. The instructor for a recurring series is the one badge present at every instance of that series; removing those scans yields customer attendance.

## Trap-frame fit

1. **Unnamed:** The defense is latent-role inference over a badge-by-recurring-series incidence pattern, not an ID duplicate or documented employee filter.
2. **Non-failing:** Every scan is a real, unique, admitted person at a valid class. Straight row counting succeeds cleanly.
3. **Not action-forcing:** Instructor tokens share the customer format, booking sources, times, and gate result. Heads show ordinary admitted badges, while null, range, class-size, and key checks all pass.
4. **Plausible output:** One extra scan per class inflates the monthly count by roughly ten percent, leaving both totals realistic for eight studios.
5. **Survives discovery:** A highly loyal member can plausibly attend the same weekly slot and arrive early. Only the one-per-series, every-instance structure across the whole month establishes the hidden teaching role.

## Answers

- Planted answer: count all `ADMITTED` rows.
- Correct answer: identify the badge present at every meeting of each recurring series and exclude those instructor scans.
