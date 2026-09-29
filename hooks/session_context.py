"""
Hook script that adds context to Claude Code and Codex sessions. `make sync` installs it in both
tools. Whatever it prints is added to what the agent sees.

    session_context.py time    On every user message: the time it was sent, so the agent can tell
                               when hours or days have passed between messages.
    session_context.py style   After compaction: a reminder of the communication style in
                               global/style.md.

Standard library only, and it never fails loudly: a hook that errors would get in the way of every
message.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

STYLE_PATH = Path(__file__).resolve().parent.parent / "global" / "style.md"
STYLE_HEADER = "Reminder of the communication style from the user's global instructions. Follow it in every reply:"


def time_line(now: datetime) -> str:
    """Return the line added to each user message, e.g. `Sent Mon 2026-09-28 21:40 PDT`."""
    return f"User message sent {now.strftime('%a %Y-%m-%d %H:%M %Z')}"


def style_reminder(style_path: Path) -> str:
    """Return the style reminder, or an empty string if the style file doesn't exist."""
    if not style_path.is_file():
        return ""
    return f"{STYLE_HEADER}\n\n{style_path.read_text(encoding='utf-8').strip()}"


def main(argv: list[str]) -> int:
    """Print the context for the requested hook. Always exits 0."""
    command = argv[0] if argv else ""
    try:
        if command == "time":
            print(time_line(datetime.now().astimezone()))
        elif command == "style" and (text := style_reminder(STYLE_PATH)):
            print(text)
    except Exception:  # noqa: BLE001 - a failing hook must never block the user's message
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
