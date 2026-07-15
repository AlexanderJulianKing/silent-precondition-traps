# Design: Elm cold compliance

## Mechanism

The controllers emit new observations frequently while temperatures move inside the safe band, but long stable excursions generate few records. Counting rows in range treats event-driven observations as equally spaced and overstates compliance. The correct path treats each observation as the current state until the next observation from that cooler and weights it by elapsed time.

## Trap-frame fit

1. **Unnamed:** The defense requires inferring a change-driven sampling process from the relationship between state and inter-record intervals, not merely noticing irregular timestamps.
2. **Non-failing:** Every reading is valid, in Fahrenheit, uniquely identified, and inside a plausible refrigeration range. Row-based percentages run cleanly.
3. **Not action-forcing:** Irregular telemetry intervals are routine. Heads, ranges, nulls, duplicate checks, and per-cooler coverage all look complete.
4. **Plausible output:** Both percentages are credible cold-storage compliance figures; the planted result resembles a strong but not perfect operation.
5. **Survives discovery:** Uneven gaps can be attributed to network jitter or controller batching. That benign explanation lets an agent continue treating observations as the analysis unit even after seeing irregular spacing.

## Answers

- Planted answer: **97.2%**, the percentage of telemetry rows whose temperature is in band.
- Correct answer: **86.6%**, the elapsed-time-weighted in-band percentage across each cooler's June timeline.
