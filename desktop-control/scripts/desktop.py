#!/usr/bin/env python3
"""Find and press controls in desktop applications, by name.

Uses AT-SPI, the accessibility layer, rather than screen coordinates. That
choice is what makes this work on Wayland: coordinate-based tools (xdotool,
pyautogui) can only reach XWayland clients, while AT-SPI reaches anything that
exposes an accessibility tree, and it addresses controls by name and role
instead of by pixel.

MUST run under the SYSTEM python (/usr/bin/python3), because `gi` is a system
package and is not in a uv venv.

    /usr/bin/python3 desktop.py apps
    /usr/bin/python3 desktop.py tree "gedit"
    /usr/bin/python3 desktop.py click "gedit" "Save"
    /usr/bin/python3 desktop.py type "gedit" "" "hello"
    /usr/bin/python3 desktop.py read "gedit"
"""

from __future__ import annotations

import re
import subprocess
import sys
import time

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi  # noqa: E402

CLICKABLE = {"push button", "toggle button", "check box", "radio button",
             "menu item", "link", "list item", "tab"}


def desktop():
    Atspi.init()
    return Atspi.get_desktop(0)


def apps() -> list:
    d = desktop()
    out = []
    for i in range(d.get_child_count()):
        try:
            out.append(d.get_child_at_index(i))
        except Exception:
            continue
    return out


def find_app(pattern: str):
    """First application whose name contains `pattern`, case-insensitively."""
    for app in apps():
        name = app.get_name() or ""
        if pattern.lower() in name.lower():
            return app
    raise SystemExit(f"no application matching {pattern!r}. Try: desktop.py apps")


def walk(node, depth: int = 0, limit: int = 4000):
    """Depth-first over the accessible tree, tolerating dead nodes."""
    stack = [(node, depth)]
    seen = 0
    while stack and seen < limit:
        current, d = stack.pop()
        seen += 1
        yield current, d
        try:
            for i in reversed(range(current.get_child_count())):
                stack.append((current.get_child_at_index(i), d + 1))
        except Exception:
            continue


def describe(node) -> str:
    try:
        name = node.get_name() or ""
        role = node.get_role_name() or "?"
        return f"{role}: {name!r}" if name else role
    except Exception:
        return "<gone>"


def find_control(app, label: str, roles: set[str] | None = None):
    """Exact name match first, then a substring match. Returns None if absent."""
    roles = roles or CLICKABLE
    fallback = None
    for node, _ in walk(app):
        try:
            if node.get_role_name() not in roles:
                continue
            name = node.get_name() or ""
        except Exception:
            continue
        if name == label:
            return node
        if fallback is None and label.lower() in name.lower():
            fallback = node
    return fallback


def do_click(node) -> str:
    """Press via the accessibility action, which needs no pointer and no focus."""
    try:
        n = Atspi.Action.get_n_actions(node)
    except Exception:
        n = 0
    if not n:
        raise SystemExit(f"{describe(node)} exposes no action")
    def action_name(index: int) -> str:
        # get_action_name is deprecated; the localized variant is the current API,
        # and older Atspi builds only have the deprecated one.
        for getter in ("get_localized_name", "get_action_name"):
            try:
                return getattr(Atspi.Action, getter)(node, index) or ""
            except (AttributeError, TypeError):
                continue
        return ""

    for i in range(n):
        if action_name(i).lower() in {"click", "press", "activate"}:
            Atspi.Action.do_action(node, i)
            return action_name(i) or "click"
    Atspi.Action.do_action(node, 0)
    return action_name(0) or "action 0"


def window_id(app_name: str) -> str:
    """The X window id for an application, via xwininfo.

    Needed because screen capture on this machine has exactly one working path:
    `xwd -id <window>`. Capturing the root window fails under XWayland with
    BadMatch, GNOME refuses ScreenshotArea over D-Bus, and its screencast writes
    a one-frame file. An application is capturable only if it is an X (XWayland)
    client -- `xlsclients` lists those.
    """
    tree = subprocess.run(["xwininfo", "-root", "-tree"],
                          capture_output=True, text=True, timeout=60).stdout
    best = None
    for line in tree.splitlines():
        if app_name.lower() not in line.lower():
            continue
        match = re.match(r"\s*(0x[0-9a-f]+)\s+\"(.*?)\"", line)
        if not match:
            continue
        size = re.search(r"(\d+)x(\d+)\+", line)
        area = int(size.group(1)) * int(size.group(2)) if size else 0
        if best is None or area > best[1]:
            best = (match.group(1), area)
    if best is None:
        raise SystemExit(f"no X window matching {app_name!r}. "
                         "Native Wayland windows cannot be captured.")
    return best[0]


def capture(app_name: str, out: str, width: int = 1200) -> str:
    """Screenshot one application window to a PNG."""
    wid = window_id(app_name)
    raw = "/tmp/_desktop_capture.xwd"
    with open(raw, "wb") as handle:
        subprocess.run(["xwd", "-id", wid, "-silent"],
                       stdout=handle, check=True, timeout=60)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw,
                    "-vf", f"scale={width}:-1", out], check=True, timeout=120)
    return f"{out} (window {wid})"


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        return
    command = sys.argv[1]

    if command == "apps":
        for app in apps():
            try:
                print(f"{app.get_name()!r:<34} {app.get_child_count()} window(s)")
            except Exception:
                continue
        return

    if command == "shot":
        print(capture(sys.argv[2], sys.argv[3]))
        return

    app = find_app(sys.argv[2])

    if command == "tree":
        for node, depth in walk(app):
            if depth > 12:
                continue
            print("  " * depth + describe(node))
        return

    if command == "read":
        for node, _ in walk(app):
            try:
                if node.get_role_name() in {"label", "static", "text", "heading"}:
                    name = node.get_name()
                    if name:
                        print(name)
            except Exception:
                continue
        return

    if command == "click":
        label = sys.argv[3]
        node = find_control(app, label)
        if node is None:
            raise SystemExit(f"no clickable control matching {label!r}; try `tree`")
        action = do_click(node)
        time.sleep(0.3)
        print(f"{action} -> {describe(node)}")
        return

    if command == "type":
        label, text = sys.argv[3], sys.argv[4]
        target = None
        for node, _ in walk(app):
            try:
                if node.get_role_name() in {"text", "entry", "password text", "terminal"}:
                    if not label or label.lower() in (node.get_name() or "").lower():
                        target = node
                        break
            except Exception:
                continue
        if target is None:
            raise SystemExit("no text field found; try `tree`")
        Atspi.EditableText.set_text_contents(target, text)
        print(f"typed into {describe(target)}")
        return

    raise SystemExit(f"unknown command {command!r}")


if __name__ == "__main__":
    main()
