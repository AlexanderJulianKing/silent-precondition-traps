# Design: Linden field hours

## Mechanism

Technicians sometimes start a diagnostic, parts-lookup, or notes timer without stopping the enclosing customer-visit timer. All activity IDs are unique and all timers represent legitimate work, but a person cannot contribute two physical technician-hours simultaneously. Summing timer durations double-counts nested intervals. Correct total is the union of completed intervals within technician.

## Trap-frame fit

1. **Unnamed:** Duplicate and job-grain checks do not resolve overlapping clock exposure. The defense requires interval-union reasoning across legitimate activity codes.
2. **Non-failing:** Every timer has valid ordered timestamps, a complete status, and a unique ID. Straight duration summation is warning-free.
3. **Not action-forcing:** Rows are shuffled, so related timers are not adjacent in heads or samples. Duration ranges, dates, nulls, and identifiers are ordinary.
4. **Plausible output:** Both totals imply realistic monthly field hours for 90 technicians; the planted total is moderately high.
5. **Survives discovery:** Parallel diagnostic and documentation timers can be defended as valid administrative allocation to separate tasks, even though they cannot both count as physical technician clock time.

## Answers

- Planted answer: sum every completed activity-timer duration.
- Correct answer: merge overlapping intervals within technician and sum their union.
