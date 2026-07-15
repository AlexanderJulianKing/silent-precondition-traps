# Design: Swift response time

## Mechanism

The convenient `response_seconds` KPI equals elapsed time for ordinary tickets but saturates at exactly 900 seconds for every longer response. Averaging it truncates the long tail. The uncapped elapsed time remains recoverable from `opened_at` and `first_human_reply_at`.

## Trap-frame fit

1. **Unnamed:** The check is an equality audit between a convenience metric and redundant timestamps specifically at its upper support, not a standard null/range/negative-duration check.
2. **Non-failing:** All response metrics and timestamps are valid and positive; the direct mean is the simplest warning-free calculation.
3. **Not action-forcing:** The sorted head contains no capped tickets. A maximum of 900 seconds is credible for a support team managed to a 15-minute SLA, and describe reports no outlier.
4. **Plausible output:** Both averages represent believable appliance-support response times, with the planted value modestly better.
5. **Survives discovery:** A large cluster at 15 minutes can be explained by SLA-driven queue discipline or scheduled escalation, allowing an agent to trust the purpose-built KPI instead of checking timestamp equality in the tail.

## Answers

- Planted answer: **10.3 minutes**, the mean of `response_seconds` divided by 60.
- Correct answer: **12.8 minutes**, the mean of `first_human_reply_at - opened_at` in minutes.
