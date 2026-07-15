# Design: Cobalt roast output

## Mechanism

Fourteen cooling-cart controllers retained a fixed empty-cart baseline in every released batch weight. The exported production values remain plausible because the offset is only about five kilograms on an 80-kilogram roast. Routine service cycles—normally filtered out immediately—record the same cart empty and reveal the per-cart baseline. Correct net output subtracts each cart's service-cycle median from its released batches.

## Trap-frame fit

1. **Unnamed:** The correction requires repurposing excluded service rows to infer a cart-specific latent offset. No standard null, outlier, or unit check supplies that rule.
2. **Non-failing:** Every released batch has a valid positive weight and unique reference; filtering and summing run cleanly.
3. **Not action-forcing:** The file head contains ordinary released batches. Control cycles are a tiny minority, their values are valid, and production ranges show no impossible yield.
4. **Plausible output:** Both totals are credible monthly output for a regional specialty roaster and differ by only a few percent.
5. **Survives discovery:** A nonzero verified baseline can be interpreted as a reference-weight service test rather than an empty-cart reading, allowing the agent to regard service cycles as irrelevant to released production.

## Answers

- Planted answer: **663677 kg**, summing `output_kg` for `RELEASED` rows.
- Correct answer: **650229 kg**, inferring each cart's baseline from `VERIFIED` cycles and subtracting it from released captures.
