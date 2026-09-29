"""
Find the current session's transcript for Claude Code or Codex, and condense it to the
conversation plus one line per tool call.

Raw transcripts are mostly tool output (file contents, command output), which reviewers don't
need. The condensed version keeps every user and assistant message, and summarizes each tool call
as one line (the tool name and its file path or command), so a reviewer can still see which files
were read and which skills ran.

`--since-days N` instead collects every session the user typed in during the last N days, across
all projects and both tools, and prints each user message with an excerpt of the reply it
answered. Sessions run by scripts (`claude -p`, `codex exec`) are skipped.

Usage:
    python3 transcript.py [--cwd DIR] [--tool auto|claude|codex] [--path FILE] [--out FILE]
    python3 transcript.py --since-days N [--out FILE]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path

# Blocks each tool injects into what the transcript records as user messages. Listed explicitly,
# because a generic tag pattern would also strip code and logs the user pasted.
INJECTED_TAGS = (
    "system-reminder",
    "local-command-caveat",
    "recommended_plugins",
    "environment_context",
    "user_instructions",
)
INJECTED_BLOCK = re.compile(
    r"<(" + "|".join(INJECTED_TAGS) + r")>.*?</\1>"
    r"|# AGENTS\.md instructions[^\n]*\s*<INSTRUCTIONS>.*?</INSTRUCTIONS>",
    re.DOTALL,
)
TOOL_SUMMARY_CHARS = 160
# A leading `cd <dir> &&` hides the actual command once the summary is truncated.
LEADING_CD = re.compile(r"""^cd\s+("[^"]*"|'[^']*'|\S+)\s*(&&|;)\s*""")
# Codex wraps shell commands in JavaScript: tools.exec_command({cmd:"..."}).
CODEX_EXEC_CMD = re.compile(r'cmd:\s*"((?:[^"\\]|\\.)*)"')
# How each tool marks a session someone typed in. `claude -p` records `sdk-cli`, and `codex exec`
# records `codex_exec`.
INTERACTIVE_CLAUDE_ENTRYPOINTS = ("cli", "claude-desktop")
AUTOMATED_CODEX_ORIGINATORS = ("codex_exec",)
REPLY_EXCERPT_CHARS = 2000
USER_EXCERPT_CHARS = 1500


@dataclass(frozen=True)
class Entry:
    """One line of the condensed transcript."""

    timestamp: str
    kind: str
    text: str


def claude_project_dir(cwd: Path, claude_home: Path) -> Path:
    """Return the folder where Claude Code stores transcripts for sessions started in `cwd`."""
    return claude_home / "projects" / re.sub(r"[^A-Za-z0-9]", "-", str(cwd))


def newest(paths: list[Path]) -> Path | None:
    """Return the most recently modified path, or None if there are none."""
    return max(paths, key=lambda path: path.stat().st_mtime, default=None)


def find_claude_transcript(cwd: Path, claude_home: Path) -> Path | None:
    """Return the most recently modified Claude Code transcript for `cwd`."""
    folder = claude_project_dir(cwd, claude_home)
    return newest(list(folder.glob("*.jsonl"))) if folder.is_dir() else None


def codex_session_meta(path: Path) -> dict[str, object]:
    """Return the session header on a Codex transcript's first line, or {} if there is none."""
    with path.open(encoding="utf-8") as handle:
        first = handle.readline()
    try:
        record = json.loads(first)
    except json.JSONDecodeError:
        return {}
    if record.get("type") != "session_meta" or not isinstance(record.get("payload"), dict):
        return {}
    return record["payload"]


def codex_session_cwd(path: Path) -> str | None:
    """Return the working directory recorded in a Codex transcript's header."""
    cwd = codex_session_meta(path).get("cwd")
    return cwd if isinstance(cwd, str) else None


def claude_session_info(path: Path) -> tuple[str | None, str | None]:
    """Return a Claude Code transcript's (entrypoint, cwd), from its first record that has them."""
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict) and "entrypoint" in record:
                return record.get("entrypoint"), record.get("cwd")
    return None, None


def interactive_sessions(since: float, claude_home: Path, codex_home: Path) -> list[Path]:
    """
    Return transcripts of sessions someone typed in, modified at or after `since`, oldest first.
    Transcripts of subagents and of scripted runs are excluded.
    """
    found: list[Path] = []
    for path in (claude_home / "projects").glob("*/*.jsonl"):
        if path.stat().st_mtime >= since and claude_session_info(path)[0] in INTERACTIVE_CLAUDE_ENTRYPOINTS:
            found.append(path)
    for path in (codex_home / "sessions").glob("**/rollout-*.jsonl"):
        if path.stat().st_mtime < since:
            continue
        originator = codex_session_meta(path).get("originator")
        if originator and originator not in AUTOMATED_CODEX_ORIGINATORS:
            found.append(path)
    return sorted(found, key=lambda path: path.stat().st_mtime)


def find_codex_transcript(cwd: Path, codex_home: Path) -> Path | None:
    """Return the most recently modified Codex transcript whose session started in `cwd`."""
    files = sorted(
        (codex_home / "sessions").glob("**/rollout-*.jsonl"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    return next((path for path in files if codex_session_cwd(path) == str(cwd)), None)


def clean_user_text(text: str) -> str:
    """Remove blocks the tool injected into a user message, keeping what the user typed."""
    return INJECTED_BLOCK.sub("", text).strip()


def shorten(detail: str) -> str:
    """
    Reduce a tool argument to its identifying part: the command inside Codex's JavaScript wrapper,
    without leading `cd` prefixes, on one line, truncated with an ellipsis.
    """
    if match := CODEX_EXEC_CMD.search(detail):
        detail = match.group(1).replace("\\n", " ")
    detail = " ".join(detail.split())
    while match := LEADING_CD.match(detail):
        detail = detail[match.end() :]
    return detail if len(detail) <= TOOL_SUMMARY_CHARS else detail[:TOOL_SUMMARY_CHARS] + "…"


def summarize_tool(name: str, arguments: object) -> str:
    """Summarize a tool call as its name plus the most identifying argument."""
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except json.JSONDecodeError:
            return f"{name}: {shorten(arguments)}"
    detail = ""
    if isinstance(arguments, dict):
        for key in ("skill", "file_path", "path", "command", "cmd", "pattern", "url", "query"):
            if key in arguments:
                value = arguments[key]
                detail = " ".join(value) if isinstance(value, list) else str(value)
                break
    return f"{name}: {shorten(detail)}" if detail else name


def parse_claude(lines: list[str]) -> list[Entry]:
    """Condense Claude Code transcript lines."""
    entries: list[Entry] = []
    for line in lines:
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if record.get("isSidechain") or record.get("type") not in ("user", "assistant"):
            continue
        message = record.get("message")
        if not isinstance(message, dict):
            continue
        timestamp = record.get("timestamp", "")
        content = message.get("content")
        if record["type"] == "user":
            if record.get("isMeta"):
                continue
            if isinstance(content, list):
                content = "\n".join(
                    part.get("text", "") for part in content if isinstance(part, dict) and part.get("type") == "text"
                )
            if isinstance(content, str) and (text := clean_user_text(content)):
                entries.append(Entry(timestamp, "USER", text))
            continue
        for part in content if isinstance(content, list) else []:
            if part.get("type") == "text" and part.get("text", "").strip():
                entries.append(Entry(timestamp, "ASSISTANT", part["text"].strip()))
            elif part.get("type") == "tool_use":
                entries.append(
                    Entry(timestamp, "TOOL", summarize_tool(part.get("name", "?"), part.get("input"))),
                )
    return entries


def parse_codex(lines: list[str]) -> list[Entry]:
    """Condense Codex transcript lines."""
    entries: list[Entry] = []
    for line in lines:
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if record.get("type") != "response_item":
            continue
        payload = record.get("payload", {})
        timestamp = record.get("timestamp", "")
        kind = payload.get("type")
        if kind == "message" and payload.get("role") in ("user", "assistant"):
            text = "\n".join(
                part.get("text", "") for part in payload.get("content", []) if isinstance(part, dict)
            )
            if payload["role"] == "user":
                text = clean_user_text(text)
                if text:
                    entries.append(Entry(timestamp, "USER", text))
            elif text.strip():
                entries.append(Entry(timestamp, "ASSISTANT", text.strip()))
        elif kind in ("function_call", "custom_tool_call"):
            arguments = payload.get("arguments", payload.get("input"))
            entries.append(Entry(timestamp, "TOOL", summarize_tool(payload.get("name", "?"), arguments)))
    return entries


def detect_format(lines: list[str]) -> str:
    """Return `codex` if the first line is a Codex session header, otherwise `claude`."""
    try:
        first = json.loads(lines[0]) if lines else {}
    except json.JSONDecodeError:
        first = {}
    return "codex" if first.get("type") == "session_meta" else "claude"


def render(entries: list[Entry], source: Path, tool: str) -> str:
    """Format condensed entries as plain text."""
    out = [f"# Condensed {tool} transcript: {source}", f"# {len(entries)} entries", ""]
    for entry in entries:
        stamp = entry.timestamp[:16].replace("T", " ")
        out.append(f"[{stamp}] {entry.kind}: {entry.text}")
    return "\n".join(out) + "\n"


@dataclass(frozen=True)
class Exchange:
    """A user message and the last assistant text before it (empty for a session's first message)."""

    timestamp: str
    reply: str
    user: str


def exchanges(entries: list[Entry]) -> list[Exchange]:
    """Pair each user message with the reply it answered: the last assistant text before it."""
    pairs: list[Exchange] = []
    reply = ""
    for entry in entries:
        if entry.kind == "ASSISTANT":
            reply = entry.text
        elif entry.kind == "USER":
            pairs.append(Exchange(entry.timestamp, reply, entry.text))
            reply = ""
    return pairs


def excerpt(text: str, limit: int) -> str:
    """Return the start of `text`, marked with an ellipsis when cut."""
    return text if len(text) <= limit else text[:limit] + "…"


def render_exchanges(source: Path, tool: str, cwd: str, pairs: list[Exchange]) -> str:
    """Format one session's exchanges as plain text."""
    out = [f"## {tool} session in {cwd} ({source.name})", ""]
    for pair in pairs:
        stamp = pair.timestamp[:16].replace("T", " ")
        if pair.reply:
            out.append(f"REPLY: {excerpt(pair.reply, REPLY_EXCERPT_CHARS)}")
        out.append(f"[{stamp}] USER: {excerpt(pair.user, USER_EXCERPT_CHARS)}")
        out.append("")
    return "\n".join(out) + "\n"


def collect_exchanges(since: float, claude_home: Path, codex_home: Path) -> tuple[str, int, int]:
    """Render every interactive session since `since`. Return (text, sessions, user messages)."""
    parts: list[str] = []
    sessions = messages = 0
    for path in interactive_sessions(since, claude_home, codex_home):
        lines = path.read_text(encoding="utf-8").splitlines()
        tool = detect_format(lines)
        if tool == "codex":
            entries, cwd = parse_codex(lines), codex_session_cwd(path)
        else:
            entries, cwd = parse_claude(lines), claude_session_info(path)[1]
        pairs = exchanges(entries)
        if not pairs:
            continue
        parts.append(render_exchanges(path, tool, cwd or "?", pairs))
        sessions += 1
        messages += len(pairs)
    header = f"# {sessions} interactive sessions, {messages} user messages\n\n"
    return header + "\n".join(parts), sessions, messages


def choose_transcript(cwd: Path, tool: str, claude_home: Path, codex_home: Path) -> Path | None:
    """Return the current session's transcript: the newest match for the requested tool."""
    candidates: list[Path] = []
    if tool in ("auto", "claude") and (found := find_claude_transcript(cwd, claude_home)):
        candidates.append(found)
    if tool in ("auto", "codex") and (found := find_codex_transcript(cwd, codex_home)):
        candidates.append(found)
    return newest(candidates)


def main(argv: list[str] | None = None) -> int:
    """Run the CLI."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cwd", type=Path, default=Path.cwd(), help="the session's working directory")
    parser.add_argument("--tool", choices=("auto", "claude", "codex"), default="auto")
    parser.add_argument("--path", type=Path, help="a transcript file to condense, instead of finding one")
    parser.add_argument("--out", type=Path, help="write here instead of standard output")
    parser.add_argument(
        "--since-days",
        type=float,
        help="collect user messages and the replies they answered from every interactive session "
        "in the last N days, across projects and both tools",
    )
    args = parser.parse_args(argv)

    claude_home = Path(os.environ.get("CLAUDE_HOME", "~/.claude")).expanduser()
    codex_home = Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser()
    if args.since_days is not None:
        since = time.time() - args.since_days * 86400
        text, sessions, messages = collect_exchanges(since, claude_home, codex_home)
        if args.out:
            args.out.write_text(text, encoding="utf-8")
            print(f"Wrote {len(text):,} characters ({sessions} sessions, {messages} messages) to {args.out}")
        else:
            sys.stdout.write(text)
        return 0
    source = args.path or choose_transcript(args.cwd.resolve(), args.tool, claude_home, codex_home)
    if source is None:
        print(f"No transcript found for {args.cwd} ({args.tool}).", file=sys.stderr)
        return 1

    lines = source.read_text(encoding="utf-8").splitlines()
    tool = detect_format(lines)
    entries = parse_codex(lines) if tool == "codex" else parse_claude(lines)
    text = render(entries, source, tool)
    if args.out:
        args.out.write_text(text, encoding="utf-8")
        print(f"Wrote {len(text):,} characters ({len(entries)} entries) from {source} to {args.out}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
