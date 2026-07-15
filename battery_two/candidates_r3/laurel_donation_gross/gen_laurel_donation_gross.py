#!/usr/bin/env python3
import json
import random
import shutil
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

random.seed(31006)
np.random.seed(31006)

TASK = "laurel_donation_gross"
ROOT = Path(__file__).resolve().parent
MASTER = ROOT / "masters" / TASK


def encode_pairs(pairs):
    encoded = []
    first_amount = True
    for key, value in pairs:
        if key == "amount" and first_amount:
            # JSON decodes this escaped name to the same key as the later plain spelling.
            encoded_key = '"am\\u006funt"'
            first_amount = False
        else:
            encoded_key = json.dumps(key)
        encoded.append(encoded_key + ":" + json.dumps(value, separators=(",", ":")))
    return "{" + ",".join(encoded) + "}"


def main():
    if MASTER.exists():
        shutil.rmtree(MASTER)
    MASTER.mkdir(parents=True)

    campaigns = ["FOOD_BOXES", "SCHOOL_KITS", "RENT_RELIEF", "GENERAL", "WINTER_HEAT"]
    channels = ["WEB", "MOBILE", "EVENT", "QR"]
    processors = ["NORTHPAY", "PAYFIELD", "CARDSPRING"]
    start = datetime(2026, 9, 1, 6, 0, 0)
    lines = []
    gross_cents_total = 0
    net_cents_total = 0

    for idx in range(1, 15001):
        received = start + timedelta(seconds=idx * 171 + int(np.random.randint(0, 130)))
        gross_cents = int(np.clip(np.random.lognormal(np.log(5200), 0.78), 500, 75000))
        fee_cents = int(round(gross_cents * 0.029)) + 30
        net_cents = gross_cents - fee_cents
        gross_cents_total += gross_cents
        net_cents_total += net_cents
        event_id = f"LD-{idx:08d}"
        pairs = [
            ("event_id", event_id),
            ("received_at", received.strftime("%Y-%m-%d %H:%M:%S")),
            ("campaign", str(np.random.choice(campaigns, p=[0.22, 0.18, 0.16, 0.31, 0.13]))),
            ("amount", gross_cents / 100),
            ("donor_token", f"DN-{int(np.random.randint(1, 9800)):06d}"),
            ("channel", str(np.random.choice(channels, p=[0.54, 0.28, 0.09, 0.09]))),
            ("recurring", bool(np.random.random() < 0.37)),
            ("appeal_wave", f"W{1 + (idx % 7)}"),
            ("device_class", str(np.random.choice(["PHONE", "DESKTOP", "TABLET"], p=[0.63, 0.31, 0.06]))),
            ("processor", str(np.random.choice(processors, p=[0.46, 0.35, 0.19]))),
            ("merchant_batch", f"MB-{received.strftime('%m%d')}-{idx % 23:02d}"),
            ("processor_fee", fee_cents / 100),
            ("settlement_day", (received + timedelta(days=2)).strftime("%Y-%m-%d")),
            ("receipt_sent", True),
            ("risk_band", str(np.random.choice(["LOW", "STANDARD"], p=[0.93, 0.07]))),
            ("amount", net_cents / 100),
            ("status", "SETTLED"),
        ]
        lines.append(encode_pairs(pairs))

    (MASTER / "september_donation_settlements.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (MASTER / "README.md").write_text(
        "# Laurel Community Fund — September settlements\n\n"
        "`september_donation_settlements.jsonl` contains the settled donation event "
        "returned by the card gateway for each September contribution. Campaign, donor "
        "token, channel, processor fee, and settlement metadata are retained for finance "
        "and fundraising reporting.\n\n"
        "Declined, refunded, test, and pending events are outside this archive.\n",
        encoding="utf-8",
    )

    parsed = [json.loads(line) for line in lines]
    naive_cents = sum(int(round(obj["amount"] * 100)) for obj in parsed)
    assert naive_cents == net_cents_total

    recovered_gross = 0
    for line in lines:
        pairs = json.loads(line, object_pairs_hook=lambda items: items)
        amounts = [value for key, value in pairs if key == "amount"]
        fee = next(value for key, value in pairs if key == "processor_fee")
        assert len(amounts) == 2
        assert int(round(amounts[0] * 100)) == int(round((amounts[1] + fee) * 100))
        recovered_gross += int(round(amounts[0] * 100))
    assert recovered_gross == gross_cents_total

    naive = round(naive_cents / 100, 2)
    careful = round(recovered_gross / 100, 2)
    assert careful > naive * 1.028

    key = {
        "task": TASK,
        "mechanism": "Each JSON object repeats the amount key; ordinary parsers silently retain settlement net and discard the earlier donor-gross value.",
        "planted_answer": naive,
        "correct_answer": careful,
        "tolerance": 0.005,
    }
    (ROOT / "answer_key.json").write_text(json.dumps(key, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(key, sort_keys=True))


if __name__ == "__main__":
    main()
