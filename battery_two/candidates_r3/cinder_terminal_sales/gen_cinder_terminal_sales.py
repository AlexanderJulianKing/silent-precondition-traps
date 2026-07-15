#!/usr/bin/env python3
import json
import random
import shutil
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

random.seed(31003)
np.random.seed(31003)

TASK = "cinder_terminal_sales"
ROOT = Path(__file__).resolve().parent
MASTER = ROOT / "masters" / TASK


def diagnostic_fingerprint(frame):
    seq_tail = frame["terminal_seq"].astype(int) % 1_000_000
    approval = frame["approval_code"].astype(str).str.zfill(6).astype(int)
    cents = np.rint(frame["approved_amount"].to_numpy() * 100).astype(int)
    seconds = pd.to_datetime(frame["approved_at"]).dt.second.to_numpy()
    return (
        (approval.to_numpy() == seq_tail.to_numpy())
        & ((cents % 100) == (frame["terminal_seq"].to_numpy(dtype=int) % 100))
        & (seconds == (frame["terminal_seq"].to_numpy(dtype=int) % 60))
    )


def main():
    if MASTER.exists():
        shutil.rmtree(MASTER)
    MASTER.mkdir(parents=True)

    rows = []
    event_no = 1
    true_probe = []
    networks = ["VISA", "MASTERCARD", "AMEX", "DISCOVER"]

    for store_num in range(1, 11):
        for terminal_num in range(1, 7):
            terminal = f"T{store_num:02d}-{terminal_num:02d}"
            seq = store_num * 1_000_000 + terminal_num * 20_000 + 117
            for day in range(1, 31):
                base = datetime(2026, 11, day, 7, 0, 0)
                count = 9 + ((store_num + terminal_num + day) % 3)
                minute_slots = sorted(np.random.choice(np.arange(15, 750), size=count, replace=False))
                for minute in minute_slots:
                    seq += 1
                    is_probe = (seq + store_num + 3 * terminal_num) % 19 == 0
                    if is_probe:
                        dollar_part = 18 + ((seq // 100 + store_num) % 39)
                        cents_value = dollar_part * 100 + seq % 100
                        approval = f"{seq % 1_000_000:06d}"
                        second = seq % 60
                    else:
                        cents_value = int(np.clip(np.random.gamma(2.7, 1650), 450, 18500))
                        # Avoid accidental completion of all three diagnostic relations.
                        approval_num = int(np.random.randint(0, 1_000_000))
                        if approval_num == seq % 1_000_000:
                            approval_num = (approval_num + 1) % 1_000_000
                        approval = f"{approval_num:06d}"
                        second = int(np.random.randint(0, 60))

                    approved_at = base + timedelta(minutes=int(minute), seconds=second)
                    rows.append(
                        {
                            "event_id": f"CT-{event_no:08d}",
                            "approved_at": approved_at.strftime("%Y-%m-%d %H:%M:%S"),
                            "store_id": f"CS-{store_num:02d}",
                            "terminal_id": terminal,
                            "terminal_seq": seq,
                            "customer_token": f"C{int(np.random.randint(100000, 999999)):06d}",
                            "item_count": int(np.random.randint(1, 6)),
                            "card_network": str(np.random.choice(networks, p=[0.48, 0.34, 0.11, 0.07])),
                            "approval_code": approval,
                            "approved_amount": cents_value / 100.0,
                            "response": "APPROVED",
                            "_probe": is_probe,
                            "_cents": cents_value,
                        }
                    )
                    true_probe.append(is_probe)
                    event_no += 1

    full = pd.DataFrame(rows).sort_values(["approved_at", "store_id", "terminal_id"]).reset_index(drop=True)
    export = full.drop(columns=["_probe", "_cents"])
    export.to_csv(MASTER / "november_card_approvals.csv", index=False, lineterminator="\n", float_format="%.2f")

    (MASTER / "README.md").write_text(
        "# Cinder Corner Market — November card approvals\n\n"
        "`november_card_approvals.csv` is the terminal-gateway closeout of approved card "
        "events at Cinder Corner Market's ten stores. Terminal sequence, approval code, "
        "and customer token are retained for processor reconciliation.\n\n"
        "Declines, reversals, training transactions, cash tenders, and open checks are not "
        "included in this file.\n",
        encoding="utf-8",
    )

    fingerprint = diagnostic_fingerprint(export)
    assert np.array_equal(fingerprint, full["_probe"].to_numpy(bool))
    naive_cents = int(full["_cents"].sum())
    careful_cents = int(full.loc[~fingerprint, "_cents"].sum())
    naive = round(naive_cents / 100, 2)
    careful = round(careful_cents / 100, 2)

    assert len(export) >= 17500
    assert export["event_id"].is_unique
    assert naive > careful * 1.035

    key = {
        "task": TASK,
        "mechanism": "Firmware heartbeat approvals are mixed with customer approvals and are identifiable only by a three-field sequence echo.",
        "planted_answer": naive,
        "correct_answer": careful,
        "tolerance": 0.005,
    }
    (ROOT / "answer_key.json").write_text(json.dumps(key, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(key, sort_keys=True))


if __name__ == "__main__":
    main()
