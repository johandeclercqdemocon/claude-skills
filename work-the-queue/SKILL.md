---
name: work-the-queue
description: Work a multi-item task through to the end without stopping to ask between items. Use whenever Johan asks for something that spans many files, chapters, tests or repos — "do all of X", "fix every Y", "continue", "auto continue", "keep going" — and whenever a queue of similar units of work has been agreed. Covers what to do per item, what still justifies stopping, and how to report.
---

# Work the queue

**Standing instruction from Johan: once the work is agreed, do it. Do not ask between items.**

"Continue" means continue to the end of the queue, not to the end of the next item. He has
already said yes; asking again spends his attention on a decision he has made.

## Build the queue first, and make it visible

Before the first item, say what the queue is and in what order — one line, not a plan document.
A queue he can see is a queue he can redirect. A queue in your head is one he has to interrupt to
inspect.

Order by what the reader or user meets first, not by what is easiest. Difficulty compounds in the
order someone encounters it.

## Per item

1. **Read the thing before changing it.** Every item in a queue looks like the last one until you
   read it; they are not the same, and a template applied to all of them produces filler.
2. **Measure before you write.** If the item involves a claim, run the code that establishes it.
   Never carry a number from one item to the next on the assumption it still holds.
3. **Verify that item alone**, with the cheapest check that covers it — a single-file check, the
   tests that touch it. Full sweeps belong at the end, not after every item.
4. **Commit it**, with a message that says what was wrong and what the evidence was. One commit
   per item keeps the work reviewable and revertible item by item.
5. **Go to the next one.** No summary, no check-in, no "shall I continue".

## What still justifies stopping

Few things, and none of them are "this item was bigger than expected".

- **Destructive or outward-facing actions** not already covered by the agreed task — deleting,
  force-pushing, publishing, sending, paying, changing a remote's visibility.
- **A finding that invalidates the rest of the queue.** If item 3 shows the whole approach is
  wrong, stop and say so; finishing items 4 through 20 on a wrong premise wastes more of his time
  than the interruption costs.
- **Genuine ambiguity that changes the work**, where proceeding on either reading produces
  something that has to be thrown away. Ambiguity you can resolve by picking the sensible option
  and saying which, you resolve.
- **Someone else's work in the tree.** Another session's files are not yours to edit. Note them
  and leave them.

A failing check is not a reason to stop. Fix it, or record it honestly and carry on with the rest.

## Do not pad to fill the queue

Some items will turn out not to need the work. Say so and move on — a short entry reported as
already adequate is a result, and inflating it to match its neighbours is a lie about the state of
the thing. This matters most when the queue was defined by a metric like word count: the metric
located the problem, it does not define the fix.

## Watch for damage your own changes do

Fixing item 3 can make item 7 redundant, contradictory or wrong. When you expand, define or
restructure something early in a queue, check whether a later item now duplicates it — and fix
that when you reach it rather than leaving two versions of the same explanation.

## Report at the end

One report, covering the whole queue:

- a table of what changed, per item, with before/after where there is a number
- what was deliberately left alone, and why
- anything deferred — rebuilt artefacts, full sweeps, stale counts — stated plainly rather than
  left for him to discover

Between items, keep output short. He is watching progress, not reading a chapter about it.

## Background work

Long verifications run in the background while the next item is read and drafted. Never idle
waiting for a check to finish when the next item can be started — but never commit an item whose
check has not come back either.

Two heavy jobs at once on this machine produce false timeouts and have twice been misreported as
failures. One at a time, and cap thread use when he is working: `OMP_NUM_THREADS=8`.
