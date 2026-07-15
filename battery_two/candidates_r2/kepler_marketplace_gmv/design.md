# Design: Kepler marketplace GMV

## Mechanism

The marketplace order service stores `order_amount` in the merchant's USD ledger but retains the shopper's checkout `currency` beside it. The presence of a complete treasury-rate file makes conversion feel mandatory. Converting the already-USD amount a second time yields the planted GMV. Correct scope is inferable because every `(SKU, quantity, promo)` combination has the exact same numeric price grid in every currency; a genuine local-currency amount would vary by exchange rate.

## Trap-frame fit

1. **Unnamed:** This is a local metadata-scope mismatch, not a malformed currency code or missing FX rate. The defense requires testing price invariance at a controlled product/promotion grain.
2. **Non-failing:** The currency join is complete, one-to-many as expected, and all conversion arithmetic is valid.
3. **Not action-forcing:** Amounts and rates have normal ranges; all four markets contain thousands of paid orders. Heads, nulls, duplicates, and per-file date checks are clean.
4. **Plausible output:** Both totals are credible marketplace GMV and differ by only several percent because the currency mix partially offsets.
5. **Survives discovery:** Global sellers often use localized price parity, so identical numeric price points across markets have a benign merchandising explanation that permits continued conversion.

## Answers

- Planted answer: multiply each paid `order_amount` by its daily `usd_per_currency_unit` rate.
- Correct answer: sum paid `order_amount` directly because it is already merchant-ledger USD.
