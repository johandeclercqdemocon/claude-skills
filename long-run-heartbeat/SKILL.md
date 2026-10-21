---
name: long-run-heartbeat
description: Report progress on a long-running job every 7 minutes instead of going silent or blocking on it. Use whenever a command, build, measurement, training run, sweep or render will take more than a few minutes — anything launched detached or with run_in_background. Covers the 7-minute heartbeat mechanism, how to measure real progress rather than liveness, and what to do between checks.
---

# Heartbeat a long run every 7 minutes

**Standing instruction from Johan: when a job is long-running, check it every 7 minutes and say
what you found.** The failure this prevents is not a crashed job — it is a silent hour in which he
cannot tell whether work is advancing, stuck, or finished.

Two things are forbidden and this skill replaces both:

- **Blocking.** Never sit in a foreground wait, and never end the turn only to wait for a
  notification. Launch detached, then keep working.
- **Silence.** Never let a long job run without reporting. "I'll check when it's done" leaves him
  with no information for however long the job takes.

## Launch so that progress is observable

Before starting, decide **what counts as progress** and make sure something on disk records it.
A job that only prints at the end is unobservable, and `PYTHONUNBUFFERED=1` is usually the
difference between a live log and an empty file.

```bash
nohup env PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8 <command> > "$SP/job.log" 2>&1 &
```

If the log will stay empty regardless, find a proxy that moves: cache entries written, output
files produced, rows appended, checkpoint files. A countable artifact is better than a log line,
because it converts into a rate and therefore into an estimate.

## The heartbeat

Arm a `Monitor` whose loop emits one line every 420 seconds and exits on any terminal state.
`timeout_ms` caps at 1,800,000 ms, so one arm covers **four** heartbeats — re-arm on expiry for
as long as the job runs.

```bash
JOB=<pid>; SP=<scratchpad>
while true; do
  if ! kill -0 "$JOB" 2>/dev/null; then echo "DONE: process $JOB exited"; break; fi
  echo "ALIVE $(date +%H:%M) :: $(ls "$SP/cache" 2>/dev/null | wc -l) artifacts :: $(tail -1 "$SP/job.log")"
  grep -qE "Traceback|FATAL|Killed|OOM" "$SP/job.log" && { echo "FAILED: see job.log"; break; }
  sleep 420
done
```

Cover every terminal state, not just success. A filter that matches only the happy path is silent
through a crash, and silence is indistinguishable from "still running".

**Do not use `pgrep -f` or `pkill -f` to find the job.** The pattern matches the searching command
itself. Use the PID from launch, or `ps` with an explicit self-exclusion.

## Each heartbeat, report a rate — not a pulse

"Still running" is almost worthless. Convert the countable artifact into an estimate:

> 423 of 759 chunks in 21 min → ~20/min → **17 min remaining**.

That is what lets Johan decide whether to wait, go and do something else, or tell you to kill it.
State the trend when it changes: a rate that halves means something is wrong and is worth saying
before the job ends rather than after.

Also say, once, whether the run **bills inference or not**. Local work costing nothing changes
what is worth doing eagerly.

## Between heartbeats, work the spine

Waiting is not an activity. Pick up work that does not depend on the pending result and does not
contend with the job for CPU, disk or a model server. Light editing, prose, structure and planning
are fine; a second heavy job is not — concurrent heavy runs have caused false timeouts here.

**Never write the pending number down.** Draft the surrounding text, leave the figure blank, and
fill it in from the run. Inventing a plausible number and forgetting to replace it is how a
fabricated measurement reaches the page.

One trap specific to measurements over files you are also editing: **if the job reads the repo, do
not edit what it reads.** Changing the corpus mid-run invalidates the result silently. Keep off
those paths until it lands.

## When it finishes

Report the outcome in the same message as the numbers, then do the thing the run was for. Do not
announce completion and stop — the run was a means to an end, and the end is still owed.

If it failed, say so with the actual error rather than a summary of it, and say what you will try
next.
