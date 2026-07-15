# Design: Garnet tip rate

## Mechanism

The POS writes a mandatory 20% large-party service charge into the same `tip_amount` field used for customer-selected gratuity, with no service-charge flag. Every party of eight or more has a tip equal to 20% of pretax sales to the cent. Summing the field across all checks treats mandatory charges as optional tips. Correct analysis infers the latent eligibility rule and limits both numerator and denominator to smaller parties.

## Trap-frame fit

1. **Unnamed:** There is no status, null, separate tender type, or documented policy to filter. The defense is recognizing a near-deterministic behavioral rule conditional on party size.
2. **Non-failing:** All checks, amounts, and tip values are valid and positive. The straightforward ratio is clean.
3. **Not action-forcing:** Date-sorted heads contain a mix dominated by ordinary small parties. Global tip ranges and summaries look normal; exact 15%, 18%, and 20% voluntary tips also occur on small checks.
4. **Plausible output:** Both rates are realistic restaurant gratuity percentages, with the planted result only a few points higher.
5. **Survives discovery:** Large groups often voluntarily choose round 20% tips, so the conditional spike has a benign social explanation unless its near-perfect determinism is tested.

## Answers

- Planted answer: total POS `tip_amount` divided by all pretax food-and-beverage sales.
- Correct answer: the same ratio restricted to parties below eight, where tipping was optional.
