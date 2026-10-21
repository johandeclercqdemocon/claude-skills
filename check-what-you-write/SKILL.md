---
name: check-what-you-write
description: "Audit text before it counts as finished: every number, identifier, link and assumption checked against what the machine printed, failures listed. Use when writing or changing a chapter, exercise, README or report that states a number, name, behavior or command."
---

# Check what you write

**Standing instruction from Johan (2026-10-13): "I hate errors in books" and "I want no errors and no wrong assumptions."** Treat an error in a book as
the worst outcome of the work, worse than a missing chapter. A missing chapter is visible. A wrong
number is trusted.

This skill exists because the pandas book showed, in one session, which errors come back:
the table below is from `~/claude/pandas-book/.notes/wrong-predictions.txt`.

| What went wrong | How it got in | What catches it |
|---|---|---|
| 12 prose numbers that disagreed with the output ("536 roaming calls" for 563) | prose written before the output existed | the number audit |
| a claim about behavior that nobody ran ("a text and an integer key join silently") | written from memory | run it; if it cannot be run, say "not run" |
| a number typed into an `# output varies` block | invented to look plausible | run the block, paste the real output |
| a measurement that depended on the parent process (`ru_maxrss` after `fork`) | trusted the first plausible number | run it twice; a baseline must not move |
| a parameter name that does not exist (`Series.map(arg=...)`) | typed from memory | print the signature with `inspect` |
| a code example that breaks on a small input (chunk size 10) | tested with one size only | test with the extreme size |
| an explanation of a cause that nobody measured | plausible story | measure it or flag it as a hypothesis |
| a limit of a tool, stated as fact ("this SQLite has no CEIL"; it has) | assumed, never tried | run one line that tests it |
| timings quoted from a probe, while another session loaded the machine | trusted a noisy run | refresh from a run on an idle machine; quote only what the assertion proves |
| edited three chapters while the full checker was reading them (a wording fix) | impatience | `freeze-during-sweep`: discard the run, restart it, and edit nothing until it ends |
| a number in an output block that nobody ever printed ("17 13 MB" for "21 16 MB") | typed to fit the prose | no number is typed into an output block |

## The order of work (never reverse it)

1. **Write the code block and an empty output marker** (`# fill`). Not the prose.
2. **Run it. Read the output.** Surprises are the content; note each one.
3. **Only then write the sentence that quotes it.** Quote by copying from the output, not from the
   memory of the output.
4. **Re-run the whole chapter** when anything it reads changed (see `freeze-during-sweep`).

## The audit, before a chapter counts as done

Do all five. Each is mechanical, and none is optional.

1. **Run the book checker.** Every snippet executes, every claimed output matches, every link
   resolves, every contract header exists. A red check is not "probably fine".
2. **Number audit.** Extract every number from the prose and look for it in the outputs of the
   book. Each number that is not there is one of three things: derived (check the arithmetic by
   running it), copied wrong (fix it), or invented (delete it). `scripts/audit_numbers.py` in the
   pandas book is the reference.
3. **Identifier audit.** Every function, parameter and file name in the prose exists. Print
   signatures with `inspect`, list files with `ls`, and compare. A renamed parameter between library
   versions is the usual cause.
4. **Claim audit.** Read the chapter once as an enemy. For each sentence that says *why*, ask: did a
   block measure this? If not, mark it "hypothesis" in the text, or measure it, or delete it.
   Sentences about *other versions* of a library that you did not install are "described, not run":
   put them in the appendix of unrun claims.
5. **Look at every artifact.** Open each figure, PDF page and rendered table. Describe it from the
   artifact, not from the code that made it. Four wrong captions in one earlier book came from
   describing the plan instead of the picture.

## When the audit finds an error

- **Fix it, and say so.** Add the error to the book's list of "what went wrong while writing"; a
  book that shows its corrections is trusted more than a book that has none.
- **Look for the same error elsewhere.** An error is a symptom of a habit. Grep for the pattern
  (the same number in an exercise, the same parameter in another chapter).
- **Suspect the verification first** when a check says something surprising. A broken regex is more
  likely than a broken artifact.

## What to say to Johan at the end

State the audit result in numbers: how many snippets ran, how many numbers were checked, how many
prose errors the audit found and fixed, and what is *not* checked. "Checked" without a count is not a
report. Never write "verified" for something that was only read.

## The assumption audit (separate from the number audit)

A wrong assumption has no number in it, so the number audit cannot find it. Do this once for each
chapter, with the text open:

1. **List the assumptions.** Write down, in a scratch file, every sentence that depends on something
   that the chapter did not print: the version of a library, what an optional package does, what a
   database supports, what "usually" happens, how real systems behave, what the reader's machine has.
2. **Sort each one** into exactly one of: *tested* (a block prints it), *given* (the book states it
   as a premise, in one place, e.g. "the data are synthetic"), *described, not run* (listed in the
   appendix, worded as "the documentation says"), or *wrong* (delete or fix).
3. **Test the cheap ones now.** A one-line probe settles "does X exist", "is Y installed", "what
   type does Z return". An untested limit of a tool is the commonest wrong assumption.
4. **Words that signal an untested assumption:** *always, never, usually, only, must be, because the
   library, in older versions, real data, in practice, on most machines, no gain, faster, slower.*
   Grep for them and justify each hit.
5. **Machine state is an assumption too.** Timings need an idle machine. Check the load before you
   run a benchmark and again before you quote it, and never quote a number from a noisy run.
