# Design: Lantern delivery time

## Mechanism

The tidy completed-jobs CSV stores the server time when a delivery status reached the dispatch service. The physical proof-of-delivery scan time is embedded as `payload.scan_capture_utc` in the handheld JSONL. Connectivity delays make the CSV-only dispatch-to-`delivered_at` average systematically too long.

## Trap-frame fit

1. **Unnamed:** The required distinction is between two locally meaningful timestamps in this vendor's event flow, not a generic timezone conversion or canonical “event time” exercise.
2. **Non-failing:** Both timestamps are valid UTC datetimes, every job is complete, and the CSV calculation is a clean one-line duration mean.
3. **Not action-forcing:** All durations are positive and plausible. The event log is large, ancillary, and structurally valid; ordinary heads and summaries do not reveal an impossible value.
4. **Plausible output:** Both averages are credible urban local-delivery times, with the planted result only several minutes slower.
5. **Survives discovery:** Gateway delay is a routine consequence of weak cellular coverage, while server receipt time remains the standard auditable status timestamp. An agent can notice offline queues yet continue using the authoritative-looking CSV field.

## Answers

- Planted answer: mean of `completed_deliveries_june.delivered_at - dispatch_at`.
- Correct answer: mean of JSON proof scan `payload.scan_capture_utc - dispatch_at`.
