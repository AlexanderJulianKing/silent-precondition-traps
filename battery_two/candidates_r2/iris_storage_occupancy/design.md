# Design: Iris storage occupancy

## Mechanism

Twelve wide rental units at each site have two doors and therefore two independently numbered controllers. Both controllers emit the same occupied state every night, but the physical space is one rentable unit. A natural sum across controllers counts occupied double-door units twice. No topology table exists; careful analysis identifies the paired doors through identical 30-day occupancy signatures within site and collapses each synchronized pair.

## Trap-frame fit

1. **Unnamed:** Ordinary duplicate checks pass because every controller/date row and reading ID is unique. The defense is inferring hidden physical topology from repeated longitudinal state signatures.
2. **Non-failing:** All 43,200 readings are complete binary states with `OK` health and exactly one row per controller/date.
3. **Not action-forcing:** Rows are shuffled and heads/tails are seeded with ordinary single-door controllers. Daily counts, ranges, nulls, and key uniqueness all look ideal.
4. **Plausible output:** Both averages imply believable occupancy for a facility with roughly one hundred rental units.
5. **Survives discovery:** Adjacent lockers are commonly rented together, so two controllers sharing a month-long occupancy history has a benign customer-behavior explanation. The repeated paired pattern across every site is what reveals double-door construction.

## Answers

- Planted answer: average the daily sum of occupied door controllers per site.
- Correct answer: collapse identical within-site 30-day controller signatures, then average occupied physical units.
