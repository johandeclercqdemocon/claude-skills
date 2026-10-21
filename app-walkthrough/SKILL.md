---
name: app-walkthrough
description: Produce a narrated screenshot walkthrough that proves a desktop application does what some documentation claims — open it, drive it by control name, capture each step, and write it up with the failures included. Use when Johan asks to demo an app, show that setup instructions work, document a GUI procedure, or make a "making-of" for one. Pairs with desktop-control, which does the actual driving.
---

# App walkthrough

Turns "the instructions work" into evidence: a numbered set of screenshots, an index, and a
written walkthrough that states what each image proves and what did not work.

The driving is `desktop-control`'s job — read that skill first, it owns the commands and the
constraints of this machine. This skill is the **procedure and the write-up**.

Reference output: `~/claude/ml-book/appendices/g-the-book-running-in-vs-code.md` (the walkthrough),
`~/claude/ml-book/artifacts/demo/` (the images and index), and
`~/claude/ml-book/HOW-WE-DROVE-VS-CODE.md` (the non-expert making-of).

## Before anything opens

1. **Name the claim.** A walkthrough exists to test one sentence of documentation — "follow
   Chapter 0 and VS Code is wired to the examples". Write that sentence down first. It decides
   which screenshots matter and which are filler.
2. **Find the money shot.** One image should carry the claim on its own. For the book it was the
   editor printing Chapter 9's three numbers. Plan the sequence backwards from it.
3. **Say what will appear on screen.** This puts windows on Johan's desktop and changes the state
   of his applications. Tell him what you are opening and why, and put the layout back afterwards.

## The sequence that works

```bash
D=~/.claude/skills/desktop-control/scripts/desktop.py
/usr/bin/python3 $D apps                      # is it visible at all
/usr/bin/python3 $D tree  "<app>"             # the real control names
/usr/bin/python3 $D click "<app>" "<control>"
/usr/bin/python3 $D read  "<app>"             # did the state actually change
/usr/bin/python3 $D shot  "<app>" NN-name.png # capture, late
```

- Number the files `01-`, `02-` … in the order a reader should see them, with a slug that says
  what the image is, not when it was taken.
- **Capture late.** A launched command is not a finished command. Wait for the output to be
  readable in `read` before `shot`, or you will photograph an empty pane and conclude the thing
  failed. That mistake has already been made once here.
- **One restoring step.** Put the application back as you found it and capture that too — it shows
  the walkthrough is reversible and it is the courteous thing to do to someone's workspace.

## The write-up

Two documents, because they have different readers.

**The walkthrough** — for someone who will follow the instructions. One section per image: the
image, then what it proves about the claim, in two or three sentences. Images that prove nothing
get cut, except one early "a control was pressed" step that establishes the app is being driven
rather than photographed.

**The making-of** — for someone who wants the method, written so a non-expert can read it. What
was tried, why the obvious approach was not used, what the accessibility layer is in plain words,
and what failed. Avoid jargon or gloss it on first use.

## The rule that makes it worth reading

**Publish the failures.** Every walkthrough on this machine has them, because Wayland blocks video
and synthetic keystrokes, and both failures are *silent* — the screencast API reports success and
writes a one-frame file, and `generate_keyboard_event` returns success and does nothing. State
them with the evidence that established them (`ffprobe -count_frames`, the three modes tried), and
state whether the limit is the machine or the method.

A walkthrough that shows only what worked is advertising, and will be read as such.

## Limits to promise honestly

- **Stills, not video**, on this machine.
- **No typing.** Drive the application through its own mechanisms instead — a task, a menu item, a
  defined command. This usually produces a better artefact than keystrokes would have.
- **Only applications that publish an accessibility tree.** Electron apps need
  `--force-renderer-accessibility` or `gsettings set org.gnome.desktop.interface
  toolkit-accessibility true`; that setting is Johan's desktop, so say before changing it, and say
  it needs changing back.

All of this is local work. No API inference is billed.
