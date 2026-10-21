---
name: measured-writing
description: "The pattern for books, guides, tutorials, READMEs and instructions: every claim measured by code that ships with the text, and a checker that fails the build when prose and code disagree. Use when asked for a book, chapter, documentation or how-to."
---

# Measured writing

**Standing instruction from Johan: use this pattern for any book or instructions, without being
asked.** Reference implementation: `~/claude/ml-book` — chapters, exercises, a checker and a PDF
(`ls ~/claude/ml-book/chapters | wc -l` for its current size). Its `STYLE.md` is the long form of §Prose below; read it before writing a chapter there.

The one idea: **nothing is asserted that was not run.** Everything else follows from that.

## The contract every chapter carries

A header block at the top, before any prose:

```markdown
> **Build** — what the reader has at the end. A thing, not a feeling.
>
> **Theory kept** — the minimum that changes what they type.
>
> **Source** — where it comes from, or `New`.
>
> **Run this first** — `uv run python -m examples.loop.splits`, which is
> [`examples/loop/splits.py`](../examples/loop/splits.py).
```

If a chapter does not end with the reader having built the thing named in **Build**, it has
failed. **Run this first** is not optional and not approximate — it is the exact command plus a
link to the file, because "run the example before you read" is useless advice without it. Where a
chapter genuinely has no code, say so in that line rather than omitting it.

## Every number comes from a script that ships with the text

- One module per chapter under `examples/`, runnable as `python -m`.
- No figure appears in prose that the reader cannot reproduce by running that module.
- Verify worked arithmetic by executing it before it goes in. This catches more than it sounds
  like it will.
- Where a result depends on hardware, the corpus, or a seed, say so where the number appears.

## The checker is part of the book

Write it early; it is what makes the rest enforceable. `scripts/check_snippets.py` is the model,
and it checks four things, all mechanical and all zero-false-positive:

| check | rule |
|---|---|
| links | every relative link resolves to a file that exists |
| contract | every chapter carries its header block |
| python | every ` ```python ` block is **executed** and must exit 0 |
| output | a ` ```text ` block directly under a code block is compared against the real output |

A reader copies a block and runs it, so the check is execution, not syntax. Blocks that are not
programs get a different fence (`text`, `bash`, `json`) and are skipped. Never weaken the checker
to accommodate a snippet — rewrite the snippet. Run it on an idle machine: a timeout under load is
not a failure, and reporting one as a failure is its own kind of wrong.

**While the checker runs, freeze what it reads.** The `freeze-during-sweep` skill has the read sets
and what to do when the freeze breaks.

## Programming books: depth and signatures, in every chapter

A book about a library, framework or language also follows the `programming-book-depth` skill
(Johan, 2026-10-13). Invoke it before drafting.

## Exercises, in three kinds

Per chapter, in `exercises/NN.md`, with worked solutions in `exercises/solutions/NN.md`:

- **[measure]** — run something, report a number. States the expected answer and a tolerance, so
  the reader can mark themselves against a measurement rather than an opinion.
- **[break]** — change one thing so a result *reverses*, and explain why. Tests whether they
  understood the mechanism or memorised the outcome.
- **[judge]** — no single right answer. The file says what a good answer weighs; the solution
  gives a position, the strongest objection, and what evidence would overturn it.

## Navigation: never make the reader guess where something is

This is the one that gets missed, and it is the one readers actually complain about. Every piece
points at every other, from the place where they are standing when they need it:

- the chapter → its command, its code file, its exercises, its solutions
- the exercise file → its chapter and its module
- the index → everything, in one table
- a chapter's last section → the next chapter

**Check it from the reader's position, not the author's.** You know where `examples/` is. They
have a PDF open and no file tree. Where a link cannot click — print, PDF — name the file anyway
and say where it appears in the contents.

## Prose in Simplified Technical English — every NEW book

**Standing instruction from Johan (2026-10-08): write every new book in Simplified Technical
English.** Invoke the `simplified-technical-english` skill (installed 2026-10-08 from
https://github.com/0xpili/simplified-technical-english, MIT) before drafting a chapter and run its
checker over the result:

```bash
python3 ~/.claude/skills/simplified-technical-english/scripts/ste_check.py --mode descriptive chapters/NN-name.md
```

**This applies to new books only.** `ml-book` was written before the instruction and stays in its
own voice; do not convert it unless he asks.

Why he asked for it: his words were *"the proza is a bit too difficult to follow."* STE is the
mechanical answer to that complaint — a sentence cap, one instruction per sentence, active voice,
and an approved word list, all of which a script can enforce. It turns readability from a matter
of taste into a check that fails.

### Where STE and this pattern agree

More than it first looks. STE's word rule — *do not use vague words, write the specific quantity,
name or action* — **is this pattern's whole thesis in STE's own vocabulary.** Both forbid adjectives
doing an argument's work. Apply the two together and they reinforce:

| instead of | write |
|---|---|
| "the difference may be noise" | "the difference is 0.031. One question moving one rank is worth 0.025." |
| "accuracy degrades significantly" | "accuracy falls from 1.000 to 0.498." |
| "this should be read as a floor" | "Read this result as a floor." |

Each rewrite loses a modal verb STE bans and gains a number this pattern demands. The hedge was
never carrying the meaning; the measurement was.

### Where they genuinely conflict, and what wins

- **Honest uncertainty needs to be sayable.** STE permits only `can`, `must` and `will`. Where a
  result is truly unresolved, do not reach for `may` or `might` — state the bound as a number, as
  above, or write the limit as a fact: "Twenty questions cannot resolve a difference this small."
  That is STE-legal and stronger.
- **Argument wants long sentences.** A 25-word cap makes connected reasoning choppier. Accept it,
  and carry the connective work with explicit back-references instead of subordinate clauses. If a
  paragraph will not survive the cap, it is usually two claims.
- **STE's exemptions still hold** and matter here: code blocks, identifiers, commands, file paths,
  quoted error messages, quoted text, and official names are all out of scope. Never rewrite a
  measured output to be STE-compliant — the output is what the machine printed.
- **Technical names are unlimited.** A book's conceptual vocabulary — `permutation importance`,
  `cross-encoder`, `reciprocal rank fusion` — is a technical name under STE and needs no
  apology. STE constrains the connective tissue, not the subject.

Keep the rest of §Prose below, except the British-spelling line: **STE requires American
spelling, and for a new book STE wins.**

## Prose

- **Concepts before measurements.** Never a table whose columns the reader cannot name.
- **The paragraph is the claim; the table is only evidence.** Read the table aloud in prose.
- **Short derivations where they illuminate**, with every symbol given a meaning in words.
- **Link backwards and forwards explicitly.** One argument, not N essays.
- Target a real chapter length (~3,500–4,500 words for a book). If it comes in short, the usual
  cause is missing explanation — but never pad.
- British spelling, em-dash sparingly, no exclamation marks.

## Honesty, which is the part that makes it worth reading

- **Keep the hypothesis that was wrong**, with the measurement that killed it. A failed mechanism
  hunt published as a null is worth more than a tidy story.
- **State bounds.** If n=20 means one item moving one rank is worth 0.025, say so before quoting a
  0.03 difference as a result.
- **Publish the failures of your own tooling** alongside the successes. A walkthrough showing only
  what worked is advertising.
- **Describe an artefact from the artefact.** Caption a screenshot by opening it, not from the
  notes you took when you made it. Four captions were wrong in `ml-book` for exactly this reason.
- If a verification says something surprising, suspect the verification first. A "the PDF is 8
  pages" report was a broken regex, not a broken PDF.
- **A false absence is the easiest wrong answer to get.** Checking a built artefact for content,
  three separate greps reported it missing in one session: two used a search string that had been
  edited out of the source (`4,945` after it became `4,914`), and one piped through `head -4`, which
  hid the match it was looking for. Before reporting that something is missing, grep for a *shorter*
  substring, drop the `head`, and search the artefact's own page range. Prose wrapping and
  hyphenation also defeat exact phrases: `pdftotext` renders `memory-bandwidth` across a line break
  as `memorybandwidth`.

## Build artefacts

PDF via **headless Chrome only**. Drive it over the DevTools protocol rather than
`--print-to-pdf`, so the footer can carry a page number and nothing else; a numbered contents then
needs two passes — print, read back each section's page with `pdftotext`, reprint, repeat until
stable. `~/claude/ml-book/scripts/build_pdf.py` is the working implementation; copy it.

## Anti-patterns

- Bullet lists where a paragraph belongs.
- "It can be shown that…" — show it or cut it.
- Adjectives doing an argument's work ("dramatically better"). Give the number.
- A pull-quote with nothing behind it.
- Claiming structure the files do not have. "Every chapter names its module at the top" was false
  in `ml-book` for weeks; the fix was to make it true, not to soften the sentence.
