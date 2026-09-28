"""
Find the current session's transcript for Claude Code or Codex, and condense it to the
conversation plus one line per tool call.

Raw transcripts are mostly tool output (file contents, command output), which reviewers don't
need. The condensed version keeps every user and assistant message, and summarizes each tool call
as one line (the tool name and its file path or command), so a reviewer can still see which files
were read and which skills ran.

Usage:
    python3 transcript.py [--cwd DIR] [--tool auto|claude|codex] [--path FILE] [--out FILE]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
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


def codex_session_cwd(path: Path) -> str | None:
    """Return the working directory recorded on a Codex transcript's first line."""
    with path.open(encoding="utf-8") as handle:
        first = handle.readline()
    try:
        record = json.loads(first)
    except json.JSONDecodeError:
        return None
    if record.get("type") != "session_meta":
        return None
    return record.get("payload", {}).get("cwd")


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


def summarize_tool(name: str, arguments: object) -> str:
    """Summarize a tool call as its name plus the most identifying argument."""
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except json.JSONDecodeError:
            detail = arguments
            return f"{name}: {' '.join(detail.split())[:TOOL_SUMMARY_CHARS]}"
    detail = ""
    if isinstance(arguments, dict):
        for key in ("skill", "file_path", "path", "command", "cmd", "pattern", "url", "query"):
            if key in arguments:
                value = arguments[key]
                detail = " ".join(value) if isinstance(value, list) else str(value)
                break
    return f"{name}: {' '.join(detail.split())[:TOOL_SUMMARY_CHARS]}" if detail else name


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
    args = parser.parse_args(argv)

    claude_home = Path(os.environ.get("CLAUDE_HOME", "~/.claude")).expanduser()
    codex_home = Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser()
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
