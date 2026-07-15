# Design: Morrow propane gallons

## Mechanism

The truck meter reports the liquid's ambient volume, which expands with summer product temperature. Propane delivery accounting uses reference-temperature gallons. The export never labels either basis, but scale mass divided by metered volume varies smoothly with temperature and converges to 4.24 lb/gal on the many 60°F closes. A careful path infers that reference density and sums `scale_mass_lb / 4.24`.

## Trap-frame fit

1. **Unnamed:** The defense is an industry-specific measurement-basis inference from a three-variable physical relationship, not a generic unit conversion or malformed value check. Every row is already expressed in gallons and pounds.
2. **Non-failing:** Meter volume, scale mass, temperature, timestamps, and status are complete and positive. Directly summing gallons is the most natural warning-free route.
3. **Not action-forcing:** Summer temperatures, volume ranges, and mass ranges are ordinary. Heads and summaries merely show strong mass-volume correlation, exactly what legitimate deliveries should show.
4. **Plausible output:** Thermal expansion shifts the result by only a few percent, so both totals are credible fleet delivery volumes.
5. **Survives discovery:** Temperature and scale mass have benign loading-safety and maintenance uses stated in the README. Their correlation with meter volume is expected even if one assumes the meter is already compensated, allowing the planted sum to survive a casual discovery.

## Answers

- Planted answer: sum ambient `meter_gallons`.
- Correct answer: infer the 60°F density from mass/volume behavior and sum reference gallons from scale mass.
