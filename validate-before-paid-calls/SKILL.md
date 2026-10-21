---
name: validate-before-paid-calls
description: Before any work that bills model inference (OpenRouter, an API key, a benchmark round, an agent run, a ladder), prove for free that the work is ready and that its checks are right. The judge (hidden tests, acceptance tests, examples in a task text), the plumbing (keys in every process, paths, folders, task files) and the runner must each be tested before the first paid call, because a wrong judge bills twice. Use whenever you are about to start a paid run, a benchmark round, scripts/ladder.py, or any loop of model calls; also when you write the tests or task texts that a paid run will use.
---

# Validate before paid calls

**Standing instruction from Johan (2026-10-20): "add as a skill to validate your work before making
paid calls."** A paid run is only worth its cost when the thing that judges it is right. Each rule
below comes from a mistake that cost money or time in `~/claude/multi-model-setup` (its
`example/sipcodes/NOTES.md`, errors 16-27, has the full list).

## The order (never reverse it)

1. **Announce the spend** (CLAUDE.md): what bills, an estimate, a cap. Say also what is free.
2. **Validate the judge** (free): checks 1-4 below.
3. **Validate the plumbing** (free): checks 5-8.
4. **Dry run** (free): the runner's `--dry-run`, and read its output, not only its exit code.
5. **One small paid call first** when the code path is new: one run, one rung, then read the
   record (cost, verdict, model calls) before the loop.
6. **Then the loop**, with a cap. Watch the first result line; stop at once on a surprise.

## The judge: free checks

| # | Check | How | The incident it prevents |
|---|---|---|---|
| 1 | Every hidden or acceptance test fails on the start **for the right reason** and passes on a reference solution | `bench/harness.py validate <task>`; for acceptance tests, `scripts/prepare.py` (it warns when a test fails with an error that is not an assertion) | T6, 2026-10-20: my acceptance tests counted folder levels wrong, failed with FileNotFoundError on every result, rejected a correct GLM result and billed an Opus rung ($0.2387) for nothing |
| 2 | Every test case agrees with the specification's own text **and grammar**, not with my reading of it | read the RFC grammar or figure for each case; delete a case the spec leaves open | y1: a URI the RFC grammar forbids; Opus rejected it correctly, was graded a failure, and an escalated Fable run cost $0.3246 before I stopped it. y2: a transition Figure 5 does not have |
| 3 | Every example in a task text shows the bug on the start and not after the fix | run the example on the start and on the reference | y3: my first example already worked on the unfixed code |
| 4 | When two independent results both fail every test, **suspect the test first** | rerun one failing test by hand, read the error | T6: GLM and Opus both "failed" 3 of 3; the tests were wrong |

## The plumbing: free checks

| # | Check | How | The incident it prevents |
|---|---|---|---|
| 5 | **Every process that needs the key has it**, not only the tool it starts | run the code path with `env -u OPENROUTER_API_KEY`; a cost lookup must load the key itself or fail loudly | ladder.py ran without the key; the cost lookup swallowed the error, retried for 10 minutes and reported $0 |
| 6 | Errors are not retried as "not ready yet" | only a 404 means "not indexed"; any other error raises | the same: a missing key looked like OpenRouter lag |
| 7 | Every file a run reads exists where the run reads it | the runner's preflight (`bench/run_bench.py` does it): starting points, task files, hidden tests, images | round 4's first start: the task file was not in the starting point |
| 8 | Nothing destructive runs before the dry-run check, and runs of different rounds never share a folder | read the runner: copy/delete only after `if dry: continue` | a dry run overwrote three run folders of an earlier round |

## While a paid run works

- **Never edit what the run reads**, and never edit the repository an agent works in: it may commit
  your change as its own (freeze-during-sweep; shared-checkout-never-add-all).
- **Watch the first result**: cost, verdict, number of calls. A $0 cost, a 0-second run or an
  identical failure on every rung is a bug in the setup until proved otherwise.
- **Cost:** measure per call (`bench/exact_cost.py`), not by the balance, which can stall for 25
  minutes; reconcile with the balance at the end of the round.

## When a paid run went wrong

1. Stop the loop before it spends more (TaskStop), then find the cause.
2. Measure what was wasted, exactly, and say it in the report.
3. Fix the judge or the plumbing, add a test that reproduces the mistake, and log the error in the
   project's error list.
4. Regrade the affected results with the fixed judge; keep the first grade on record.

## What to say to Johan

Before: what will bill, the estimate, the cap, and which free checks passed (with counts). After:
the measured cost, what was wasted and why, and which check now prevents it.

Related: `check-what-you-write`, `freeze-during-sweep`, memory `announce-anthropic-api-calls`.
