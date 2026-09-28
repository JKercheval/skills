"""Tests for skills/reflect/scripts/transcript.py, using small synthetic transcripts."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest

import transcript as tr


def claude_lines() -> list[str]:
    """A small Claude Code transcript: user text, injected reminder, assistant text, tool use."""
    records = [
        {"type": "user", "timestamp": "2026-09-28T10:00:00Z", "message": {"content": "Fix the bug in slug.py"}},
        {
            "type": "user",
            "timestamp": "2026-09-28T10:00:01Z",
            "message": {"content": "<system-reminder>Injected context.</system-reminder>"},
        },
        {
            "type": "user",
            "timestamp": "2026-09-28T10:00:02Z",
            "message": {"content": "Also <system-reminder>noise</system-reminder>keep this part"},
        },
        {
            "type": "assistant",
            "timestamp": "2026-09-28T10:00:03Z",
            "message": {
                "content": [
                    {"type": "thinking", "thinking": "private reasoning"},
                    {"type": "text", "text": "I'll read the file first."},
                    {"type": "tool_use", "name": "Read", "input": {"file_path": "/repo/slug.py"}},
                    {"type": "tool_use", "name": "Skill", "input": {"skill": "tdd", "args": "slugify"}},
                ],
            },
        },
        {
            "type": "user",
            "timestamp": "2026-09-28T10:00:04Z",
            "message": {"content": [{"type": "tool_result", "content": "x" * 5000}]},
        },
        {
            "type": "assistant",
            "isSidechain": True,
            "timestamp": "2026-09-28T10:00:05Z",
            "message": {"content": [{"type": "text", "text": "subagent chatter"}]},
        },
        {"type": "attachment", "timestamp": "2026-09-28T10:00:06Z"},
        "not json",
    ]
    return [record if isinstance(record, str) else json.dumps(record) for record in records]


def codex_lines(cwd: str = "/repo") -> list[str]:
    """A small Codex transcript: session header, injected context, user and assistant messages, tool calls."""

    def message(role: str, text: str, part_type: str) -> dict[str, object]:
        return {
            "type": "response_item",
            "timestamp": "2026-09-28T11:00:00Z",
            "payload": {"type": "message", "role": role, "content": [{"type": part_type, "text": text}]},
        }

    records = [
        {"type": "session_meta", "payload": {"cwd": cwd}},
        message("developer", "<skills_instructions>...</skills_instructions>", "input_text"),
        message("user", "# AGENTS.md instructions\n\n<INSTRUCTIONS>\nglobal rules\n</INSTRUCTIONS>", "input_text"),
        message("user", "# AGENTS.md instructions for /repo\n\n<INSTRUCTIONS>\nrepo rules\n</INSTRUCTIONS>", "input_text"),
        message("user", "<environment_context>\n<cwd>/repo</cwd>\n</environment_context>", "input_text"),
        message("user", "<recommended_plugins>\nDropbox\n</recommended_plugins>", "input_text"),
        message("user", "What could commit abc123 break?", "input_text"),
        message("assistant", "I'll use the blast-radius skill.", "output_text"),
        {
            "type": "response_item",
            "timestamp": "2026-09-28T11:00:01Z",
            "payload": {"type": "function_call", "name": "shell", "arguments": json.dumps({"command": ["git", "show", "abc123"]})},
        },
        {
            "type": "response_item",
            "timestamp": "2026-09-28T11:00:02Z",
            "payload": {"type": "custom_tool_call", "name": "exec", "input": "cat SKILL.md\n  && ls"},
        },
        {"type": "response_item", "payload": {"type": "function_call_output", "output": "y" * 5000}},
        {"type": "event_msg", "payload": {"type": "token_count"}},
    ]
    return [json.dumps(record) for record in records]


def test_parse_claude_keeps_conversation_and_one_line_per_tool_call() -> None:
    entries = tr.parse_claude(claude_lines())

    assert [(entry.kind, entry.text) for entry in entries] == [
        ("USER", "Fix the bug in slug.py"),
        ("USER", "Also keep this part"),
        ("ASSISTANT", "I'll read the file first."),
        ("TOOL", "Read: /repo/slug.py"),
        ("TOOL", "Skill: tdd"),
    ]


def test_parse_codex_drops_injected_context_and_tool_output() -> None:
    entries = tr.parse_codex(codex_lines())

    assert [(entry.kind, entry.text) for entry in entries] == [
        ("USER", "What could commit abc123 break?"),
        ("ASSISTANT", "I'll use the blast-radius skill."),
        ("TOOL", "shell: git show abc123"),
        ("TOOL", "exec: cat SKILL.md && ls"),
    ]


def test_clean_user_text_keeps_pasted_tags_that_are_not_injected() -> None:
    pasted = "<harness>my pasted config</harness>"

    assert tr.clean_user_text(pasted) == pasted


def test_summarize_tool_truncates_long_details() -> None:
    summary = tr.summarize_tool("Bash", {"command": "echo " + "a" * 500})

    assert summary.startswith("Bash: echo aaa")
    assert len(summary) == len("Bash: ") + tr.TOOL_SUMMARY_CHARS


def test_summarize_tool_without_known_argument_is_just_the_name() -> None:
    assert tr.summarize_tool("TodoWrite", {"todos": []}) == "TodoWrite"


def test_detect_format() -> None:
    assert tr.detect_format(codex_lines()) == "codex"
    assert tr.detect_format(claude_lines()) == "claude"
    assert tr.detect_format([]) == "claude"


def test_claude_project_dir_replaces_every_non_alphanumeric() -> None:
    folder = tr.claude_project_dir(Path("/Users/me/Application Support/my.repo"), Path("/home/.claude"))

    assert folder == Path("/home/.claude/projects/-Users-me-Application-Support-my-repo")


def write_file(path: Path, lines: list[str], mtime: float) -> Path:
    """Write transcript lines to `path` and set its modification time."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")
    os.utime(path, (mtime, mtime))
    return path


def test_find_claude_transcript_picks_newest_in_project_folder(tmp_path: Path) -> None:
    cwd = Path("/work/repo")
    folder = tr.claude_project_dir(cwd, tmp_path)
    now = time.time()
    write_file(folder / "old.jsonl", claude_lines(), now - 100)
    newest = write_file(folder / "new.jsonl", claude_lines(), now)

    assert tr.find_claude_transcript(cwd, tmp_path) == newest
    assert tr.find_claude_transcript(Path("/other"), tmp_path) is None


def test_find_codex_transcript_matches_session_cwd(tmp_path: Path) -> None:
    now = time.time()
    sessions = tmp_path / "sessions" / "2026" / "09" / "28"
    mine = write_file(sessions / "rollout-a.jsonl", codex_lines("/work/repo"), now - 50)
    write_file(sessions / "rollout-b.jsonl", codex_lines("/other/repo"), now)

    assert tr.find_codex_transcript(Path("/work/repo"), tmp_path) == mine
    assert tr.find_codex_transcript(Path("/nowhere"), tmp_path) is None


@pytest.mark.parametrize(("tool", "expected"), [("auto", "codex"), ("claude", "claude"), ("codex", "codex")])
def test_choose_transcript_picks_newest_for_requested_tool(tmp_path: Path, tool: str, expected: str) -> None:
    cwd = Path("/work/repo")
    now = time.time()
    claude_home = tmp_path / "claude"
    codex_home = tmp_path / "codex"
    claude_file = write_file(tr.claude_project_dir(cwd, claude_home) / "s.jsonl", claude_lines(), now - 100)
    codex_file = write_file(codex_home / "sessions" / "rollout-x.jsonl", codex_lines(str(cwd)), now)

    chosen = tr.choose_transcript(cwd, tool, claude_home, codex_home)

    assert chosen == {"claude": claude_file, "codex": codex_file}[expected]


def test_main_writes_condensed_file(tmp_path: Path) -> None:
    source = write_file(tmp_path / "t.jsonl", claude_lines(), time.time())
    out = tmp_path / "out.txt"

    exit_code = tr.main(["--path", str(source), "--out", str(out)])

    text = out.read_text()
    assert exit_code == 0
    assert text.startswith(f"# Condensed claude transcript: {source}\n# 5 entries\n")
    assert "[2026-09-28 10:00] USER: Fix the bug in slug.py" in text
    assert "x" * 100 not in text


def test_main_reports_missing_transcript(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CLAUDE_HOME", str(tmp_path / "claude"))
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "codex"))

    assert tr.main(["--cwd", str(tmp_path)]) == 1
