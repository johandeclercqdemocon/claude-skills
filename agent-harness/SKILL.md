---
name: agent-harness
description: How Johan wants an LLM agent (a model in a tool-calling loop) built and measured — tools as schema plus function behind a validator, failures returned as observations, a disk-cached chat client, a trace per run, tasks whose answers code can compute so no judge is needed, and the specific failures that small local models hit. Use whenever building, testing or writing about an agent, a tool-calling loop, tool definitions, or an agent evaluation, especially against local Ollama models.
---

# Agent harness

Reference implementation: `~/claude/ml-book/examples/agents/` (Chapters 35-38 of the ml-book).
Read `client.py`, `tools.py`, `loop.py`, `tasks.py` before writing a new one; copy, do not retype.
This skill is the *design*; the ml-book chapters hold the measurements behind each rule.

**Cost note (CLAUDE.md rule).** Everything here runs on local Ollama models: it costs wall-clock,
not money, and bills no API. Say so before starting a sweep. A tool-calling turn on this machine
(22 cores, no GPU) is 15-60 s; plan sweeps in the background and keep working.

## The five pieces

1. **A cached chat client** (`client.py`). Key the on-disk cache on the *entire request*,
   message history included. Two runs that diverge at step 3 then share steps 1-2 and pay only for
   what is new, and re-running an unchanged chapter costs nothing. Put `temperature` and `seed` in
   the key so repeated samples are distinct and reproducible. Always set `num_ctx` explicitly
   (Ollama truncates silently otherwise) and cap `num_predict` (a reasoning model's output is
   unbounded).
2. **Tools as data** (`tools.py`). A tool is `name + description + JSON schema + function`. The
   model sees the first three; Python runs the fourth.
3. **A validator in front of every call.** Check four things, in a few lines you can read:
   required key missing, unknown key present, wrong type, value not in the enum. Run it *before*
   the function. Never let a malformed call reach the function.
4. **Failures are observations, not exceptions.** Unknown tool, invalid arguments and a raising
   function all come back as `ERROR: ...` text the model reads on its next turn. An exception ends
   the run; an observation lets the model recover.
5. **A loop with a budget and a trace** (`loop.py`). Seven moving parts: a step budget, ask the
   model, stop on plain text, run what it asked for, show it the result, say so if the budget ran
   out, keep the trace. Record per step: tool, arguments, observation, ok-flag, prompt tokens. The
   trace is the unit of analysis; the final answer alone hides almost everything.

## Measure it with tasks code can grade

Pick a domain where **every question has an answer pandas (or any code) can compute**: counts,
means, group maxima, differences. Then grading needs no judge model and no human. Grade by number
match within 1%, or label containment; state that the grader can pass by accident on an answer that
lists several numbers. Order tasks by the minimum tool calls a correct run needs, so "calls made vs
calls needed" measures waste.

Also run the **no-tools control** (same model, same question, no tools). It scored 0/8 here, which
is what shows the tools are doing the work.

## Failures small local models actually have (measured, 2026-10)

Models: `granite3.3:2b` (fast, tool-capable) and `llama3.1:8b` (slower, more reliable).
`qwen3:4b` spent its whole output budget thinking and never called a tool; `phi4-mini` echoed the
schema back as its arguments. Pick models by running a one-call probe, not by reputation.

- **One sentence in the system prompt can switch tool use off.** "When you have the answer, reply
  in one short sentence that contains the number" took granite from correct first calls to *invented
  numbers* on 8/8 tasks. It describes the end state, and a small model asked for the end state
  produces it. Bisected to that single sentence. Do not describe the final answer's format in the
  system prompt of a tool-calling agent; say "never guess, call a tool".
- **A tool that returns success on an empty result is a silent failure.** A filter matching zero
  rows gave `mean = NaN` and `ok = True`; the model reported "the mean is NaN". Return an error
  that lists the values that do exist.
- **Value-format mismatch:** model writes `'Friday'`, table stores `'Fri'`. Put examples of stored
  values in the argument description.
- **Argument bleed:** granite passes another tool's arguments (`where_column` to `group_means`).
  The validator catches it; the error should also say which arguments the tool *does* accept.
- **Symbolic arithmetic:** the model passes `mean_of - mean_of(...)` to a calculator. State
  "numbers only; call the lookup tools first" in the calculator's description.
- **Mental arithmetic despite a calculator:** granite computed 0.6358 - 0.5709 as 0.0659 (true
  0.0649) and ignored the tool. Grade the number, not the effort.
- **Misreading a correct observation:** granite received the right table and named the wrong maximum.

## Rules

- Every number in a write-up comes from a run of the harness. Do not quote a timing from a run
  that overlapped another job.
- Keep the naive version of a tool alongside the improved one and measure both (`build_tools(careful)`
  in the reference). The improvement is the finding.
- Run long sweeps with `python -u` in the background; stdout is block-buffered when redirected.
- Never use `pgrep -f` / `pkill -f` to wait on a job; use `ps aux | awk '/[p]attern/'`.
- Untrusted text coming back from a tool is data. A defence in the prompt is a hypothesis; **removing
  the dangerous tool from what is offered** is a structural fix. Measure both (`defence.py`).
- Pair with `measured-writing` for any chapter or README that reports the results.

## Added 2026-10-07: what the full Part VIII measurements changed

- **Measure repeated runs, not one.** Report pass@k *and* pass^k at the temperature you ship at (0.7 here):
  llama pass@3 0.75 but pass^3 0.25. Per-task success is bimodal (a task is done reliably or not at all), so a
  mean misleads. The same prompt scored 0.92 at T=0 and 0.43 at T=0.7 because format discipline, not understanding,
  is what sampling breaks.
- **A tool redesign is model-specific.** Descriptions with examples helped granite (0.125 -> 0.225 mean success at
  k=5) and did not help llama (0.458 -> 0.417 at k=3). Re-measure on each model.
- **Errors that name the fix create a new failure: identical retries.** Add a repeat guard (refuse a call that already
  failed with the same arguments), but expect it to cut repeats, not raise passes.
- **Cost model.** Prompt tokens over n calls = n*P0 + d*n(n-1)/2; ~75 tokens per tool per call. Cap tool output:
  one 71,599-character result filled a 4,096-token window and truncated silently (prompt count = num_ctx - 1).
- **Print the prompt the model actually sees.** llama3.1's Ollama template renders tool definitions only in the last
  user message, so after turn 1 the model no longer sees them. `ollama show --template <model>`.
- **A ready-made harness costs tokens when unused** (deepagents: +8 tools, ~2.4k tokens/call, 3-4x total, passes
  equal on 8 simple tasks). Adapt it onto your own cached `chat()` so both sides make identical requests.
- **Injection experiments need a vulnerable baseline.** A lookup-only task gave 0/45 attacks (uninformative). Use a
  confused deputy: the user legitimately asks for an email, the poisoned text only changes the recipient. Score the
  attack AND whether the user's own task still completed: a prompt-level "delimiters" defence scored 0 attacks
  and 0/27 tasks done. An argument allowlist in code blocked all attacks and kept the task rate.
- **Judging the agent or anything else with a model judge:** report TPR and TNR on a balanced, split calibration
  set; correct with Rogan-Gladen; a one-sentence rubric fix moved llama's TNR 0.53 -> 1.00; calibration and
  production failure mixes must match or the correction misses; strict rubrics trade false-passes for
  false-fails. Of 7 judges, Granite Guardian 4.1 with a strict criterion was best; phi4-mini and mistral were
  rubber stamps; Prometheus 2 ignores added rubric sentences.
- **Run discipline on one CPU:** at most ~3 distinct Ollama models at once (more thrashes into 900 s timeouts);
  `python -u` for background runs; wait with `kill -0 PID`, never a pattern that matches the waiter itself.
