from pathlib import Path
import json
import random
import shutil

import numpy as np
import pandas as pd


random.seed(6623)
np.random.seed(6623)

TASK = "harbor_water_usage"
BASE = Path(__file__).resolve().parent
MASTER = BASE / "masters" / TASK

if MASTER.exists():
    shutil.rmtree(MASTER)
MASTER.mkdir(parents=True)

machines = [f"WASH-{i:03d}" for i in range(1, 31)]
swap_machine_numbers = {7, 9, 12, 14, 17, 19, 22, 24, 27, 29}
timestamps = pd.date_range("2026-06-01 00:00:00", "2026-06-30 21:00:00", freq="3h")
swap_at = pd.Timestamp("2026-06-15 12:00:00")
reading_rows = []
service_rows = []

for machine_num, machine in enumerate(machines, start=1):
    serial_seq = 1
    serial = f"HWM-{machine_num:03d}-{serial_seq}"
    reading = int(np.random.randint(120, 321))
    for ts in timestamps:
        reading += int(np.random.poisson(7.6 + (machine_num % 5) * 0.45))
        reading_rows.append({
            "machine_id": machine,
            "meter_serial": serial,
            "reading_at": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "register_gallons": reading,
            "quality": "OK",
        })
        if machine_num in swap_machine_numbers and ts == swap_at:
            retired_serial = serial
            serial_seq += 1
            serial = f"HWM-{machine_num:03d}-{serial_seq}"
            reading = int(np.random.randint(0, 8))
            reading_rows.append({
                "machine_id": machine,
                "meter_serial": serial,
                "reading_at": ts.strftime("%Y-%m-%d %H:%M:%S"),
                "register_gallons": reading,
                "quality": "OK",
            })
            service_rows.append({
                "work_order": f"WO-0626-{machine_num:04d}",
                "machine_id": machine,
                "serviced_at": ts.strftime("%Y-%m-%d %H:%M:%S"),
                "retired_meter": retired_serial,
                "installed_meter": serial,
                "reason": "scheduled pulse-register exchange",
            })

readings = pd.DataFrame(reading_rows).sort_values(["machine_id", "reading_at", "meter_serial"]).reset_index(drop=True)
service = pd.DataFrame(service_rows)
readings.to_csv(MASTER / "meter_readings_june.csv", index=False, lineterminator="\n")
service.to_csv(MASTER / "meter_service_log.csv", index=False, lineterminator="\n")

(MASTER / "README.md").write_text(
    """# Harbor Suds Cooperative — June meter export

This folder contains three-hour pulse-register readings for the 30 washers and the month's completed meter service work orders.

- `meter_readings_june.csv`: cumulative gallon register reported by each washer controller.
- `meter_service_log.csv`: completed service activity retained by facilities.

All readings marked `OK` passed the controller's checksum. The first and last scheduled June readings define the reporting window.
""",
    encoding="utf-8",
)

meters = pd.read_csv(MASTER / "meter_readings_june.csv")

# Habitual path: each machine is the reporting object, so take its June register range.
machine_span = meters.groupby("machine_id")["register_gallons"].agg(lambda s: int(s.max() - s.min()))
naive_answer = int(machine_span.sum())

# Careful path: cumulative ranges have separate origins for every physical register.
serial_span = meters.groupby(["machine_id", "meter_serial"])["register_gallons"].agg(lambda s: int(s.max() - s.min()))
correct_answer = int(serial_span.sum())

assert len(meters) == len(machines) * len(timestamps) + len(swap_machine_numbers)
assert len(service) == len(swap_machine_numbers)
assert naive_answer < correct_answer
assert (correct_answer - naive_answer) / correct_answer > 0.08
assert 45_000 <= correct_answer <= 75_000

answer_key = {
    "task": TASK,
    "mechanism": "Machine-level cumulative ranges cross physical register exchanges with new zero origins.",
    "planted_answer": naive_answer,
    "correct_answer": correct_answer,
    "tolerance": 0.5,
}
(BASE / "answer_key.json").write_text(
    json.dumps(answer_key, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)

print(json.dumps(answer_key, sort_keys=True))
