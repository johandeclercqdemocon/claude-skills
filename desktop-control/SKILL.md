---
name: desktop-control
description: Find and press buttons, read labels and fill fields in DESKTOP applications on this machine, by control name rather than screen coordinates. Use when Johan asks to click something in an app, drive a GUI, check that a desktop program works, or automate a window. Not for web pages — use the selenium skill for those.
---

# Desktop control

Drives desktop applications through **AT-SPI**, the accessibility layer. Controls are addressed by
**name and role**, never by pixel coordinates.

That choice is the whole reason this works here. **This machine runs Wayland**
(`XDG_SESSION_TYPE=wayland`), and under Wayland the coordinate-based tools cannot do the job:
`xdotool` and `pyautogui` reach only XWayland clients, and capturing the root window fails with
`BadMatch`. AT-SPI reaches anything that exposes an accessibility tree, and it is immune to window
position, scaling and overlap.

Verified on this machine: a GTK button pressed three times by name, label read back as
`clicked 3`.

## Run it with the SYSTEM python

`gi` is a system package and is **not** in any uv venv. Always:

```bash
/usr/bin/python3 ~/.claude/skills/desktop-control/scripts/desktop.py <command>
```

## Commands

```bash
desktop.py apps                          # applications AT-SPI can see
desktop.py tree  "<app>"                 # the accessible tree — use this first
desktop.py read  "<app>"                 # all label/text content
desktop.py click "<app>" "<control>"     # press by name (exact, then substring)
desktop.py type  "<app>" "<field>" "txt" # set a text field ("" = first field)
desktop.py shot  "<app>" out.png         # screenshot that window
```

`<app>` is a case-insensitive substring of the application name from `apps`.

## The order that works

1. **`apps`** — confirm the application is visible at all. If it is not, it either is not running
   or does not expose accessibility (see below).
2. **`tree`** — read the actual control names. Guessing a label wastes a round trip; the tree tells
   you what is really there, including the window-manager buttons (`Minimize`, `Maximize`, `Close`)
   which are real and clickable.
3. **`click`** — then **`read`** to confirm the state changed. A click that reports success only
   means the action fired, not that the application did what you expected.

## What this cannot reach

**Applications that expose no accessibility tree.** Some Qt, Java and game applications, and
Electron apps that have not enabled it. If `apps` does not list it, nothing here will work.

**Electron apps, including VS Code, may need a flag.** Launch with
`--force-renderer-accessibility`, or enable accessibility first:

```bash
gsettings set org.gnome.desktop.interface toolkit-accessibility true
```

That setting is currently **false** on this machine. Changing it is a user-level setting needing no
sudo, but it is Johan's desktop — say what you are changing and why before changing it.

**Raw pointer and keyboard injection.** There is none here. `ydotool` would provide it on Wayland
but is not installed and needs uinput permissions, and `sudo` requires a password on this machine,
so a system package cannot be installed unattended. Do not promise coordinate clicking.

**Screenshots work, but only one way.** `desktop.py shot` captures a single window with
`xwd -id` and converts it with ffmpeg. Everything else on this machine fails: `xwd -root` gives
`BadMatch` under XWayland, GNOME refuses `org.gnome.Shell.Screenshot.ScreenshotArea` with
`AccessDenied`, and its screencast D-Bus API reports success while writing a `.webm` containing
**exactly one frame** — so **there is no video here**, only stills. A window is capturable only if
it is an X (XWayland) client; `xlsclients` lists those.

**Synthetic keystrokes do not work at all.** `Atspi.generate_keyboard_event` is a no-op in every
mode — `STRING`, keycode `PRESSRELEASE`, keysym `SYM` — even against a confirmed X client with
XTEST present on the server, because Mutter does not route synthetic input from the accessibility
bus under Wayland. **Do not promise typing.** To run a command in an editor, use the application's
own mechanism instead: a VS Code task under *Terminal → Run Task…* is how the book's examples were
driven without a keystroke.

## Rules

- **Read before you act.** `tree` first, every time. The tree is cheap and a wrong click is not.
- **Confirm with `read`.** Report what the application actually shows afterwards, not that the
  command returned zero.
- **These are Johan's real windows.** Do not close, save over, or submit anything in an application
  he did not ask you to touch. Ask before anything destructive or outward-facing — sending,
  publishing, deleting, paying.
- Launching a GUI application puts a window on his screen. Say so, and close what you opened.
- **Capture late.** A command that has been launched is not a command that has finished. Capturing
  too early shows an empty pane and invites the wrong conclusion — that happened while producing
  the book's demo, and the output had in fact been correct all along.

All of this is local: no API inference is billed.
