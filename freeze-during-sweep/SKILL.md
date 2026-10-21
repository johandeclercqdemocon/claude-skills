---
name: freeze-during-sweep
description: Never edit the files a verification run is reading. Use whenever a checker, test suite, measurement module or book build is running — check_snippets.py, pytest, examples.rag.*, build_pdf.py — and before touching any file while one is in flight. Defines exactly what counts as a sweep, what each kind reads, and what to do when the freeze has already been broken.
---

# Freeze the inputs while a sweep runs

**Standing instruction from Johan (2026-10-08), after I broke it twice in one session: do not edit
anything a running verification reads.** A verification that races a writer is worth less than no
verification, because it produces a verdict you then have to disbelieve.

## What counts as a sweep

A **sweep** is any run that reads the repository in order to produce a verdict or a published
number. Four kinds exist in `~/claude/ml-book`, and they differ in what they read:

| sweep | command | reads |
|---|---|---|
| **snippet check** | `uv run python scripts/check_snippets.py [files]` | `README.md`, `chapters/*.md`, `appendices/*.md`, `exercises/*.md`, `exercises/solutions/*.md`, **and every module those blocks import** |
| **test suite** | `uv run pytest` | `tests/`, `examples/`, and `git ls-files` output |
| **measurement** | `uv run python -m examples.rag.<module>` | **`chapters/*.md` — the corpus is the book** |
| **book build** | `uv run --with markdown --with websockets python scripts/build_pdf.py` | `chapters/`, `appendices/`, `artifacts/*.png` |

Read that list before deciding a file is safe. The three that surprise people:

- **`README.md` is in the snippet check's read set**, so it is not a safe place to work during one.
- **Every measurement module reads `chapters/`**, because Part VI retrieves over this book's own
  text. Editing any chapter during `examples.rag.*` changes the index mid-measurement.
- **Snippet blocks execute with `cwd=ROOT`**, so a block can write into the repository, and the
  files it writes are part of the run's state.

## The rule

**While a sweep is running, the entire read set is frozen.** Not "mostly frozen", not "except small
edits", not "except reverting in a few seconds".

Safe during a sweep:

- Reading anything.
- Writing to the scratchpad directory.
- `git add`, `git commit`, `git restore --staged` — these touch the index, not working-tree content.
- Editing files genuinely outside the read set, after checking the table above.

Not safe, and both of these are mistakes I actually made:

- **Editing a chapter** to fix something the sweep just reported. Wait, then fix, then re-run.
- **Moving a file "briefly" to test an error path.** I moved `artifacts/tokens-snapshot.json` for
  about five seconds to see the missing-file message. The window happened to miss the block that
  reads it. Test error paths on a copy in the scratchpad, never in the live tree.

## Check for other writers first

Being the only writer is an assumption, and on 2026-10-08 it was false — a spawned task ran in the
same checkout. Before trusting a sweep:

```bash
git worktree list
ps -eo pid,etime,args | awk '/check_snippets|bin\/pytest|examples\.rag/ && !/awk/'
ls -lt --time-style=+%H:%M chapters/*.md | head -5
```

A chapter mtime newer than the sweep's start means the result is already suspect. See
[[shared-checkout-never-add-all]] for coordinating with the other session.

## Waiting for a sweep

Use a **harness-tracked** background wait, not a detached guard. A `nohup bash -c '...' &` guard
armed from a tool call did not survive here, and only a direct check revealed it was already dead —
it would have let a 3.5-hour run start that we had agreed to skip.

```bash
until [ "$(ps -eo args | grep -v grep | grep -c 'check_snippets')" -eq 0 ]; do sleep 10; done
echo "SWEEP CLEAR"
```

Run that with `run_in_background: true`, and pair it with a 7-minute heartbeat
([[long-run-heartbeat-7-min]]) so the wait is visible. Verify an armed guard is actually alive
rather than assuming; a bare `grep -c` can match its own command line.

## When the freeze has already been broken

Say so and discard the run. Do not report it, and do not salvage the parts that look unaffected —
you cannot tell which blocks executed before the edit landed.

1. Kill the sweep.
2. Finish the edits, all of them.
3. Re-run clean, and only then report numbers.

Both times this happened, discarding cost a few minutes. Reporting a racing run as verification
would have put an unverified number in a book whose entire claim is that its numbers are verified.
