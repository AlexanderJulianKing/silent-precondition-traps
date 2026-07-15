> Release note: this copy is scrubbed for publication. Internal model-review quotations and verdicts are removed; all data, version history, incidents, and adopted revisions are retained. Review transcripts are not released.

# Trapping Frontier Data-Science Agents: Consolidated Results (v1–v8.1, ablations, cross-model, effort 2×2)

*2026-07-08. Subjects: GPT-5.4-mini and Codex/GPT-5.5 (`codex exec`, workspace-write OS sandbox, effort per section), Claude Sonnet 5 and Claude Opus 4.8 (`claude -p --setting-sources project`, probe-verified clean context, tool-scoped permissions, effort per section). Final methodology: n=5 fresh runs per cell, pristine redeploys per run, ~500 scored runs total. All environments synthetic, seeded, self-verified, contamination-scanned; every subject transcript scanned for out-of-scope access (clean). Generators, prompts, transcripts, and answer keys in the session scratchpad; environments under `/private/tmp/`. Sections are ordered chronologically and preserve each phase's numbers; where later phases supersede earlier claims, the earlier section says so inline.*

## Headline

Across **eight battery generations, prompt ablations with generalization tests, controlled doc-hint pairs, a lab×effort 2×2, and n=5 rate studies over four models from two labs (~500 scored agent runs)**, exactly **one trap family reliably defeated frontier agents: instrument-precondition traps** — tasks where the agent's chosen extraction tool has a silently violated assumption confined to a region of the data no habitual sample touches. The family began 4-for-4 (2 models × 2 surface skins, byte-identical planted answers) and matured into a **10-task battery with per-model fall rates of 100% (GPT-5.4-mini), 88% (Codex 5.5), 41% (Opus 4.8), and 31% (Sonnet 5)** — every fall converging on the planted answer, with `nullmerch` (a merchant literally coded "NULL", swallowed by pandas defaults) at **30/30 unwarned across every model and effort configuration tested**.

**And the ablations resolved its nature: it is primarily an elicitation deficit — with a stubborn core.** A single generic hygiene paragraph prepended to the prompt — reconcile matched-vs-in-scope records, treat anomalies in your own intermediates as bugs, verify format assumptions across the whole dataset; never naming the trap — flipped the initial four failing cells to **exact ground truth (4/4)**, and at scale produced a **~4× fall-rate reduction that generalizes to trap classes the paragraph never mentions**. But it is not a complete fix: each model retains a warned-resistant residue (Codex: burst 3/3; Opus: nullmerch 3/3 — see the generalization section). Elicitation moves the anomaly-investigation threshold; it does not remove it. Warned Opus's transcript narrates the trap as its own discovery ("Critical gotcha found: the log has two formats… a naive parser would silently miss those requests"); warned runs itemized the precise blind spot (a by-format error table: 1,365 + 5,294 = 6,659) that unwarned runs had reported flatly ("Hours 10:00–13:00 logged zero errors" — verbatim; the phrase "quiet hours," used in earlier versions of this document as if quoted, was an editorial gloss, caught during human quote-verification and corrected here).

Everything else — documented tells, cross-artifact inference, misleading endorsements, false ticket premises, unit mixes, stale docs, version sorts, and the entire v5 battery of *named* statistical idioms (weighted means, float64 ID precision, Simpson's reversal, timezone normalization) — was caught by default, usually with verification quality exceeding the answer key (Opus diagnosed the broken randomization mechanism behind the Simpson task and standardized correctly; Codex fit a segment-adjusted logistic regression).

## Results grid

| Battery | Trap | Mechanism | Codex 5.5 | Opus 4.8 |
|---|---|---|---|---|
| v1 | Leakage (named column) | semantic tell | ✅ caught | — |
| v1 | Coding inversion (explicit NOTE) | doc tell | ✅ caught | — |
| v1 | Rotated logs | filesystem tell | ✅ caught | — |
| v2 | Leakage (opaque name + PM endorsement) | doc-inference + authority misdirection | ✅ caught | ✅ caught |
| v2 | Coding inversion (inference-only + cross-doc) | prior-confirming trap | ✅ caught | ✅ caught |
| v2 | **Log format drift (canary `up=` token)** | **instrument precondition** | ❌ **1,407 / checkout** | ❌ **1,407 / checkout** |
| v2 | False-premise ticket (innocent fx.py) | frame rejection | ✅ caught | ✅ caught (counterfactual proof) |
| v3 | Stale schema doc (order→item grain) | doc-trust inversion | ✅ caught | ✅ caught |
| v3 | Cents/dollars mix (undocumented) | distributional tell only | ✅ caught | ✅ caught (distribution-alignment proof) |
| v3 | Payment re-posts (dedup) | cross-aggregate consistency | ⚠️ **half-fell**: trap revenue $252,296.44 + true count 2,976 | ✅ caught ($231,561.30 / 2,976) |
| v3 | Version sort (2.9.3 vs 2.10.1) | `sorted()` precondition | ✅ caught | ✅ caught (+ overlap-window confound check) |
| v4 | **Logfmt canary (ERROR→level=error)** | **instrument precondition, new skin** | ❌ **1,365 / hour 16** | ❌ **1,365 / hour 16** |
| v5 | Average-of-averages (weights present) | unweighted-mean reflex | ✅ caught ($26.52) | ✅ caught (pre-refuted the $45.67 trap) |
| v5 | Float64 ID collision (1e18 ids + blanks) | pandas dtype inference | ✅ caught (read as string, 5,000) | ✅ caught (5,000) |
| v5 | Simpson's reversal (imbalanced arms) | headline-aggregate reflex | ✅ caught (logit w/ segment; ship) | ✅ caught (standardization + broken-randomization diagnosis; ship) |
| v5 | Timezone local-hour (offset column) | UTC-hour reflex | ✅ caught (49.88%) | ✅ caught (49.88%) |
| **ablation** | **v2 drift, WARNED (generic hygiene preamble)** | elicitation test | ✅ **fixed — 10,014 / search (8,446)** | ✅ **fixed — 10,014 / search (8,446)** |
| **ablation** | **v4 canary, WARNED** | elicitation test | ✅ **fixed — 6,659 / hour 11** | ✅ **fixed — 6,659 / hour 11** |

Ground truths: v2 drift — 10,014 5xx, worst `/api/search` (8,446). v4 canary — 6,659 errors, peak hour 11:00 UTC.

## V6: the generalization battery

Five new environments held the mechanism constant (silently violated instrument precondition, hidden from habitual sampling, plausible wrong output) while varying the instrument — so the family claim can't be reduced to "bad at log parsing."

| Trap (instrument varied) | Codex 5.5 | Opus 4.8 |
|---|---|---|
| `crestline_growth` — region code "NA" in pandas default `na_values` (CSV-reader defaults) | ❌ **FELL — EMEA/2,414** (truth: NA/3,412) | ✅ caught — traced NaN to raw "NA" strings |
| `pulsepay_events` — `amount`→`amount_usd` rename mid-stream (JSON schema access) | ✅ caught | ✅ caught (+ verified same-currency via distributions) |
| `relaycdn_ops` — copytruncate rotation duplicates 10 min verbatim (file disjointness) | ✅ caught (per-file range check → uniq -d) | ✅ caught (same path) |
| `cascade_commerce` — legacy backfill block breaks keep='first' (order-dependent dedup) | ✅ caught (ranked by date) | ✅ caught (noted non-chronological order IDs) |
| `vertexweb_analytics` — epoch-seconds window in ts column (timestamp serialization) | ✅ caught **via loud crash** (strict `to_datetime` raised) | ✅ caught (mechanism narrated) |

**The decisive cell is NA-region, and it produced the day's clearest psychological result.** Both models surfaced the identical anomaly — Codex literally ran `value_counts(dropna=False)` and printed `NaN 3412` as the largest group. Codex then wrote a benign story ("keeping missing values separate from named billing regions") and reported EMEA; Opus refused the story, went back to the raw file, and found pandas silently converting the string "NA" to NaN. Same evidence, divergent thresholds for anomaly *investigation* vs anomaly *narration*. This is the cross-instrument twin of Opus's own v4 zero-error-hole failure — confirming anomaly-normalization as a cross-model failure mode whose firing is threshold-y and run-dependent, not a fixed model property. (Subsequently measured at n=5: Codex 5/5 falls, Opus 0/5 — Codex's fall and Opus's catch are both stable on this instance; the threshold story is carried by nullmerch, where a *smaller* anomaly defeats Opus 5/5.)

**Why v6's fall rate (1/10) is lower than v2/v4's (4/4), and why that sharpens rather than weakens the thesis:** each caught v6 trap leaked through one of the five airtight conditions. A reliable trap must be (1) unnamed — no retrievable defensive idiom; (2) silent on *every* natural path — the epoch trap self-disclosed because strict `to_datetime` crashes loudly; (3) invisible to standing world-checks — copytruncate died to the per-file range check, the JSONL rename died to null visibility; (4) plausible in its wrong output; and (5) able to survive its own discovery — the anomaly, if surfaced, must admit a benign story. v2-drift and v4-canary satisfy all five and went 4/4. NA-region satisfies all five *if* the benign story wins — which it did for one model out of two.

## The first n=5 study (six tasks, two models): rates, not anecdotes

Six tasks × two models × five fresh runs each (60 runs, frozen protocol, pristine redeploys per run; one Opus cell excluded as a no-answer harness artifact, one Codex cell scored manually from its transcript). Fall = reported the planted trap answer.

| Task | Condition-five status | Codex 5.5 falls | Opus 4.8 falls |
|---|---|---|---|
| v2 drift (`up=` token) | airtight vs both | **4/5** | **4/4** |
| v4 canary (logfmt window) | airtight vs both | **5/5** | **4/5** |
| NA-region (pandas na_values) | airtight vs Codex; Opus standing check defeats it | **5/5** | **0/5** |
| burst (duplicated window) | airtight vs Codex; Opus standing check defeats it | **5/5** | **0/5** |
| refunds (prefix join) | leaky — anomaly visible in head() (condition 3 violated) | 0/5 | 0/5 |
| status (trailing space) | leaky — defense is a reflexive named idiom (condition 1 violated) | 0/5 | 0/5 |

**The dichotomy: 27 falls in 29 scoreable runs (93%) where all five conditions hold for that model — 0 falls in 30 runs (0%) where any condition fails.** *Circularity concession (per external review, adopted): as used here, conditions 3 and 5 were partly outcome-conditioned — "airtight vs Codex / defeated by Opus's standing check" labels tasks by model behavior, so this dichotomy is partly classification, not prediction. The partially-predictive uses were the v7/v8 designs (built to the conditions, with registered predictions, before their runs) and the negative controls failing as predicted. The clean validation — preregistered observable conditions, blinded raters, frozen out-of-sample battery — is listed in Remaining work.*

Three findings the rates add beyond the anecdotes:

1. **Within this battery, errors concentrate almost entirely on the planted answers.** Four-outcome rescoring of all 480 battery runs, both denominators stated: **277 of 279 answered-but-wrong runs (99.3%) were the planted answer** (2 other wrong answers, 1 no-answer); **277 of 480 total runs (58%) were planted-answer falls**. MAJ@5 for every high-fall cell is the trap answer. This shows the constructions work as designed and execute stably — it is *not* evidence that frontier-agent errors are generally systematic outside this selected battery.
2. **A stable cross-model playbook difference, cleanly separated:** NA-region and burst went 10/10 against Codex and 0/10 against Opus. Opus runs raw-file-vs-parse reconciliation and duplicate-ID checks as standing policy; Codex does not. (Both remain ~80–100% vulnerable to the log-parser pair, so this is a difference in *which* checks are standing, not overall superiority.)
3. **The leaky traps' 0/20 is consistent with the proposed taxonomy** (retrospective organization, not validation): the refunds trap's anomaly sat in rows 1–4 of every `head()` because the generator shuffled the file (condition 3), and the status trap's defense (`str.strip()`) is applied reflexively before any anomaly is noticed (condition 1).

## The final 10-task battery (two-model core; the four-model table below is the paper's Table 1)

Ten airtight tasks across six mechanism classes, n=5 per model per task, frozen protocol (~100 additional runs). Falls = reported the planted answer; partial-day answers naming June 30 *with* an explicit partial-snapshot caveat graded as catches (pre-stated rule; affected one Opus run).

| # | Task | Mechanism class | Codex 5.5 falls | Opus 4.8 falls |
|---|---|---|---|---|
| 1 | drift | parser/format window | 4/5 | 4/4¹ |
| 2 | canary | parser/format window | 5/5 | 4/5 |
| 3 | jsonwin | parser/format window | 5/5 | 3/5 |
| 4 | NA-region | reader-default swallow | 5/5 | 0/5 |
| 5 | nullmerch | reader-default swallow (small anomaly) | **5/5** | **5/5** |
| 6 | burst | duplication | 5/5 | 0/5 |
| 7 | restamp-terse | duplication, check-defeating | 5/5 | 0/5 |
| 8 | netgross-quiet | cross-column invariant | 5/5 | 3/5 |
| 9 | partial-day | scope/coverage | 5/5² | 1/5 |
| 10 | trailspace | silent join | 0/5 | 0/5 |
| | **Aggregate** | | **44/50 (88%)** | **20/49 (41%)** |
| | *task-clustered 95% CI* | | *[68%, 100%]* | *[18%, 66%]* |

¹ one no-answer excluded. ² three of five Codex partial-day runs printed the anomalous `as_of_ts 09:15` value in their own final output and answered without comment.

*Scope note: the mechanism-class column is a descriptive organizing scheme, not a tested factor — several classes have a single instance, so no class-level potency comparisons are made or implied. The unit of analysis throughout is the task; aggregate CIs are bootstrapped over tasks (the runs within a task are not independent). The one class-flavored observation we retain — all three join-style designs were caught, 0/30 — is offered as a hypothesis (orphaned payments admit no benign story), not a measured class effect.*

Notes that carry the paper:

- **nullmerch is the strongest universal trap measured (10/10)** — the same mechanism Opus defeated 5/5 at NA-region falls 5/5 when the anomaly shrinks from 38% of rows to 13%: anomaly-investigation is a *threshold*, and condition five's benign story wins below it.
- **The doc-hint controlled pairs are a clean dissociation.** Same traps, ± one README sentence: restamp with hint → Codex 3/5 falls; hint removed → 5/5. netgross with hint → 2/5; removed → 5/5. Opus's restamp protection survived de-hinting (0/5 both ways — self-generated check), but its netgross protection was partly hint-driven (0/5 → 3/5). One sentence of documentation is worth 40–60 points of fall rate to Codex; Codex's apparent audits are substantially *doc-derived*, Opus's are substantially *self-generated but threshold-y*.
- **The join class is defended only by some configurations** (originally over-claimed as "structurally defended"; corrected after GPT-5.4-mini fell 5/5 and the GPT-5.6 mid/low tiers also fell on trailspace): Codex 5.5, Opus, Sonnet, and Fable catch it via payment-match reconciliation — plausibly because unmatched money lacks a benign story *for models that run the check at all*. The "condition five is domain-unsatisfiable" reading was too strong; the honest statement is configuration-specific defense.
- **Negative controls behaved as predicted** (refunds 0/10, status 0/10, zeropad 0/10), with the leaky-hint variants (restamp-v1 3/10, netgross-v1 2/10) falling *partway* — the hint only protects when read-and-acted-on, which Codex does inconsistently.

## Cross-model extension (four models, two labs)

Same battery, same protocol, n=5 per cell, unwarned. GPT-5.4-mini and Sonnet 5 added; the first Sonnet batch was discarded and rerun after a stdin-redirection bug leaked battery-map lines into prompts (caught by Sonnet itself reporting anomalous input; codex runs were immune because every codex invocation closes stdin — the CLAUDE.md `< /dev/null` rule).

| Task | GPT-5.4-mini | Codex 5.5 (xhigh) | Sonnet 5 | Opus 4.8 |
|---|---|---|---|---|
| drift | 5/5 | 4/5 | 1/5 | 4/4 |
| canary | 5/5 | 5/5 | 2/5 | 4/5 |
| jsonwin | 5/5 | 5/5 | 5/5 | 3/5 |
| NA-region | 5/5 | 5/5 | 1/5 | 0/5 |
| nullmerch | **5/5** | **5/5** | **5/5** | **5/5** |
| burst | 5/5 | 5/5 | 0/5 | 0/5 |
| restamp-terse | 5/5 | 5/5 | 0/5 | 0/5 |
| netgross-quiet | 5/5 | 5/5 | 0/5 | 3/5 |
| partial-day | 5/5 | 5/5 | 1/5¹ | 1/5 |
| trailspace | **5/5** | 0/5 | 0/5 | 0/5 |
| **Aggregate** | **50/50 (100%)** | **44/50 (88%)** | **15/49 (31%)** | **20/49 (41%)** |
| *clustered 95% CI* | — | *[68%, 100%]* | *[10%, 56%]* | *[18%, 66%]* |

¹ one Sonnet run rejected the trap correctly, then named the wrong full day — an ordinary computation error, scored as a non-fall.

Findings:

1. **The lab-lineage hypothesis.** The two OpenAI configurations fall at 100% and 88%; the two Anthropic configurations at 41% and 31%; mid-tier Sonnet 5 resists ~3× better than frontier Codex 5.5 at maximum effort. Per external review (adopted), the *defensible* claim is: **these model–scaffold configurations differed sharply on this adaptively-developed battery** — with lab lineage as *one* hypothesis for why (not rankable above the alternatives on this design), standing against alternatives the design cannot exclude: scaffold/product-policy differences, adaptive task-selection bias (the battery was iterated against Codex and Opus), designer-policy alignment, and product-objective specialization. Two labs × two models is no replication at the lab level; the effort 2×2 below removes only the effort alternative. Upgrading hypothesis → finding requires 3+ labs, crossed scaffolds, and a frozen independently-designed battery (Remaining work).

   *Effort documentation and the honest caveat:* per Claude Code docs, the Anthropic subjects ran at the CLI default effort **`high`** with extended thinking enabled by default; both OpenAI subjects ran at **`xhigh`** (banner-verified, user config); temperature is not a configurable setting in Claude Code v2.1.190 — all runs are "as-shipped" sampling. Reading (a): Codex fell at 88% *at its ceiling* while Claude models fell less *below theirs* — strengthens the lab gap. Reading (b): the inverse-scaling-in-test-time-compute literature shows longer reasoning can *amplify* distractor pickup, so xhigh could have been hurting Codex — effort was a genuine either-direction confound when this section was written. **Resolved by the effort 2×2 below: effort explains none of the gap** (Codex identical at both efforts; Opus improves with effort).
2. **`nullmerch` is a universal item: 20/20 across four models, two labs, three capability tiers.** The pandas NULL-swallow plus a small-anomaly benign story defeats every configuration tested. This is the SimpleBench-grade question of the battery.
3. **`trailspace` separates the capability floor:** 5/5 at the mini tier, 0/15 above it — join-key reconciliation is the one audit that tracks tier rather than lab.
4. **Within-lab tier ordering is flat or inverted** (Sonnet 31% vs Opus 41%, heavily overlapping CIs): more capability does not by itself buy more instrument-auditing.
5. GPT-5.4-mini's 50/50 sweep doubles as a battery-validity check: at the floor, all runs converge on the planted answers — the naive path is the natural path everywhere.

## Designer-as-subject: Claude Fable 5 (full battery, n=5)

The trap designer's own model, run cold on the full battery (fresh sessions, probe-verified clean context, no memory of the design work). **14/50 falls (28%), clustered CI [6%, 52%]** — squarely inside the Anthropic band (Opus 41%, Sonnet 31%; heavily overlapping intervals), not below it.

Per-task: drift, jsonwin, NA-region, partial, restamp-terse, trailspace 0/5; canary 2/5; **burst 3/5** (worse than Opus's 0/5); **nullmerch 4/5**; **netgross-quiet 5/5 — the designer's twin falls deterministically for its own cross-column trap.**

Two lessons this cell teaches:

1. **The round-1 trial (2/10, celebrated below its own weight) was a lucky draw — a live demonstration of why every claim in this report is a rate.** The famous first-ever nullmerch catch is real but fires ~1 in 5: Fable's transcript that round showed *preemptive instrument distrust* ("pandas' default CSV parsing treats the string 'NULL' as missing data and would have silently dropped it, making RUBY (494) look like the top merchant… `keep_default_na=False`") — predicting the tool's failure mode and the exact trap answer before running the tool. The audit exists in the repertoire; like every self-generated audit in this study, its firing is threshold-y. One round made it look like a new tier; five rounds show the same stochastic machinery as its siblings.
2. **The designer-self-similarity confound largely dissolves in the data**: no designer advantage is visible — the designer's own weights fall for the designer's own traps at Anthropic-typical rates, including 5/5 on one of its own designs. This strengthens rather than weakens the mechanism claim (the blind spots are habits, not knowledge, and are not escapable by the policy that invented them), though the independent-designer battery remains the clean version for publication.

## The GPT-5.6 family: a frozen, out-of-sample evaluation (n=5, release-day)

GPT-5.6 Sol, Terra, and Luna (released 2026-07-09) were run on the identical battery under the hardened protocol: answer keys and generators archived off the working set before runs, per-round out-of-scope hunt-scans (motivated by METR's report of record evaluation-gaming by Sol). **Methodological status: for these three rows, the adaptive-selection objection does not apply — the battery was frozen before these models existed.** This is the study's first genuinely out-of-sample model evaluation.

| Task | Sol (flagship) | Terra (mid) | Luna (fast) |
|---|---|---|---|
| drift | 4/5 | 5/5 | 5/5 |
| canary | 5/5 | 5/5 | 5/5 |
| NA-region | 5/5 | 3/4¹ | 4/5 |
| burst | 5/5 | 5/5 | 5/5 |
| nullmerch | **5/5** | **5/5** | **5/5** |
| jsonwin | 5/5 | 5/5 | 5/5 |
| partial-day | 4/5 | 2/5 | 5/5 |
| restamp-terse | 4/5 | 5/5 | 5/5 |
| netgross-quiet | 5/5 | 5/5 | 5/5 |
| trailspace | 0/5 | 3/5 | 1/5 |
| **Aggregate** | **42/50 (84%)** | **43/49 (88%)** | **45/50 (90%)** |
| *clustered 95% CI* | *[64%, 98%]* | *[73%, 100%]* | *[74%, 100%]* |

¹ one no-answer excluded (run died mid-output). One Luna wave was lost to a runner timeout and rerun as a make-up round (documented).

- **Hunt-scans: 0 out-of-scope accesses in all 160 runs.** The model METR could not score because it cheated did not cheat here — there was nothing to steal (no grader, no hidden tests, keys off disk) — it was simply, confidently wrong. Evaluation-gaming and instrument-auditing are distinct faculties; the newest generation improved only the first.
- **The configuration-family band replicated on release day, out-of-sample:** OpenAI-family configurations now span five models over two generations at **84–100%** (mini 100, Luna 90, Terra 88, Codex 5.5 88, Sol 84); Anthropic-family configurations sit at **28–41%**. The bands do not overlap.
- `nullmerch` extends to **49/50 unwarned across ten configurations** (the sole escape: one Fable 5 run; plus warned-resistance for Opus). Sol carries its predecessor's trailspace defense (0/5); Terra and Luna mostly lack it — the join check is neither lab-wide nor tier-monotone. *(Correction: an earlier revision of this bullet said "45/45 across eight configurations" — a manuscript-preparation recount caught the arithmetic error.)*

## The effort 2×2 (lab × reasoning effort, full battery, n=5 per cell)

New cells: Codex@high (`-c model_reasoning_effort=high`, banner-verified) and Opus@xhigh (`claude --effort xhigh`); existing cells: Codex@xhigh, Opus@high (the CLI default).

| Aggregate falls | effort = high | effort = xhigh |
|---|---|---|
| Codex 5.5 | 44/50 (88%) | 44/50 (88%) |
| Opus 4.8 | 20/49 (41%) | 13/50 (26%) |

**The configuration gap persisted under both nominal product effort settings and widened at matched-xhigh (88% vs 26%).** (Caveat: "high"/"xhigh" are product labels, not cross-lab calibrated compute; this removes the effort *setting* as an explanation, not effort per se.) Codex's fall profile is effort-*invariant* to the task (identical 44/50, same per-task pattern): its missing checks are not purchasable with more thinking, consistent with the doc-hint result that its audits are externally cued. Opus's falls *decrease* with effort (41% → 26%; netgross-quiet 3/5→0/5, partial 1/5→0/5), refuting the overthinking-hurts alternative for this battery — extra effort deepens Opus's self-generated auditing. (Clustered CIs overlap between the two Opus cells; the direction is consistent across tasks but the magnitude is not individually significant.)

Registered-prediction scorecard: Codex@high was predicted 70–90% (landed 88% — correct; lab gap survives its strongest challenger); Opus@xhigh was predicted flat-to-slightly-worse (landed better — direction wrong, and the overthinking concern imported from the test-time-compute literature did not materialize here).

**`nullmerch` is now 30/30 unwarned across every model and effort configuration tested** — and warned-resistant for Opus on top. It is the single most robust item in the study.

## Warned-preamble generalization (n=3)

The hygiene preamble (written for the parse-coverage traps before most of this battery existed) was prepended unchanged to every task each model falls on. Result: **~4× mitigation with stable, model-specific residues — not a fix.**

- Codex warned: 98% → 22% falls. Fixed outright: drift, canary, jsonwin, NA-region, nullmerch, partial (0/3 each). Residues: **burst 3/3** (it never audits row identity, even when told to reconcile records), netgross-quiet 2/3, restamp-terse 1/3.
- Opus warned: 69% → 17% falls. Fixed everything except **nullmerch: 3/3 falls** — its round-3 answer says "among *actual* merchant codes, RUBY leads": it saw the excluded group, classified it as not-real-codes, and dropped it under an instruction that explicitly says to account for every dropped record. The benign story survives explicit warning.
- Generalization verdict: the preamble transfers well beyond its original trap class (it fixed duplication- and scope-class traps its text never mentions), but **condition five has an elicitation-resistant core**: for each model there exists a trap whose benign story defeats warned scrutiny. Elicitation moves the anomaly-investigation threshold; it does not remove it.

## The ablation, precisely

The warned prompt prepends one generic paragraph (full text in `warn_preamble.txt`): reconcile records matched vs in scope and account for every drop; treat any zero/gap/surprise in intermediate results as a suspected bug until confirmed; verify format/unit/structure assumptions across the entire dataset, not just the first rows. It names no trap, mentions no format, and would be a reasonable standing instruction for any production agent.

Result: **unwarned 0/4 → warned 4/4, all exact ground truths.** The models do not lack the skill — warned-Codex built dual-format parsers up front and reported "reconciled all 146,100 records with 0 malformed"; warned-Opus produced a per-format, per-hour error table itemizing exactly the 5,294 logfmt errors its unwarned run was blind to. The default verification *policy* simply never allocates effort to auditing the agent's own instrument; one sentence re-prices that allocation. This initial two-task result looked like a complete fix (the agentic analog of SimpleBench's engineered-prompt result, +13.5 pts partial, supporting the "inference-time elicitation deficit" account of arXiv:2412.12173). **The full-battery generalization study above supersedes that reading**: ~4× mitigation with stable model-specific residues, not saturation.

## The shape of the gap (final form)

**What frontier agents reliably do** — the standing playbook observed in every transcript: enumerate and read every artifact before computing; profile per source (dtypes, nulls, ranges, distributions); resolve doc–data conflicts toward the data while flagging the doc; challenge task premises against the code; check temporal validity, referential integrity, confounds (Opus ran an overlap-window A/B check unprompted), and even imagined failure modes (Opus tested whether message text could inflate a grep count). Traps living anywhere this playbook looks get caught.

**The supported mechanism claim, stated at descriptive (not causal) scope:** *under some scaffolds, agents omit coverage validation after some silent coverage-changing transformations and then report plausible, task-satisfying answers.* Whether plausibility causes the omission is a hypothesis for the dose-response experiments. This is narrower than "agents don't audit their instruments" — the same models demonstrably run instrument audits sometimes (per-file ranges, duplicate checks, dtype-safe reads); what's absent is reliable triggering when nothing looks wrong. Candidate drivers the design cannot separate: satisficing stopping rules, observability (the filter destroys its own contrary evidence), salience-driven scrutiny allocation, and a cost-calibrated verification tradeoff (the warned 2–3× token tax is real).

**What they reliably don't do** — two coupled blind spots, both self-facing rather than world-facing:

1. **No instrument audit.** Neither model ever reconciled "lines my filter matched" against "lines in scope." Codex's v2 output contained both numbers (29,623 in-window vs 1,407 extracted); Codex's v4 ripgrep pattern was format-anchored and structurally blind to half the file; neither noticed. The tool template ("status is field 9," "errors match ` ERROR `") is retrieved like a memorized fact and its precondition is never re-verified against the actual data — the procedure-level version of MATH-Perturb's "blindly applies memorized techniques without judging whether the modified setting is suitable."
2. **Own output isn't treated as evidence.** The deepest instance: Opus's v4 hourly table displayed a 4.5-hour zero-error hole on a service with a ~29 errors/hour baseline — while INFO traffic continued — and it reported the hole flatly ("Hours 10:00–13:00 logged zero errors") without investigation. The anomaly was *printed, read, and described*, but a benign prior absorbed it. This is SimpleBench's "impossible detail in plain sight" failure relocated into the agent's own results. Codex's v3 half-fall is the same species: its two reported numbers (deduped order count, un-deduped revenue) were mutually inconsistent and adjacent, and no self-reconciliation fired.

**Why the failures are systematic:** the trap answers are *plausible* (1,365 errors is a fine-looking number; $252k is a fine-looking June), so no anomaly triggers escalation to deeper scrutiny. Perceived task difficulty sets the verification budget — a "grep job" gets grep-grade checking (the misjudged-difficulty result from the inverse-scaling literature, agentified). When the wrong answer confirms expectations, nothing pulls the emergency brake. Hence identical planted answers across four models from two labs, at rates up to 30/30.

**The final synthesis (post doc-hint pairs, warned residues, and effort 2×2):** agent auditing has two parameters — *where checks come from* and *whether effort scales them*. Codex's audits are externally cued (one README sentence swings its fall rate 40–60 points) and effort-invariant (88% at high and at xhigh alike); Opus's are self-generated (survive de-hinting) and effort-scaled (41% → 26% from high to xhigh) but threshold-y (a small-enough anomaly with a benign story — nullmerch — defeats them at any setting tested).

## Interpretation for benchmark design ("agentic SimpleBench")

- Don't hide tells in artifacts — frontier agents read everything. Don't rely on false premises — they check. Don't rely on statistical camouflage alone — they profile.
- Do target the seam between the agent and its instruments: preconditions violated only in unsampled regions (mid-file, mid-window, format-reverted), with plausible naive outputs and a conclusion that flips under correct handling.
- The measurable signature transfers from SimpleBench: identical wrong answers across runs/models (MAJ@k-style convergence), rather than noise.
- Grade final artifacts, not traces (CoT-faithfulness caveat), but log inspection behavior as a secondary metric: the discriminating behavior is "counted what the filter excluded," not "read the docs."

## Practical defenses (worth adding to any agent's operating rules)

1. After any filter/parse, reconcile: rows in scope vs rows matched; explain the residual.
2. Any zero (or step-change) in a time-bucketed result is a red flag to investigate, not a fact to report.
3. When reporting two aggregates from the same table, verify they're mutually consistent.
4. Before reusing a format assumption (field position, token case), sample the *middle* of the data, not just head/tail.

(Alex's CLAUDE.md rule "check for rotated logs and confirm dataset scope" is this genre — these four are its siblings. Caveat from the generalization study: a preamble embodying these rules reduced falls ~4× but did **not** prevent every failure — each model kept one warned-resistant residue. Standing rules are strong mitigation, not immunity.)

## Where the boundary actually sits (synthesis after v5; qualified by later phases)

The v5 sweep sharpened the thesis. Traps whose correct handling is a **named idiom** — weight your means, read IDs as strings, stratify before concluding, convert to local time — are saturated at this tier: the idiom's name appears in training data a million times, and encountering the setup retrieves the defense. The traps that work have **no name**: there is no famous rule called "your grep can go blind mid-file." The failure boundary is not intelligence, coverage, or care — it is whether the required check exists as a *retrievable procedure*. When we handed the models the procedure (one generic paragraph), they mostly executed it and even narrated the traps back to us — though the later generalization study shows execution is itself threshold-y (the benign story can defeat the handed procedure: warned-Opus on nullmerch, warned-Codex on burst). The gap is a missing-or-underweighted entry in the standing playbook, not a missing capability.

Benchmark implication: an "agentic SimpleBench" that wants durable headroom must mine failure modes that lack names — because anything nameable is already trained in, and anything you publish gets named.

## Caveats (current)

- n=5 per cell for all battery/cross-model/2×2 results (warned generalization n=3; the pre-battery phases v1–v6 were n=1 screening and are labeled as such). Aggregate CIs are task-clustered.
- Scaffold ≠ model: cross-lab comparisons are of agent products as shipped (different CLIs, system prompts, sandboxing — codex OS sandbox vs claude tool-scoped permissions). Not weight-attributable.
- Effort documented and 2×2-tested (explains none of the lab gap); temperature not configurable in either CLI — all runs "as-shipped" sampling.
- Designer (Claude Fable 5) is an Anthropic sibling and the lab gap matches designer lineage; mitigations: conditions pre-registered before cross-model runs, v8.1 traps adversarially targeted Opus's known checks, designer predictions overridden in both directions. Clean fix = independent task regeneration from the condition spec.
- Single instance per trap shape; no paraphrase/perturbation sweep yet. Two models per lab. No human baseline yet (the "observant analyst catches it" claim rests on the designer plus the traps' construction).
- Protocol incidents (all documented above): one stdin-leak batch quarantined and rerun; one runner live-edit incident; occasional no-answer cells excluded; partial-day flag rule pre-stated.

## Revision provenance

This report was revised across multiple internal review rounds (model-based reviewers; review transcripts are not released). Revisions adopted from those rounds are incorporated throughout, including: the four-outcome rescoring with both denominators; the circularity concession on conditions 3 and 5; the lab-lineage downgrade from finding to one unranked hypothesis among several; the join-class correction; and the descriptive mechanism wording. The reviews are not independent external validation: reviewer and subject configurations share model policy, so the reviews and the subject results are not used to validate each other, and the pre-review subject run is treated as pilot data.

## Remaining work

1. **GPT-5.6 family n=5** (in progress): Sol/Terra/Luna under keys-off-disk protocol with per-round hunt-scans.
2. **Placebo-preamble control**: length-matched generic-diligence prompt + equal-compute + second-pass-review arms vs the targeted preamble, on traps frozen before the prompts — plus a further arm: **a model-authored vulnerability self-description as a preamble on fresh GPT-5.6 runs** (does reading an accurate self-model close the knowledge-to-policy gap?).
3. **Preregistered taxonomy validation**: observable condition definitions, blinded raters, frozen out-of-sample battery including all failed designs (attempted-trap registry: this report's negative controls and leaky variants already constitute it).
4. **Independent-designer battery** (de-confounds designer lineage; also legitimizes Fable as subject) and **crossed scaffolds** (same models through the same harness).
5. **Dose-response sweeps**: within-task anomaly-size/placement/plausibility manipulation — replaces the two-task threshold inference.
6. **Hierarchical analysis** over tasks/models/labs; **hygiene-tax accounting** (warned 2–3× tokens).
7. **Human practitioner baseline** (future work unless recruits materialize).
8. **Manuscript drafting**, with public release of generators, seeds, prompts, transcripts, keys, exclusions, and scoring decisions.
