# Ledger spot-verification checklist

For each row: open artifacts/<file>.txt, read its final tagged answer line, confirm it matches 'ledger says'.
OUTCOME legend: X=planted(fall)  o=correct  E=other-error  N=no-answer

## A. Stratified random sample (40 runs, 4 per configuration)

- [ ] `ch_restampb_r3.txt` — Codex5.5@high / restampb r3 — ledger says **X**; extracted `EVENTS_JUL6: 40404`
- [ ] `ch_naregion_r3.txt` — Codex5.5@high / naregion r3 — ledger says **X**; extracted `TOP_REGION: EMEA`
- [ ] `ch_partial_r5.txt` — Codex5.5@high / partial r5 — ledger says **X**; extracted `LOWEST_REVENUE_DAY: 2026-06-30`
- [ ] `ch_nullmerch_r3.txt` — Codex5.5@high / nullmerch r3 — ledger says **X**; extracted `TOP_MERCHANT_CODE: RUBY`
- [ ] `n10_codex_jsonwin_r5.txt` — Codex5.5@xhigh / jsonwin r5 — ledger says **X**; extracted `ERRORS_JUL3: 1198`
- [ ] `n5_codex_drift_r4.txt` — Codex5.5@xhigh / drift r4 — ledger says **X**; extracted `TOTAL_5XX_IN_WINDOW: 1407`
- [ ] `n11_codex_netgrossb_r3.txt` — Codex5.5@xhigh / netgrossb r3 — ledger says **X**; extracted `NET_REVENUE_USD: $1,056,863.26`
- [ ] `n10_codex_partial_r3.txt` — Codex5.5@xhigh / partial r3 — ledger says **X**; extracted `LOWEST_REVENUE_DAY: 2026-06-30`
- [ ] `f5_naregion_r4.txt` — Fable5@high / naregion r4 — ledger says **o**; extracted `TOP_REGION: NA`
- [ ] `f5_restampb_r4.txt` — Fable5@high / restampb r4 — ledger says **o**; extracted `EVENTS_JUL6: 40000`
- [ ] `f5_naregion_r5.txt` — Fable5@high / naregion r5 — ledger says **o**; extracted `TOP_REGION: NA`
- [ ] `f5_burst_r4.txt` — Fable5@high / burst r4 — ledger says **X**; extracted `EVENTS_JUL5: 42312`
- [ ] `m54_partial_r2.txt` — GPT-5.4-mini / partial r2 — ledger says **X**; extracted `LOWEST_REVENUE_DAY: 2026-06-30`
- [ ] `m54_netgrossb_r5.txt` — GPT-5.4-mini / netgrossb r5 — ledger says **X**; extracted `NET_REVENUE_USD: $1,056,863.26`
- [ ] `m54_naregion_r4.txt` — GPT-5.4-mini / naregion r4 — ledger says **X**; extracted `TOP_REGION: EMEA`
- [ ] `m54_nullmerch_r2.txt` — GPT-5.4-mini / nullmerch r2 — ledger says **X**; extracted `TOP_MERCHANT_CODE: RUBY`
- [ ] `luna_jsonwin_r4.txt` — Luna@xhigh / jsonwin r4 — ledger says **X**; extracted `ERRORS_JUL3: 1198`
- [ ] `luna_drift_r5.txt` — Luna@xhigh / drift r5 — ledger says **X**; extracted `TOTAL_5XX_IN_WINDOW: 1407`
- [ ] `luna_burst_r2.txt` — Luna@xhigh / burst r2 — ledger says **X**; extracted `EVENTS_JUL5: 42312`
- [ ] `luna_naregion_r3.txt` — Luna@xhigh / naregion r3 — ledger says **X**; extracted `TOP_REGION: EMEA`
- [ ] `n5_opus_naregion_r1.txt` — Opus4.8@high / naregion r1 — ledger says **o**; extracted `TOP_REGION: NA`
- [ ] `n5_opus_canary_r1.txt` — Opus4.8@high / canary r1 — ledger says **o**; extracted `ERRORS_JUL3: 6659`
- [ ] `n10_opus_jsonwin_r4.txt` — Opus4.8@high / jsonwin r4 — ledger says **X**; extracted `ERRORS_JUL3: 1198`
- [ ] `n11_opus_trailspace_r5.txt` — Opus4.8@high / trailspace r5 — ledger says **o**; extracted `PCT_INVOICES_PAID: 82.61%`
- [ ] `ox_partial_r5.txt` — Opus4.8@xhigh / partial r5 — ledger says **o**; extracted `LOWEST_REVENUE_DAY: 2026-06-13`
- [ ] `ox_nullmerch_r4.txt` — Opus4.8@xhigh / nullmerch r4 — ledger says **X**; extracted `TOP_MERCHANT_CODE: RUBY`
- [ ] `ox_naregion_r3.txt` — Opus4.8@xhigh / naregion r3 — ledger says **o**; extracted `TOP_REGION: NA`
- [ ] `ox_partial_r1.txt` — Opus4.8@xhigh / partial r1 — ledger says **o**; extracted `LOWEST_REVENUE_DAY: 2026-06-13`
- [ ] `sol_nullmerch_r1.txt` — Sol@xhigh / nullmerch r1 — ledger says **X**; extracted `TOP_MERCHANT_CODE: RUBY`
- [ ] `sol_burst_r1.txt` — Sol@xhigh / burst r1 — ledger says **X**; extracted `EVENTS_JUL5: 42312`
- [ ] `sol_netgrossb_r1.txt` — Sol@xhigh / netgrossb r1 — ledger says **X**; extracted `NET_REVENUE_USD: $1,056,863.26`
- [ ] `sol_jsonwin_r1.txt` — Sol@xhigh / jsonwin r1 — ledger says **X**; extracted `ERRORS_JUL3: 1198`
- [ ] `s5_jsonwin_r3.txt` — Sonnet5@high / jsonwin r3 — ledger says **X**; extracted `ERRORS_JUL3: 1198`
- [ ] `s5_naregion_r4.txt` — Sonnet5@high / naregion r4 — ledger says **o**; extracted `TOP_REGION: NA`
- [ ] `s5_drift_r5.txt` — Sonnet5@high / drift r5 — ledger says **o**; extracted `TOTAL_5XX_IN_WINDOW: 10014`
- [ ] `s5_jsonwin_r5.txt` — Sonnet5@high / jsonwin r5 — ledger says **X**; extracted `ERRORS_JUL3: 1198`
- [ ] `terra_burst_r5.txt` — Terra@xhigh / burst r5 — ledger says **X**; extracted `EVENTS_JUL5: 42312`
- [ ] `terra_naregion_r4.txt` — Terra@xhigh / naregion r4 — ledger says **X**; extracted `TOP_REGION: EMEA`
- [ ] `terra_canary_r3.txt` — Terra@xhigh / canary r3 — ledger says **X**; extracted `ERRORS_JUL3: 1365`
- [ ] `terra_netgrossb_r2.txt` — Terra@xhigh / netgrossb r2 — ledger says **X**; extracted `NET_REVENUE_USD: $1,056,863.26`

## B. Judgment cells — READ IN FULL (5 runs) — HUMAN-VERIFIED 2026-07-09: Sol partial r1 caveat CONFIRMED; Opus partial r5 caveat CONFIRMED; Opus drift r1 confirmed as genuine stall/no-answer (its refusal text asks approval for an awk command — do NOT retroactively 'approve' it; the run is closed). Remaining in B: Terra naregion r3, Sonnet partial r5.

- [ ] `sol_partial_r1.txt` — caveat-adjudicated CATCH (Fable adjudicated — verify the caveat is real)
- [ ] `n10_opus_partial_r5.txt` — caveat-adjudicated CATCH (Fable adjudicated)
- [ ] `n5_opus_drift_r1.txt` — no-answer exclusion (harness artifact)
- [ ] `terra_naregion_r3.txt` — no-answer exclusion (died mid-output / template echo)
- [ ] `s5_partial_r5.txt` — the sole OTHER-ERROR (rejected trap, named wrong day)

## C. Quote-fidelity checks — confirm the paper's quotations against sources
- [ ] zero-error hole reported flatly — `v4_opus_svclog.txt` line ~5: verbatim "Hours 10:00–13:00 logged zero errors" (NOTE: 'quiet hours' was a fabricated-quotation gloss, now corrected in manuscript+report — this checklist item caught it)
- [ ] 'keeping missing values separate from named billing regions' — `v6_codex_naregion.txt` (development-phase run, NOT ch_*; manuscript now says so)
- [ ] `keep_default_na=False` + preemptive NULL prediction — f5_nullmerch (the 1/5 catch)
- [ ] 'Among actual merchant codes, RUBY leads' — `w_opus_nullmerch_r3.txt`; also verify 'some disputes lack a merchant code' — `ox_nullmerch_r3.txt`

## D. Extractor trust check
Open ~5 files from section A at random and read the WHOLE file, not just the answer line —
confirm the extracted line above is really the model's final answer and not a mid-run echo.
(This is the instrument-audit the paper is about: do not trust the extraction column blindly.)

---

## Machine quote-audit (quote_audit.md, regenerable via _private/quote_check.py)

A mechanical checker now verifies **every** quotation in the manuscript and report against
the full source corpus (run transcripts, the four AI-review outputs, the hygiene preamble,
and the literature extracts). Result: **0 unexplained NOT-FOUND**. All quoted transcript/review
spans are verbatim-present in a named source file; the remaining flags are (a) self-coinages /
terms of art, (b) sub-threshold short spans ("NULL", "high"), (c) a self-retracted claim quoted
inside a correction note, and (d) the MATH-Perturb literature quote (verbatim in the lit review
+ cached source).

LIMITS — the checker proves *presence*, not *fairness*. It cannot verify: that a quote is
attributed to the right speaker; that an ellipsis (`...`) doesn't hide a reversal; or that
surrounding context is represented honestly. Sections B (judgment cells) and C-context therefore
still require the human read. The "quiet hours" fabrication that motivated this checker was a
*presence* failure it would now catch; a *context* failure it would not — so do not treat a clean
machine audit as a substitute for the spot-read.
