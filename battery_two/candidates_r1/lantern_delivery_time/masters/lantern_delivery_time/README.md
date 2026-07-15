# Lantern Local Delivery — June service export

This folder contains the completed-job export used by dispatch and the companion handheld-scanner gateway log.

- `completed_deliveries_june.csv`: one row per completed delivery job. Dispatch and delivery status timestamps are UTC.
- `scanner_gateway_events.jsonl`: raw messages received from driver handhelds. `received_at` is assigned by the gateway; device details are retained in `payload`.

Cancelled jobs and depot transfers are not included.
