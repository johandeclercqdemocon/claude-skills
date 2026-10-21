---
name: programming-book-depth
description: Every chapter of a programming book carries a "How it works" section and a "Reference" section with printed signatures and a row per parameter. Use with measured-writing for a book, chapter, tutorial or guide about a library, framework or API.
---

# Programming books: depth and signatures

> **Decided by Johan, 2026-10-13: keep this skill.** A parallel session had written
> `programming-book-reference` from the same instruction. Johan chose this one, and that skill no longer
> exists. The deciding difference: this skill *prints* each signature with `inspect` and compares the whole
> text, defaults included, so it cannot drift. The other one typed it in a ```signature block and checked
> parameter *names* only. The section names are `## How it works` and `## Reference`.
>
> **A working implementation:** `~/claude/numpy-book/scripts/check_snippets.py` (`#### name` heading,
> printed signature block, parameter table, defaults checked) and `examples/signatures.py`, which also
> parses C functions whose signature is the first line of the docstring.

**Standing instruction from Johan (2026-10-13): every programming book gets both, in every chapter,
without being asked.** Written for the Keras book; applies to any library or language.
It adds to `measured-writing` and `simplified-technical-english`. It replaces neither.

## 1. "How it works" — one section per chapter, deeper than the usage

Usage tells the reader what to type. This section tells them what happens when they type it.
Johan's words: *"a bit deeper explanation per chapter."* So: a bit, not a treatise.

- **300–500 words and at least one executed block** that reproduces the mechanism with the simplest
  code that can show it. Examples that worked: one `fit` step redone by hand (forward, loss, gradient,
  update) and compared to the library; attention written from its formula and compared to the built-in;
  a counter layer that exposes how many times the framework calls it.
- **Name the invariant.** What is always true, in one sentence the reader can test.
- **Name the failure.** What breaks when the invariant is violated, with the number from a run.
- **Put it after the usage and before the exercises.** The reader has used the thing and now wants to know why.
- A mechanism claim that no block measured is a hypothesis. Say so, as the Keras Chapter 11 did
  before its edge-token test confirmed it.

## 2. "Reference" — the real signatures, printed, then explained

Johan's words: *"add function signatures and their parameters in the chapters themselves."*

**Never type a signature from memory.** Library signatures drift and memory is wrong. Print them from the
installed version, in a block the checker executes and compares:

```python
import inspect
import keras

for fn in (keras.layers.Dense, keras.Model.compile, keras.Model.fit):
    print(f"{fn.__qualname__}{inspect.signature(fn)}")
```

followed by the `text` block that holds the real output, so the build fails when the library changes.
Other languages: `go doc`, `cargo doc`/`rustdoc --test`, `--help` output, `javap`, TypeScript `.d.ts`.
Whatever the language, the signature in the book is produced by a tool, not by a person.

Then, under the printed signature, a **parameter table** with **one row for every parameter** of the signature,
`*args` and `**kwargs` included:

| parameter | default | what it does | what goes wrong |
|---|---|---|---|
| `from_logits` | `False` | tells the loss whether the output is raw scores | accuracy 0.709 instead of 0.971, no warning |

> **Changed by Johan, 2026-10-13** ("on page 4 I miss already 2 parameter explanations"): the earlier rule
> "only the parameters the chapter uses" left 54 parameters without a row in the NumPy book and 418 rows to add in
> the Keras book. Every parameter gets a row. A row with nothing measured says `—` in the last column.

Rules for the table:

- **One `####` block per callable, at its first use** in the book: a heading ``#### `lib.name` ``, the signature
  in a ```text block (printed by the checker's `--signatures`, one parameter per line), its prose (what it
  returns, the behaviour that matters here), then **one sentence that says where its table is**. A later chapter
  links back to the block. It never repeats it.
- **The table sits in the chapter's `## Reference` section**, not in the block: first a short index
  (callable | introduced in | contract) that names only callables with a block, then `### Parameters` with one
  ``##### `lib.name` `` heading and its table per block, in the order the blocks appear. Five hashes, so the
  `####` count is unchanged.

  > **Changed by Johan, 2026-10-15**: tables at first use made the text hard to read (one book reached 658 pages);
  > the signature stays inline, the table moves to Reference. `~/claude/utilities/move_param_tables.py` converts a
  > book written the old way.
- **Every default comes from the installed signature**, never from memory. `*args`/`**kwargs` have the default `—`.
- The last column is a measured consequence, or `—` if none was measured. Never invent one. **Run the claim before
  you write the row**, in a script per chapter that ships with the book (`scripts/rows/chNN.py` plus its saved
  output), so a reader can see the evidence of a number that no chapter block prints.
- Do not restate the docstring. The useful rows were the ones where the run disagreed with it or with folklore:
  a misleading error message, a keyword that is silently ignored, a default that changes the number.
- Mark parameters that are positional-only, keyword-only, deprecated, or back-end specific.

## 3. Make the checker enforce it

- **contract**: check that the chapter contains the headings `## How it works` and `## Reference`. A chapter
  that has no API (a theory or field-guide chapter) says so in one line instead of omitting the headings.
- **params** (required): for each `####` block, the ```text block equals the installed signature; its table is
  under ``##### `name` `` in Reference (a table left inside the block fails); every row is a real parameter with
  its real default; **every parameter has a row**; no callable has two blocks; every name in a Reference index
  (the part before `### Parameters`) has a block. Implementations: `~/claude/pandas-book/scripts/check_snippets.py` (`pdbook/sigs.py`)
  and `~/claude/keras-book/scripts/check_snippets.py` (`examples/signatures.py`, constructor of a class = its
  `__init__` without `self`).
- **names**: every `lib.name` in the prose exists in the installed library.

## 3b. The samples: four checks for every code block

Johan's review of a first example (2026-10-13), turned into rules. Apply them to **every** code sample, not
only the first.

1. **It builds what the sentence says, directly.** "Make a 2-by-3 array" is `np.array([[...], [...]])`, not
   `np.arange(6).reshape(2, 3)`. A chain hides a step. The reader must not meet a call that no sentence has
   introduced yet. Introduce a callable in the sentence right after the sample that first uses it.
2. **No silent non-default choice.** A `dtype=`, a seed, a size or a flag that the text does not explain
   changes the numbers for the reader who types the obvious call. State the reason in the text, or drop the
   choice. Where the choice is the subject (a chapter on dtypes), it is explained by the chapter.
3. **Values are not their positions.** Data that equal their index (`0, 1, 2, ...`) hide the difference between
   what is stored and where it is stored. Use distinct, meaningful values. Keep `arange` data only when the
   position *is* the point, and say so in one sentence.
4. **Not an accidental view.** A sample that the text calls "an array" must not silently be a view of a block
   that no name points to (`flags.owndata` is `False`). A view is allowed when it is the lesson.

**Enforce it.** A small audit script that lists, for every sample, `arange(...).reshape(...)` chains, `dtype=`
without a reason, and calls that come before the signature block of that callable. The NumPy book has one:
`~/claude/numpy-book/scripts/audit_examples.py`. It never fails. It prints a list for a person to read, and a
person decides each hit.

## 4. Retrofitting a finished book

Do it chapter by chapter in chapter order. Add the two sections, `--refill` only the new blocks' outputs,
run the STE check on the new prose, and re-read each quoted number against the output. Do not touch the
chapter's existing measured results while doing this.

## Anti-patterns

- A signature that was typed. It is wrong the day the library updates.
- A parameter table that restates the docstring. The value is the *consequence*, not the description.
- "How it works" that is a longer tour of the API. It is about the mechanism under the API.
- Depth by length. One executed block that shows the mechanism beats 500 more words.
