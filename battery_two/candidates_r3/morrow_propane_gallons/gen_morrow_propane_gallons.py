#!/usr/bin/env python3
import json
import random
import shutil
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

random.seed(31007)
np.random.seed(31007)

TASK = "morrow_propane_gallons"
ROOT = Path(__file__).resolve().parent
MASTER = ROOT / "masters" / TASK
REFERENCE_DENSITY = 4.24
EXPANSION = 0.00155


def main():
    if MASTER.exists():
        shutil.rmtree(MASTER)
    MASTER.mkdir(parents=True)

    rows = []
    for idx in range(1, 12001):
        day = 1 + ((idx * 17) % 31)
        minute = int(np.random.randint(5 * 60, 21 * 60))
        delivered_at = datetime(2026, 7, day) + timedelta(minutes=minute, seconds=int(np.random.randint(0, 60)))
        if idx % 47 == 0:
            temperature = 60.0
        else:
            daily_heat = 73.0 + 13.0 * np.sin((minute - 7 * 60) / (14 * 60) * np.pi)
            temperature = round(float(np.clip(np.random.normal(daily_heat, 7.5), 48.0, 103.0)), 1)
        standard_gallons = float(np.clip(np.random.gamma(3.4, 78.0) + 45.0, 55.0, 820.0))
        scale_mass = round(standard_gallons * REFERENCE_DENSITY, 2)
        observed_density = REFERENCE_DENSITY * (1.0 - EXPANSION * (temperature - 60.0))
        meter_gallons = round(scale_mass / observed_density, 2)
        rows.append(
            {
                "delivery_id": f"MP-{idx:08d}",
                "delivered_at": delivered_at.strftime("%Y-%m-%d %H:%M:%S"),
                "truck_id": f"PT-{1 + idx % 18:02d}",
                "route_id": f"R{day:02d}-{1 + idx % 42:03d}",
                "customer_zone": f"Z{1 + idx % 9}",
                "meter_gallons": meter_gallons,
                "scale_mass_lb": scale_mass,
                "product_temp_f": temperature,
                "close_status": "DELIVERED",
            }
        )

    frame = pd.DataFrame(rows).sort_values(["delivered_at", "delivery_id"]).reset_index(drop=True)
    frame.to_csv(MASTER / "july_delivery_closes.csv", index=False, lineterminator="\n", float_format="%.2f")

    (MASTER / "README.md").write_text(
        "# Morrow Propane — July delivery closes\n\n"
        "`july_delivery_closes.csv` contains the completed delivery close returned by each "
        "truck meter in July. The onboard scale mass and product temperature at close are "
        "retained for loading reconciliation and fleet maintenance.\n\n"
        "Cancelled stops, hose tests, and depot transfers are excluded; every row has a "
        "final `DELIVERED` close status.\n",
        encoding="utf-8",
    )

    naive = round(float(frame["meter_gallons"].sum()), 1)
    sixty = frame[frame["product_temp_f"] == 60.0]
    inferred_density = round(float((sixty["scale_mass_lb"] / sixty["meter_gallons"]).median()), 2)
    assert inferred_density == REFERENCE_DENSITY
    careful = round(float((frame["scale_mass_lb"] / inferred_density).sum()), 1)

    assert frame["delivery_id"].is_unique
    assert len(sixty) > 200
    assert naive > careful * 1.025

    key = {
        "task": TASK,
        "mechanism": "Truck meters report temperature-expanded liquid volume, while delivered gallons are settled at the latent 60°F reference density recoverable from scale mass.",
        "planted_answer": naive,
        "correct_answer": careful,
        "tolerance": 0.05,
    }
    (ROOT / "answer_key.json").write_text(json.dumps(key, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(key, sort_keys=True))


if __name__ == "__main__":
    main()
