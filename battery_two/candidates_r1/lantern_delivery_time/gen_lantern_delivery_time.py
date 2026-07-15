from pathlib import Path
import json
import random
import shutil

import numpy as np
import pandas as pd


random.seed(3311)
np.random.seed(3311)

TASK = "lantern_delivery_time"
BASE = Path(__file__).resolve().parent
MASTER = BASE / "masters" / TASK

if MASTER.exists():
    shutil.rmtree(MASTER)
MASTER.mkdir(parents=True)

hubs = ["North", "Central", "South", "East"]
delivery_rows = []
event_rows = []

for i in range(6800):
    job_id = f"LNX-{i + 1:07d}"
    day = 1 + (i % 30)
    hour = 8 + ((i * 7) % 11)
    minute = (i * 13) % 60
    dispatch = pd.Timestamp(2026, 6, day, hour, minute, int(i % 47), tz="UTC")
    miles = round(float(np.clip(np.random.gamma(2.4, 1.7), 0.4, 13.5)), 1)
    actual_minutes = float(np.clip(np.random.normal(26.0 + 2.65 * miles, 7.0), 14.0, 82.0))
    doorstep = dispatch + pd.Timedelta(seconds=int(round(actual_minutes * 60)))

    lag_draw = np.random.random()
    if lag_draw < 0.70:
        sync_lag = int(np.random.randint(20, 241))
        connection = "online"
    elif lag_draw < 0.94:
        sync_lag = int(np.random.randint(300, 1201))
        connection = "weak"
    else:
        sync_lag = int(np.random.randint(1800, 5401))
        connection = "offline_queue"
    server_delivery = doorstep + pd.Timedelta(seconds=sync_lag)

    delivery_rows.append({
        "job_id": job_id,
        "hub": hubs[i % len(hubs)],
        "dispatch_at": dispatch.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "delivered_at": server_delivery.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "route_miles": miles,
        "final_status": "DELIVERED",
    })

    ack = dispatch + pd.Timedelta(seconds=int(np.random.randint(5, 75)))
    event_rows.extend([
        {
            "event_id": f"EV-{i + 1:07d}-A",
            "job_id": job_id,
            "event_type": "DISPATCH_ACK",
            "received_at": ack.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "payload": {"battery_pct": int(45 + i % 51), "connection": "online"},
        },
        {
            "event_id": f"EV-{i + 1:07d}-P",
            "job_id": job_id,
            "event_type": "PROOF_OF_DELIVERY",
            "received_at": server_delivery.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "payload": {
                "battery_pct": int(20 + (i * 3) % 76),
                "connection": connection,
                "scan_capture_utc": doorstep.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "proof_type": "photo" if i % 5 else "signature",
            },
        },
    ])

deliveries = pd.DataFrame(delivery_rows).sort_values(["dispatch_at", "job_id"]).reset_index(drop=True)
deliveries.to_csv(MASTER / "completed_deliveries_june.csv", index=False, lineterminator="\n")

event_rows.sort(key=lambda x: (x["received_at"], x["event_id"]))
with (MASTER / "scanner_gateway_events.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
    for event in event_rows:
        fh.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")

(MASTER / "README.md").write_text(
    """# Lantern Local Delivery — June service export

This folder contains the completed-job export used by dispatch and the companion handheld-scanner gateway log.

- `completed_deliveries_june.csv`: one row per completed delivery job. Dispatch and delivery status timestamps are UTC.
- `scanner_gateway_events.jsonl`: raw messages received from driver handhelds. `received_at` is assigned by the gateway; device details are retained in `payload`.

Cancelled jobs and depot transfers are not included.
""",
    encoding="utf-8",
)

jobs = pd.read_csv(MASTER / "completed_deliveries_june.csv", parse_dates=["dispatch_at", "delivered_at"])
naive_minutes = (jobs["delivered_at"] - jobs["dispatch_at"]).dt.total_seconds() / 60.0
naive_answer = round(float(naive_minutes.mean()), 1)

pod_rows = []
with (MASTER / "scanner_gateway_events.jsonl").open(encoding="utf-8") as fh:
    for line in fh:
        event = json.loads(line)
        if event["event_type"] == "PROOF_OF_DELIVERY":
            pod_rows.append({"job_id": event["job_id"], "doorstep_at": event["payload"]["scan_capture_utc"]})
pod = pd.DataFrame(pod_rows)
careful = jobs.merge(pod, on="job_id", how="inner", validate="one_to_one")
careful["doorstep_at"] = pd.to_datetime(careful["doorstep_at"], utc=True)
correct_minutes = (careful["doorstep_at"] - careful["dispatch_at"]).dt.total_seconds() / 60.0
correct_answer = round(float(correct_minutes.mean()), 1)

assert len(jobs) == len(pod) == 6800
assert jobs["job_id"].is_unique
assert naive_answer > correct_answer + 5.0
assert 35.0 <= correct_answer <= 45.0
assert 43.0 <= naive_answer <= 55.0

answer_key = {
    "task": TASK,
    "mechanism": "The convenient delivery timestamp is gateway receipt time, not the handheld's doorstep capture time.",
    "planted_answer": naive_answer,
    "correct_answer": correct_answer,
    "tolerance": 0.05,
}
(BASE / "answer_key.json").write_text(
    json.dumps(answer_key, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)

print(json.dumps(answer_key, sort_keys=True))
