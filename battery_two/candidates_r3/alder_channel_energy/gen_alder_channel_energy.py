#!/usr/bin/env python3
import json
import random
import shutil
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

random.seed(31001)
np.random.seed(31001)

TASK = "alder_channel_energy"
ROOT = Path(__file__).resolve().parent
MASTER = ROOT / "masters" / TASK


def infer_redundant_channels(site_frame):
    """Find channels whose daily series is almost an additive copy of 2-3 others."""
    wide = site_frame.pivot(index="close_date", columns="channel_id", values="kwh")
    channels = list(wide.columns)
    redundant = set()
    for target in channels:
        y = wide[target].to_numpy(float)
        best_error = float("inf")
        best_corr = -1.0
        others = [c for c in channels if c != target]
        for size in (2, 3):
            for parts in combinations(others, size):
                x = wide[list(parts)].sum(axis=1).to_numpy(float)
                error = float(np.median(np.abs(y - x) / np.maximum(y, 1.0)))
                corr = float(np.corrcoef(y, x)[0, 1])
                if (error, -corr) < (best_error, -best_corr):
                    best_error, best_corr = error, corr
        if best_error < 0.004 and best_corr > 0.999:
            redundant.add(target)
    return redundant


def main():
    if MASTER.exists():
        shutil.rmtree(MASTER)
    MASTER.mkdir(parents=True)

    dates = pd.date_range("2026-09-01", "2026-09-30", freq="D")
    rows = []
    expected_redundant = {}
    reading_no = 1

    for site_idx in range(1, 13):
        site = f"AW-{site_idx:02d}"
        codes = [f"CH-{x:03d}" for x in np.random.choice(np.arange(101, 999), 12, replace=False)]
        leaf_codes = codes[:10]
        feeder_codes = codes[10:]
        expected_redundant[site] = set(feeder_codes)

        bases = np.concatenate(
            [np.random.uniform(82.0, 118.0, size=4), np.random.uniform(185.0, 315.0, size=6)]
        )
        phases = np.random.uniform(0, 2 * np.pi, size=10)
        leaf_matrix = []
        for day_idx, _ in enumerate(dates):
            shop_factor = 0.88 + 0.14 * np.sin(day_idx / 4.3 + site_idx / 3.0) + np.random.normal(0, 0.035)
            values = []
            for leaf_idx in range(10):
                independent = 1.0 + 0.13 * np.sin(day_idx / (2.1 + leaf_idx * 0.17) + phases[leaf_idx])
                independent += np.random.normal(0, 0.045)
                values.append(max(45.0, bases[leaf_idx] * shop_factor * independent))
            leaf_matrix.append(values)
        leaf_matrix = np.asarray(leaf_matrix)

        # These upstream channel readings cover already-submetered production cells.
        subsets = [(0, 1), (2, 3)]
        feeder_matrix = []
        for parts in subsets:
            base_sum = leaf_matrix[:, list(parts)].sum(axis=1)
            meter_noise = np.random.normal(0, 0.0011, size=len(dates))
            feeder_matrix.append(base_sum * (1.0 + meter_noise))
        all_values = np.column_stack([leaf_matrix, np.column_stack(feeder_matrix)])

        for day_idx, date in enumerate(dates):
            for channel_idx, channel in enumerate(codes):
                rows.append(
                    {
                        "reading_id": f"AE-{reading_no:07d}",
                        "site_id": site,
                        "close_date": date.strftime("%Y-%m-%d"),
                        "channel_id": channel,
                        "kwh": round(float(all_values[day_idx, channel_idx]), 2),
                        "health": "OK",
                    }
                )
                reading_no += 1

    frame = pd.DataFrame(rows)
    frame = frame.sample(frac=1, random_state=31001).reset_index(drop=True)
    frame.to_csv(MASTER / "september_channel_closes.csv", index=False, lineterminator="\n")

    (MASTER / "README.md").write_text(
        "# Alder Works — September energy archive\n\n"
        "`september_channel_closes.csv` contains the stabilized daily kWh close returned "
        "by every active production-energy channel at Alder Works' 12 workshops. Channel "
        "identifiers follow the electrician's commissioning labels and are retained for "
        "maintenance lookup.\n\n"
        "Office, exterior-lighting, and HVAC loads are outside this export. Every channel "
        "reported `OK` health throughout September.\n",
        encoding="utf-8",
    )

    naive = round(float(frame["kwh"].sum()), 1)
    inferred = {}
    for site, group in frame.groupby("site_id"):
        inferred[site] = infer_redundant_channels(group)
        assert inferred[site] == expected_redundant[site]
    keep = [row.channel_id not in inferred[row.site_id] for row in frame.itertuples()]
    careful = round(float(frame.loc[keep, "kwh"].sum()), 1)

    assert naive == round(float(frame["kwh"].sum()), 1)
    assert careful == round(float(frame.loc[keep, "kwh"].sum()), 1)
    assert naive > careful * 1.12

    key = {
        "task": TASK,
        "mechanism": "Opaque upstream energy channels are additive near-copies of already-counted downstream production channels.",
        "planted_answer": naive,
        "correct_answer": careful,
        "tolerance": 0.05,
    }
    (ROOT / "answer_key.json").write_text(json.dumps(key, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(key, sort_keys=True))


if __name__ == "__main__":
    main()
