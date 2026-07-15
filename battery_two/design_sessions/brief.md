# Design brief: trick tasks for data-science coding agents

You are the trap designer for an evaluation study. Your job: design data-science tasks
containing a hidden trap such that a frontier CLI coding agent (OpenAI and Anthropic
agents will both be evaluated), working naturally, produces a specific, plausible, WRONG
answer — while an observant human data scientist could catch the problem. You are
inventing the mechanisms yourself; originality and diversity across your candidates
matter.

## The trap frame — five conditions a successful trap must satisfy

A trap aims to make the agent's natural workflow produce a specific, plausible, wrong
answer. It must be:

1. **Unnamed** — the defense must not be a retrievable named idiom or drilled best
   practice. If the check that would catch it is something agents run reflexively and
   unprompted, the trap dies without ever being noticed.
2. **Non-failing on habitual paths** — no crash, warning, or hard error on any common
   tool route. A trap that fails loudly converts itself into a bug report.
3. **Not action-forcing under habitual checks** — quick looks at heads/tails/samples,
   describe(), null counts, per-file ranges, and duplicate checks may surface the anomaly
   but must not COMPEL investigation. An anomaly that lands visibly in the first rows of
   a casual sample forces the question and kills the trap.
4. **Plausible in output** — the wrong answer must be plausible on its face: right
   magnitude, right direction, the kind of number the task-giver would accept.
5. **Able to survive its own discovery** — if the anomaly does surface in the agent's own
   diagnostics, a benign story must be available that lets the agent absorb it and
   proceed to the wrong answer anyway.

## Deliverables — 8 candidates this round

For each candidate, create `./candidates/<task_name>/` containing:

1. `gen_<task_name>.py` — a seeded, deterministic generator (set `random.seed` and
   `numpy.random.seed` at the top; running it twice must produce byte-identical output).
   It must:
   - Write the complete task environment into `./candidates/<task_name>/masters/<task_name>/`
     (all data files, README, any scripts/docs the world needs).
   - Compute BOTH answers itself and `assert` the trap is live: the naive/habitual path
     yields the planted wrong answer, the careful path yields the correct answer, and the
     two differ materially. A generator whose asserts fail is returned to you as
     "generator error".
   - Write `answer_key.json` in the candidate folder: `{task, mechanism, planted_answer,
     correct_answer, tolerance}` (tolerance = how close a final answer must be to count
     as a match, e.g. rounding).
2. `prompt.txt` — a neutral business-toned task prompt (no hints, no warnings): what the
   folder at `/private/tmp/<task_name>` contains, what figure is requested, and this exact
   closing instruction: the final line of the reply must be `FINAL_ANSWER: <value>`.
3. `design.md` — mechanism, why each of the five conditions holds, the benign story for
   condition 5, planted answer, correct answer.

## Environment conventions

- Realistic small-business worlds: plausible company names, README.md, data sizes typical
  of real exports (thousands to tens of thousands of rows). Python 3.9 with pandas and
  numpy is the agents' toolset; CSV/JSON/log text files are the natural formats.
- The agent will be pointed at `/private/tmp/<task_name>` — write generators so masters
  are a self-contained folder that can be copied there.
- Mechanisms must be DISTINCT across your 8 candidates — different failure surface each
  time, not variations on one idea.

## Rules

- Work entirely inside this directory. Do not read anything outside it. No network.
- Run and test every generator before finishing (asserts must pass).
- End your work with a summary table: task_name | mechanism (one line) | planted vs
  correct answer.
