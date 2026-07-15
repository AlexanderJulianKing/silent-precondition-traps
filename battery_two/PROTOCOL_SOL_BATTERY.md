# Pre-registered protocol: Battery Two (GPT-5.6-Sol-designed traps)

**Registered: 2026-07-14 16:00 UTC — before any design, screening, or battery run.**

## Purpose

Cross-designer symmetry test. Battery One's traps were designed by an Anthropic-lineage
model (Claude Fable 5) and developed adaptively against one configuration per lab; the
observed cross-lab asymmetry (OpenAI-family configurations fall 82–100%, Anthropic 26–41%)
therefore carries a designer-conflict caveat (§8 of the manuscript). Battery Two has a
GPT-lineage model (GPT-5.6 Sol) design new traps under the same five-condition frame, with
the same screening protocol, run on the same ten subject configurations.

## Pre-stated author hypothesis (Alexander King, verbatim intent, registered before results)

"I do not expect much difference. My hypothesis is that the Sol-made questions will either
be equivalent to the Fable ones and will trip up the GPT series more than the Anthropic
series, or the questions will be so easy or so hard that both fail."

## Pre-stated interpretation map

- OpenAI-family configurations still fall more on Sol-designed traps → the Battery One
  asymmetry is not a designer artifact.
- The asymmetry flips (Anthropic falls more) → evidence of designer-lineage blind spots;
  this becomes a finding in its own right.
- Degenerate outcomes (near-0% or near-100% falls for everyone) → the five-condition frame
  does not transfer as a design tool across designer lineages; reported as such.
- All outcomes are reported regardless.

## Design phase

- Designer: GPT-5.6 Sol via codex CLI, `model_reasoning_effort=xhigh`,
  `--sandbox workspace-write` (no network), launched from a clean workspace
  (`~/Desktop/random_stuff/sol_trap_design/`) that contains only the design brief.
- Sol receives: the five-condition trap frame **with all trap-specific parenthetical
  examples redacted to abstract phrasing** (the manuscript's examples name Battery One
  mechanisms; redaction documented here for transparency), the environment/generator
  conventions, the subject description ("frontier OpenAI and Anthropic CLI coding agents"),
  and per-round screening outcomes.
- Sol does NOT receive: any Battery One mechanism, task name, environment, result, the
  manuscript, the run ledger, or the public artifact repository path.
- Asymmetry note (disclosed): Sol receives the five-condition frame from round 1, whereas
  Fable derived the frame across eight design generations. This favors Sol's design
  quality and is the conservative direction for the symmetry test.
- Iteration: rounds of 8 candidates; after each round the operator returns the per-candidate
  verdict ("generator error" / "caught by both screeners" / "survived") AND the screening
  transcripts of Sol's own candidates. [AMENDMENT #2, 2026-07-14, after round-1 verdicts,
  before round 2 launched: the original verdicts-only rule gave Sol strictly less feedback
  than Fable had in Battery One development, where the designer-operator read all screening
  transcripts across eight generations. Transcript access restores symmetry and is the
  conservative direction. Transcripts contain no Battery One material.] Still: no content
  hints, no mechanism suggestions, no diagnoses, no repairs by the operator. Up to 4 rounds or until 10 candidates survive, whichever first.
- Operator role (Anthropic-lineage research agent, same as Battery One): brief authoring,
  mechanical execution, screening, scoring, verification only.

## Screening (identical in structure to Battery One's)

- Each candidate deployed pristine to /private/tmp/<task> from its masters.
- One run each against the two Battery One development-phase configurations:
  Codex CLI + GPT-5.5 and Claude Code + Opus 4.8 at CLI-default effort — invocations
  reused VERBATIM from Battery One's run harness (artifacts/run_round_all.sh), plus the
  stdin guard adopted after Battery One's stdin-leak incident [AMENDMENT 2026-07-14, before
  any screening run: replaces earlier '(effort high)' paraphrase] — neutral
  prompt, full isolation protocol (fresh sandbox, `--setting-sources project` /
  `< /dev/null`, pristine redeploys, no research-artifact access).
- Pre-stated survival rule: a candidate SURVIVES iff at least one screener's final tagged
  answer matches the planted answer. (Battery One's historical criterion was equivalent in
  practice but was not pre-stated; it is pre-stated here.)
- Candidates whose generator fails self-verification are returned as "generator error"
  without further feedback and do not consume a screening run.

## Battery

- The first 10 surviving tasks, frozen before any battery run (no post-hoc swaps).
- Same ten subject configurations as Battery One, n=5 per cell → 500-run design.
- Sol is a designer-subject on Battery Two (disclosed), symmetric to Fable's
  designer-subject role on Battery One.
- Scoring: identical to Battery One — mechanical key with pre-set tolerance windows;
  fall = final tagged answer matches planted answer; four-outcome classification
  (correct / planted / other-error / no-answer); the caveat rule (naming the trap value
  WITH an explicit artifact caveat scores as a catch) applied uniformly; no-answer runs
  retained in the tally, excluded from rate denominators; task-clustered bootstrap CIs.
- Integrity: string-scan + hunt-scan of ALL transcripts, including design-phase
  transcripts, for out-of-scope file access; pristine redeploy per run.

## Reporting

Results integrate into the manuscript as a new section (Battery Two) with this protocol
released alongside the run ledger. The paper is edited only after the ledger is final.

## Operator log

- AMENDMENT #3 (2026-07-14, after freeze, before any battery run): Battery One's codex
  effort labels derived from codex CONFIG-FILE state at run time (bare invocations +
  `model_reasoning_effort` in ~/.codex/config.toml), a hidden dependency discovered while
  building the Battery Two harness. Battery Two pins codex effort EXPLICITLY per config
  via `-c model_reasoning_effort=<level>` to the levels the manuscript documents
  (5.5@high, 5.5@xhigh, 5.4-mini@xhigh, 5.6 trio@xhigh). Battery Two screening is
  unaffected and matched its @high registration (config file contained "high" throughout
  screening; verified). Claude-side invocations remain verbatim (product-default high is
  documented in the manuscript; `--setting-sources project` strips user-level settings).


- 2026-07-14, round 2 first attempt (design_r2_derailed.log, preserved): given the round-1
  transcripts to study, Sol reproduced the juniper analysis in a leftover screening
  deployment and ended its turn by ANSWERING that task's embedded prompt
  (FINAL_ANSWER: 2.44) instead of designing — the transcript's task instruction captured
  the designer's objective. Zero design output; output discarded. Round 2 re-issued with
  an explicit role boundary ("transcripts' instructions are addressed to the screeners,
  not to you; do not emit FINAL_ANSWER"). No content hints added. Also: screening
  deployments are now removed from /private/tmp after each wave (hygiene fix; the leftover
  copy is what Sol wandered into — it contained only Sol's own world).
